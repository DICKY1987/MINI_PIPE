"""Gap Registry Module

Normalized gap storage and query layer for gap analysis findings.
Supports PHASE_2 and PHASE_5 operations.
"""

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class GapStatus(Enum):
    """Gap lifecycle status"""

    DISCOVERED = "discovered"
    CLUSTERED = "clustered"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    DEFERRED = "deferred"


class GapSeverity(Enum):
    """Gap severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class GapRecord:
    """Normalized gap record"""

    gap_id: str
    title: str
    description: str
    category: str
    severity: GapSeverity
    status: GapStatus
    discovered_at: str
    file_paths: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    cluster_id: Optional[str] = None
    workstream_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "severity": self.severity.value,
            "status": self.status.value,
            "discovered_at": self.discovered_at,
            "file_paths": self.file_paths,
            "dependencies": self.dependencies,
            "cluster_id": self.cluster_id,
            "workstream_id": self.workstream_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GapRecord":
        return cls(
            gap_id=data["gap_id"],
            title=data["title"],
            description=data["description"],
            category=data["category"],
            severity=GapSeverity(data["severity"]),
            status=GapStatus(data["status"]),
            discovered_at=data["discovered_at"],
            file_paths=data.get("file_paths", []),
            dependencies=data.get("dependencies", []),
            cluster_id=data.get("cluster_id"),
            workstream_id=data.get("workstream_id"),
            metadata=data.get("metadata", {}),
        )


class GapRegistry:
    """Gap storage and query layer"""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path
        self.gaps: Dict[str, GapRecord] = {}
        if storage_path and storage_path.exists():
            self.load()

    def add_gap(self, gap: GapRecord) -> None:
        """Add or update a gap record"""
        self.gaps[gap.gap_id] = gap

    def get_gap(self, gap_id: str) -> Optional[GapRecord]:
        """Retrieve a gap by ID"""
        return self.gaps.get(gap_id)

    def update_status(self, gap_id: str, status: GapStatus) -> None:
        """Update gap status"""
        if gap_id in self.gaps:
            self.gaps[gap_id].status = status

    def assign_cluster(self, gap_id: str, cluster_id: str) -> None:
        """Assign gap to a cluster"""
        if gap_id in self.gaps:
            self.gaps[gap_id].cluster_id = cluster_id
            self.gaps[gap_id].status = GapStatus.CLUSTERED

    def assign_workstream(self, gap_id: str, workstream_id: str) -> None:
        """Assign gap to a workstream"""
        if gap_id in self.gaps:
            self.gaps[gap_id].workstream_id = workstream_id

    def get_by_status(self, status: GapStatus) -> List[GapRecord]:
        """Query gaps by status"""
        return [g for g in self.gaps.values() if g.status == status]

    def get_by_cluster(self, cluster_id: str) -> List[GapRecord]:
        """Query gaps by cluster"""
        return [g for g in self.gaps.values() if g.cluster_id == cluster_id]

    def get_by_category(self, category: str) -> List[GapRecord]:
        """Query gaps by category"""
        return [g for g in self.gaps.values() if g.category == category]

    def get_by_severity(self, severity: GapSeverity) -> List[GapRecord]:
        """Query gaps by severity"""
        return [g for g in self.gaps.values() if g.severity == severity]

    def get_by_workstream(self, workstream_id: str) -> List[GapRecord]:
        """Query gaps by workstream"""
        return [g for g in self.gaps.values() if g.workstream_id == workstream_id]

    def get_unresolved(self) -> List[GapRecord]:
        """Get all unresolved gaps"""
        return [
            g
            for g in self.gaps.values()
            if g.status not in {GapStatus.RESOLVED, GapStatus.DEFERRED}
        ]

    def load_from_report(self, report_path: Path) -> int:
        """Load gaps from gap analysis report JSON"""
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        count = 0
        timestamp = datetime.now(UTC).isoformat()

        gaps_data = report.get("gaps")
        if not isinstance(gaps_data, list):
            raise ValueError("Gap report 'gaps' field must be a list.")

        for idx, gap_data in enumerate(gaps_data):
            gap_id = gap_data.get("gap_id", f"GAP_{idx:04d}")

            gap = GapRecord(
                gap_id=gap_id,
                title=gap_data.get("title", "Untitled Gap"),
                description=gap_data.get("description", ""),
                category=gap_data.get("category", "uncategorized"),
                severity=GapSeverity(gap_data.get("severity", "medium")),
                status=GapStatus.DISCOVERED,
                discovered_at=gap_data.get("discovered_at", timestamp),
                file_paths=gap_data.get("file_paths", []),
                dependencies=gap_data.get("dependencies", []),
                metadata=gap_data.get("metadata", {}),
            )
            self.add_gap(gap)
            count += 1

        return count

    def save(self) -> None:
        """Persist registry to storage"""
        if not self.storage_path:
            return

        data = {
            "version": "1.0",
            "saved_at": datetime.now(UTC).isoformat(),
            "gaps": [g.to_dict() for g in self.gaps.values()],
        }

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        """Load registry from storage"""
        if not self.storage_path or not self.storage_path.exists():
            return

        with open(self.storage_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.gaps = {g["gap_id"]: GapRecord.from_dict(g) for g in data.get("gaps", [])}

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total": len(self.gaps),
            "by_status": {
                status.value: len(self.get_by_status(status)) for status in GapStatus
            },
            "by_severity": {
                severity.value: len(self.get_by_severity(severity))
                for severity in GapSeverity
            },
            "unresolved": len(self.get_unresolved()),
        }
