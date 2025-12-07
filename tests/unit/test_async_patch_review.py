"""
Tests for Async Patch Review Workflow
"""

import sqlite3
from pathlib import Path

import pytest

from src.minipipe.patch_ledger import PatchLedger


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.close()
    return db_path


@pytest.fixture
def patch_ledger(temp_db):
    """Create a PatchLedger with test database."""
    try:
        from core.state.db import Database
        db = Database(temp_db)
        db.connect()
        return PatchLedger(db=db)
    except ImportError:
        pytest.skip("Database not available")


class TestAsyncPatchReview:
    """Tests for async patch review workflow."""
    
    def test_awaiting_review_state_exists(self, patch_ledger):
        """Test that awaiting_review state exists."""
        assert "awaiting_review" in patch_ledger.VALID_STATES
    
    def test_validated_can_transition_to_review(self, patch_ledger):
        """Test that validated patches can transition to awaiting_review."""
        assert "awaiting_review" in patch_ledger.STATE_TRANSITIONS["validated"]
    
    def test_awaiting_review_transitions(self, patch_ledger):
        """Test valid transitions from awaiting_review."""
        valid_transitions = patch_ledger.STATE_TRANSITIONS["awaiting_review"]
        
        assert "queued" in valid_transitions  # After approval
        assert "dropped" in valid_transitions  # After rejection
    
    def test_mark_for_review(self, patch_ledger):
        """Test marking a patch for review."""
        # Create and validate a patch
        ledger_id = patch_ledger.create_entry(
            patch_id="patch-001",
            run_id="run-001",
            workstream_id="ws-001",
        )
        
        # Transition to validated
        patch_ledger.transition_state(ledger_id, "validated")
        
        # Mark for review
        result = patch_ledger.mark_for_review(
            ledger_id,
            reviewer="alice@example.com",
            review_reason="High-risk changes",
        )
        
        assert result is True
        
        entry = patch_ledger.get_entry(ledger_id)
        assert entry["state"] == "awaiting_review"
    
    def test_mark_for_review_wrong_state(self, patch_ledger):
        """Test that marking for review only works from validated state."""
        ledger_id = patch_ledger.create_entry(
            patch_id="patch-002",
            run_id="run-002",
            workstream_id="ws-002",
        )
        
        # Try to mark for review from created state
        result = patch_ledger.mark_for_review(ledger_id)
        
        assert result is False
    
    def test_approve_patch(self, patch_ledger):
        """Test approving a patch."""
        # Create, validate, and mark for review
        ledger_id = patch_ledger.create_entry(
            patch_id="patch-003",
            run_id="run-003",
            workstream_id="ws-003",
        )
        patch_ledger.transition_state(ledger_id, "validated")
        patch_ledger.mark_for_review(ledger_id)
        
        # Approve
        result = patch_ledger.approve_patch(
            ledger_id,
            reviewer="bob@example.com",
            comment="Looks good to me",
        )
        
        assert result is True
        
        entry = patch_ledger.get_entry(ledger_id)
        assert entry["state"] == "queued"
    
    def test_approve_patch_wrong_state(self, patch_ledger):
        """Test that approval only works from awaiting_review state."""
        ledger_id = patch_ledger.create_entry(
            patch_id="patch-004",
            run_id="run-004",
            workstream_id="ws-004",
        )
        
        # Try to approve from created state
        result = patch_ledger.approve_patch(
            ledger_id,
            reviewer="charlie@example.com",
        )
        
        assert result is False
    
    def test_reject_patch(self, patch_ledger):
        """Test rejecting a patch."""
        # Create, validate, and mark for review
        ledger_id = patch_ledger.create_entry(
            patch_id="patch-005",
            run_id="run-005",
            workstream_id="ws-005",
        )
        patch_ledger.transition_state(ledger_id, "validated")
        patch_ledger.mark_for_review(ledger_id)
        
        # Reject
        result = patch_ledger.reject_patch(
            ledger_id,
            reviewer="dave@example.com",
            reason="Breaking changes detected",
        )
        
        assert result is True
        
        entry = patch_ledger.get_entry(ledger_id)
        assert entry["state"] == "dropped"
    
    def test_reject_patch_wrong_state(self, patch_ledger):
        """Test that rejection only works from awaiting_review state."""
        ledger_id = patch_ledger.create_entry(
            patch_id="patch-006",
            run_id="run-006",
            workstream_id="ws-006",
        )
        
        # Try to reject from created state
        result = patch_ledger.reject_patch(
            ledger_id,
            reviewer="eve@example.com",
            reason="Test",
        )
        
        assert result is False
    
    def test_list_patches_awaiting_review(self, patch_ledger):
        """Test listing patches awaiting review."""
        # Create multiple patches
        for i in range(3):
            ledger_id = patch_ledger.create_entry(
                patch_id=f"patch-{i:03d}",
                run_id="run-007",
                workstream_id="ws-007",
            )
            patch_ledger.transition_state(ledger_id, "validated")
            patch_ledger.mark_for_review(ledger_id)
        
        # List awaiting review
        patches = patch_ledger.list_patches_awaiting_review(run_id="run-007")
        
        assert len(patches) == 3
        assert all(p["state"] == "awaiting_review" for p in patches)
    
    def test_list_patches_awaiting_review_filtered(self, patch_ledger):
        """Test listing patches with filters."""
        # Create patches in different workstreams
        ledger_id1 = patch_ledger.create_entry(
            patch_id="patch-ws1",
            run_id="run-008",
            workstream_id="ws-A",
        )
        ledger_id2 = patch_ledger.create_entry(
            patch_id="patch-ws2",
            run_id="run-008",
            workstream_id="ws-B",
        )
        
        patch_ledger.transition_state(ledger_id1, "validated")
        patch_ledger.mark_for_review(ledger_id1)
        
        patch_ledger.transition_state(ledger_id2, "validated")
        patch_ledger.mark_for_review(ledger_id2)
        
        # List only ws-A
        patches = patch_ledger.list_patches_awaiting_review(workstream_id="ws-A")
        
        assert len(patches) >= 1
        assert all(p["workstream_id"] == "ws-A" for p in patches)
    
    def test_review_metadata_captured(self, patch_ledger):
        """Test that review metadata is properly captured."""
        ledger_id = patch_ledger.create_entry(
            patch_id="patch-meta",
            run_id="run-009",
            workstream_id="ws-009",
        )
        
        patch_ledger.transition_state(ledger_id, "validated")
        patch_ledger.mark_for_review(
            ledger_id,
            reviewer="frank@example.com",
            review_reason="Security review required",
        )
        
        entry = patch_ledger.get_entry(ledger_id)
        import json
        metadata = json.loads(entry["metadata"]) if entry["metadata"] else {}
        
        assert metadata.get("manual_review_required") is True
        assert metadata.get("review_status") == "pending"
        assert metadata.get("reviewer") == "frank@example.com"
        assert metadata.get("review_reason") == "Security review required"
        assert "review_requested_at" in metadata
    
    def test_approval_metadata_captured(self, patch_ledger):
        """Test that approval metadata is properly captured."""
        ledger_id = patch_ledger.create_entry(
            patch_id="patch-approval-meta",
            run_id="run-010",
            workstream_id="ws-010",
        )
        
        patch_ledger.transition_state(ledger_id, "validated")
        patch_ledger.mark_for_review(ledger_id)
        patch_ledger.approve_patch(
            ledger_id,
            reviewer="grace@example.com",
            comment="All checks passed",
        )
        
        entry = patch_ledger.get_entry(ledger_id)
        import json
        metadata = json.loads(entry["metadata"]) if entry["metadata"] else {}
        
        assert metadata.get("review_status") == "approved"
        assert metadata.get("reviewed_by") == "grace@example.com"
        assert metadata.get("review_comment") == "All checks passed"
        assert "reviewed_at" in metadata
    
    def test_rejection_metadata_captured(self, patch_ledger):
        """Test that rejection metadata is properly captured."""
        ledger_id = patch_ledger.create_entry(
            patch_id="patch-rejection-meta",
            run_id="run-011",
            workstream_id="ws-011",
        )
        
        patch_ledger.transition_state(ledger_id, "validated")
        patch_ledger.mark_for_review(ledger_id)
        patch_ledger.reject_patch(
            ledger_id,
            reviewer="hank@example.com",
            reason="Code quality issues",
        )
        
        entry = patch_ledger.get_entry(ledger_id)
        import json
        metadata = json.loads(entry["metadata"]) if entry["metadata"] else {}
        
        assert metadata.get("review_status") == "rejected"
        assert metadata.get("reviewed_by") == "hank@example.com"
        assert metadata.get("rejection_reason") == "Code quality issues"
        assert "reviewed_at" in metadata
    
    def test_review_workflow_end_to_end(self, patch_ledger):
        """Test complete review workflow from creation to approval."""
        # 1. Create patch
        ledger_id = patch_ledger.create_entry(
            patch_id="patch-e2e",
            run_id="run-e2e",
            workstream_id="ws-e2e",
        )
        
        assert patch_ledger.get_entry(ledger_id)["state"] == "created"
        
        # 2. Validate
        patch_ledger.transition_state(ledger_id, "validated")
        assert patch_ledger.get_entry(ledger_id)["state"] == "validated"
        
        # 3. Mark for review
        patch_ledger.mark_for_review(
            ledger_id,
            reviewer="reviewer@example.com",
            review_reason="High impact",
        )
        assert patch_ledger.get_entry(ledger_id)["state"] == "awaiting_review"
        
        # 4. Approve
        patch_ledger.approve_patch(
            ledger_id,
            reviewer="reviewer@example.com",
            comment="Approved",
        )
        assert patch_ledger.get_entry(ledger_id)["state"] == "queued"
        
        # 5. Can now proceed with application
        patch_ledger.transition_state(ledger_id, "applied")
        assert patch_ledger.get_entry(ledger_id)["state"] == "applied"
