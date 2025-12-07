# WS1 Automation Triggers (Archived)

**Archived:** 2025-12-07  
**Reason:** Never integrated into main execution flow  
**Status:** Safe to archive - no imports found in codebase

---

## Files

### monitoring_trigger.py
- **Purpose:** Auto-start monitoring on RUN_CREATED event (WS1-005)
- **Lines:** 150+
- **Design:** Event-driven trigger for monitoring system
- **Status:** Never wired into orchestrator

### router_trigger.py  
- **Purpose:** Auto-trigger router on task_queue.json changes (WS1-004)
- **Lines:** 120+
- **Design:** File watcher for automatic router invocation
- **Status:** Never integrated; manual invocation used instead

### request_builder_trigger.py
- **Purpose:** Auto-trigger on PLANNING_COMPLETE event (WS1-003)
- **Lines:** 110+
- **Design:** Event-based automation for request builder
- **Status:** Never wired into event bus

---

## Background

These scripts were part of **WS1 (Workstream 1)** automation design to provide event-driven triggers for various MINI_PIPE subsystems. The original intent was to reduce manual orchestration by:

1. Automatically starting monitoring when a run is created
2. Automatically invoking the router when task queues change
3. Automatically building requests when planning completes

However, during implementation, it was found that **manual invocation** via Invoke tasks and the orchestrator's built-in coordination was sufficient and more predictable than event-driven automation.

---

## Why Never Integrated

1. **Complexity vs. Value:** Event-driven automation added complexity without clear benefits
2. **Testing Difficulty:** File watchers and event triggers are harder to test reliably
3. **Orchestrator Sufficiency:** The ACMS controller already coordinates these steps
4. **Invoke Tasks:** Modern Invoke task system provides better developer UX

---

## Restoration

If automation is needed in the future:

### Option 1: Restore and Integrate
```bash
# Restore from archive
git checkout archive/ws1_automation_triggers/*.py -o src/minipipe/

# Wire into event bus
# - Add to orchestrator lifecycle
# - Subscribe to event bus events
# - Add tests for trigger functionality
```

### Option 2: Modernize with Invoke
Instead of complex file watchers, use Invoke tasks with `--watch` flag or similar:

```python
@task
def watch_and_route(c):
    """Watch for task queue changes and auto-route"""
    # Use watchdog library or similar
    # Simpler than custom file watchers
```

---

## Related Documentation

- **Original Design:** See WS1 documentation (if exists)
- **Event Bus System:** `src/acms/event_bus.py`
- **Orchestrator:** `src/acms/controller.py`
- **Invoke Tasks:** `tasks.py`

---

## Decision History

**2025-12-07:** Archived as part of overlap/deprecation cleanup
- No imports found in codebase
- Manual orchestration preferred
- Invoke tasks provide better UX
- Can be restored from git history if needed

---

**Archived by:** Automated cleanup process  
**Verification:** No references found via `grep -rn "import.*_trigger" src/`  
**Restoration:** Available from git history or this archive directory
