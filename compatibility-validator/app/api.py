"""Read-only HTTP API with revision-consistent validation and bounded requests."""

import logging
import csv
import threading
from collections import OrderedDict
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .catalog import CatalogUnavailable, LiveCatalog
from .config import (COMPAT_CACHE_MAX_ENTRIES, DATA_PATH, MAX_REQUEST_BYTES, PROFILE_PATH,
                     STATIC_DIR, MAX_PROJECT_BYTES, MAX_BREAKOUT_BYTES)
from .models import ConnectionRequest, Fabric, HardwareInspection, PortEvaluation, RecommendationRequest
from .rules import decide, evaluate, validate_connection
from .hardware import effective_host, inspect_hardware, identity_checks, qualify
from .recommendations import recommend
from .topology_models import BreakoutRequest, ProjectRequest, ProjectCSV
from .topology import validate_breakout
from .projects import StaleProject, validate_project, import_project_csv, bom_csv, connection_csv, CSV_FIELDS

VERSION = "0.04-dev"
logger = logging.getLogger("uvicorn.error")
app = FastAPI(title="NVIDIA Networking Compatibility Validator", version=VERSION)
catalog = LiveCatalog(DATA_PATH, PROFILE_PATH)
_cache = OrderedDict()
_cache_lock = threading.RLock()
_cache_revision = None


class BodyLimitMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            await self.app(scope, receive, send)
            return
        body = bytearray()
        limit = MAX_PROJECT_BYTES if scope["path"] in {"/api/project", "/api/project/import-csv", "/api/project/bom.csv", "/api/project/connections.csv"} else MAX_BREAKOUT_BYTES if scope["path"] == "/api/breakout" else MAX_REQUEST_BYTES
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > limit:
                await JSONResponse({"detail": "Request body too large"}, status_code=413)(scope, receive, send)
                return
            body.extend(chunk)
            if not message.get("more_body"):
                break
        consumed = False

        async def replay():
            nonlocal consumed
            if consumed:
                return await receive()
            consumed = True
            return {"type": "http.request", "body": bytes(body), "more_body": False}

        await self.app(scope, replay, send)


app.add_middleware(BodyLimitMiddleware)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def response_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    if request.url.path == "/":
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'self'"
    return response


@app.exception_handler(CatalogUnavailable)
async def unavailable(_request, _exc):
    return JSONResponse(status_code=503, content={"detail": "Service unavailable"})


@app.exception_handler(Exception)
async def server_error(_request, exc):
    logger.error("Unexpected request failure", exc_info=(type(exc), exc, exc.__traceback__))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def metadata(snapshot, state):
    return {**{key: snapshot[key] for key in ("revision", "schema_version", "profiles_schema_version", "snapshot_date", "generated_at")},
            "application_version": VERSION, "device_count": len(snapshot["devices"]),
            "interconnect_count": len(snapshot["interconnects"]),
            "hardware_profile_count": len(snapshot["hardware_profiles"]),
            "fiber_assembly_count": len(snapshot["fiber_assemblies"]), "catalog": state}


def snapshot_for_revision(revision=None):
    snapshot = catalog.get()
    if revision is not None and snapshot["revision"] != revision:
        raise HTTPException(409, "Catalog changed; reload the selection before validating")
    return snapshot


def find_group(snapshot, device_id, group_id):
    device = next((d for d in snapshot["devices"] if d["id"] == device_id), None)
    if not device:
        raise HTTPException(404, "Unknown device")
    group = next((g for g in device["port_groups"] if g["id"] == group_id), None)
    if not group:
        raise HTTPException(404, "Unknown port group")
    return group


def evaluated_products(snapshot, device_id, group_id, fabric=None, mode_id=None):
    global _cache_revision
    group = find_group(snapshot, device_id, group_id)
    if mode_id and mode_id not in {m["id"] for m in group["modes"]}:
        raise HTTPException(422, "Unknown mode for selected port group")
    key = (snapshot["revision"], device_id, group_id, fabric, mode_id)
    with _cache_lock:
        if _cache_revision != snapshot["revision"]:
            _cache.clear()
            _cache_revision = snapshot["revision"]
        if key in _cache:
            _cache.move_to_end(key)
            return _cache[key]
    result = [{**item, "validation": evaluate(group, item, fabric, mode_id)} for item in snapshot["interconnects"]]
    with _cache_lock:
        _cache[key] = result
        _cache.move_to_end(key)
        while len(_cache) > COMPAT_CACHE_MAX_ENTRIES:
            _cache.popitem(last=False)
    return result


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/healthz")
def healthz():
    catalog.get()
    return {"status": "ok"}


@app.get("/api/meta")
def meta():
    return metadata(*catalog.view())


@app.get("/api/catalog")
def catalog_bundle():
    snapshot, state = catalog.view()
    return {"meta": metadata(snapshot, state), "devices": snapshot["devices"], "products": snapshot["interconnects"],
            "hardware_profiles": snapshot["hardware_profiles"], "fiber_assemblies": snapshot["fiber_assemblies"]}


@app.get("/api/devices")
def devices(response: Response):
    snapshot = catalog.get()
    response.headers["X-Catalog-Revision"] = snapshot["revision"]
    return snapshot["devices"]


@app.get("/api/products")
def products():
    snapshot = catalog.get()
    return {"revision": snapshot["revision"], "products": snapshot["interconnects"]}


@app.get("/api/evaluate")
def evaluate_products(
    device_id: str = Query(..., min_length=1, max_length=128),
    port_group_id: str = Query(..., min_length=1, max_length=64),
    fabric: Fabric | None = None,
    mode_id: str | None = Query(None, min_length=1, max_length=64),
    revision: str | None = Query(None, pattern=r"^[0-9a-f]{12}$"),
):
    snapshot = snapshot_for_revision(revision)
    return {"revision": snapshot["revision"], "device_id": device_id, "port_group_id": port_group_id,
            "products": evaluated_products(snapshot, device_id, port_group_id, fabric, mode_id)}


@app.get("/api/compatible")
def compatible(
    device_id: str = Query(..., min_length=1, max_length=128),
    port_group_id: str = Query(..., min_length=1, max_length=64),
):
    snapshot = catalog.get()
    return [{**item, "revision": snapshot["revision"],
             "compatibility_confidence": item["validation"]["match_type"],
             "compatibility_reasons": [c["message"] for c in item["validation"]["checks"]]}
            for item in evaluated_products(snapshot, device_id, port_group_id)
            if item["status"] == "active" and item["validation"]["status"] in {"compatible", "conditional"}]


@app.post("/api/connection")
def connection(request: ConnectionRequest):
    snapshot = snapshot_for_revision(request.revision)
    try:
        result = validate_connection(snapshot, request)
    except KeyError as exc:
        # resolve() only emits constant public lookup errors.
        raise HTTPException(404, exc.args[0]) from None
    return {**result, "application_version": VERSION, "evaluated_at": datetime.now(timezone.utc).isoformat()}


@app.post("/api/hardware/inspect")
def hardware_inspection(request: HardwareInspection):
    snapshot = snapshot_for_revision(request.revision)
    try:
        return inspect_hardware(snapshot, request)
    except KeyError as exc:
        raise HTTPException(404, exc.args[0]) from None


@app.post("/api/evaluate")
def evaluate_hardware_products(request: PortEvaluation):
    snapshot = snapshot_for_revision(request.revision)
    try:
        _, group, profile = effective_host(snapshot, request)
    except KeyError as exc:
        raise HTTPException(404, exc.args[0]) from None
    if request.mode_id and request.mode_id not in {m["id"] for m in group["modes"]}:
        raise HTTPException(422, "Unknown mode for selected hardware profile")
    products = []
    for item in snapshot["interconnects"]:
        validation = evaluate(group, item, request.fabric, request.mode_id)
        validation["technical_status"] = validation["status"]
        validation["checks"] += identity_checks(profile, request.runtime)
        validation["status"] = decide(validation["checks"])
        validation["qualification"] = qualify(snapshot, request, item, request.fabric, request.mode_id)
        products.append({**item, "validation": validation})
    return {"revision": snapshot["revision"], "device_id": request.device_id,
            "port_group_id": request.port_group_id, "products": products,
            "hardware": inspect_hardware(snapshot, request)}


@app.post("/api/recommendations")
def recommendations(request: RecommendationRequest):
    snapshot = snapshot_for_revision(request.revision)
    try:
        result = recommend(snapshot, request)
    except KeyError as exc:
        raise HTTPException(404, exc.args[0]) from None
    return {**result, "application_version": VERSION, "evaluated_at": datetime.now(timezone.utc).isoformat()}


@app.post("/api/breakout")
def breakout(request: BreakoutRequest):
    snapshot = snapshot_for_revision(request.revision)
    try:
        result = validate_breakout(snapshot, request)
    except KeyError as exc:
        raise HTTPException(404, exc.args[0]) from None
    return {**result, "application_version": VERSION, "evaluated_at": datetime.now(timezone.utc).isoformat()}


def project_result(request):
    snapshot = snapshot_for_revision(request.revision)
    try:
        result = validate_project(snapshot, request)
    except StaleProject as exc:
        raise HTTPException(409, str(exc)) from None
    return {**result, "application_version": VERSION, "evaluated_at": datetime.now(timezone.utc).isoformat()}


@app.post("/api/project")
def project(request: ProjectRequest):
    return project_result(request)


@app.post("/api/project/import-csv")
def project_csv_import(request: ProjectCSV):
    snapshot = snapshot_for_revision(request.revision)
    try:
        imported = import_project_csv(snapshot, request)
    except (ValueError, csv.Error) as exc:
        # Pydantic's rich exception text may contain raw input; report its public
        # summary separately instead of leaking unbounded CSV content.
        from pydantic import ValidationError
        detail = "CSV project fails validation: " + exc.errors()[0]["msg"] if isinstance(exc, ValidationError) else str(exc)
        raise HTTPException(422, detail) from None
    return {"revision": snapshot["revision"], "project": imported.model_dump()}


def csv_response(content, filename):
    return Response(content="\ufeff" + content, media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@app.post("/api/project/bom.csv")
def project_bom_export(request: ProjectRequest):
    return csv_response(bom_csv(project_result(request)), "project-bom.csv")


@app.post("/api/project/connections.csv")
def project_connections_export(request: ProjectRequest):
    snapshot_for_revision(request.revision)
    try:
        content = connection_csv(request)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    return csv_response(content, "project-connections.csv")


@app.get("/api/project/template.csv")
def project_csv_template():
    return csv_response(",".join(CSV_FIELDS) + "\r\n", "project-template.csv")
