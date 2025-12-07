import unittest
import json
from pathlib import Path
import shutil
from datetime import datetime


from src.acms.gap_registry import GapRegistry, GapRecord, GapStatus, GapSeverity


class TestGapRegistry(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("./test_registry_temp").resolve()
        # Clean up before test
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()
        self.storage_path = self.test_dir / "gap_registry.json"
        self.report_path = self.test_dir / "gap_analysis_report.json"

    def tearDown(self):
        # Clean up after test
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Tests that the GapRegistry can be initialized."""
        registry = GapRegistry(self.storage_path)
        self.assertEqual(registry.storage_path, self.storage_path)
        self.assertEqual(len(registry.gaps), 0)

    def test_load_from_report(self):
        """Tests loading gaps from a JSON report (Steps 13-14)."""
        report_data = {
            "gaps": [
                {
                    "gap_id": "GAP_001",
                    "title": "Missing Docstring",
                    "description": "The function `foo` is missing a docstring.",
                    "category": "documentation",
                    "severity": "low",
                    "file_paths": ["src/main.py"],
                },
                {
                    "title": "No Error Handling",
                    "severity": "high",
                    "category": "correctness",
                },
            ]
        }
        with open(self.report_path, "w") as f:
            json.dump(report_data, f)

        registry = GapRegistry()
        count = registry.load_from_report(self.report_path)

        self.assertEqual(count, 2)
        self.assertEqual(len(registry.gaps), 2)

        # Test first gap
        gap1 = registry.get_gap("GAP_001")
        self.assertIsNotNone(gap1)
        self.assertEqual(gap1.title, "Missing Docstring")
        self.assertEqual(gap1.severity, GapSeverity.LOW)
        self.assertEqual(gap1.status, GapStatus.DISCOVERED)
        self.assertEqual(gap1.file_paths, ["src/main.py"])

        # Test second gap (with default values)
        gap2 = registry.get_gap("GAP_0001")  # Auto-generated ID
        self.assertIsNotNone(gap2)
        self.assertEqual(gap2.title, "No Error Handling")
        self.assertEqual(gap2.severity, GapSeverity.HIGH)
        self.assertIn("discovered_at", gap2.to_dict())

    def test_save_and_load(self):
        """Tests saving the registry to and loading from a file."""
        registry = GapRegistry(self.storage_path)

        # Add a gap
        gap = GapRecord(
            gap_id="GAP_SAVE",
            title="Test Save",
            description="...",
            category="testing",
            severity=GapSeverity.MEDIUM,
            status=GapStatus.PLANNED,
            discovered_at=datetime.utcnow().isoformat(),
        )
        registry.add_gap(gap)
        self.assertEqual(len(registry.gaps), 1)

        # Save it
        registry.save()
        self.assertTrue(self.storage_path.exists())

        # Create a new registry and load from the file
        new_registry = GapRegistry(self.storage_path)
        self.assertEqual(len(new_registry.gaps), 1)

        loaded_gap = new_registry.get_gap("GAP_SAVE")
        self.assertIsNotNone(loaded_gap)
        self.assertEqual(loaded_gap.title, "Test Save")
        self.assertEqual(loaded_gap.status, GapStatus.PLANNED)

    def test_status_and_assignment(self):
        """Tests updating status and assigning clusters/workstreams."""
        registry = GapRegistry()
        gap = GapRecord(
            "GAP_ASSIGN",
            "title",
            "desc",
            "cat",
            GapSeverity.INFO,
            GapStatus.DISCOVERED,
            "time",
        )
        registry.add_gap(gap)

        # Update status
        registry.update_status("GAP_ASSIGN", GapStatus.IN_PROGRESS)
        self.assertEqual(registry.get_gap("GAP_ASSIGN").status, GapStatus.IN_PROGRESS)

        # Assign to cluster
        registry.assign_cluster("GAP_ASSIGN", "CLUSTER_1")
        self.assertEqual(registry.get_gap("GAP_ASSIGN").cluster_id, "CLUSTER_1")
        self.assertEqual(
            registry.get_gap("GAP_ASSIGN").status, GapStatus.CLUSTERED
        )  # Status should update

        # Assign to workstream
        registry.assign_workstream("GAP_ASSIGN", "WS_A")
        self.assertEqual(registry.get_gap("GAP_ASSIGN").workstream_id, "WS_A")

    def test_get_stats(self):
        """Tests the statistics generation."""
        registry = GapRegistry()
        registry.add_gap(
            GapRecord(
                "G1", "t", "d", "c", GapSeverity.CRITICAL, GapStatus.RESOLVED, "time"
            )
        )
        registry.add_gap(
            GapRecord(
                "G2", "t", "d", "c", GapSeverity.LOW, GapStatus.DISCOVERED, "time"
            )
        )
        registry.add_gap(
            GapRecord(
                "G3", "t", "d", "c", GapSeverity.LOW, GapStatus.DISCOVERED, "time"
            )
        )

        stats = registry.get_stats()

        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["unresolved"], 2)
        self.assertEqual(stats["by_status"]["resolved"], 1)
        self.assertEqual(stats["by_status"]["discovered"], 2)
        self.assertEqual(stats["by_severity"]["critical"], 1)
        self.assertEqual(stats["by_severity"]["low"], 2)


if __name__ == "__main__":
    unittest.main()
