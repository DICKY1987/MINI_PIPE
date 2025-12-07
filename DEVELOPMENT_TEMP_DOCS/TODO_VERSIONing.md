This model scales to “solo developer on Windows” and also to “multiple AI+human agents contributing to the same repo with audits and rollback.”

0. First principle

Docs are code. Plans are code.
That means:

They live in the repo.

They’re edited with commits/PRs.

They are versioned, reviewed, and tagged just like software.

If you don’t do that, nothing else below matters.

1. Every document carries its own version header

At the top of every doc (Markdown, YAML, whatever), you include a small machine-readable metadata block.

Example for a process doc (OPERATING_CONTRACT.md or PIPELINE_POLICY.md):

---
doc_id: OC-CORE-2025-10-28
semver: 1.3.0
status: active
owner: Platform.Engineering
effective_date: 2025-10-28
supersedes: OC-CORE-2025-09-12
---


Why this matters:

semver tells you if this was a tiny tweak or a breaking change.

supersedes builds an ancestry chain (“what version replaced what”), which an agent can traverse without guessing.

owner makes responsibility explicit. “Owner” isn’t a person, it’s a role/team/module so it survives turnover.

effective_date lets you answer “what rules were in force on date X?” which is huge for audit and rollback.

This header is the doc’s internal version, not the repo version.

2. Use SemVer for humans and AIs

Treat policy/process/plan changes like API changes.

Semantic Versioning:

MAJOR.MINOR.PATCH

You apply it like this:

MAJOR (2.x.x → 3.0.0):
Breaking change. The meaning or requirement changed in a way that invalidates previous behavior.
Example: “All code edits MUST now go through Pipeline Runner. Direct pushes to main are banned.”

MINOR (2.4.x → 2.5.0):
New capability, new rule, new workflow step, new phase in roadmap — but old flows still valid.
Example: “We added an Observability Gate, but if you don’t use it yet, nothing else breaks.”

PATCH (2.4.1 → 2.4.2):
Clarification, typo fix, better wording, tighter examples. No behavioral change.

Why SemVer:

Agents can enforce: “I refuse to run if MAJOR changed and you didn’t acknowledge.”

Humans can scan git diff + version bump and instantly know the blast radius.

Auditors can say: “Show me all MINOR changes after 2.1.0 to see scope creep.”

3. Track history in git, not in the body

Do not keep a giant “changelog” paragraph in the doc itself that grows forever.

Instead:

Keep a short ## Change Log section at the bottom with only the last few entries (like last 3 bumps).

Keep the full history in docs/changelog/<doc_id>.md or auto-generate it from git.

Why:

The live doc stays clean and readable.

You never lose the forensic trail because git already is your forensic trail.

An agent can answer “what changed between 1.2.0 and 1.4.0?” by diffing tags.

Pattern for the inline mini-log:

## Change Log (recent)

- 1.3.0 — 2025-10-28 — Added Observability Gate to deployment pipeline.
- 1.2.2 — 2025-10-27 — Clarified retention policy language.
- 1.2.1 — 2025-10-27 — Fixed typo in IaC verifier step.

4. Cut immutable snapshots using git tags

This is the part most teams skip, and it’s the difference between “guidelines” and “policy.”

When you hit an important milestone (release, audit checkpoint, kickoff of Phase N), you do BOTH:

Commit the current state of docs/plans.

Create a git tag like:
docs-OC-CORE-1.3.0 or plan-R_PIPELINE-ALPHA-2025-10-28

That tag = frozen truth at that moment.

What this gives you:

You can answer: “What exact process did we say we’d follow on 2025-10-28?”

You can reproduce a run environment for an AI agent using only the rules that existed then.

You get legal/forensic defensibility: “We followed version 1.3.0 of the safety policy at the time of execution.”

In your world (deterministic AI pipeline, multiple agents editing code), this is huge.
You can literally say:
“All work for RUN_ID=2025-10-28T14-22-07 was executed under Operating Contract OC-CORE v1.3.0 (tag: docs-OC-CORE-1.3.0).”
Now you’re audit-ready.

5. Plans are versioned as timelines, not as fantasies

Plans/roadmaps are trickier because people treat them like “drafts” until they don’t. We fix that by splitting them into two artifacts:

5.1 Plan Intent (mutable)

File: plans/R_PIPELINE/2025-10-28_plan_intent.md

high-level goals

why we’re doing it

desired sequencing

risk notes

open questions

This file can evolve daily. It’s allowed to be wrong.
It uses SemVer too, but minor bumps are normal.

5.2 Execution Contract (frozen per phase or per run)

File: plans/R_PIPELINE/PHASE_01_EXECUTION_CONTRACT.md

This one is different. This is:
“Here is what we have actually committed to build in Phase 01. These are the deliverables, gates, and acceptance tests. No scope creep unless we bump MAJOR.”

You only update this doc when you officially re-baseline the phase.
And every baseline gets a git tag like:
plan-R_PIPELINE-PHASE01-v1.0.0

Why split them:

Agents (and humans) need one doc they can iterate on freely (Intent).

Compliance / audit needs one doc they can treat like law during a run (Execution Contract).

6. Never edit in-place without bumping

Rule you enforce on yourself and on agents:

If the meaning changes, version changes.

So:

You fix a comma? PATCH.

You clarify “we deploy nightly” to “we deploy at 02:00 UTC”? PATCH, because it’s precision not policy shift.

You add a new security verification step to IaC before merge? MINOR.

You remove the human approval gate and let the agent auto-merge into main? MAJOR. Always.

This makes drift visible. Silent edits are how teams get burned.

7. File naming and layout

You want structure that machines can crawl and humans can guess. This layout works well:

/docs
  /standards
    OC_CORE.md               # Operating Contract (core rules)
    OC_CORE.changelog.md     # Long-form history
    PIPELINE_POLICY.md       # How code is allowed to land
    PIPELINE_POLICY.changelog.md

/plans
  /R_PIPELINE
    PHASE_01_EXECUTION_CONTRACT.md
    PHASE_01_EXECUTION_CONTRACT.changelog.md
    2025-10-28_plan_intent.md
    2025-10-21_plan_intent.md


Notes:

The date prefix on plan intent files gives you a natural timeline.

The .changelog.md files can be generated from git later. Humans almost never read them directly, but auditors and agents do.

8. Tie runtime output to a version

In your deterministic pipeline, each run (each atomic workstream / ULID) should log something like this in its ledger entry:

{
  "run_id": "2025-10-28T14-22-07Z_ULID01Q3...",
  "repo_commit": "d4e9c8a",
  "policy_version": {
    "OC_CORE": "1.3.0",
    "PIPELINE_POLICY": "2.1.2"
  },
  "plan_contract_version": {
    "R_PIPELINE_PHASE_01": "1.0.0"
  }
}


Now you can:

Re-simulate why the AI or script made a specific decision.

Prove you were compliant with your own rules at that time.

Detect “rogue runs” that used outdated policy versions.

9. Who’s allowed to bump versions?

This is governance. You don’t want every tool silently bumping MAJOR.

Recommended pattern:

PATCH: Anyone, including agents, if tests still pass.

MINOR: Must pass review from an owner role (ex: Platform.Engineering or Compliance.Observer).

MAJOR: Must be explicitly blessed and tagged. You’re basically saying “new contract.”

This governance itself should be written down (and versioned), usually in the main Operating Contract.

That way an AI agent can refuse dangerous work:

“Requested workflow violates PIPELINE_POLICY v2.1.2 section 3.2.2. I cannot proceed without updated contract approval.”
That’s the dream. That’s guardrails, not vibes.

10. TL;DR checklist you can adopt immediately

You can drop this straight into your repo today:

Add metadata headers to every important doc: semver, effective_date, owner, status.

Bump SemVer on every meaningful edit.

Keep short recent change log in the doc, full history in git.

Store docs/plans in repo folders (/docs, /plans).

Tag important baselines in git.

Log “which version of which contract” in every pipeline run ledger.

Split plans into:

evolving “intent” docs (mutable)

locked “execution contracts” (frozen per phase and tagged)

If you follow those seven rules, you get:

auditability,

rollback,

reproducibility,

and agents that can defend you instead of improvise.

This is an **exceptionally well-designed system** for treating documentation as code with proper version control. Here's my assessment:

## What's Brilliant About It

**1. It solves the real problem**
Most teams have documentation drift because there's no accountability mechanism. By making docs first-class versioned artifacts with SemVer, you create the same forcing function that keeps code quality high.

**2. The audit trail is built-in, not bolted-on**
The ability to say "Run X was executed under Policy Y version Z at commit ABC" is exactly what you need for:
- Debugging why an AI agent made a specific decision
- Compliance/regulatory review
- Rollback to a known-good state
- Multi-agent coordination (they're all reading from the same versioned contract)

**3. SemVer for docs is genuinely clever**
Using MAJOR/MINOR/PATCH for policy changes makes the "blast radius" immediately visible. An agent can be programmed to refuse MAJOR changes without acknowledgment. A human can scan git history and understand scope at a glance.

**4. The Intent vs. Execution Contract split is crucial**
This solves the "planning paradox" where plans need to be both flexible (during exploration) and rigid (during execution). Most systems fail because they try to make one document do both jobs.

**5. Git tags as immutable snapshots = forensic gold**
Being able to checkout `docs-OC-CORE-1.3.0` and reproduce the exact governance environment that existed at a point in time is powerful for both humans and AI agents.

## Potential Friction Points (and how to mitigate)

**1. Version bump discipline**
The system only works if people actually bump versions consistently. Consider:
- Pre-commit hooks that check for version bumps when docs/ or plans/ change
- CI that fails if semver isn't incremented
- A simple CLI tool: `./scripts/bump-doc.sh OC_CORE patch "Fixed typo in section 3"`

**2. Owner governance overhead**
The "who can bump what" rules (PATCH=anyone, MINOR=owner review, MAJOR=blessed) need enforcement. Options:
- CODEOWNERS file in GitHub that requires approval for specific version levels
- Branch protection rules
- Bot that validates version bumps against change scope

**3. Changelog automation**
While you correctly say "don't maintain a giant changelog in the doc," you still need the short recent log. Consider:
- A script that auto-generates the "last 3 entries" section from git history + tags
- Convention: commit messages for doc changes must start with `[PATCH]`, `[MINOR]`, or `[MAJOR]`

**4. Initial migration cost**
For existing projects with organic docs, retrofitting this system takes work. Maybe start with:
- Version only the most critical contracts (Operating Contract, Pipeline Policy)
- Grandfather existing docs at `1.0.0`
- Expand gradually

## Missing Piece: Deprecation Strategy

One thing I'd add: **How do you sunset/deprecate old versions?**

Consider adding to the header:
```yaml
deprecated: false
deprecated_date: null
deprecated_by: null  # what version replaced this
retention_until: 2026-10-28  # when can we delete old tags
```

This prevents the repo from becoming a graveyard of dead policy versions while maintaining audit trail requirements.

## Bottom Line

This plan is **production-ready** for your use case (deterministic AI pipeline with multiple agents + human oversight).

The real test will be: **Can you enforce it?**

The system is only as good as your discipline around:
- Never silently editing docs
- Always tagging baselines
- Logging policy versions in every run

Looking at this chat, here's what I see for the versioning process:

## The Proposed Process (Structured View)

### 1. **Commit-Level Control**
- **Conventional Commits** as the base standard (feat/fix/BREAKING CHANGE)
- This feeds automatic SemVer derivation
- Optionally signed commits for auditability

### 2. **PR-Level Enforcement** (The Critical Gates)
```
When you open a PR touching docs/plans/:
├─ Pre-merge checks (automated, blocking):
│  ├─ Semantic PR title validation ✓
│  ├─ Front-matter version bump detection ✓
│  ├─ Markdown lint (markdownlint) ✓
│  ├─ Prose style (Vale) ✓
│  └─ Broken links (lychee) ✓
├─ Required reviews:
│  └─ CODEOWNERS approval for /docs/** or /plans/** ✓
└─ PR template checklist (human confirms):
   ├─ Updated semver: in front matter
   ├─ Updated effective_date: if meaning changed
   ├─ Trimmed changelog to last 3 entries
   └─ MAJOR/MINOR got owner approval
```

### 3. **Merge-Level Automation**
- **Merge Queue** batches PRs and re-tests before landing on `main`
- **Release Please** (or semantic-release) watches `main`:
  - Reads Conventional Commits since last release
  - Opens a "Release PR" with:
    - Auto-bumped version number
    - Generated CHANGELOG
  - When merged → creates git tag + GitHub Release automatically

### 4. **Post-Release Documentation**
- On new tag (`v*.*.*` or `docs-*`):
  - **mike** (MkDocs) or **Docusaurus** publishes versioned docs
  - Frozen snapshot becomes browsable at `/docs/v1.3.0/`

## My Assessment

### ✅ **What's Excellent**

1. **Layered enforcement**: Multiple checkpoints (bot checks, human checklist, CODEOWNERS) mean you'd have to actively bypass 3+ gates to skip versioning.

2. **Automation reduces cognitive load**: Release Please removes the "did I tag this?" question entirely—it's automatic from commit messages.

3. **GitHub-native**: Uses built-in features (branch protection, required checks, CODEOWNERS) rather than external systems.

4. **Fail-fast on PRs**: The `docs-guard.yml` workflow that fails if docs changed but `semver:` didn't is exactly the forcing function you need.

### ⚠️ **Potential Gaps vs. Your Original Plan**

Comparing this to your document versioning plan from earlier:

| Your Plan Says | This Chat Implements | Gap? |
|---|---|---|
| Track `supersedes:` in header | Not mentioned | **Minor gap** - could add to front-matter validation |
| `doc_id:` in header (e.g., `OC-CORE-2025-10-28`) | Not mentioned | **Gap** - Release Please doesn't handle doc-specific IDs |
| Split Intent vs. Execution Contract | Not explicitly addressed | **Gap** - needs separate folder structure + enforcement |
| Log policy versions in runtime ledger | Not mentioned | **Gap** - you'd need custom code to extract versions from headers during pipeline runs |
| Git tags like `docs-OC-CORE-1.3.0` (doc-specific) | Chat suggests `v*.*.*` (repo-wide) | **Mismatch** - you want per-doc tags, they're doing per-release |

### 🔧 **What's Missing for Full Compliance**

**1. Per-Document Versioning vs. Repo Versioning**

The chat assumes **monolithic releases** (entire repo gets one version). Your plan needs **per-document versions** because:
- Operating Contract might be v1.3.0
- Pipeline Policy might be v2.1.2
- R_PIPELINE Phase 01 Execution Contract might be v1.0.0

**Fix**: You'd need a custom workflow that:
```yaml
# When /docs/standards/OC_CORE.md changes:
- Extract semver from its front matter
- Create tag: docs-OC-CORE-{extracted-version}
- Publish doc-specific changelog
```

**2. The Front-Matter Validation is Too Shallow**

The example `docs-guard.yml` only checks if `semver:` *changed*, not if it changed *correctly* (e.g., PATCH→MINOR→MAJOR rules).

**Fix**: Add validation logic:
```bash
# Parse old and new semver
# Verify bump follows SemVer rules given diff scope
# Fail if MAJOR change but only MINOR bump
```

**3. No `supersedes:` Chain Validation**

Your plan wants ancestry tracking (`supersedes: OC-CORE-2025-09-12`). The chat doesn't enforce this.

**Fix**: Add to the guard workflow:
```bash
# If semver bumped, require supersedes: field update
# Validate superseded version actually exists in git history
```

**4. Execution Contract Freezing Not Automated**

Your "frozen per phase" Execution Contracts need special handling—they shouldn't bump versions casually. The chat doesn't distinguish these from mutable Intent docs.

**Fix**:
- Separate CODEOWNERS for `/plans/**/EXECUTION_CONTRACT.md`
- Require explicit `[CONTRACT-FREEZE]` commit prefix
- Block edits unless version is MAJOR bump

## Recommendation: Hybrid Approach

**Use the chat's GitHub automation backbone, but customize for your per-doc versioning needs:**

```yaml
# .github/workflows/doc-versioning.yml
name: Per-doc version enforcement
on:
  pull_request:
    paths:
      - 'docs/**.md'
      - 'plans/**.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      # For each changed doc:
      - name: Parse front matter and validate
        run: |
          # Extract doc_id, semver, supersedes
          # Verify semver bump matches diff scope
          # Check supersedes: points to valid ancestor
          # Fail if Execution Contract edited without MAJOR bump

      - name: Create per-doc tags on merge to main
        if: github.event_name == 'push'
        run: |
          # Auto-create tags like docs-OC-CORE-1.3.0
          # These supplement Release Please's repo-wide tags
```

**Then layer your runtime logging:**
```python
# In your pipeline runner:
def get_active_policy_versions():
    """Extract current doc versions from repo."""
    return {
        "OC_CORE": parse_semver("docs/standards/OC_CORE.md"),
        "PIPELINE_POLICY": parse_semver("docs/standards/PIPELINE_POLICY.md"),
        "R_PIPELINE_PHASE_01": parse_semver("plans/R_PIPELINE/PHASE_01_EXECUTION_CONTRACT.md")
    }

# Log to ledger:
ledger.record_run(
    run_id=...,
    repo_commit=git.head.commit.hexsha,
    policy_versions=get_active_policy_versions()
)
```

## Bottom Line

The chat gives you **80% of what you need**—the GitHub enforcement scaffolding is solid. But it's designed for typical software releases (one repo, one version), not your multi-document governance model.

You need to **fork their approach** and add:
1. Per-document tagging (not just repo-wide)
2. Deeper front-matter validation (semver rules, supersedes chain)
3. Execution Contract special handling
4. Runtime policy version logging

This assessment and implementation is **excellent** and directly addresses the gaps I identified. Here's my analysis:

## What Makes This a Strong Single Source of Truth

### ✅ **Solves the Per-Document Versioning Problem**

The refined front-matter schema with `doc_key` as a stable identifier is the key breakthrough:

```yaml
doc_key: OC_CORE              # Stable, tag-safe identifier
semver: 1.3.0                 # Version travels with the doc
supersedes_version: 1.2.2     # Explicit ancestry
contract_type: execution_contract  # Special handling flag
```

This enables:
- **Deterministic tags**: `docs-OC_CORE-1.3.0` (not ambiguous)
- **Per-doc history**: Each document has its own version timeline
- **Ancestry validation**: `supersedes_version` can be programmatically verified
- **Different lifecycle rules**: Execution contracts vs. intent docs vs. policies

### ✅ **Deep Enforcement That Actually Works**

The `docs-guard.yml` workflow implements what I said was missing:

| Gap I Identified | How This Fixes It |
|---|---|
| Shallow version bump detection | Now validates semver **increases** and **aligns with PR intent** (BREAKING→MAJOR, feat→MINOR) |
| No supersedes validation | Checks that `supersedes_version` matches the previous `semver` |
| Execution contract loophole | Explicitly blocks MINOR bumps (only MAJOR for scope, PATCH for editorial) |
| No effective_date enforcement | Warns if unchanged during MAJOR/MINOR bumps |

The Python validation logic is **robust** and checks:
- Required fields present
- Valid semver syntax
- Monotonic version increases
- PR intent vs. bump size alignment
- Contract-type-specific rules

### ✅ **Per-Document Tagging on Merge**

The `doc-tags.yml` workflow creates immutable snapshots **per document**, not per repo:

```bash
# Instead of one tag: v1.0.0 (entire repo)
# You get:
docs-OC_CORE-1.3.0
docs-PIPELINE_POLICY-2.1.2
docs-R_PIPELINE_PHASE_01-1.0.0
```

This means:
- Each document's version history is independent
- You can checkout `docs-OC_CORE-1.3.0` and get that exact policy state
- Runtime ledgers can log precise multi-doc versions

### ✅ **Runtime Integration Hook**

The PowerShell snippet for extracting versions at runtime closes the loop:

```powershell
$policy = @{
  OC_CORE = Get-DocSemVer "docs/standards/OC_CORE.md"
  PIPELINE_POLICY = Get-DocSemVer "docs/standards/PIPELINE_POLICY.md"
  R_PIPELINE_PHASE_01 = Get-DocSemVer "plans/R_PIPELINE/PHASE_01_EXECUTION_CONTRACT.md"
}
# Log to ledger alongside commit SHA
```

Now every pipeline run captures **exactly which version of which policy it operated under**.

## For Your Single Source of Truth Document

Here's what you need to include to make it complete and actionable:

### **1. The Canonical Front-Matter Schema**

```markdown
## Required Front Matter for All Governance Documents

Every document in `/docs` and `/plans` MUST include:

\`\`\`yaml
---
doc_key: OC_CORE              # Stable identifier (no dates, no version)
semver: 1.3.0                 # Required: MAJOR.MINOR.PATCH
status: active                # active | deprecated | frozen
effective_date: 2025-10-28    # When this version takes effect
supersedes_version: 1.2.2     # Previous semver (omit for new docs)
owner: Platform.Engineering   # CODEOWNERS team/role
contract_type: policy         # policy | intent | execution_contract
---
\`\`\`

**Field Definitions:**
- **doc_key**: Permanent identifier. Never changes. Used in git tags.
- **semver**: Current version. MUST increase monotonically.
- **status**: Lifecycle state. `active` = in force, `deprecated` = superseded, `frozen` = immutable snapshot.
- **effective_date**: Date when this version becomes authoritative (YYYY-MM-DD).
- **supersedes_version**: The `semver` this version replaces. Enables ancestry validation.
- **owner**: CODEOWNERS team responsible for approvals.
- **contract_type**: Determines validation rules (see below).
```

### **2. Contract Type Rules**

```markdown
## Contract Type Enforcement

### `policy`
General governance documents (Operating Contract, Pipeline Policy).
- **MAJOR**: Breaking changes to requirements/process
- **MINOR**: New capabilities, additional rules (backward compatible)
- **PATCH**: Clarifications, typos, formatting

### `intent`
Mutable planning documents (project plans, roadmaps).
- **MAJOR**: Complete pivot in direction
- **MINOR**: Scope additions, timeline shifts (common)
- **PATCH**: Editorial improvements

### `execution_contract`
Frozen commitments for a phase/sprint/milestone.
- **MAJOR ONLY**: Scope rebaseline (requires explicit approval)
- **PATCH ONLY**: Editorial/clarification (meaning unchanged)
- **MINOR BLOCKED**: No silent scope creep allowed
```

### **3. Enforcement Architecture**

```markdown
## How Versioning is Enforced (Never Miss a Step)

### Layer 1: Pre-Merge Validation (GitHub Actions)
**Workflow: `.github/workflows/docs-guard.yml`**
- ✅ Validates all front-matter fields present and well-formed
- ✅ Ensures `semver` increases from previous version
- ✅ Checks PR intent (BREAKING/feat/fix) matches bump size
- ✅ Blocks MINOR bumps to execution contracts
- ✅ Warns if `effective_date` unchanged during MAJOR/MINOR
- ✅ Validates `supersedes_version` points to actual prior version

**Status**: Required check. PRs cannot merge if this fails.

### Layer 2: Human Review (CODEOWNERS)
**File: `.github/CODEOWNERS`**
\`\`\`
/docs/standards/**           @team-compliance
/plans/**/EXECUTION_CONTRACT.md  @team-compliance @team-pmo
\`\`\`
- MINOR/MAJOR bumps require owner approval
- Execution contract changes require two-team approval
- Status: Required via branch protection rules

### Layer 3: Post-Merge Tagging (GitHub Actions)
**Workflow: `.github/workflows/doc-tags.yml`**
- Creates immutable git tags: `docs-{doc_key}-{semver}`
- Runs on every push to `main` that touches docs/plans
- Enables precise rollback and audit trails

### Layer 4: Runtime Validation (Pipeline Code)
**Function**: `Get-ActivePolicyVersions`
- Extracts `semver` from each document's front matter
- Logs to run ledger alongside commit SHA and ULID
- Enables: "This run executed under OC_CORE v1.3.0"
```

### **4. The PR Workflow (Step-by-Step)**

```markdown
## Developer Workflow: How to Update a Governance Document

### Step 1: Edit Document
1. Open the document (e.g., `docs/standards/OC_CORE.md`)
2. Make your changes
3. Update front matter:
   - Bump `semver` according to change type (MAJOR/MINOR/PATCH)
   - Update `effective_date` if meaning changed
   - Set `supersedes_version` to the previous `semver`
4. Update "Change Log (recent)" section (keep last 3 entries only)

### Step 2: Create PR
1. Create PR with Conventional Commit title:
   - `feat: Add observability gate to pipeline` (→ requires MINOR)
   - `fix: Clarify IaC retention policy` (→ requires PATCH)
   - `feat!: Require all edits via Pipeline Runner` (→ requires MAJOR)
2. Fill out PR template checklist

### Step 3: Automated Validation
GitHub Actions runs `docs-guard.yml`:
- ✅ Validates front matter
- ✅ Checks semver bump matches PR intent
- ✅ Enforces contract-type rules
- ❌ **PR blocked if validation fails**

### Step 4: Human Approval
- CODEOWNERS automatically requested for review
- MAJOR/MINOR changes require explicit approval
- Execution contracts require multi-team signoff

### Step 5: Merge
- Merge queue ensures `main` stays stable
- On merge, `doc-tags.yml` creates git tag automatically
- Example: `docs-OC_CORE-1.4.0`

### Step 6: Automatic Documentation
- Versioned docs published (MkDocs/Docusaurus)
- Tag becomes browsable snapshot
- Runtime code can reference specific versions
```

### **5. Audit and Rollback Procedures**

```markdown
## Audit Trail and Rollback

### To Answer: "What policy was in force on date X?"
\`\`\`bash
# Find all docs tags before the date
git tag -l 'docs-*' --sort=-creatordate --format='%(creatordate:short) %(refname:short)' \
  | awk '$1 <= "2025-10-28"' \
  | head -20

# Checkout specific version
git checkout docs-OC_CORE-1.3.0 -- docs/standards/OC_CORE.md
\`\`\`

### To Answer: "What versions did Run X use?"
\`\`\`powershell
# Query your ledger
Get-RunLedger -RunID "2025-10-28T14-22-07Z_ULID01Q3..." |
  Select-Object -ExpandProperty PolicyVersions

# Returns:
# OC_CORE: 1.3.0
# PIPELINE_POLICY: 2.1.2
# R_PIPELINE_PHASE_01: 1.0.0
\`\`\`

### To Rollback a Bad Policy Change
\`\`\`bash
# Revert to previous version
git checkout docs-OC_CORE-1.2.2 -- docs/standards/OC_CORE.md

# Update front matter to bump version (this is a new MAJOR)
# semver: 1.4.0 (or 2.0.0 if reverting a breaking change)
# supersedes_version: 1.3.0
# effective_date: 2025-10-29

# Create PR with title: "fix!: Rollback OC_CORE to 1.2.2 baseline"
\`\`\`
```

### **6. Governance Rules**

```markdown
## Version Bump Authority

| Bump Type | Who Can Approve | Conditions |
|-----------|-----------------|------------|
| PATCH | Any team member | Automated tests pass |
| MINOR | Document owner | Owner review required (CODEOWNERS) |
| MAJOR | Document owner + Compliance | Multi-approver required |
| Execution Contract (any) | Owner + PMO | Special label `contract-change` required |

These rules are enforced via:
- Branch protection (required status checks)
- CODEOWNERS (required reviews)
- Rulesets (org-wide, cannot be bypassed)
```

### **7. Bootstrap Instructions**

```markdown
## Setup Checklist for New Repos

1. **Add GitHub Actions workflows:**
   - Copy `.github/workflows/docs-guard.yml`
   - Copy `.github/workflows/doc-tags.yml`
   - Copy `.github/workflows/release-please.yml` (optional, for repo releases)

2. **Configure branch protection on `main`:**
   - Require pull requests
   - Require status checks: `validate` (from docs-guard)
   - Require CODEOWNERS review
   - Enable merge queue
   - Require signed commits (optional)

3. **Add CODEOWNERS file:**
   \`\`\`
   /docs/standards/** @team-compliance
   /plans/**/EXECUTION_CONTRACT.md @team-compliance @team-pmo
   \`\`\`

4. **Update existing docs with front matter:**
   - Grandfather at `1.0.0` if no prior versioning
   - Set `effective_date` to current date
   - Set `status: active`
   - Assign `owner` from CODEOWNERS

5. **Add runtime version extraction:**
   - Implement `Get-DocSemVer` function (PowerShell example provided)
   - Log to ledger in pipeline startup code

6. **Enable versioned docs publishing:**
   - Configure MkDocs + mike OR Docusaurus
   - Add workflow to publish on tag creation
```

## My Recommendation

**Create this document structure:**

```
/docs/standards/
  VERSIONING_OPERATING_CONTRACT.md  ← Your single source of truth
  OC_CORE.md                         ← Operating contract (governs dev process)
  PIPELINE_POLICY.md                 ← Pipeline rules

/docs/guides/
  VERSIONING_QUICKSTART.md           ← 5-minute tutorial
  VERSIONING_TROUBLESHOOTING.md      ← Common issues

/.github/
  workflows/
    docs-guard.yml                   ← Copy from assessment
    doc-tags.yml                     ← Copy from assessment
  CODEOWNERS                         ← Define ownership
  pull_request_template.md           ← Checklist
```

**In `VERSIONING_OPERATING_CONTRACT.md`, include:**

1. **Section 1**: Front-matter schema (canonical spec)
2. **Section 2**: Contract type rules (MAJOR/MINOR/PATCH definitions)
3. **Section 3**: Enforcement architecture (the 4 layers)
4. **Section 4**: Developer workflow (step-by-step)
5. **Section 5**: Audit/rollback procedures
6. **Section 6**: Governance (who approves what)
7. **Section 7**: Bootstrap checklist
8. **Appendix A**: Full workflow YAML files (copy-paste ready)
9. **Appendix B**: Runtime integration code samples

**Make it self-bootstrapping**: The versioning contract should itself follow its own rules—include front matter at the top:

```yaml
---
I'll draft the complete versioning operating contract as a comprehensive, self-governing document.I've created a comprehensive **Versioning Operating Contract** that serves as your single source of truth. Here's what makes it production-ready:

## Key Features

### 1. **Self-Governing**
The document itself has front matter and follows all the rules it defines—it versions itself using the system it describes.

### 2. **Complete Implementation Guide**
- Full front-matter specification with validation rules
- SemVer rules mapped to Conventional Commits
- Three contract types (policy/intent/execution_contract) with distinct rules
- Four-layer enforcement architecture

### 3. **Step-by-Step Workflows**
- Developer workflow (7 steps from edit to merge)
- Bootstrap instructions (8 steps to set up in any repo)
- Audit and rollback procedures (3 scenarios)

### 4. **Copy-Paste Ready**
- Complete GitHub Actions workflows (inline, expandable)
- CODEOWNERS template
- PR template
- Runtime integration code (PowerShell, Python, Bash)

### 5. **Troubleshooting Section**
Common issues with solutions so teams don't get stuck

### 6. **Authority Matrix**
Clear governance rules for who approves what

## What to Do Next

1. **Review the document** for your specific needs
2. **Customize**:
   - Team names in CODEOWNERS
   - Document paths in runtime extraction functions
   - Contract types if you need different categories
3. **Place it** in your repo as `docs/standards/VERSIONING_OPERATING_CONTRACT.md`
4. **Bootstrap** following Step 1-8 in the document
5. **Train your team** using the quickstart guide template

The document is **~500 lines** of comprehensive, production-ready guidance. It's designed to be:
- **Authoritative** (single source of truth)
- **Actionable** (no theory, just concrete steps)
- **Self-contained** (everything needed to implement)
- **Auditable** (itself versioned and tagged)

Want me to customize any section for your specific environment or create additional supporting documents (quickstart guide, training slides, etc.)?
