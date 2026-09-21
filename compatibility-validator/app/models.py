"""Strict input contracts. Unknown hardware facts are represented by null/empty lists."""

import re
from datetime import date, datetime
from typing import Annotated, Any, Literal
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Text = Annotated[str, Field(min_length=1, max_length=4096)]
Identifier = Annotated[str, Field(min_length=1, max_length=256)]
Positive = Annotated[int, Field(gt=0, le=100000)]
Distance = Annotated[float, Field(gt=0, le=1000000, allow_inf_nan=False)]
Fabric = Literal["ETH", "IB", "NVL"]
Connector = Literal["OSFP", "QSFP-DD", "QSFP112", "QSFP56", "QSFP28", "QSFP+", "SFP56", "SFP28", "SFP+", "MMC-12", "MPO-12", "RJ45"]
Outcome = Literal["compatible", "conditional", "unknown", "incompatible"]


class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", validate_default=True)


def check_url(value: str | None) -> str | None:
    if value is not None:
        url = urlsplit(value)
        if url.scheme not in {"https", "http"} or not url.hostname or url.username or url.password:
            raise ValueError("source URL must be an HTTP(S) URL without credentials")
    return value


def unique(values: list[Any], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {label}")


class PortMode(StrictModel):
    id: Annotated[str, Field(min_length=1, max_length=64)]
    links: Annotated[int, Field(ge=1, le=16)]
    speed_gbps: Positive
    electrical_lanes: Annotated[int, Field(ge=1, le=16)] | None = None
    lane_rate_gbps: Distance | None = None
    fec: list[Text] = Field(default_factory=list)

    @property
    def capacity(self) -> int:
        return self.links * self.speed_gbps

    @model_validator(mode="after")
    def consistent(self):
        unique(self.fec, "FEC setting")
        if self.electrical_lanes and self.lane_rate_gbps and abs(self.electrical_lanes * self.lane_rate_gbps - self.capacity) > 0.01:
            raise ValueError("electrical lanes and nominal lane rate disagree with mode capacity")
        return self


class PortGroup(StrictModel):
    id: Annotated[str, Field(min_length=1, max_length=64)]
    label: Text
    count: Annotated[int, Field(ge=0)] | None = None
    connector_family: Connector
    accepted_connector_families: list[Connector] = Field(default_factory=list)
    accepted_interface_types: list[Literal["OSFP-finned", "OSFP-flattop"]] = Field(default_factory=list)
    module_speed_gbps: Positive | None = None
    modes: list[PortMode] = Field(default_factory=list)
    fabrics: list[Fabric] = Field(default_factory=list)
    pluggable: bool | None = None
    source_url: Text | None = None
    scope_note: Text | None = None
    conditions: list[Text] = Field(default_factory=list)

    _source = field_validator("source_url")(check_url)

    @model_validator(mode="after")
    def consistent(self):
        unique([m.id for m in self.modes], "port mode ID")
        unique(self.accepted_connector_families, "accepted connector")
        unique(self.fabrics, "fabric")
        if self.module_speed_gbps and any(m.capacity > self.module_speed_gbps for m in self.modes):
            raise ValueError("port mode exceeds cage capacity")
        if self.connector_family != "OSFP" and self.accepted_interface_types:
            raise ValueError("OSFP mechanics only apply to OSFP cages")
        if self.pluggable is False and self.accepted_connector_families:
            raise ValueError("fixed interfaces cannot accept pluggable modules")
        return self


class DeviceProfile(StrictModel):
    id: Annotated[str, Field(min_length=1, max_length=128)]
    kind: Text
    model: Text
    family: Text | None = None
    sku: Text | None = None
    source_url: Text | None = None
    notes: Text | None = None
    port_groups: list[PortGroup]

    _source = field_validator("source_url")(check_url)

    @model_validator(mode="after")
    def consistent(self):
        unique([g.id for g in self.port_groups], "port group ID")
        return self


class Endpoint(StrictModel):
    id: Literal["A", "B"]
    role: Literal["module", "head", "branch", "peer"]
    count: Annotated[int, Field(ge=1, le=16)] = 1
    connector_family: Connector
    interface_type: Text
    modes: list[PortMode] = Field(default_factory=list)

    @model_validator(mode="after")
    def consistent(self):
        unique([m.id for m in self.modes], "endpoint mode ID")
        if self.connector_family == "OSFP" and self.interface_type not in {"OSFP", "OSFP-finned", "OSFP-flattop"}:
            raise ValueError("unknown OSFP mechanical interface")
        if self.connector_family != "OSFP" and self.interface_type != self.connector_family:
            raise ValueError("endpoint interface and connector family disagree")
        if self.role == "branch" and self.count < 2:
            raise ValueError("a breakout branch must describe at least two terminations")
        return self


class SKU(StrictModel):
    part_number: Text
    length_m: Distance | None = None
    source_url: Text | None = None

    _source = field_validator("source_url")(check_url)


class OpticalProfile(StrictModel):
    standard: Text | None = None
    connector: Text | None = None
    lanes: Annotated[int, Field(ge=1, le=32)] | None = None
    lane_rate_gbps: Distance | None = None
    wavelengths_nm: list[Distance] = Field(default_factory=list)
    fec: list[Text] = Field(default_factory=list)


class InterconnectDetail(StrictModel):
    endpoints: list[Endpoint] = Field(default_factory=list)
    skus: list[SKU] = Field(default_factory=list)
    cable_type: Literal["Transceiver", "AOC", "DAC", "ACC", "LACC", "Copper", "Unknown"] = "Unknown"
    optics: OpticalProfile | None = None
    source_url: Text | None = None
    conditions: list[Text] = Field(default_factory=list)

    _source = field_validator("source_url")(check_url)

    @model_validator(mode="after")
    def consistent(self):
        unique([e.id for e in self.endpoints], "endpoint ID")
        unique([s.part_number for s in self.skus], "SKU")
        if self.endpoints:
            expected = 1 if self.cable_type == "Transceiver" else 2
            if len(self.endpoints) != expected:
                raise ValueError("transceivers need one endpoint; cable assemblies need two")
        if len(self.endpoints) == 2:
            a, b = self.endpoints
            totals_a = {m.capacity * a.count for m in a.modes}
            totals_b = {m.capacity * b.count for m in b.modes}
            if totals_a and totals_b and totals_a != totals_b:
                raise ValueError("cable endpoints disagree on total bandwidth")
        return self


class ProfileDocument(StrictModel):
    schema_version: Literal[2]
    profiles: list[DeviceProfile]
    interconnect_details: dict[Identifier, InterconnectDetail]

    @model_validator(mode="after")
    def consistent(self):
        unique([p.id for p in self.profiles], "device profile ID")
        return self


class EquipmentRow(StrictModel):
    model: Text
    family: Text | None = None
    speed: Text | None = None
    connectors: Text | None = None
    port_counts: dict[Text, Annotated[int, Field(ge=0)]] | None = None
    throughput: Text | None = None
    height: Text | None = None
    cooling: Text | None = None
    compatibility: list[Text] | None = None
    reach: dict[Text, Distance] | None = None
    availability: Text | None = None


class ProductSummary(StrictModel):
    model: Text
    speed: Text
    category: Text


class ProductRow(StrictModel):
    category: Literal["Transceiver", "AOC", "Copper"]
    model: Text
    variant: Text | None
    status: Literal["active", "planned", "prototype", "no_longer_for_sale", "discontinued"]
    part_numbers: list[Text]
    source_url: Text | None
    interface_count: Positive | None
    interface_speed: Text | None
    interface_connector: Text | None
    speed: Text | None
    interface_type: Text | None
    medium: Literal["SM", "MM", "Copper"] | None
    reach: dict[Text, Distance] | None
    fabric_compatibility: list[Fabric] = Field(default_factory=list)

    _source = field_validator("source_url")(check_url)

    @field_validator("speed")
    @classmethod
    def speed_format(cls, value):
        if value is not None and not re.fullmatch(r"\d+(?:\.\d+)?\s*(?:G|T)(?:b/s|bE)?", value, re.I):
            raise ValueError("product speed must be numeric G/T; use null for unknown")
        return value

    @model_validator(mode="after")
    def consistent(self):
        unique(self.part_numbers, "part number")
        unique(self.fabric_compatibility, "fabric")
        return self


class InterfaceCompatibility(StrictModel):
    pluggable: bool | None = None
    accepted_pluggables: list[Text] = Field(default_factory=list)
    fixed_interfaces: list[Text] = Field(default_factory=list)
    source_url: Text | None = None
    scope_note: Text | None = None
    variants: list[Text] = Field(default_factory=list)
    notes: list[Text] = Field(default_factory=list)

    _source = field_validator("source_url")(check_url)


def validate_table(section: dict[str, Any], row_type: type[StrictModel]) -> list[dict]:
    if not isinstance(section, dict) or set(section) != {"fields", "items"}:
        raise ValueError("tables require exactly fields and items")
    fields, rows = section["fields"], section["items"]
    if not isinstance(fields, list) or not fields or not all(isinstance(f, str) and f for f in fields):
        raise ValueError("invalid table fields")
    unique(fields, "column")
    if not isinstance(rows, list):
        raise ValueError("table items must be an array")
    result = []
    for row in rows:
        if not isinstance(row, list) or len(row) != len(fields):
            raise ValueError("table row length does not match its fields")
        result.append(row_type.model_validate(dict(zip(fields, row))).model_dump())
    return result


class CatalogDocument(StrictModel):
    schema_version: Literal[8]
    snapshot_date: Text
    generated_at: Text
    timezone: Text
    sources: dict[Text, Text]
    linkx: dict[str, Any]
    ethernet: dict[str, Any]
    infiniband: dict[str, Any]
    silicon_photonics: dict[str, Any]
    dpu: dict[str, Any]
    supernic: dict[str, Any]
    summary: dict[Text, Annotated[int, Field(ge=0)]]
    notes: list[Text]
    port_interface_compatibility: dict[Literal["ethernet_switching", "infiniband_and_appliances", "dpu", "supernic"], dict[Text, InterfaceCompatibility]]

    @model_validator(mode="after")
    def consistent(self):
        date.fromisoformat(self.snapshot_date)
        if datetime.fromisoformat(self.generated_at).utcoffset() is None:
            raise ValueError("generated_at needs a timezone")
        ZoneInfo(self.timezone)
        if not self.sources:
            raise ValueError("catalog sources cannot be empty")
        for url in self.sources.values():
            check_url(url)
        for name in ("ethernet", "infiniband", "silicon_photonics", "dpu", "supernic"):
            rows = validate_table(getattr(self, name), EquipmentRow)
            unique([r["model"] for r in rows], f"{name} model")
        expected = {"product_fields", "active", "no_longer_for_sale", "transceiver_fields", "transceivers", "transceiver_fabric_compatibility", "detailed_interconnect_fields", "aoc", "copper"}
        if set(self.linkx) != expected:
            raise ValueError("unsupported LinkX table layout")
        for bucket, fields, kind in (("active", "product_fields", ProductSummary), ("no_longer_for_sale", "product_fields", ProductSummary), ("transceivers", "transceiver_fields", ProductRow), ("aoc", "detailed_interconnect_fields", ProductRow), ("copper", "detailed_interconnect_fields", ProductRow)):
            validate_table({"fields": self.linkx[fields], "items": self.linkx[bucket]}, kind)
        fabric_map = self.linkx["transceiver_fabric_compatibility"]
        if not isinstance(fabric_map, dict):
            raise ValueError("fabric map must be an object")
        for key, fabrics in fabric_map.items():
            if not isinstance(key, str) or not key or not isinstance(fabrics, list) or any(f not in {"ETH", "IB", "NVL"} for f in fabrics):
                raise ValueError("invalid transceiver fabric map")
            unique(fabrics, "fabric")
        return self


class Selection(StrictModel):
    device_id: Annotated[str, Field(min_length=1, max_length=128)]
    port_group_id: Annotated[str, Field(min_length=1, max_length=64)]
    product_id: Identifier
    endpoint_id: Literal["A", "B"] | None = None
    mode_id: Annotated[str, Field(min_length=1, max_length=64)] | None = None
    part_number: Text | None = None


class FiberCable(StrictModel):
    medium: Literal["SM", "MM"]
    fiber_type: Literal["OS2", "OM3", "OM4", "OM5"]
    connector_a: Text
    connector_b: Text
    # Pinout is checked explicitly; a matching MPO shell alone is insufficient.
    pinout_verified: bool = False

    @model_validator(mode="after")
    def consistent(self):
        if (self.medium == "SM") != (self.fiber_type == "OS2"):
            raise ValueError("OS2 is single-mode; OM3/OM4/OM5 are multi-mode")
        return self


class ConnectionRequest(StrictModel):
    a: Selection
    b: Selection
    fabric: Fabric
    length_m: Distance | None = None
    fiber: FiberCable | None = None
    revision: Annotated[str, Field(pattern=r"^[0-9a-f]{12}$")] | None = None
