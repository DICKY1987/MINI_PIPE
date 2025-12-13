# Agent Execution Profile Bundle

## Overview
This bundle combines two complementary execution profiles into a single indexed JSON file for clean composition and precision editing.

## Bundle Structure

```
AGENT_EXECUTION_PROFILE_BUNDLE.json
├── meta (bundle-level metadata)
├── index (namespaced indices for both profiles)
│   ├── profiles (root paths)
│   ├── multi_agent (22 entries with /profiles/multi_agent prefix)
│   └── dont_stop (8 entries with /profiles/dont_stop prefix)
├── profiles
│   ├── multi_agent (full MULTI_AGENT_AUTONOMOUS_EXECUTION content)
│   └── dont_stop (full DONT_STOP_AUTONOMOUS_EXECUTION content)
└── composition (application rules)
```

## Profiles Included

### 1. Multi-Agent Autonomous Execution
**Path**: `/profiles/multi_agent`
**Source**: `MULTI AGENT PROMNT.json`
**ID**: `MULTI_AGENT_AUTONOMOUS_EXECUTION`

**Content**:
- Agent context and role definition
- Execution instructions and constraints
- Reasoning framework
- 4-phase execution protocol (Planning → Implementation → Validation → Delivery)
- Complete git workflow for task completion
- Integration flow for multi-agent orchestration
- Structured output format

**Index Categories**:
- `metadata` - Bundle and version info
- `variables` - Agent number, workstream ID
- `core_config` - Role, instructions, reasoning, execution protocol
- `constraints` - Mandatory actions, prohibited behaviors, quality gates
- `workflow` - Completion workflow, preconditions, agent steps, integration flow
- `output` - Output format specifications
- `tasks` - Task instructions

### 2. Don't Stop Autonomous Execution
**Path**: `/profiles/dont_stop`
**Source**: `dont stop.json`
**ID**: `DONT_STOP_AUTONOMOUS_EXECUTION`

**Content**:
- Continuous execution directives
- Autonomous decision-making principles
- No-stop-until-complete mandate
- Completion protocol (branch creation + commit)
- Performance focus and monitoring

**Index Categories**:
- `metadata` - Directive identification
- `directives` - 6 execution directives (complete tasks, autonomous decisions, no stop, completion protocol, performance focus, operating mode)

## Composition Rules

The bundle includes application rules in the `composition` section:

1. **Load** `/profiles/multi_agent` as the base execution prompt
2. **Apply** directive semantics from `/profiles/dont_stop/directives` and `/profiles/dont_stop/execution_characteristics`
3. **Conflict resolution**: Let explicit directive fields win for execution behavior (e.g., `user_interaction`, `completion_requirement`)

## Usage

### For AI CLI Tools

```python
import json

# Load bundle
with open('AGENT_EXECUTION_PROFILE_BUNDLE.json') as f:
    bundle = json.load(f)

# Get base prompt
multi_agent = bundle['profiles']['multi_agent']

# Get directives
dont_stop = bundle['profiles']['dont_stop']

# Apply composition
# - Use multi_agent for workflow structure
# - Override with dont_stop for execution characteristics
execution_mode = dont_stop['directives']['no_stop_until_complete']
# execution_mode['execution_mode'] == 'run_to_completion'
```

### Precision Editing with JSON Pointer

The index enables targeted edits without brittle array indexing:

```python
# Look up what to edit
agent_number_path = bundle['index']['multi_agent']['variables']['AGENT_NUMBER']['path']
# Returns: "/profiles/multi_agent/agent_context/agent_number"

# Apply JSON Patch
import jsonpatch
patch = [
    {
        "op": "replace",
        "path": agent_number_path,
        "value": "5"
    }
]
patched = jsonpatch.apply_patch(bundle, patch)
```

### Finding All Directive Paths

```python
# List all dont_stop directives
for directive_name, directive_info in bundle['index']['dont_stop']['directives'].items():
    print(f"{directive_name}: {directive_info['path']}")
    print(f"  Description: {directive_info['description']}")
```

## Index Structure

### Profile Root Paths
```json
{
  "index": {
    "profiles": {
      "MULTI_AGENT_AUTONOMOUS_EXECUTION": {
        "path": "/profiles/multi_agent",
        "description": "Root of the multi-agent execution prompt profile"
      },
      "DONT_STOP_AUTONOMOUS_EXECUTION": {
        "path": "/profiles/dont_stop",
        "description": "Root of the dont-stop autonomous execution directive profile"
      }
    }
  }
}
```

### Namespaced Entry Example
Original path in `MULTI AGENT PROMNT.json`:
```json
{
  "path": "/agent_context/agent_number"
}
```

Namespaced path in bundle:
```json
{
  "path": "/profiles/multi_agent/agent_context/agent_number"
}
```

## File Statistics

- **Bundle ID**: `AGENT_EXECUTION_PROFILE_V1`
- **Version**: `1.0.0`
- **Profiles**: 2
- **Total Index Entries**: 32
  - Multi-agent: 22 entries
  - Dont-stop: 8 entries
  - Profile roots: 2 entries
- **File Size**: ~19KB

## Benefits

1. **Single Source of Truth**: One file contains both profiles with clear namespace separation
2. **Precision Editing**: Index enables JSON Pointer-based edits without fragile array positions
3. **Composition Clarity**: Explicit rules for how profiles layer together
4. **Backward Compatible**: Each profile retains its original structure under `/profiles/*`
5. **Tool-Friendly**: Easy for automation to parse, compose, and patch

## Version History

### v1.0.0 (2025-12-06)
- Initial bundle creation
- Combined MULTI_AGENT_AUTONOMOUS_EXECUTION and DONT_STOP_AUTONOMOUS_EXECUTION
- Namespaced index with path rewriting
- Composition rules defined

## Related Files

- `MULTI AGENT PROMNT.json` - Original multi-agent prompt
- `dont stop.json` - Original dont-stop directive
- `JSON_CONVERSION_AND_MERGE_SUMMARY.md` - Earlier conversion/merge documentation
