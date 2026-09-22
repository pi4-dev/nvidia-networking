"""Bounded contracts for whole fanouts and projects with physical port ownership."""

from typing import Annotated, Literal

from pydantic import Field, model_validator

from .models import (ConnectionRequest, Distance, Evidence, Fabric, FiberCable, OwnedPart,
                     Selection, ShortText, StrictModel, unique)

AssetID = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$")]
Channel = Annotated[int, Field(ge=1, le=32)]
Revision = Annotated[str, Field(pattern=r"^[0-9a-f]{12}$")]


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

    @model_validator(mode="after")
    def consistent(self):
        unique([c.id for c in self.connections] + [b.id for b in self.breakouts], "project connection ID")
        unique([p.part_number for p in self.owned_parts], "owned PN")
        if not self.connections and not self.breakouts:
            raise ValueError("project must contain at least one connection or breakout")
        if 2 * len(self.connections) + sum(1 + len(b.branches) for b in self.breakouts) > 512:
            raise ValueError("project exceeds 512 physical endpoint assignments")
        return self


class ProjectCSV(StrictModel):
    name: ShortText = "Imported project"
    csv: Annotated[str, Field(min_length=1, max_length=750000)]
    revision: Revision | None = None
