---
doc_id: DOC-GUIDE-DOC-ID-SYSTEM-TECHNICAL-DOCUMENTATION-001
title: Doc ID System - Technical Documentation
version: 1.0.0
author: Technical Documentation Engineer
date: 2025-12-13
status: active
category: guide
---

# Doc ID System - Technical Documentation

## Assumptions

This document assumes the following:

1. The repository is a Python-based monorepo with multiple file types (Python, Markdown, YAML, JSON, PowerShell, Shell scripts)
2. The doc_id system is intended for documentation traceability and discoverability across the entire codebase
3. Users have Python 3.7+ installed with the following packages: PyYAML, watchdog (optional for file watching)
4. The system operates in both Windows and Unix-like environments
5. Git is used for version control
6. The system is designed to scale to thousands of documents
7. Integration with CI/CD pipelines is a key requirement

---

## 1. System Overview

### 1.1 Purpose

The **doc_id system** is a comprehensive documentation identifier management framework designed to:

- Assign unique identifiers (doc_ids) to all eligible files in the repository
- Track documentation coverage across the codebase
- Detect and remediate documentation drift and duplicates
- Enable cross-referencing and traceability between documents
- Automate documentation quality validation
- Generate coverage reports and trends
- Integrate with pre-commit hooks and CI/CD pipelines

### 1.2 Business Context

In large-scale AI development pipelines, maintaining documentation consistency and traceability is critical. The doc_id system addresses:

- **Discoverability**: Finding documents by unique identifiers rather than file paths
- **Version Control**: Tracking documentation changes over time
- **Quality Assurance**: Ensuring documentation coverage meets baseline thresholds
- **Automation**: Reducing manual effort in documentation management
- **Integration**: Connecting documentation with code, patterns, and execution templates
- **Compliance**: Meeting internal documentation standards

### 1.3 Core Concepts

**Doc ID Format**: `DOC-{CATEGORY}-{NAME}-{NUMBER}`
- Example: `DOC-CORE-SCHEDULER-123`
- Category: Classification of document type (CORE, GUIDE, PAT, SCRIPT, etc.)
- Name: Descriptive identifier (can have multiple segments separated by dashes)
- Number: Three-digit sequential identifier (001-999)

**Registry**: Central YAML file (`DOC_ID_REGISTRY.yaml`) that stores all doc_id assignments with metadata

**Inventory**: JSON Lines file (`docs_inventory.jsonl`) that tracks the current state of all eligible files in the repository

---

## 2. Component Architecture

### 2.1 Core Components

| Component | Purpose | Type |
|-----------|---------|------|
| **DOC_ID_REGISTRY.yaml** | Central registry of all doc_id assignments | Data Store |
| **docs_inventory.jsonl** | Real-time inventory of file scan results | Data Store |
| **doc_id_registry_cli.py** | CLI for managing registry operations | Service |
| **doc_id_scanner.py** | Repository scanner for doc_id detection | Service |
| **doc_id_assigner.py** | Automated doc_id assignment engine | Service |
| **file_watcher.py** | Real-time file system monitor | Service |

### 2.2 Automation Services

| Service | Purpose | Execution Mode |
|---------|---------|----------------|
| **automation_runner.ps1** | Orchestrates all automation tasks | Batch/Scheduled |
| **pre_commit_hook.py** | Pre-commit validation | Git Hook |
| **scheduled_report_generator.py** | Daily/weekly reporting | Scheduled Task |
| **alert_monitor.py** | Threshold-based alerting | Scheduled Task |

### 2.3 Maintenance Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| **fix_duplicate_doc_ids.py** | Resolves duplicate doc_ids | Manual/Automated |
| **fix_invalid_doc_ids.py** | Remediates malformed doc_ids | Manual/Automated |
| **cleanup_invalid_doc_ids.py** | Removes invalid entries | Manual/Automated |
| **sync_registries.py** | Synchronizes registry and inventory | Scheduled |
| **detect_doc_drift.py** | Detects documentation drift | Scheduled |

### 2.4 Validation & Reporting

| Tool | Purpose | Integration |
|------|---------|-------------|
| **validate_doc_id_coverage.py** | Validates coverage thresholds | CI/CD |
| **validate_doc_id_consistency.ps1** | Ensures format consistency | CI/CD |
| **doc_id_coverage_trend.py** | Tracks coverage trends | Reporting |
| **test_doc_id_system.py** | Comprehensive system tests | Testing |

---

## 3. File Breakdown

### 3.1 Data Files

#### DOC_ID_REGISTRY.yaml
- **Purpose**: Central registry of all doc_id assignments
- **Location**: `doc_id/DOC_ID_REGISTRY.yaml`
- **Input**: None (managed by registry CLI)
- **Output**: Registry data for all tools
- **Dependencies**: PyYAML
- **Structure**:
  ```yaml
  doc_id: DOC-GUIDE-DOC-ID-REGISTRY-724
  metadata:
    version: 1.0.0
    created: '2025-12-04'
    last_updated: '2025-12-05'
    total_docs: 2357
  categories:
    core:
      prefix: CORE
      description: Core system components
      next_id: 764
      count: 261
  docs:
    - doc_id: DOC-CORE-SCHEDULER-001
      category: core
      name: scheduler
      title: Task Scheduler
      status: active
      artifacts: []
      created: '2025-12-03'
      last_modified: '2025-12-03'
      tags: []
  ```

#### docs_inventory.jsonl
- **Purpose**: Real-time inventory of file scan results
- **Location**: `docs_inventory.jsonl` (repository root)
- **Input**: Generated by doc_id_scanner.py
- **Output**: Consumed by all analysis tools
- **Dependencies**: None (JSON Lines format)
- **Structure**:
  ```json
  {"path": "core/scheduler.py", "doc_id": "DOC-CORE-SCHEDULER-001", "status": "registered", "file_type": "py", "last_modified": "2025-12-05T10:30:00", "scanned_at": "2025-12-05T12:00:00"}
  {"path": "docs/guide.md", "doc_id": null, "status": "missing", "file_type": "md", "last_modified": "2025-12-04T09:15:00", "scanned_at": "2025-12-05T12:00:00"}
  ```

### 3.2 Core Services

#### doc_id_registry_cli.py
- **Purpose**: CLI for managing the DOC_ID_REGISTRY.yaml
- **Location**: `doc_id/tools/doc_id_registry_cli.py`
- **Input**: Command-line arguments
- **Output**: Updated registry, console output
- **Dependencies**: PyYAML
- **Key Functions**:
  - `mint_doc_id()`: Generate new doc_id
  - `validate()`: Validate registry integrity
  - `search()`: Search for doc_ids by pattern
  - `stats()`: Display registry statistics
- **Usage**:
  ```bash
  python doc_id/tools/doc_id_registry_cli.py mint --category CORE --name SCHEDULER
  python doc_id/tools/doc_id_registry_cli.py validate
  python doc_id/tools/doc_id_registry_cli.py search --pattern "CORE-.*"
  ```

#### doc_id_scanner.py
- **Purpose**: Scan repository for doc_id presence and generate inventory
- **Location**: `doc_id/doc_id_scanner.py`
- **Input**: Repository files
- **Output**: docs_inventory.jsonl
- **Dependencies**: None (stdlib only)
- **Key Functions**:
  - `scan()`: Full repository scan
  - `extract_doc_id_python()`: Extract doc_id from Python files
  - `extract_doc_id_markdown()`: Extract doc_id from Markdown YAML frontmatter
  - `extract_doc_id_yaml()`: Extract doc_id from YAML files
- **Usage**:
  ```bash
  python doc_id/doc_id_scanner.py scan
  python doc_id/doc_id_scanner.py stats
  python doc_id/doc_id_scanner.py report --format markdown
  ```

#### doc_id_assigner.py
- **Purpose**: Automatically assign doc_ids to files missing them
- **Location**: `doc_id/doc_id_assigner.py`
- **Input**: docs_inventory.jsonl, DOC_ID_REGISTRY.yaml
- **Output**: Updated files with doc_ids, updated registry
- **Dependencies**: PyYAML, doc_id_registry_cli module
- **Key Functions**:
  - `auto_assign()`: Assign doc_ids to eligible files
  - `inject_doc_id()`: Write doc_id into file content
  - `determine_category()`: Infer category from file path
- **Usage**:
  ```bash
  python doc_id/doc_id_assigner.py auto-assign --dry-run
  python doc_id/doc_id_assigner.py auto-assign --limit 50
  python doc_id/doc_id_assigner.py auto-assign
  ```

#### file_watcher.py
- **Purpose**: Monitor file system changes and trigger automatic scans
- **Location**: `doc_id/file_watcher.py`
- **Input**: File system events
- **Output**: Triggered scans via doc_id_scanner.py
- **Dependencies**: watchdog
- **Key Functions**:
  - `on_modified()`: Handle file modification events
  - `on_created()`: Handle file creation events
  - `trigger_scan()`: Execute scanner subprocess
- **Usage**:
  ```bash
  python doc_id/file_watcher.py
  python doc_id/file_watcher.py --debounce 600
  ```

### 3.3 Automation & Integration

#### automation_runner.ps1
- **Purpose**: Orchestrate all doc_id automation tasks
- **Location**: `doc_id/automation_runner.ps1`
- **Input**: Task parameter (scan, validate, cleanup, report, sync, all)
- **Output**: Execution logs, updated files
- **Dependencies**: Python, PowerShell
- **Key Functions**:
  - `Invoke-Scanner()`: Run scanner
  - `Invoke-Validation()`: Run coverage validation
  - `Invoke-Cleanup()`: Run cleanup tasks
  - `Invoke-Reporting()`: Generate reports
  - `Invoke-Sync()`: Synchronize registries
- **Usage**:
  ```powershell
  .\doc_id\automation_runner.ps1 -Task scan
  .\doc_id\automation_runner.ps1 -Task all -DryRun
  ```

#### pre_commit_hook.py
- **Purpose**: Validate doc_ids in staged files before commit
- **Location**: `doc_id/pre_commit_hook.py`
- **Input**: Git staged files
- **Output**: Exit code 0 (pass) or 1 (fail)
- **Dependencies**: Git
- **Key Functions**:
  - `get_staged_files()`: Get list of staged files
  - `validate_file_doc_ids()`: Validate doc_ids in file
- **Installation**:
  ```bash
  python doc_id/install_pre_commit_hook.py
  ```

#### scheduled_report_generator.py
- **Purpose**: Generate daily/weekly coverage and trend reports
- **Location**: `doc_id/scheduled_report_generator.py`
- **Input**: Inventory, registry, historical reports
- **Output**: JSON reports in doc_id/DOC_ID_reports/
- **Dependencies**: Python subprocess
- **Key Functions**:
  - `generate_daily_report()`: Create daily snapshot
  - `generate_weekly_report()`: Create weekly trend analysis
- **Usage**:
  ```bash
  python doc_id/scheduled_report_generator.py daily
  python doc_id/scheduled_report_generator.py weekly
  ```

### 3.4 Maintenance & Fix Tools

#### fix_duplicate_doc_ids.py
- **Purpose**: Detect and resolve duplicate doc_ids
- **Location**: `doc_id/fix_duplicate_doc_ids.py`
- **Input**: docs_inventory.jsonl
- **Output**: Updated files with unique doc_ids
- **Dependencies**: None
- **Key Functions**:
  - `analyze_duplicates()`: Find all duplicates
  - `generate_unique_doc_id()`: Create unique replacement
- **Usage**:
  ```bash
  python doc_id/fix_duplicate_doc_ids.py analyze
  python doc_id/fix_duplicate_doc_ids.py fix --dry-run
  python doc_id/fix_duplicate_doc_ids.py fix
  ```

#### fix_invalid_doc_ids.py
- **Purpose**: Detect and fix malformed doc_ids
- **Location**: `doc_id/fix_invalid_doc_ids.py`
- **Input**: docs_inventory.jsonl
- **Output**: Updated files with valid doc_ids
- **Dependencies**: None
- **Key Functions**:
  - `scan_invalid_doc_ids()`: Find malformed doc_ids
  - `fix_invalid_doc_id()`: Replace with valid format
- **Usage**:
  ```bash
  python doc_id/fix_invalid_doc_ids.py scan
  python doc_id/fix_invalid_doc_ids.py fix --backup
  ```

#### sync_registries.py
- **Purpose**: Synchronize doc_ids between registry and inventory
- **Location**: `doc_id/sync_registries.py`
- **Input**: DOC_ID_REGISTRY.yaml, docs_inventory.jsonl
- **Output**: Synchronized registry
- **Dependencies**: PyYAML
- **Key Functions**:
  - `check_sync()`: Check synchronization status
  - `sync_registries()`: Perform synchronization
- **Usage**:
  ```bash
  python doc_id/sync_registries.py check
  python doc_id/sync_registries.py sync --dry-run
  python doc_id/sync_registries.py sync
  ```

#### detect_doc_drift.py
- **Purpose**: Detect drift between documentation and code
- **Location**: `doc_id/detect_doc_drift.py`
- **Input**: Suite index, codebase index, file system
- **Output**: Drift findings report
- **Dependencies**: PyYAML
- **Key Functions**:
  - `detect_hash_mismatches()`: Detect content changes
  - `detect_temporal_drift()`: Detect timestamp mismatches
  - `detect_broken_cross_references()`: Detect broken links
  - `detect_documentation_gaps()`: Detect missing docs
- **Usage**:
  ```bash
  python doc_id/detect_doc_drift.py --suite-index suite-index.yaml --codebase-index codebase-index.yaml
  ```

### 3.5 Validation & Testing

#### validate_doc_id_coverage.py
- **Purpose**: Validate doc_id coverage against baseline threshold
- **Location**: `doc_id/validate_doc_id_coverage.py`
- **Input**: Repository files
- **Output**: Coverage report, exit code
- **Dependencies**: None
- **Key Functions**:
  - `scan_repository()`: Scan and calculate coverage
  - `validate_coverage()`: Check against baseline
- **Usage**:
  ```bash
  python doc_id/validate_doc_id_coverage.py
  python doc_id/validate_doc_id_coverage.py --baseline 0.92
  python doc_id/validate_doc_id_coverage.py --report coverage_report.json
  ```

#### test_doc_id_system.py
- **Purpose**: Comprehensive system tests
- **Location**: `doc_id/test_doc_id_system.py`
- **Input**: Registry, inventory, repository files
- **Output**: Test results
- **Dependencies**: pytest, PyYAML
- **Key Test Classes**:
  - `TestDocIDFormat`: Format compliance tests
  - `TestDocIDUniqueness`: Uniqueness validation
  - `TestDocIDRegistry`: Registry integrity tests
  - `TestDocIDScanner`: Scanner functionality tests
- **Usage**:
  ```bash
  pytest doc_id/test_doc_id_system.py
  pytest doc_id/test_doc_id_system.py -v -k "test_format"
  ```

---

## 4. Automation Flow

### 4.1 Manual Workflow

```
1. Developer creates new file
   ↓
2. Developer runs scanner:
   python doc_id/doc_id_scanner.py scan
   ↓
3. Scanner detects missing doc_id
   Updates docs_inventory.jsonl with status="missing"
   ↓
4. Developer runs assigner:
   python doc_id/doc_id_assigner.py auto-assign
   ↓
5. Assigner:
   - Loads inventory (finds files with status="missing")
   - Determines category from file path
   - Mints new doc_id via registry CLI
   - Injects doc_id into file content
   - Updates registry
   ↓
6. Developer commits changes
   ↓
7. Pre-commit hook validates doc_ids
   - Checks format compliance
   - Blocks commit if invalid
   ↓
8. Changes pushed to repository
```

### 4.2 Automated Workflow (Scheduled)

```
Daily Schedule (2:00 AM):
   ↓
1. automation_runner.ps1 -Task all
   ↓
2. Invoke-Scanner:
   - Runs doc_id_scanner.py scan
   - Generates updated docs_inventory.jsonl
   - Displays statistics
   ↓
3. Invoke-Validation:
   - Runs validate_doc_id_coverage.py
   - Checks against baseline threshold (e.g., 55%)
   - Logs pass/fail status
   ↓
4. Invoke-Cleanup:
   - Scans for invalid doc_ids
   - Fixes with backup (if not dry-run)
   - Removes malformed entries
   ↓
5. Invoke-Reporting:
   - Generates daily report (JSON)
   - Stores in doc_id/DOC_ID_reports/
   - Includes scanner stats, coverage results
   ↓
6. Invoke-Sync:
   - Checks registry-inventory sync
   - Updates registry with new doc_ids from inventory
   - Resolves discrepancies
   ↓
7. Alert Monitor (separate task):
   - Loads latest daily report
   - Checks metrics against thresholds
   - Generates alerts if thresholds breached
   - Logs alerts to .state/doc_id_alerts.json
```

### 4.3 File Watcher Workflow (Real-time)

```
1. file_watcher.py starts in background
   ↓
2. Monitors eligible file patterns:
   - *.py, *.md, *.yaml, *.yml, *.json, *.ps1, *.sh, *.txt
   ↓
3. File created/modified event detected
   ↓
4. Checks if file is eligible (not excluded)
   ↓
5. Debounce check (default 300 seconds)
   - If last scan < debounce interval: mark pending
   - Else: trigger scan
   ↓
6. Trigger scan:
   - Spawns subprocess: python doc_id_scanner.py scan
   - Updates inventory
   - Logs timestamp and file count
   ↓
7. Returns to monitoring state
```

### 4.4 CI/CD Integration Flow

```
1. Developer pushes changes
   ↓
2. CI/CD pipeline starts
   ↓
3. Pre-build validation:
   - python doc_id/validate_doc_id_coverage.py --baseline 0.55
   ↓
4. If coverage < baseline:
   - Exit code 1 (fail)
   - Pipeline halts
   - Developer notified
   ↓
5. If coverage >= baseline:
   - Exit code 0 (pass)
   - Pipeline continues
   ↓
6. Post-build reporting:
   - python doc_id/scheduled_report_generator.py daily
   - Archives report as CI artifact
```

### 4.5 Conditional Logic

**Category Determination (doc_id_assigner.py)**:
```python
if "test" in file_path or file_path.startswith("tests/"):
    category = "test"
elif "script" in file_path or file_path.startswith("scripts/"):
    category = "script"
elif "pattern" in file_path or file_path.startswith("patterns/"):
    category = "patterns"
elif "doc" in file_path or file_path.startswith("docs/"):
    category = "guide"
elif "core" in file_path:
    category = "core"
else:
    category = "guide"  # default
```

**Doc ID Injection Logic**:
```python
if file_type == "py":
    # Inject as comment at top: # DOC_LINK: DOC-CATEGORY-NAME-123
    inject_after_shebang()
elif file_type == "md":
    # Inject as YAML frontmatter
    if has_frontmatter():
        update_frontmatter(doc_id)
    else:
        create_frontmatter(doc_id)
elif file_type in ["yaml", "yml"]:
    # Inject as top-level field: doc_id: DOC-CATEGORY-NAME-123
    inject_yaml_field(doc_id)
elif file_type == "json":
    # Inject as root property: "doc_id": "DOC-CATEGORY-NAME-123"
    inject_json_field(doc_id)
elif file_type in ["ps1", "sh"]:
    # Inject as comment: # DOC_LINK: DOC-CATEGORY-NAME-123
    inject_comment(doc_id)
```

---

## 5. System Functions

### 5.1 Registry Management

#### Function: `DocIDRegistry.mint_doc_id(category, name, title, artifacts, tags)`
**Purpose**: Generate a new unique doc_id

**Logic**:
1. Validate category exists in registry
2. Get category prefix and next_id
3. Extract all used numbers for that category
4. Find next available 3-digit number (001-999)
5. Construct doc_id: `DOC-{prefix}-{name}-{number:03d}`
6. Validate format with regex
7. Check for duplicates
8. Create doc entry with metadata
9. Add to registry docs list
10. Increment category next_id
11. Update registry metadata (last_updated)
12. Save registry to YAML

**Returns**: New doc_id string (e.g., "DOC-CORE-SCHEDULER-123")

#### Function: `DocIDRegistry.validate()`
**Purpose**: Validate registry integrity

**Checks**:
- Format compliance for all doc_ids
- No duplicate doc_ids
- All categories have valid prefixes
- All doc entries have required fields
- Numeric IDs within valid range (001-999)
- Category counts match actual doc counts

**Returns**: Validation report (pass/fail + details)

### 5.2 Scanning & Inventory

#### Function: `DocIDScanner.scan()`
**Purpose**: Scan repository and generate inventory

**Logic**:
1. Iterate through repository using eligible patterns
2. For each file:
   - Check if excluded (e.g., .git, __pycache__)
   - Determine file type from extension
   - Extract doc_id based on file type
   - Get file metadata (last_modified, size)
   - Determine status (registered, missing, invalid)
3. Build inventory list
4. Write to docs_inventory.jsonl (JSON Lines format)
5. Calculate and display statistics

**Output**: docs_inventory.jsonl

#### Function: `DocIDScanner.extract_doc_id_python(content)`
**Purpose**: Extract doc_id from Python file

**Logic**:
1. Read first 50 lines
2. Search for patterns:
   - `DOC_ID: DOC-CATEGORY-NAME-123` (module docstring)
   - `# DOC_LINK: DOC-CATEGORY-NAME-123` (comment)
3. Validate format with regex
4. Return first valid match or None

**Returns**: doc_id string or None

### 5.3 Assignment & Injection

#### Function: `auto_assign(limit, dry_run)`
**Purpose**: Automatically assign doc_ids to files

**Logic**:
1. Load docs_inventory.jsonl
2. Filter entries with status="missing"
3. For each file (up to limit):
   - Determine category from file path
   - Generate name from file path/stem
   - Mint new doc_id via registry CLI
   - Read file content
   - Inject doc_id based on file type
   - Write updated content to file
   - Update inventory entry status="registered"
4. Save updated inventory
5. Display summary

**Dry-run**: Performs all logic but skips file writes

#### Function: `inject_doc_id(file_path, doc_id, file_type)`
**Purpose**: Inject doc_id into file content

**Logic**:
```python
if file_type == "py":
    # Find insertion point (after shebang/encoding)
    lines = content.split('\n')
    insert_idx = 0
    if lines[0].startswith('#!'):
        insert_idx = 1
    if insert_idx < len(lines) and 'coding' in lines[insert_idx]:
        insert_idx += 1
    # Insert: # DOC_LINK: {doc_id}
    lines.insert(insert_idx, f"# DOC_LINK: {doc_id}")
    return '\n'.join(lines)

elif file_type == "md":
    if content.startswith('---'):
        # Update YAML frontmatter
        # Note: Proper implementation should validate frontmatter is closed
        try:
            end_idx = content.index('---', 3)
        except ValueError:
            # Frontmatter not properly closed, create new one
            return f"---\ndoc_id: {doc_id}\n---\n\n{content}"
        frontmatter = content[3:end_idx]
        updated = frontmatter + f"\ndoc_id: {doc_id}\n"
        return '---' + updated + '---' + content[end_idx+3:]
    else:
        # Create new frontmatter
        return f"---\ndoc_id: {doc_id}\n---\n\n{content}"

# Similar logic for YAML, JSON, PS1, SH...
```

### 5.4 Validation & Compliance

#### Function: `validate_coverage(baseline)`
**Purpose**: Validate doc_id coverage against threshold

**Logic**:
1. Scan repository for eligible files
2. Count total eligible files
3. Count files with valid doc_ids
4. Calculate coverage: `(files_with_doc_id / total_eligible) * 100`
5. Compare to baseline
6. Return pass/fail with details

**Exit Codes**:
- 0: Coverage >= baseline
- 1: Coverage < baseline

#### Function: `validate_file_doc_ids(file_path)`
**Purpose**: Validate doc_ids in a file (pre-commit)

**Logic**:
1. Read file content
2. Extract all doc_ids using regex
3. Validate each doc_id format
4. Collect invalid doc_ids
5. Return pass/fail with list of invalid IDs

### 5.5 Synchronization & Drift Detection

#### Function: `sync_registries()`
**Purpose**: Synchronize registry and inventory

**Logic**:
1. Load registry doc_ids
2. Load inventory doc_ids
3. Compute set differences:
   - only_in_registry = registry_ids - inventory_ids
   - only_in_inventory = inventory_ids - registry_ids
4. For only_in_inventory:
   - Mint registry entry
   - Update registry
5. Display sync report

#### Function: `detect_drift()`
**Purpose**: Detect documentation drift

**Types of Drift**:
1. **Hash Mismatch**: File content changed but metadata hash unchanged
2. **Temporal Drift**: File modified after metadata timestamp
3. **Broken Cross-references**: doc_id referenced but doesn't exist
4. **Documentation Gap**: Code exists but no corresponding documentation

**Logic**:
1. Load suite index and codebase index
2. For each document:
   - Compute current file hash
   - Compare to stored hash
   - Check file mtime vs metadata timestamp
   - Extract doc_id references
   - Validate references exist
3. Generate drift findings list
4. Calculate severity scores
5. Return findings report

---

## 6. Data Structures

### 6.1 Doc ID Format

**Pattern**: `DOC-{CATEGORY}-{NAME}-{NUMBER}`

**Regex**: `^DOC-[A-Z0-9]+-[A-Z0-9]+(-[A-Z0-9]+)*-[0-9]{3}$`

**Components**:
- **Prefix**: Always "DOC"
- **Category**: Uppercase alphabetic prefix (e.g., CORE, GUIDE, PAT, SCRIPT)
- **Name**: One or more uppercase alphanumeric segments separated by dashes
- **Number**: Three-digit zero-padded number (001-999)

**Valid Examples**:
- `DOC-CORE-SCHEDULER-001`
- `DOC-GUIDE-SETUP-README-123`
- `DOC-PAT-BATCH-MINT-337`
- `DOC-SCRIPT-DOC-ID-SCANNER-046`

**Invalid Examples**:
- `DOC-TEST` (missing number)
- `DOC-TEST-1` (number not 3 digits)
- `doc-test-001` (lowercase)
- `DOC_TEST-001` (underscore instead of dash)
- `TEST-001` (missing DOC prefix)

### 6.2 Registry Schema

```yaml
doc_id: DOC-GUIDE-DOC-ID-REGISTRY-724
metadata:
  version: string             # Registry schema version
  created: date               # Initial creation date (YYYY-MM-DD)
  last_updated: date          # Last update timestamp (YYYY-MM-DD)
  total_docs: integer         # Total number of registered docs

categories:
  {category_name}:            # e.g., "core", "guide", "patterns"
    prefix: string            # Category prefix (e.g., "CORE", "GUIDE")
    description: string       # Human-readable description
    next_id: integer          # Next available ID number
    count: integer            # Number of docs in category

docs:
  - doc_id: string            # Unique doc identifier
    category: string          # Category name (lowercase)
    name: string              # Name identifier (lowercase with underscores)
    title: string             # Human-readable title
    status: string            # Status: "active", "deprecated", "archived"
    artifacts:                # List of associated artifacts
      - type: string          # Artifact type (e.g., "file", "module")
        path: string          # Relative path
    created: date             # Creation date (YYYY-MM-DD)
    last_modified: date       # Last modification date (YYYY-MM-DD)
    tags: [string]            # Optional tags for categorization
```

### 6.3 Inventory Schema (JSON Lines)

Each line is a JSON object:

```json
{
  "path": "string",                    // Relative file path
  "doc_id": "string|null",             // Assigned doc_id or null
  "status": "string",                  // "registered", "missing", "invalid"
  "file_type": "string",               // File extension (e.g., "py", "md")
  "last_modified": "ISO8601",          // File last modified timestamp
  "scanned_at": "ISO8601"              // Scan timestamp
}
```

**Status Values**:
- `registered`: File has valid doc_id
- `missing`: File is eligible but has no doc_id
- `invalid`: File has malformed doc_id

### 6.4 Report Schema (Daily Report)

```json
{
  "report_type": "daily",
  "generated_at": "ISO8601",
  "scanner": {
    "success": boolean,
    "output": "string"
  },
  "coverage": {
    "success": boolean,
    "output": "string",
    "exit_code": integer
  },
  "status": "string"                   // "✅ PASS" or "❌ FAIL"
}
```

### 6.5 Alert Schema

```json
{
  "threshold_name": "string",
  "metric": "string",
  "actual_value": float,
  "threshold_value": float,
  "operator": "string",                // "<", ">", "=="
  "message": "string",
  "severity": "string"                 // "critical", "warning", "info"
}
```

---

## 7. Deliverables

### 7.1 Primary Deliverables

| Deliverable | Format | Location | Frequency |
|-------------|--------|----------|-----------|
| **Doc ID Assignments** | YAML | DOC_ID_REGISTRY.yaml | Continuous |
| **Inventory Report** | JSON Lines | docs_inventory.jsonl | On-demand / Real-time |
| **Daily Coverage Report** | JSON | doc_id/DOC_ID_reports/daily_report_YYYYMMDD.json | Daily (2:00 AM) |
| **Weekly Trend Report** | JSON | doc_id/DOC_ID_reports/weekly_report_YYYYMMDD.json | Weekly |
| **Alert Log** | JSON | .state/doc_id_alerts.json | Real-time |

### 7.2 Deliverable Conditions

**Doc ID Assignment**:
- **Condition**: File is eligible (correct extension, not excluded)
- **Condition**: File does not already have a doc_id
- **Format**: Injected into file as comment, frontmatter, or field
- **Persistence**: Committed to version control

**Inventory Report**:
- **Condition**: Triggered by scan command or file watcher
- **Format**: JSON Lines (one JSON object per line)
- **Content**: All scanned files with doc_id status

**Daily Coverage Report**:
- **Condition**: Scheduled task executes (2:00 AM daily)
- **Format**: JSON with scanner and coverage results
- **Content**: 
  - Scanner statistics (total files, coverage %)
  - Coverage validation (pass/fail vs baseline)
  - Status summary

**Weekly Trend Report**:
- **Condition**: Scheduled task executes (weekly)
- **Format**: JSON with aggregated daily reports
- **Content**:
  - Trend analysis (coverage over time)
  - Regression detection
  - Summary statistics

**Alert Log**:
- **Condition**: Metric breaches threshold
- **Format**: JSON array of alert objects
- **Content**:
  - Threshold name and metric
  - Actual vs expected value
  - Severity level
  - Timestamp

### 7.3 Output Examples

**Console Output (Scan)**:
```
Scanning repository for doc_ids...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scan completed in 2.3 seconds

Total files scanned:     3,245
Files with doc_id:       1,782
Missing doc_id:          1,420
Invalid doc_id:          43

Coverage: 54.9%

Inventory saved to: docs_inventory.jsonl
```

**Console Output (Validation Fail)**:
```
Validating doc_id coverage...

Current coverage: 52.3% (1,698 / 3,245 files)
Baseline: 55.0%

❌ FAIL: Coverage below baseline
Shortfall: 88 files needed

Exit code: 1
```

---

## 8. Example Scenario

### Scenario: New Developer Adds Feature Module

**Initial State**:
- Repository has 3,000 files
- Coverage: 54%
- Registry has 1,620 doc_ids assigned

**Step 1: Developer creates new file**
```bash
# Developer creates new scheduler module
$ touch core/scheduler.py

# Writes code without doc_id
$ cat core/scheduler.py
#!/usr/bin/env python3
"""Task scheduler module."""

class TaskScheduler:
    def schedule(self, task):
        pass
```

**Step 2: Developer runs scanner**
```bash
$ python doc_id/doc_id_scanner.py scan

Scanning repository for doc_ids...
Total files scanned:     3,246
Files with doc_id:       1,620
Missing doc_id:          1,626 (+1)
Coverage: 49.9%
```

**Step 3: Scanner updates inventory**
```json
{"path": "core/scheduler.py", "doc_id": null, "status": "missing", "file_type": "py", "last_modified": "2025-12-13T10:30:00", "scanned_at": "2025-12-13T10:35:00"}
```

**Step 4: Developer runs auto-assigner (dry-run)**
```bash
$ python doc_id/doc_id_assigner.py auto-assign --limit 1 --dry-run

[DRY RUN] Auto-assigning doc_ids...

File: core/scheduler.py
  Category: core (inferred from path)
  Name: scheduler
  Would mint: DOC-CORE-SCHEDULER-764

Changes:
  1 file would be updated
  0 files actually modified (dry-run)
```

**Step 5: Developer approves and runs for real**
```bash
$ python doc_id/doc_id_assigner.py auto-assign --limit 1

Auto-assigning doc_ids...

File: core/scheduler.py
  Category: core
  Name: scheduler
  Minted: DOC-CORE-SCHEDULER-764
  Injected doc_id into file
  Updated registry

✅ 1 file updated
```

**Step 6: File now has doc_id**
```python
#!/usr/bin/env python3
# DOC_LINK: DOC-CORE-SCHEDULER-764
"""Task scheduler module."""

class TaskScheduler:
    def schedule(self, task):
        pass
```

**Step 7: Registry updated**
```yaml
categories:
  core:
    next_id: 765  # Incremented
    count: 262    # Incremented

docs:
  # ... existing docs ...
  - doc_id: DOC-CORE-SCHEDULER-764
    category: core
    name: scheduler
    title: scheduler
    status: active
    artifacts: []
    created: '2025-12-13'
    last_modified: '2025-12-13'
    tags: []
```

**Step 8: Developer commits changes**
```bash
$ git add core/scheduler.py doc_id/DOC_ID_REGISTRY.yaml
$ git commit -m "Add task scheduler module"

🔍 Validating doc_ids in staged files...
Checking 2 file(s)...
✅ All doc_ids valid

[feature/scheduler abc1234] Add task scheduler module
 2 files changed, 15 insertions(+)
```

**Step 9: CI/CD validates coverage**
```bash
# In CI pipeline
$ python doc_id/validate_doc_id_coverage.py --baseline 0.50

Current coverage: 49.9%
Baseline: 50.0%

❌ FAIL: Coverage below baseline
Exit code: 1

# Pipeline fails, notifies developer
```

**Step 10: Developer assigns more doc_ids**
```bash
$ python doc_id/doc_id_assigner.py auto-assign --limit 100

✅ 89 files updated

$ python doc_id/validate_doc_id_coverage.py --baseline 0.50

Current coverage: 52.7%
Baseline: 50.0%

✅ PASS: Coverage meets baseline
Exit code: 0
```

**Final State**:
- Repository has 3,246 files
- Coverage: 52.7%
- Registry has 1,709 doc_ids assigned (+89)
- CI pipeline passes

---

## 9. Error Handling & Logging

### 9.1 Error Categories

| Error Category | Handling Strategy | Recovery |
|----------------|-------------------|----------|
| **File Read/Write Errors** | Try-except with fallback | Skip file, log error, continue |
| **Invalid Doc ID Format** | Validation check, reject | Log invalid ID, offer fix |
| **Duplicate Doc IDs** | Detection + unique generation | Re-mint with unique suffix |
| **Registry Corruption** | Schema validation | Restore from backup |
| **Scanner Timeout** | Configurable timeout | Retry with increased timeout |
| **Category Not Found** | Validation before mint | Prompt for valid category |
| **Disk Space Exhausted** | Pre-flight space check | Abort with clear message |

### 9.2 Logging Locations

| Component | Log Location | Format |
|-----------|--------------|--------|
| **Scanner** | Console (stdout) | Structured text |
| **Assigner** | Console (stdout) | Structured text |
| **Automation Runner** | Console (stdout/stderr) | Structured text |
| **Pre-commit Hook** | Git output | Structured text |
| **File Watcher** | Console (stdout) | Timestamped events |
| **Daily Reports** | doc_id/DOC_ID_reports/*.json | JSON |
| **Alerts** | .state/doc_id_alerts.json | JSON |
| **Test Results** | pytest output | Pytest format |

### 9.3 Error Messages

**Format Validation Error**:
```
❌ {file_path}: Invalid doc_ids found:
   - {invalid_doc_id_1}
   - {invalid_doc_id_2}

Expected format: DOC-{CATEGORY}-{NAME}-{NUMBER}
Example: DOC-CORE-SCHEDULER-123
```

**Coverage Threshold Error**:
```
❌ FAIL: Coverage below baseline
Current coverage: 52.3% (1,698 / 3,245 files)
Baseline: 55.0%
Shortfall: 88 files needed

Action required: Assign doc_ids to more files
Command: python doc_id/doc_id_assigner.py auto-assign
```

**Duplicate Detection**:
```
⚠️  Duplicate doc_id detected
doc_id: DOC-PAT-ATOMIC-CREATE-TEMPLATE-001
Occurrences: 3 files
  - patterns/atomic/create_template.md
  - patterns/atomic/create_template_v2.md
  - patterns/atomic/create_template_backup.md

Action required: Fix duplicates
Command: python doc_id/fix_duplicate_doc_ids.py fix
```

### 9.4 Exception Handling Patterns

**File Processing**:
```python
try:
    content = file_path.read_text(encoding='utf-8')
    doc_id = extract_doc_id(content)
except UnicodeDecodeError:
    # Binary file or encoding issue
    print(f"⚠️  Warning: Could not read {file_path} (encoding issue)")
    return None
except PermissionError:
    print(f"⚠️  Warning: Permission denied: {file_path}")
    return None
except Exception as e:
    print(f"⚠️  Warning: Unexpected error reading {file_path}: {e}")
    return None
```

**Registry Operations**:
```python
try:
    registry = yaml.safe_load(registry_path.read_text())
except yaml.YAMLError as e:
    print(f"❌ Error: Registry is corrupted: {e}")
    print("Restore from backup or recreate registry")
    sys.exit(1)
except FileNotFoundError:
    print(f"❌ Error: Registry not found: {registry_path}")
    print("Run: python doc_id/tools/doc_id_registry_cli.py init")
    sys.exit(1)
```

**Subprocess Execution**:
```python
try:
    result = subprocess.run(
        [sys.executable, scanner_script, 'scan'],
        capture_output=True,
        text=True,
        check=True,
        timeout=300  # 5 minutes
    )
except subprocess.TimeoutExpired:
    print("❌ Error: Scanner timed out after 5 minutes")
    sys.exit(1)
except subprocess.CalledProcessError as e:
    print(f"❌ Error: Scanner failed with exit code {e.returncode}")
    print(f"Output: {e.stderr}")
    sys.exit(1)
```

### 9.5 Backup & Recovery

**File Modification Backup**:
```python
def backup_file(file_path: Path) -> Path:
    """Create backup before modifying file."""
    backup_path = file_path.with_suffix(file_path.suffix + '.backup')
    shutil.copy2(file_path, backup_path)
    return backup_path

# Usage in fix tools:
python doc_id/fix_invalid_doc_ids.py fix --backup
# Creates {file}.backup before modifying
```

**Registry Backup** (automated):
- Daily backup via scheduled task
- Location: `doc_id/DOC_ID_REGISTRY.yaml.backup.YYYYMMDD`
- Retention: 7 days

**Recovery Commands**:
```bash
# Restore registry from backup
$ cp doc_id/DOC_ID_REGISTRY.yaml.backup.20251213 doc_id/DOC_ID_REGISTRY.yaml

# Regenerate inventory from scratch
$ rm docs_inventory.jsonl
$ python doc_id/doc_id_scanner.py scan

# Restore file from backup
$ mv core/scheduler.py.backup core/scheduler.py
```

---

## 10. Integration Points

### 10.1 Git Integration

**Pre-commit Hook**:
- **Trigger**: `git commit`
- **Action**: Validate doc_ids in staged files
- **Integration**: `.git/hooks/pre-commit`
- **Exit Code**: 0 (pass) or 1 (fail)
- **Bypass**: `git commit --no-verify` (not recommended)

**Installation**:
```bash
python doc_id/install_pre_commit_hook.py
# Copies pre_commit_hook.py to .git/hooks/pre-commit
# Makes executable
```

### 10.2 CI/CD Integration

**GitHub Actions / GitLab CI / Jenkins**:

**Pipeline Stage: Validation**
```yaml
# Example: .github/workflows/doc-id-validation.yml
name: Doc ID Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install pyyaml
      
      - name: Validate doc_id coverage
        run: python doc_id/validate_doc_id_coverage.py --baseline 0.55
      
      - name: Generate coverage report
        if: always()
        run: python doc_id/doc_id_scanner.py report --format markdown > coverage_report.md
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report
          path: coverage_report.md
```

**Exit Codes**:
- 0: Validation passed
- 1: Validation failed (coverage below baseline)

### 10.3 Scheduled Task Integration

**Windows Task Scheduler**:
```bash
python doc_id/setup_scheduled_tasks.py
# Creates task: "DOC_ID_Daily_Report"
# Schedule: Daily at 2:00 AM
# Command: python doc_id/scheduled_report_generator.py daily
```

**Linux Cron**:
```bash
python doc_id/setup_scheduled_tasks.py
# Adds cron entry:
# 0 2 * * * cd /path/to/repo && python doc_id/scheduled_report_generator.py daily
```

**Manual Task Configuration**:
```bash
# Windows
schtasks /create /tn "DOC_ID_Daily_Report" /tr "python C:\repo\doc_id\scheduled_report_generator.py daily" /sc daily /st 02:00

# Linux
echo "0 2 * * * cd /path/to/repo && python doc_id/scheduled_report_generator.py daily" | crontab -
```

### 10.4 Monitoring Integration

**Alert Integration**:
- **Output**: `.state/doc_id_alerts.json`
- **Format**: JSON array of alerts
- **Integration**: Can be consumed by monitoring tools (e.g., Prometheus, Grafana, PagerDuty)

**Webhook Integration** (future):
```python
# In alert_monitor.py (future enhancement)
if alert.severity == "critical":
    requests.post(
        "https://monitoring.example.com/webhook",
        json=alert_data
    )
```

**Metrics Export** (future):
```python
# Export metrics in Prometheus format
# doc_id_coverage_percent{repo="ai-pipeline"} 54.9
# doc_id_invalid_count{repo="ai-pipeline"} 43
# doc_id_total_files{repo="ai-pipeline"} 3245
```

### 10.5 External Tools Integration

**Documentation Generators**:
- Doc IDs can be referenced in generated documentation
- Example: Sphinx, MkDocs can use doc_ids as anchors/cross-references

**IDEs & Editors**:
- VSCode extension (future): Auto-complete doc_ids, jump to definition
- Integration via Language Server Protocol (LSP)

**Project Management Tools**:
- Doc IDs can be linked to JIRA/GitHub issues
- Example: "Related doc: DOC-CORE-SCHEDULER-764"

**Search & Discovery**:
- Doc IDs enable powerful search capabilities
- Example: `grep -r "DOC-CORE-SCHEDULER-764" .`
- Can build doc_id index for full-text search (future)

---

## Appendix A: Configuration Files

### A.1 Alert Thresholds Configuration

File: `doc_id/alert_thresholds.yaml`

```yaml
thresholds:
  - name: coverage_critical
    metric: coverage
    operator: "<"
    value: 90.0
    severity: critical
  
  - name: coverage_warning
    metric: coverage
    operator: "<"
    value: 95.0
    severity: warning
  
  - name: invalid_ids_critical
    metric: invalid_count
    operator: ">"
    value: 10
    severity: critical
  
  - name: drift_warning
    metric: drift_count
    operator: ">"
    value: 50
    severity: warning
  
  - name: duplicates_critical
    metric: duplicate_count
    operator: ">"
    value: 5
    severity: critical
```

### A.2 File Patterns Configuration

Eligible file patterns (in doc_id_scanner.py):
```python
ELIGIBLE_PATTERNS = [
    "**/*.py",
    "**/*.md",
    "**/*.yaml",
    "**/*.yml",
    "**/*.json",
    "**/*.ps1",
    "**/*.sh",
    "**/*.txt",
]
```

Exclude patterns:
```python
EXCLUDE_PATTERNS = [
    ".venv",
    "__pycache__",
    ".git",
    "node_modules",
    ".pytest_cache",
    ".worktrees",
    "legacy",
    ".state",
    "refactor_paths.db",
    "*.db-shm",
    "*.db-wal",
]
```

---

## Appendix B: Troubleshooting Guide

### B.1 Common Issues

**Issue**: Coverage validation fails in CI
**Cause**: Baseline threshold too high
**Solution**:
```bash
# Check current coverage
python doc_id/doc_id_scanner.py stats

# Adjust baseline in CI config or assign more doc_ids
python doc_id/doc_id_assigner.py auto-assign --limit 100
```

**Issue**: Scanner timeout in large repository
**Cause**: Too many files to scan
**Solution**:
```python
# Increase timeout in subprocess calls
timeout=600  # 10 minutes

# Or exclude more directories
EXCLUDE_PATTERNS.append("large_dataset/")
```

**Issue**: Invalid doc_ids detected
**Cause**: Manual doc_id edits
**Solution**:
```bash
# Scan for invalid doc_ids
python doc_id/fix_invalid_doc_ids.py scan

# Fix with backup
python doc_id/fix_invalid_doc_ids.py fix --backup
```

**Issue**: Duplicate doc_ids
**Cause**: Parallel execution or manual copy-paste
**Solution**:
```bash
# Analyze duplicates
python doc_id/fix_duplicate_doc_ids.py analyze

# Fix automatically
python doc_id/fix_duplicate_doc_ids.py fix
```

**Issue**: Registry-inventory sync drift
**Cause**: Registry updated manually
**Solution**:
```bash
# Check sync status
python doc_id/sync_registries.py check

# Synchronize
python doc_id/sync_registries.py sync
```

---

## Appendix C: Best Practices

### C.1 Development Workflow

1. **Always run scanner before assignment**:
   ```bash
   python doc_id/doc_id_scanner.py scan
   python doc_id/doc_id_assigner.py auto-assign --dry-run
   ```

2. **Use dry-run mode for validation**:
   - Test changes before applying
   - Review minted doc_ids

3. **Commit registry with file changes**:
   - Always commit both file and registry updates together
   - Prevents sync drift

4. **Monitor coverage trends**:
   - Review daily/weekly reports
   - Set baseline thresholds appropriately

### C.2 Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Scan repository | Daily | `python doc_id/doc_id_scanner.py scan` |
| Validate coverage | Daily | `python doc_id/validate_doc_id_coverage.py` |
| Fix invalid IDs | Weekly | `python doc_id/fix_invalid_doc_ids.py fix` |
| Fix duplicates | Weekly | `python doc_id/fix_duplicate_doc_ids.py fix` |
| Sync registries | Daily | `python doc_id/sync_registries.py sync` |
| Generate reports | Daily | `python doc_id/scheduled_report_generator.py daily` |
| Review alerts | Daily | Check `.state/doc_id_alerts.json` |

### C.3 Security Considerations

1. **File permissions**: Ensure proper read/write permissions
2. **Backup sensitive files**: Always use `--backup` flag for fix tools
3. **Validate inputs**: All user inputs are validated before processing
4. **No arbitrary code execution**: All subprocess calls use explicit paths
5. **Error handling**: Graceful degradation on permission errors

---

## Appendix D: Future Enhancements

1. **Language Server Protocol (LSP)**: IDE integration for doc_id auto-completion
2. **Web Dashboard**: Real-time coverage visualization
3. **Webhooks**: Integration with Slack/Teams for alerts
4. **Metrics Export**: Prometheus/Grafana integration
5. **AI-Powered Categorization**: Automatic category inference using ML
6. **Cross-Repository Linking**: Support for doc_ids across multiple repos
7. **Version History**: Track doc_id changes over time
8. **API Gateway**: RESTful API for doc_id operations

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-13 | Technical Documentation Engineer | Initial comprehensive documentation |

---

**Document Status**: Active  
**Maintenance**: This document should be reviewed quarterly and updated when system changes occur.  
**Contact**: For questions or issues, refer to repository maintainers.
