"""Quick validation script for Wave 1 optimizations"""

import sys
from pathlib import Path

# Add src to path (scripts/ is one level below root)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_router_batching():
    """Verify router batching implementation"""
    from minipipe.router import FileBackedStateStore
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "test_state.json"
        store = FileBackedStateStore(str(state_file), auto_save_interval=5)
        
        # Should NOT write until 5 updates
        for i in range(4):
            store.set_round_robin_index(f"rule_{i}", i)
            assert not state_file.exists(), f"Should not save before interval (i={i})"
        
        # 5th update should trigger save
        store.set_round_robin_index("rule_4", 4)
        assert state_file.exists(), "Should save after 5 updates"
        
        # Flush should always save
        store.set_round_robin_index("rule_5", 5)
        os.remove(state_file)
        store.flush()
        assert state_file.exists(), "Flush should always save"
        
    print("✅ Router batching test PASSED")
    return True

def test_frozenset_constants():
    """Verify frozenset constants are defined"""
    from minipipe import orchestrator
    
    assert hasattr(orchestrator, '_ACTIVE_STATES'), "Missing _ACTIVE_STATES"
    assert hasattr(orchestrator, '_SUCCESS_STATES'), "Missing _SUCCESS_STATES"
    
    assert isinstance(orchestrator._ACTIVE_STATES, frozenset), "_ACTIVE_STATES should be frozenset"
    assert isinstance(orchestrator._SUCCESS_STATES, frozenset), "_SUCCESS_STATES should be frozenset"
    
    assert "PENDING" in orchestrator._ACTIVE_STATES
    assert "RUNNING" in orchestrator._ACTIVE_STATES
    assert "SUCCESS" in orchestrator._SUCCESS_STATES
    assert "SKIPPED" in orchestrator._SUCCESS_STATES
    
    print("✅ Frozenset constants test PASSED")
    return True

def test_performance_improvement():
    """Quick performance comparison"""
    import time
    
    # Test O(1) vs O(n) lookups
    statuses_list = ["PENDING", "RUNNING"]
    statuses_set = frozenset(["PENDING", "RUNNING"])
    
    test_value = "PENDING"
    iterations = 1000000
    
    # List lookup
    start = time.perf_counter()
    for _ in range(iterations):
        _ = test_value in statuses_list
    list_time = time.perf_counter() - start
    
    # Frozenset lookup
    start = time.perf_counter()
    for _ in range(iterations):
        _ = test_value in statuses_set
    set_time = time.perf_counter() - start
    
    speedup = list_time / set_time
    print(f"✅ Frozenset speedup: {speedup:.2f}x faster ({list_time:.4f}s vs {set_time:.4f}s)")
    assert speedup > 1.5, f"Expected speedup > 1.5x, got {speedup:.2f}x"
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Wave 1 Optimization Validation")
    print("=" * 60)
    
    tests = [
        ("Router I/O Batching", test_router_batching),
        ("Frozenset Constants", test_frozenset_constants),
        ("Performance Improvement", test_performance_improvement),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n[TEST] {name}")
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {name} FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)
