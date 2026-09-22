"""Bounded contracts for whole fanouts and projects with physical port ownership."""

from typing import Annotated, Literal

from pydantic import AfterValidator, Field, model_validator

from .models import (ConnectionRequest, Distance, Evidence, Fabric, FiberCable, OwnedPart,
                     Selection, ShortText, StrictModel, unique)

AssetID = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$")]
Channel = Annotated[int, Field(ge=1, le=32)]
Revision = Annotated[str, Field(pattern=r"^[0-9a-f]{12}$")]


def printable(value):
    if any(ord(c) < 32 or 0x7f <= ord(c) <= 0x9f for c in value):
        raise ValueError("use printable characters without control codes")
    return value


InstallationText = Annotated[str, Field(min_length=1, max_length=64), AfterValidator(printable)]


class DeviceLocation(StrictModel):
    instance_id: AssetID
    rack: InstallationText | None = None
    rack_u: Annotated[int, Field(ge=1, le=1000)] | None = None


class PortLabel(StrictModel):
    instance_id: AssetID
    port_group_id: Annotated[str, Field(min_length=1, max_length=64)]
    port_number: Annotated[int, Field(ge=1, le=1024)]
    label: InstallationText


class InstallationProgress(StrictModel):
    branch_id: AssetID | None = None
    installed: bool = False
    checked: bool = False
    # Binds a user declaration to the exact physical installation definition.
    definition: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")] | None = None
    notes: Annotated[str, Field(max_length=512), AfterValidator(printable)] = ""

    @model_validator(mode="after")
    def consistent(self):
        if self.checked and not self.installed:
            raise ValueError("a checked connection must also be installed")
        if (self.installed or self.checked) and not self.definition:
            raise ValueError("installation confirmations require the cabling plan definition fingerprint")
        return self


class CableInstallation(StrictModel):
    entry_id: AssetID
    cable_id: AssetID | None = None
    progress: Annotated[list[InstallationProgress], Field(max_length=16)] = Field(default_factory=list)

    @model_validator(mode="after")
    def consistent(self):
        unique([p.branch_id for p in self.progress], "installation branch")
        return self


class CablingOptions(StrictModel):
    locations: Annotated[list[DeviceLocation], Field(max_length=512)] = Field(default_factory=list)
    port_labels: Annotated[list[PortLabel], Field(max_length=512)] = Field(default_factory=list)
    cables: Annotated[list[CableInstallation], Field(max_length=264)] = Field(default_factory=list)

    @model_validator(mode="after")
    def consistent(self):
        unique([l.instance_id for l in self.locations], "device location")
        unique([(p.instance_id, p.port_group_id, p.port_number) for p in self.port_labels], "physical port label")
        unique([c.entry_id for c in self.cables], "cable installation entry")
        return self


class InstalledSelection(Selection):
    instance_id: AssetID
    # A 1-based ordinal within the physical group, not a vendor CLI port name.
    port_number: Annotated[int, Field(ge=1, le=1024)]


class BreakoutSelection(InstalledSelection):
    mode_id: Annotated[str, Field(min_length=1, max_length=64)]


class BreakoutBranch(StrictModel):
    id: AssetID
    selection: BreakoutSelection
    termination: Annotated[int, Field(ge=1, le=16)]
    head_links: Annotated[list[Channel], Field(max_length=16)] = Field(default_factory=list)
    head_optical_port: Annotated[int, Field(ge=1, le=16)] = 1
    head_optical_lanes: Annotated[list[Channel], Field(max_length=32)] = Field(default_factory=list)
    branch_optical_lanes: Annotated[list[Channel], Field(max_length=32)] = Field(default_factory=list)
    interop_evidence: Evidence | None = None


class OpticalFanout(StrictModel):
    part_number: ShortText | None = None
    branch_count: Annotated[int, Field(ge=2, le=16)]
    head_ports: Annotated[int, Field(ge=1, le=16)] = 1
    fiber: FiberCable
    # Evidence covers the complete harness including PN, lengths and lane map.
    evidence: Evidence | None = None


class BreakoutRequest(StrictModel):
    topology: Literal["cable", "optical"] = "cable"
    head: BreakoutSelection
    branches: Annotated[list[BreakoutBranch], Field(min_length=1, max_length=16)]
    fabric: Fabric
    length_m: Distance | None = None
    mapping_verified: bool = False
    optical_fanout: OpticalFanout | None = None
    revision: Revision | None = None

    @model_validator(mode="after")
    def consistent(self):
        unique([b.id for b in self.branches], "branch ID")
        if self.topology == "cable" and self.optical_fanout is not None:
            raise ValueError("a cable assembly cannot include a separate optical fanout")
        return self


class ProjectConnection(ConnectionRequest):
    id: AssetID
    a: InstalledSelection
    b: InstalledSelection


class ProjectBreakout(BreakoutRequest):
    id: AssetID


class ProjectRequest(StrictModel):
    format: Literal["nvidia-connection-project-v1"] = "nvidia-connection-project-v1"
    name: ShortText = "Untitled project"
    connections: Annotated[list[ProjectConnection], Field(max_length=200)] = Field(default_factory=list)
    breakouts: Annotated[list[ProjectBreakout], Field(max_length=64)] = Field(default_factory=list)
    owned_parts: Annotated[list[OwnedPart], Field(max_length=512)] = Field(default_factory=list)
    revision: Revision | None = None
    cabling: CablingOptions = Field(default_factory=CablingOptions)

    @model_validator(mode="after")
    def consistent(self):
        unique([c.id for c in self.connections] + [b.id for b in self.breakouts], "project connection ID")
        unique([p.part_number for p in self.owned_parts], "owned PN")
        if not self.connections and not self.breakouts:
            raise ValueError("project must contain at least one connection or breakout")
        if 2 * len(self.connections) + sum(1 + len(b.branches) for b in self.breakouts) > 512:
            raise ValueError("project exceeds 512 physical endpoint assignments")
        entries = {e.id: e for e in [*self.connections, *self.breakouts]}
        selections = [s for c in self.connections for s in (c.a, c.b)] + [s for b in self.breakouts for s in [b.head, *(x.selection for x in b.branches)]]
        ports = {(s.instance_id, s.port_group_id, s.port_number) for s in selections}
        instances = {s.instance_id for s in selections}
        if any(l.instance_id not in instances for l in self.cabling.locations):
            raise ValueError("a cabling location refers to a device outside this project")
        if any((p.instance_id, p.port_group_id, p.port_number) not in ports for p in self.cabling.port_labels):
            raise ValueError("a cabling port label refers to a port outside this project")
        overrides = {c.entry_id: c for c in self.cabling.cables}
        for id_, cable in overrides.items():
            if id_ not in entries:
                raise ValueError("a cabling entry refers to a missing connection/breakout")
            entry = entries[id_]
            branches = {b.id for b in entry.branches} if isinstance(entry, ProjectBreakout) else {None}
            if any(p.branch_id not in branches for p in cable.progress):
                raise ValueError("installation progress refers to a missing branch")
        unique([(overrides[e].cable_id if e in overrides and overrides[e].cable_id else 'C-' + e).casefold() for e in entries], "cable ID")
        return self


class ProjectCSV(StrictModel):
    name: ShortText = "Imported project"
    csv: Annotated[str, Field(min_length=1, max_length=750000)]
    revision: Revision | None = None
