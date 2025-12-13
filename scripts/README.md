# Scripts

This folder contains executable scripts and orchestration tools for the MINI_PIPE system.

## Contents

### Test Harness
- `acms_test_harness.py` - End-to-end test harness for ACMS/MINI_PIPE
  - Usage: `python scripts/acms_test_harness.py plan --repo-root <path>`
  - Usage: `python scripts/acms_test_harness.py e2e --repo-root <path>`

### Orchestration
- `multi_agent_orchestrator.py` - Multi-agent orchestrator for workstream execution
  - Automates parallel execution of workstreams across multiple AI agents
  - Manages workstream dependencies and execution state

### Validation
- `validate_wave1.py` - Wave 1 validation script
  - Standalone validation tool (not part of main invoke tasks)

## Purpose

This folder contains:
- Test harnesses and end-to-end testing tools
- Orchestration scripts for complex workflows
- Standalone validation and utility scripts

## Usage

These scripts are meant to be run directly from the command line:

```bash
# Run test harness
python scripts/acms_test_harness.py plan --repo-root .

# Run orchestrator
python scripts/multi_agent_orchestrator.py [options]
```

## Note

For common development tasks, use the `invoke` task runner instead (see `inv --list`). These scripts are for specialized use cases or standalone execution.
