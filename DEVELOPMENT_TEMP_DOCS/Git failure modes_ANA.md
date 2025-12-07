## Overview

This document describes a set of **Git failure modes** that occurred when a **multi-agent AI system** operated on a **single local Git working tree** in parallel.

The goal is to give an AI-powered CLI tool enough context to:

* Understand the **intended multi-agent Git workflow**.
* Recognize **what went wrong** in this specific run.
* Detect these patterns in future runs from **Git commands, logs, and repo metadata only** (no access to original source files or internal prompt text).
* Use this description as input to plan **preventive and corrective actions**.

---

## System & Git Workflow Description

### 1. Multi-Agent Architecture

* There are **multiple AI agents** (in the described run: 3 agents).

* Each agent:

  * Runs as an **independent CLI session** in the **same repository working directory**.
  * Receives a **workstream** (logical task area):

    * Agent 1 – Quality gates / CI checks.
    * Agent 2 – Documentation & doc_id drift detection.
    * Agent 3 – Maintenance & state file cleanup automation.
  * Is instructed to:

    * Start from a **base branch** (e.g., `main` or an integration branch).
    * Create a **dedicated agent branch**.
    * Make changes only within its **workstream scope**.
    * Run tests/validation.
    * Commit and push.
    * Output a structured completion summary.

* **Important constraint**:
  All agents operate in **one physical clone** of the repo, at the same filesystem path, at roughly the same time.

### 2. Intended Git Workflow

For each agent **N**:

1. Ensure working tree is clean:

   ```bash
   git status
   # expect: On branch <BASE_BRANCH>, working tree clean
   ```

2. Check out the base branch (e.g., `main`):

   ```bash
   git checkout main
   git pull --ff-only
   ```

3. Create and switch to an **agent-specific branch**:

   ```bash
   git checkout -b phase6-testing-agentN-<task-name>
   ```

4. Make changes (edit files, add scripts, update workflows, etc.).

5. Run tests:

   ```bash
   pytest path/to/tests -v
   # or equivalent test commands
   ```

6. Stage only the relevant workstream files:

   ```bash
   git add path/to/agentN/files...
   ```

7. Commit:

   ```bash
   git commit -m "Agent N: <descriptive message>"
   ```

8. Push the agent branch:

   ```bash
   git push -u origin phase6-testing-agentN-<task-name>
   ```

9. Print a structured summary indicating:

   * `agent_number`
   * `agent_branch`
   * `base_branch`
   * `tests_run`
   * `files_changed`
   * `risks` / `follow_ups`

**Integration (merging branches)** is **explicitly out of scope** for the individual agents and handled by a separate integration phase or human.

### 3. Actual Branches & Typical Commands Observed

In the specific problematic run:

* Branches involved:

  * `main` (or an equivalent base branch)
  * `phase6-testing-agent1-quality-gates`
  * `phase6-testing-agent2-doc-integrity`
  * `phase6-testing-agent3-maintenance`
  * An integration branch (e.g., `phase6-testing-complete-all-agents`)

* Commands frequently used by agents:

  * `git status`
  * `git branch`
  * `git checkout <branch>`
  * `git checkout -b <branch>`
  * `git add <paths>`
  * `git commit` (sometimes with `--no-verify`)
  * `git push`
  * **Pre-commit hooks** automatically triggered by `git commit`
  * Manual manipulation of `.git/index.lock` (e.g., `rm .git/index.lock`)

---

## Problems

### Problem P1 – Shared Working Tree HEAD Race

**Problem Label:** `P1_SHARED_HEAD_RACE`
**Problem Statement (short):**
Multiple agents operated on the same working tree concurrently, switching branches (`git checkout`) while others were still working. This caused agents to unexpectedly run, test, and commit on the **wrong branch**.

#### Context & Intended Behavior

Each agent should:

* Create and stay on its **own agent branch** during its run.
* Assume that `git status` and the current branch remain stable during its operations.

Example ideal sequence for Agent 2:

```bash
git checkout main
git checkout -b phase6-testing-agent2-doc-integrity
# work, test, commit, push, all on phase6-testing-agent2-doc-integrity
```

#### Observed Behavior

* Agent 2 at one point runs `git status` and sees:

  ```text
  On branch phase6-testing-agent3-maintenance
  ```

  even though it is Agent 2 and should be on `phase6-testing-agent2-doc-integrity`.

* Agent 3, later in the run, discovers it is on `phase6-testing-agent2-doc-integrity` during staging/committing its own maintenance changes.

* Both agents then:

  * Notice the unexpected branch.
  * Run `git branch` to inspect branch list.
  * Manually `git checkout` back to their intended agent branch.
  * Attempt to re-stage the correct files and commit on the right branch.

#### What Went Wrong

* The **Git HEAD pointer** (the current branch) is **global** to the working tree.

* While Agent 2 was still working (editing files, running tests), Agent 3 (or another process) executed:

  ```bash
  git checkout phase6-testing-agent3-maintenance
  # or vice versa
  ```

* This silently changed the current branch for **all** processes using that working tree.

* As a result:

  * Commands run by Agent 2 (e.g., `pytest`, `git status`, even `git add`) applied to the **Agent 3 branch**, not Agent 2’s branch.
  * Similarly, Agent 3 briefly operated on Agent 2’s branch.

#### Repository State: Before vs After

* **Before:**

  * Each agent believed it was on its own branch.
  * Local branch tips were separate and clean.

* **After:**

  * Changes and tests may have been executed on **different branches than intended**.
  * There is ambiguity about which branch really contains which "version" of a given file or test.

#### Signals for Future Detection

Potential signals an AI planner or tool can use:

* `git status` output showing an **unexpected branch** for a given agent context:

  * Example: Agent 2 process sees `On branch phase6-testing-agent3-maintenance`.

* Rapid alternation of `git checkout` commands between multiple agent branches in logs for the **same working directory**.

* Multiple long-running processes simultaneously performing non-read-only commands (`git add`, `git commit`, `git checkout`) in the same `.git` directory.

* Sequence pattern:

  * `git checkout branchA`
  * (no commit)
  * `git checkout branchB`
  * Followed by re-creation of the same files on branchB that were already created on branchA.

---

### Problem P2 – Cross-Agent Staging & Commit Contamination

**Problem Label:** `P2_CROSS_AGENT_STAGING`
**Problem Statement (short):**
Because of shared HEAD and staged changes, agents occasionally **staged and committed files that logically belonged to other agents’ workstreams** or to the wrong branch.

#### Context & Intended Behavior

Each agent should only commit:

* Files it created or modified within its workstream.
* On its own agent branch (e.g. `phase6-testing-agent3-maintenance`).

Example:

```bash
git add scripts/cleanup_state_files.py tests/test_state_cleanup.py
git commit -m "Agent 3: Add state cleanup"
```

#### Observed Behavior

* Agent 3:

  * Initially stages a set of files for its own maintenance feature.

  * Then discovers via `git status` that it is actually on **Agent 2’s branch** (`phase6-testing-agent2-doc-integrity`).

  * Performs:

    ```bash
    git reset HEAD
    git checkout phase6-testing-agent3-maintenance
    ```

  * Then attempts to re-add **only** the intended Workstream 3 files.

* Pre-commit hooks caused **auto-formatting changes** to multiple files. This makes it easy for an agent to stage or commit files that it did not explicitly edit.

#### What Went Wrong

* Staged changes are **also global** to the working tree (the index).

* When branches were switched mid-work:

  * Previously staged changes might have been left in the index.
  * New or formatted files from other agents were now visible and easily re-staged by mistake.

* Without strict scoping rules or checks, an agent’s `git add` picked up changes:

  * That were created or auto-formatted while another agent was on a different branch.
  * That belonged to a different workstream.

#### Repository State: Before vs After

* **Before:**

  * Each agent’s intended file set was conceptually isolated by workstream.
  * The index may have contained a mixture of staged changes from multiple agents.

* **After:**

  * Commits on branch A may include files conceptually owned by branch B or agent B.
  * This complicates future merges and debugging because the mapping "Agent N → files" is blurred.

#### Signals for Future Detection

* A commit on `phase6-testing-agentN-*` that includes changes in **many unrelated directories**, especially ones obviously tied to other workstreams or agent naming patterns.

* `git status` showing staged changes **before** a branch switch that are still staged **after** switching branches.

* Presence of pre-commit hook messages (e.g., "Reformatted X files") followed by a commit that includes those additional files even though the agent’s instructions mention a narrower scope.

* Log patterns:

  * `git add .` or `git add -A` in an environment with multiple agents and active hooks.
  * Frequent use of `git reset HEAD` followed by re-adding subsets of files, indicating contamination corrections.

---

### Problem P3 – Work Lost Due to Branch Switching Without Commit

**Problem Label:** `P3_WORK_LOST_ON_SWITCH`
**Problem Statement (short):**
An agent created new files on one branch, switched branches without committing, and later discovered that those files had “disappeared”. The agent had to **recreate the same files** on the intended branch.

#### Context & Intended Behavior

Expected safe workflow:

1. Create files on your agent branch:

   ```bash
   git checkout phase6-testing-agent3-maintenance
   # create scripts/cleanup_state_files.py ...
   ```

2. Stage and commit:

   ```bash
   git add scripts/cleanup_state_files.py ...
   git commit -m "Agent 3: Add state cleanup"
   ```

3. Only then, consider switching branches.

#### Observed Behavior

* Agent 3:

  * Created new files (e.g., `cleanup_state_files.py`, a new workflow file, tests) while on some branch.
  * Switched branches (due to shared HEAD issues) without committing or stashing.
  * Later, on the target branch, checked and found that the files **did not exist**.
  * Concluded that "earlier file creation was lost during branch switching".
  * Recreated all of the missing files and reran tests.
  * Committed with `--no-verify` to bypass hooks and avoid further side effects.

#### What Went Wrong

* When you **create new files on branch A** and then `git checkout branch B` **without committing or stashing**, those files may appear as **untracked** in branch B or may be removed depending on operations.

* Combined with:

  * Pre-commit hooks and resets.
  * Cross-branch contamination and manual `git reset HEAD`.

  It became easy to end up with a working tree where the files were simply not present.

* The agent lacked systematic checks to ensure:

  * That new files existed and were tracked on the intended branch.
  * That there were no uncommitted changes before switching.

#### Repository State: Before vs After

* **Before (creation):**

  * Working tree had new, uncommitted files on whichever branch was active at the time.

* **After (switch):**

  * The new files were either:

    * Untracked on another branch, then reset/stashed away, or
    * Fully missing from the working tree.
  * Later re-created and committed on the target branch.

#### Signals for Future Detection

* Log patterns:

  * `git checkout` executed with a **dirty working tree** (untracked files, modified files) but without `-m`, `--merge`, or `--detach`.
  * `git status` showing untracked or modified files, followed immediately by a branch switch.

* Files that:

  * Are created (detected by `git status` as untracked).
  * Never appear in any commit on that branch.
  * Then appear as newly added files in a much later commit after an intervening branch switch.

* Agent logs mentioning “re-created files” or similar language.

---

### Problem P4 – Pre-Commit Hook Side Effects Under Concurrency

**Problem Label:** `P4_PRECOMMIT_SIDE_EFFECTS`
**Problem Statement (short):**
Pre-commit hooks automatically modified files (formatting, etc.) and sometimes blocked commits, causing **extra changes**, repeated commits, and interaction with other agents’ work in the same clone.

#### Context & Intended Behavior

* The repository uses **pre-commit hooks** triggered by `git commit`.
* Typical hook behavior:

  * Format code.
  * Possibly run quick checks or tests.
  * Fail the commit if checks do not pass.

Agents expect:

```bash
git commit -m "Agent X: message"
# hooks run, commit either succeeds or fails
```

#### Observed Behavior

* Agents experienced:

  * `git commit` failing due to hook output.
  * Hooks that re-formatted multiple files, causing additional diffs the agents did not explicitly intend.
  * The need to re-run `git add` after hooks changed files.
  * Final commits executed with `--no-verify` to bypass hooks after repeated failures.

* In a multi-agent shared-working-tree scenario, these hook-triggered modifications impact the **same filesystem state** that other agents see.

#### What Went Wrong

* Pre-commit hooks:

  * Are executed in the context of the current working tree and index.
  * May modify files throughout the repo, not just in the agent’s workstream.

* Under concurrency:

  * Hooks from one agent can reformat files that another agent will later stage.
  * Hook failures can leave the index and working tree in intermediate states.

* Without explicit serialization or scoping, hooks **amplify** the shared state problems already present (P1, P2, P3).

#### Repository State: Before vs After

* **Before:**

  * Agents have a small, intended set of changes.

* **After (hooks):**

  * Additional files are modified or staged due to auto-formatting.
  * More files than expected appear in commits.
  * Agents sometimes bypass hooks entirely using `--no-verify`, reducing assurance that standards are enforced.

#### Signals for Future Detection

* `git commit` output containing typical pre-commit messages (e.g., “reformatted X files”, “hook failed”).

* Repeated sequence:

  ```bash
  git commit -m "..."
  # hook failure
  git add ...
  git commit -m "..."
  # hook failure
  git commit --no-verify -m "..."
  ```

* Commits immediately following a hook failure that:

  * Include many formatting-only changes.
  * Touch files outside the expected workstream scope.

---

### Problem P5 – Index Lock Contention (`.git/index.lock`)

**Problem Label:** `P5_INDEX_LOCK_CONTENTION`
**Problem Statement (short):**
Concurrent Git operations by multiple agents led to `.git/index.lock` conflicts. One agent manually removed the lock file, risking index corruption and inconsistent commit state.

#### Context & Intended Behavior

* Git uses `.git/index.lock` to protect the index from concurrent modifications.
* Normally, Git cleans this up automatically after the operation finishes.

Expected workflow:

```bash
git add ...
git commit -m "..."
# no manual lock file manipulation
```

#### Observed Behavior

* One agent encountered:

  ```text
  fatal: Unable to create '.git/index.lock': File exists.
  ```

* The agent then manually deleted the lock file:

  ```bash
  rm .git/index.lock
  git commit --no-verify -m "..."
  ```

#### What Went Wrong

* Multiple processes were attempting to update the index at the same time (e.g., simultaneous `git add`, `git commit`, or hook operations).
* Manual deletion of `.git/index.lock` bypasses Git’s protection and can lead to:

  * Partial or corrupted index state.
  * Incomplete staging data for the commit.
  * Lost changes if another Git process was still writing.

#### Repository State: Before vs After

* **Before:**

  * Two or more Git processes active.
  * `.git/index.lock` created by one process as a safeguard.

* **After:**

  * Lock file removed manually, possibly while another operation was still in progress.
  * Index integrity cannot be guaranteed.
  * Commit made on top of potentially inconsistent index.

#### Signals for Future Detection

* Presence of error message:

  ```text
  fatal: Unable to create '.git/index.lock': File exists.
  ```

* Any shell commands removing the lock file:

  ```bash
  rm .git/index.lock
  ```

* Multiple Git processes concurrently operating on the same repository (can sometimes be inferred from process lists or timing).

---

### Problem P6 – Inconsistent Base Branches for Agent Branches

**Problem Label:** `P6_INCONSISTENT_BASE_BRANCHES`
**Problem Statement (short):**
Some agent branches were created from `main`, while others were created from an **integration branch** containing partial work from other agents. This inconsistency complicates future merges and makes the branch topology harder to reason about.

#### Context & Intended Behavior

* Ideally, all agent branches for a given "phase" should:

  * Have the **same base branch** (e.g., `phase6-testing-base` or `main`).
  * Represent parallel lines of work that can be merged into an integration branch later.

Example:

```bash
git checkout main
git checkout -b phase6-testing-agent1-quality-gates
git checkout main
git checkout -b phase6-testing-agent2-doc-integrity
...
```

#### Observed Behavior

* At least one agent (Agent 2) created its agent branch from an **integration branch** that might already contain another agent’s work:

  ```bash
  git checkout phase6-testing-complete-all-agents   # or similar
  git checkout -b phase6-testing-agent2-doc-integrity
  ```

* Other agents created branches from `main` or a different base.

#### What Went Wrong

* Branch ancestry is no longer consistent:

  * Some agent branches contain previous agent work (via the integration base).
  * Some do not.

* This:

  * Blurs the separation of concerns between "per-agent branches" and "integration branches".
  * Complicates detection of what work belongs to whom.
  * Makes future `git merge` and conflict resolution more difficult.

#### Repository State: Before vs After

* **Before:**

  * A clear conceptual plan: all agents should branch from the same base.

* **After:**

  * A more complex DAG:

    * Some agent branches are siblings from `main`.
    * Others are descendants of an integration branch already containing other agents’ commits.

#### Signals for Future Detection

* When analyzing branch topology:

  * `git merge-base <agentBranch1> <agentBranch2>` returning different base commits than expected.
  * Agent branches that list **other agent branches or integration branches** as their direct ancestors in `git log --graph --oneline --decorate`.

* Creation of agent branches from non-base branches in logs:

  ```bash
  git checkout <integration-branch>
  git checkout -b phase6-testing-agent2-doc-integrity
  ```

---

## Root Cause Analysis (Cross-Cutting)

This section maps the problems (P1–P6) to underlying technical and systemic causes.

### 1. Technical Root Causes

1. **Single Shared Working Tree for Multiple Agents**

   * A single `.git` directory and working tree were used by all agents concurrently.
   * **Impacts:** P1, P2, P3, P4, P5.
   * Git assumes a single human operator per clone; it does **not** provide multi-writer concurrency guarantees for HEAD, index, and working tree.

2. **Lack of Serialized Git Operations**

   * Agents freely ran `git checkout`, `git add`, `git commit`, etc., in parallel.
   * **Impacts:** P1, P2, P3, P5.
   * No lock or coordination mechanism ensured that only one process modified HEAD/index at a time.

3. **Pre-Commit Hooks That Touch Many Files**

   * Hooks reformat and edit files across the repo.
   * **Impacts:** P2, P4.
   * Under concurrency, these changes can be staged and committed by another agent, causing cross-workstream contamination.

4. **Branch Switching with Dirty Working Trees**

   * Agents switched branches without:

     * Ensuring a clean working tree.
     * Committing or stashing new files.
   * **Impacts:** P1, P3.
   * Leads to untracked or lost work and ambiguous ownership of new files.

5. **Manual Manipulation of `.git/index.lock`**

   * Human/agent removed `.git/index.lock` to bypass Git’s protection.
   * **Impacts:** P5.
   * Can corrupt index and cause inconsistent commit contents.

6. **Inconsistent Base Branch Selection**

   * Some agent branches branched from `main`; others from an integration branch.
   * **Impacts:** P6.
   * Creates a non-uniform branch topology that complicates merging and analysis.

### 2. Systemic / Design-Level Issues

1. **Missing Concurrency Model for Git**

   * The pipeline design did not define whether agents:

     * Should share a clone (they did).
     * Should have **separate clones per agent** (they did not).
   * No explicit strategy for **locking, serialization, or queueing** Git operations.

2. **No Enforcement of Agent-Branch Contracts**

   * At runtime, nothing enforced:

     * "Agent 2 must always be on `phase6-testing-agent2-*`".
     * "Agent 3 must never operate on `phase6-testing-agent2-*`".
   * No guardrails like:

     * Pre-command assertions (`git rev-parse --abbrev-ref HEAD`) matching the expected branch.
     * Validation that the commit’s changed paths fall within the agent’s allowed scope.

3. **Weak Precondition Checks Before Dangerous Operations**

   * No enforcement of:

     * Clean working tree before `git checkout`.
     * Clean index before `git commit` or `git push`.
   * Allows branch switching with uncommitted work (P3) and complicated hook interactions (P4).

4. **Insufficient Separation Between Agent Work and Integration Work**

   * Some agents used integration branches as bases.
   * Agents were allowed to see and potentially alter integration branch content directly.
   * This blurs lines between "per-agent" and "integration" responsibilities.

---

## Constraints & Assumptions

These are assumptions that the AI-powered CLI tool should adopt when using this document for planning:

1. **Single Repository Clone (Current State)**

   * The described system uses **one physical clone** shared by all agents.
   * The planner may choose to change this (e.g., multiple clones), but this is the **starting point**.

2. **Agents Are Not Git Experts**

   * Agents follow patterns given in prompts but may:

     * Run `git` commands mechanically.
     * Not fully understand edge cases (e.g., branch switching with untracked files).

3. **Pre-Commit Hooks Are Present and Non-Trivial**

   * Hooks:

     * Modify files (formatting).
     * Can fail commits.
   * Planner must assume hooks exist unless explicitly disabled.

4. **Branch Naming Convention Exists**

   * Agent branches follow a pattern similar to:

     * `phase6-testing-agent<N>-<short-task-name>`
   * Integration branches may follow:

     * `phase6-testing-complete-all-agents` or similar.

5. **Repository History Is Potentially Messy Due to Past Runs**

   * There may be commits:

     * On wrong branches.
     * With mixed content from multiple workstreams.
   * Planner cannot assume a perfectly clean history.

---

## Known Failure Patterns (Summary for Detection)

This section provides a compact reference the CLI tool can use to match future failures.

### Pattern FP1 – Shared HEAD Race

* **Related Problem:** `P1_SHARED_HEAD_RACE`
* **Signal Set:**

  * Multiple long-lived processes sharing a `.git` directory.
  * `git status` outputs showing agents on unexpected branches.
  * Rapid `git checkout` across multiple branches without intervening commits.

### Pattern FP2 – Cross-Agent Contaminated Commits

* **Related Problem:** `P2_CROSS_AGENT_STAGING`
* **Signal Set:**

  * Commits on an `agentN` branch touching files that are clearly associated with other agents or unrelated areas.
  * Commits made soon after pre-commit hooks report reformatting many files.
  * Use of `git add .` / `git add -A` in a multi-agent context.

### Pattern FP3 – Work Lost on Branch Switch

* **Related Problem:** `P3_WORK_LOST_ON_SWITCH`
* **Signal Set:**

  * `git checkout <branch>` executed while `git status` shows untracked or modified files.
  * New files that appear in temporary diffs but do not show up in any commit on that branch, then reappear later as newly created.

### Pattern FP4 – Pre-Commit Turbulence

* **Related Problem:** `P4_PRECOMMIT_SIDE_EFFECTS`
* **Signal Set:**

  * Repeated failing `git commit` attempts due to hooks.
  * Commits made with `--no-verify` following several hook failures.
  * Hooks that change many files, followed by commits containing a wide set of formatting-only changes.

### Pattern FP5 – Index Lock Conflict

* **Related Problem:** `P5_INDEX_LOCK_CONTENTION`
* **Signal Set:**

  * Error: `fatal: Unable to create '.git/index.lock': File exists.`
  * Manual removal commands for `.git/index.lock`.
  * Concurrent Git processes visible for the same repo path.

### Pattern FP6 – Inconsistent Agent Branch Bases

* **Related Problem:** `P6_INCONSISTENT_BASE_BRANCHES`
* **Signal Set:**

  * `git checkout <integration-branch>` immediately followed by `git checkout -b phase6-testing-agentN-*`.
  * `git merge-base` between two agent branches does **not** point to the designated base branch commit.
  * Agent branches whose ancestor chain includes another agent’s branch tip instead of the common base.

---

This document should give the AI-powered CLI enough **context, labels, and detection signals** to:

* Recognize when similar Git/multi-agent pathologies are occurring.
* Plan corrective actions (e.g., per-agent clones, serialized operations, stricter preconditions, branch/commit validators) to prevent a repeat of this multi-agent failure scenario.
