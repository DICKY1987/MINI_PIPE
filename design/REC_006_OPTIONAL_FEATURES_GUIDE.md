# REC_006: Optional Features Integration - Implementation Guide

**Document ID:** REC_006_OPTIONAL_FEATURES_GUIDE  
**Version:** 1.0.0  
**Date:** 2025-12-07  
**Status:** 📋 **SPECIFICATION** (Ready for Implementation)  
**Priority:** P3 (Enhancement - Not Required for Production)  
**Estimated Time:** 30-45 minutes

---

## Overview

This document describes how to integrate resilience and patch ledger features into ACMS in a **controlled, opt-in manner**. These features add robustness and granular audit capabilities but increase complexity, so they should:

1. Be **disabled by default** on the golden path
2. Be **explicitly enabled** via configuration
3. **Not break** existing minimal/golden path flows
4. Have **clear logging** when active

---

## Goal

Integrate advanced features behind configuration flags:
- **Resilience Layer:** Circuit breakers, retries, recovery logic
- **Patch Ledger:** Granular change tracking and state machine for individual patches

Both features should be:
- ✅ Optional (default: OFF)
- ✅ Clearly documented
- ✅ Easy to enable/disable
- ✅ Well-tested independently

---

## Architecture

### Current (Golden Path)

```
acms_controller.run_full_cycle()
  → gap_registry
  → execution_planner
  → phase_plan_compiler
  → acms_minipipe_adapter
      → MINI_PIPE_orchestrator
          → MINI_PIPE_scheduler
          → MINI_PIPE_executor  <-- Direct execution
              → MINI_PIPE_tools
```

### With Optional Features Enabled

```
acms_controller.run_full_cycle()
  → gap_registry
  → execution_planner
  → phase_plan_compiler
  → acms_minipipe_adapter [resilience_enabled=True, patch_ledger_enabled=True]
      → MINI_PIPE_orchestrator
          → MINI_PIPE_scheduler
          → MINI_PIPE_resilient_executor  <-- Wraps executor
              → MINI_PIPE_executor
                  → MINI_PIPE_circuit_breaker
                  → MINI_PIPE_retry
                  → MINI_PIPE_tools
                      → MINI_PIPE_patch_converter
                      → MINI_PIPE_patch_ledger
```

---

## Configuration Model

### Central Config File: `acms_config.yaml`

Create a central configuration file (YAML or JSON) that controls optional features:

```yaml
# acms_config.yaml
run:
  default_mode: "full"
  max_concurrent_tasks: 4
  timeout_seconds: 3600

features:
  # Resilience features (circuit breakers, retries, recovery)
  enable_resilience: false
  
  # Patch ledger for granular change tracking
  enable_patch_ledger: false
  
  # Process spawner for long-lived workers
  enable_process_spawner: false
  
  # File system triggers (auto-routing, monitoring)
  enable_triggers: false

resilience:
  # Circuit breaker settings
  circuit_breaker:
    failure_threshold: 5
    timeout_seconds: 60
    half_open_attempts: 3
  
  # Retry settings
  retry:
    max_attempts: 3
    initial_delay_seconds: 1
    max_delay_seconds: 30
    backoff_multiplier: 2.0
  
  # Recovery settings
  recovery:
    enable_auto_recovery: true
    max_recovery_attempts: 2

patch_ledger:
  # Patch tracking settings
  storage_path: ".acms_runs/{run_id}/patches/"
  track_verification: true
  auto_quarantine_on_failure: true

logging:
  level: "INFO"
  format: "json"
  log_file: ".acms_runs/{run_id}/run.log"
```

### Environment Variable Override

Support environment variables for CI/CD:

```bash
# Enable resilience in CI
export ACMS_ENABLE_RESILIENCE=true

# Enable patch ledger in production
export ACMS_ENABLE_PATCH_LEDGER=true
```

### CLI Flag Override

Support command-line flags for one-off usage:

```bash
# Enable resilience for this run
python acms_controller.py . --enable-resilience

# Enable both features
python acms_controller.py . --enable-resilience --enable-patch-ledger
```

---

## Implementation Tasks

### Task 1: Create Configuration System

**File:** `acms_config.py`

```python
"""
ACMS configuration management with defaults and overrides.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "run": {
        "default_mode": "full",
        "max_concurrent_tasks": 4,
        "timeout_seconds": 3600,
    },
    "features": {
        "enable_resilience": False,
        "enable_patch_ledger": False,
        "enable_process_spawner": False,
        "enable_triggers": False,
    },
    "resilience": {
        "circuit_breaker": {
            "failure_threshold": 5,
            "timeout_seconds": 60,
            "half_open_attempts": 3,
        },
        "retry": {
            "max_attempts": 3,
            "initial_delay_seconds": 1,
            "max_delay_seconds": 30,
            "backoff_multiplier": 2.0,
        },
        "recovery": {
            "enable_auto_recovery": True,
            "max_recovery_attempts": 2,
        },
    },
    "patch_ledger": {
        "storage_path": ".acms_runs/{run_id}/patches/",
        "track_verification": True,
        "auto_quarantine_on_failure": True,
    },
    "logging": {
        "level": "INFO",
        "format": "json",
        "log_file": ".acms_runs/{run_id}/run.log",
    },
}

class AcmsConfig:
    """ACMS configuration with layered overrides."""
    
    def __init__(self, config_path: str = None):
        """
        Load configuration with precedence:
        1. Environment variables (highest)
        2. Config file (if provided)
        3. Defaults (lowest)
        """
        self.config = DEFAULT_CONFIG.copy()
        
        # Layer 1: Load from file if provided
        if config_path and Path(config_path).exists():
            self._load_from_file(config_path)
        
        # Layer 2: Override with environment variables
        self._load_from_env()
    
    def _load_from_file(self, path: str):
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            file_config = yaml.safe_load(f)
        self._deep_merge(self.config, file_config)
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Boolean feature flags
        for feature in ["resilience", "patch_ledger", "process_spawner", "triggers"]:
            env_var = f"ACMS_ENABLE_{feature.upper()}"
            if env_var in os.environ:
                value = os.environ[env_var].lower() in ("true", "1", "yes")
                self.config["features"][f"enable_{feature}"] = value
    
    def _deep_merge(self, base: Dict, override: Dict):
        """Deep merge override into base."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, path: str, default=None) -> Any:
        """Get config value by dot-separated path."""
        parts = path.split(".")
        current = self.config
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    
    def is_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        return self.get(f"features.enable_{feature}", False)
    
    def to_dict(self) -> Dict:
        """Return full config as dict."""
        return self.config.copy()


# Global config instance
_config = None

def get_config(config_path: str = None) -> AcmsConfig:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = AcmsConfig(config_path)
    return _config
```

**Estimated Time:** 10 minutes

---

### Task 2: Update `acms_controller.py`

Add configuration awareness and feature toggling:

```python
# In acms_controller.py

from acms_config import get_config

class AcmsController:
    def __init__(self, repo_root: str, config_path: str = None):
        self.repo_root = repo_root
        self.config = get_config(config_path)
        self.run_id = None
        self.current_state = RunState.INIT
        # ... existing code ...
    
    def run_full_cycle(self, mode: str = "full") -> Dict[str, Any]:
        """Run full ACMS pipeline with optional features."""
        self.run_id = self._generate_run_id()
        
        # Log feature status
        self._log_feature_status()
        
        try:
            # ... existing phases ...
            
            # Phase 4: Execution (with optional features)
            if mode in ("full", "execute_only"):
                self._transition_state(RunState.EXECUTION)
                execution_result = self._run_execution_phase()
        
        # ... rest of method ...
    
    def _log_feature_status(self):
        """Log which optional features are enabled."""
        features = {
            "resilience": self.config.is_enabled("resilience"),
            "patch_ledger": self.config.is_enabled("patch_ledger"),
            "process_spawner": self.config.is_enabled("process_spawner"),
            "triggers": self.config.is_enabled("triggers"),
        }
        
        enabled_features = [k for k, v in features.items() if v]
        
        if enabled_features:
            print(f"[CONFIG] Optional features enabled: {', '.join(enabled_features)}")
        else:
            print("[CONFIG] Running with golden path (no optional features)")
        
        self._log_event("config_loaded", meta={"features": features})
    
    def _run_execution_phase(self) -> Dict[str, Any]:
        """Execute via MINI_PIPE with optional features."""
        from acms_minipipe_adapter import execute_with_minipipe
        
        return execute_with_minipipe(
            plan_path=self.execution_plan_path,
            run_id=self.run_id,
            repo_root=self.repo_root,
            resilience_enabled=self.config.is_enabled("resilience"),
            patch_ledger_enabled=self.config.is_enabled("patch_ledger"),
        )
```

**Estimated Time:** 10 minutes

---

### Task 3: Update `acms_minipipe_adapter.py`

Add feature flags and conditional wiring:

```python
# In acms_minipipe_adapter.py

def execute_with_minipipe(
    plan_path: str,
    run_id: str,
    repo_root: str,
    resilience_enabled: bool = False,
    patch_ledger_enabled: bool = False,
) -> Dict[str, Any]:
    """
    Execute plan via MINI_PIPE with optional features.
    
    Args:
        plan_path: Path to execution plan JSON
        run_id: Unique run identifier
        repo_root: Repository root path
        resilience_enabled: Enable circuit breakers, retries, recovery
        patch_ledger_enabled: Enable granular patch tracking
    
    Returns:
        Execution results with metrics
    """
    from MINI_PIPE_orchestrator import create_run, execute_plan
    from acms_config import get_config
    
    config = get_config()
    
    # Log feature usage
    features = []
    if resilience_enabled:
        features.append("resilience")
    if patch_ledger_enabled:
        features.append("patch_ledger")
    
    print(f"[MINIPIPE] Executing with features: {', '.join(features) if features else 'none'}")
    
    # Create MINI_PIPE run
    mini_run_id = create_run(
        run_id=run_id,
        plan_path=plan_path,
        repo_root=repo_root,
    )
    
    # Configure executor based on features
    executor_config = {
        "use_resilient_executor": resilience_enabled,
        "enable_patch_ledger": patch_ledger_enabled,
    }
    
    if resilience_enabled:
        # Add resilience configuration
        executor_config.update({
            "circuit_breaker": config.get("resilience.circuit_breaker"),
            "retry": config.get("resilience.retry"),
            "recovery": config.get("resilience.recovery"),
        })
    
    if patch_ledger_enabled:
        # Add patch ledger configuration
        executor_config.update({
            "patch_storage_path": config.get("patch_ledger.storage_path").format(run_id=run_id),
            "track_verification": config.get("patch_ledger.track_verification"),
            "auto_quarantine": config.get("patch_ledger.auto_quarantine_on_failure"),
        })
    
    # Execute with configured features
    result = execute_plan(
        run_id=mini_run_id,
        executor_config=executor_config,
    )
    
    return result
```

**Estimated Time:** 10 minutes

---

### Task 4: Wire Resilience Features (Conditional)

Update MINI_PIPE components to check configuration:

```python
# In MINI_PIPE_executor.py or new executor_factory.py

from acms_config import get_config

def create_executor(config_dict: Dict = None):
    """
    Factory to create executor based on configuration.
    
    Returns:
        - ResilientExecutor if resilience enabled
        - Standard Executor otherwise
    """
    if config_dict and config_dict.get("use_resilient_executor"):
        from MINI_PIPE_resilient_executor import ResilientExecutor
        from MINI_PIPE_circuit_breaker import CircuitBreaker
        from MINI_PIPE_retry import RetryStrategy
        
        print("[EXECUTOR] Using ResilientExecutor with circuit breakers and retries")
        
        return ResilientExecutor(
            circuit_breaker_config=config_dict.get("circuit_breaker"),
            retry_config=config_dict.get("retry"),
            recovery_config=config_dict.get("recovery"),
        )
    else:
        from MINI_PIPE_executor import Executor
        print("[EXECUTOR] Using standard Executor (golden path)")
        return Executor()
```

**Estimated Time:** 5 minutes

---

### Task 5: Wire Patch Ledger (Conditional)

Update tool execution to use patch ledger when enabled:

```python
# In MINI_PIPE_tools.py

def execute_tool(tool_id: str, task: Dict, config: Dict = None) -> Dict:
    """Execute tool with optional patch ledger tracking."""
    
    use_patch_ledger = config and config.get("enable_patch_ledger", False)
    
    if use_patch_ledger:
        from MINI_PIPE_patch_converter import convert_output_to_patches
        from MINI_PIPE_patch_ledger import PatchLedger
        
        print(f"[TOOL] Executing {tool_id} with patch ledger enabled")
        
        # Execute tool
        raw_result = _execute_tool_raw(tool_id, task)
        
        # Convert to patches
        patches = convert_output_to_patches(raw_result)
        
        # Track in ledger
        ledger = PatchLedger(storage_path=config["patch_storage_path"])
        for patch in patches:
            ledger.record_patch(patch)
        
        return {
            "status": "success",
            "patches_created": len(patches),
            "ledger_path": ledger.get_ledger_path(),
        }
    else:
        # Standard execution (golden path)
        return _execute_tool_raw(tool_id, task)
```

**Estimated Time:** 5 minutes

---

### Task 6: Update Documentation

Update key documents to describe optional features:

**Files to update:**
- `acms_golden_path.py` - Add section on optional features
- `README_ACMS.md` - Document feature flags
- `ACMS_IMPLEMENTATION_GUIDE.md` - Add configuration examples

**Example addition to acms_golden_path.py:**

```python
OPTIONAL_FEATURES = {
    "resilience": {
        "description": "Circuit breakers, retries, and recovery logic",
        "default": False,
        "components": [
            "MINI_PIPE_resilient_executor",
            "MINI_PIPE_circuit_breaker",
            "MINI_PIPE_retry",
            "MINI_PIPE_recovery",
        ],
        "use_cases": [
            "Production environments with flaky AI services",
            "Long-running executions that need fault tolerance",
            "Environments with rate limits or quotas",
        ],
    },
    "patch_ledger": {
        "description": "Granular change tracking with state machine per patch",
        "default": False,
        "components": [
            "MINI_PIPE_patch_converter",
            "MINI_PIPE_patch_ledger",
        ],
        "use_cases": [
            "Compliance environments requiring detailed audit trails",
            "Rollback capabilities at patch granularity",
            "Verification workflows before applying changes",
        ],
    },
}
```

**Estimated Time:** 5 minutes (total for all docs)

---

## Testing Plan

### Test 1: Default Golden Path (No Features)

```bash
# Should work exactly as before
python demo_minimal_scenario.py
```

**Expected:**
- No resilience components loaded
- No patch ledger created
- Logs show: "Running with golden path (no optional features)"

### Test 2: Resilience Enabled

```bash
# Via environment variable
export ACMS_ENABLE_RESILIENCE=true
python demo_minimal_scenario.py
```

**Expected:**
- Logs show: "Optional features enabled: resilience"
- ResilientExecutor used instead of standard Executor
- Circuit breaker metrics visible in run_status.json

### Test 3: Patch Ledger Enabled

```bash
# Via config file
cat > acms_config.yaml << EOF
features:
  enable_patch_ledger: true
EOF

python acms_controller.py test_repo/ --config acms_config.yaml
```

**Expected:**
- Logs show: "Optional features enabled: patch_ledger"
- Patches directory created at `.acms_runs/{run_id}/patches/`
- Patch ledger JSON files created

### Test 4: Both Features Enabled

```bash
# Via CLI flags
python acms_controller.py test_repo/ --enable-resilience --enable-patch-ledger
```

**Expected:**
- Both features active
- No conflicts or errors
- All artifacts created correctly

### Test 5: Schema Validation

```bash
# Validate that new config structures pass validation
python validate_everything.py
```

**Expected:**
- Config files validate against schema
- Run status includes feature flags
- No validation errors

---

## Definition of Done

- [ ] `acms_config.py` created with layered configuration
- [ ] `acms_controller.py` updated with feature logging
- [ ] `acms_minipipe_adapter.py` passes feature flags to MINI_PIPE
- [ ] Resilience components wired conditionally
- [ ] Patch ledger components wired conditionally
- [ ] Documentation updated (3 files)
- [ ] All 5 tests pass
- [ ] No breaking changes to golden path
- [ ] Feature flags visible in run_status.json
- [ ] Logs clearly indicate which features are active

---

## Migration Notes

### For Existing Users

No changes required. All optional features are **disabled by default**.

### For Users Wanting Resilience

```yaml
# Add to acms_config.yaml
features:
  enable_resilience: true
```

### For Users Wanting Patch Ledger

```yaml
# Add to acms_config.yaml
features:
  enable_patch_ledger: true

patch_ledger:
  storage_path: ".acms_runs/{run_id}/patches/"
  track_verification: true
  auto_quarantine_on_failure: true
```

---

## Benefits of This Approach

✅ **Backward Compatible:** Golden path unchanged  
✅ **Opt-In:** Features explicitly enabled, not accidentally triggered  
✅ **Observable:** Clear logging when features are active  
✅ **Testable:** Each feature can be tested independently  
✅ **Documented:** Configuration model is explicit and versioned  
✅ **Flexible:** CLI, env vars, or config file can control features  

---

## File Checklist

**New Files (1):**
- [ ] `acms_config.py` - Configuration system

**Modified Files (5):**
- [ ] `acms_controller.py` - Feature logging and config integration
- [ ] `acms_minipipe_adapter.py` - Feature flag passing
- [ ] `MINI_PIPE_executor.py` or `executor_factory.py` - Conditional executor
- [ ] `MINI_PIPE_tools.py` - Conditional patch ledger
- [ ] `acms_golden_path.py` - Optional features documentation

**Updated Documentation (3):**
- [ ] `README_ACMS.md` - Feature flags section
- [ ] `ACMS_IMPLEMENTATION_GUIDE.md` - Configuration examples
- [ ] `ACMS_HARDENING_PROGRESS.md` - Mark REC_006 complete

---

## Timeline

| Task | Time | Cumulative |
|------|------|------------|
| Task 1: Configuration system | 10 min | 10 min |
| Task 2: Update controller | 10 min | 20 min |
| Task 3: Update adapter | 10 min | 30 min |
| Task 4: Wire resilience | 5 min | 35 min |
| Task 5: Wire patch ledger | 5 min | 40 min |
| Task 6: Update docs | 5 min | 45 min |
| Testing | 10 min | 55 min |

**Total Estimated Time:** 45-55 minutes

---

## Next Steps

1. Review this specification
2. Implement tasks 1-6 in order
3. Run all 5 tests
4. Update `ACMS_HARDENING_PROGRESS.md` to mark REC_006 complete
5. Update `ACMS_PROJECT_COMPLETION_REPORT.md` to show 100% completion

---

**Status:** Ready for implementation  
**Complexity:** Low (well-scoped, clear interfaces)  
**Risk:** Very low (additive changes, no golden path modifications)  
**Value:** High for production users needing resilience or audit trails
