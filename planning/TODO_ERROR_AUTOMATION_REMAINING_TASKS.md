# TODO: Error Automation - Remaining Action Items

**Created**: 2025-12-06  
**Status**: Phases 1 & 2 COMPLETE - Phase 3 & Deployment PENDING  
**Priority**: HIGH - Production deployment and monitoring needed

---

## 🚨 IMMEDIATE ACTIONS (This Week)

### TODO-001: Set Up Production Environment Variables ⚡ CRITICAL
**Priority**: CRITICAL  
**Time**: 15 minutes  
**Owner**: DevOps/Team Lead

**Steps**:
```bash
# 1. Generate GitHub Personal Access Token
# Go to: https://github.com/settings/tokens
# Scopes needed: repo, workflow, write:packages

# 2. Set environment variable (Linux/Mac)
export GITHUB_TOKEN='ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# 3. Or set in CI/CD secrets
# GitHub Actions: Settings > Secrets > New repository secret
# Name: GITHUB_TOKEN
# Value: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 4. Optional: Slack webhook for alerts
export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX'
```

**Verification**:
```bash
python -c "import os; print('✅ GITHUB_TOKEN set' if os.getenv('GITHUB_TOKEN') else '❌ GITHUB_TOKEN missing')"
```

**Blockers**: None  
**Blocks**: TODO-002, TODO-003

---

### TODO-002: Install Dependencies ⚡ CRITICAL
**Priority**: CRITICAL  
**Time**: 5 minutes  
**Owner**: DevOps/Developer

**Steps**:
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Verify installations
python -c "from github import Github; print('✅ PyGithub installed')"
python -c "import requests; print('✅ requests installed')"

# 3. Install GitHub CLI (for auto-merge)
# Mac:
brew install gh

# Linux:
sudo apt install gh

# Windows:
winget install GitHub.cli

# 4. Authenticate GitHub CLI
gh auth login
```

**Verification**:
```bash
gh --version
python -c "from error.automation.pr_creator import PRCreator; print('✅ All imports working')"
```

**Blockers**: None  
**Blocks**: TODO-003

---

### TODO-003: Test System with Sample Patch ⚡ CRITICAL
**Priority**: CRITICAL  
**Time**: 30 minutes  
**Owner**: Developer

**Steps**:
```bash
# 1. Create a test patch file
cat > /tmp/test-fix.patch << 'EOF'
diff --git a/README.md b/README.md
index 1234567..abcdefg 100644
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # Project Title
 
+This is a test change.
 Documentation here.
EOF

# 2. Test with low confidence (should queue for manual review)
python scripts/run_error_automation.py apply /tmp/test-fix.patch \
  --auto-merge-threshold 0.98 \
  --pr-threshold 0.85

# 3. Check manual review queue
python scripts/run_error_automation.py process-queue --action list

# 4. Approve the queued patch
python scripts/run_error_automation.py process-queue \
  --action approve \
  --patch-id /tmp/test-fix.patch

# 5. Check metrics
python scripts/run_error_automation.py status --days 7
```

**Expected Results**:
- ✅ Patch validated successfully
- ✅ Queued to manual review (confidence < 0.80)
- ✅ Queue entry visible in list
- ✅ Metrics show 1 processed patch

**Blockers**: TODO-001, TODO-002  
**Blocks**: TODO-004

---

### TODO-004: Set Up Automated Monitoring ⚡ HIGH
**Priority**: HIGH  
**Time**: 30 minutes  
**Owner**: DevOps

**Option A: Cron Job (Linux/Mac)**
```bash
# Add to crontab
crontab -e

# Add this line (runs hourly)
0 * * * * cd /path/to/repo && /usr/bin/python3 scripts/monitor_error_automation.py >> /var/log/error_automation_monitor.log 2>&1
```

**Option B: GitHub Actions**
```yaml
# Create: .github/workflows/error-automation-monitor.yml
name: Error Automation Health Check

on:
  schedule:
    - cron: '0 * * * *'  # Hourly
  workflow_dispatch:  # Manual trigger

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run health check
        run: python scripts/monitor_error_automation.py
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      
      - name: Check exit code
        run: |
          if [ $? -eq 2 ]; then
            echo "❌ CRITICAL: Queue backlog detected"
            exit 1
          elif [ $? -eq 1 ]; then
            echo "⚠️ WARNING: Queue approaching threshold"
          else
            echo "✅ Queue healthy"
          fi
```

**Verification**:
```bash
# Test monitoring script
python scripts/monitor_error_automation.py
echo "Exit code: $?"  # Should be 0 for healthy
```

**Blockers**: TODO-003  
**Blocks**: None

---

## 📊 WEEK 1-2 ACTIONS (After Deployment)

### TODO-005: Monitor Real-World Usage
**Priority**: HIGH  
**Time**: 1-2 hours/week  
**Owner**: Team Lead

**Tasks**:
- [ ] Check `.state/alerts.jsonl` daily for patterns
- [ ] Review manual review queue weekly
- [ ] Track time saved (manual log for first 2 weeks)
- [ ] Collect feedback from team members
- [ ] Document any false positives/negatives

**Metrics to Track**:
```bash
# Weekly review
python scripts/run_error_automation.py status --days 7

# Check specific metrics
cat .state/manual_review_queue.jsonl | jq -r '.timestamp' | wc -l  # Total queued
cat .state/alerts.jsonl | jq -r 'select(.type=="patch_failed")' | wc -l  # Failures
```

**Success Criteria**:
- Manual review queue < 10 items
- Alert frequency acceptable
- No critical failures
- Team satisfied with automation

**Blockers**: TODO-004  
**Blocks**: TODO-006

---

### TODO-006: Tune Confidence Thresholds
**Priority**: MEDIUM  
**Time**: 2 hours  
**Owner**: Developer

**Current Defaults**:
```python
AUTO_MERGE_THRESHOLD = 0.95  # Direct merge to main
PR_THRESHOLD = 0.80          # Create PR with auto-merge
# Below 0.80 → Manual review queue
```

**Analysis Steps**:
```bash
# 1. Review confidence scores from first 2 weeks
cat .state/patch_decisions.jsonl | jq -r '.confidence.overall' | sort -n

# 2. Identify patterns
# - Are too many going to manual review? → Lower PR threshold
# - Are any auto-merged patches problematic? → Raise auto-merge threshold
# - Are PRs mostly approved? → Raise PR threshold

# 3. Adjust thresholds in scripts/run_error_automation.py
# Edit default values or add to config file
```

**Considerations**:
- **Conservative start**: Keep thresholds high initially
- **Gradual adjustment**: Move in 0.05 increments
- **Team comfort**: Adjust based on team confidence
- **Error cost**: Balance automation vs. manual review cost

**Blockers**: TODO-005  
**Blocks**: None

---

### TODO-007: Create Slack Channel for Alerts
**Priority**: MEDIUM  
**Time**: 30 minutes  
**Owner**: Team Lead

**Steps**:
1. Create Slack channel: `#error-automation-alerts`
2. Add incoming webhook integration
3. Copy webhook URL
4. Set environment variable:
   ```bash
   export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'
   ```
5. Test alert:
   ```bash
   python -c "
   from error.automation.alerting import AlertManager
   mgr = AlertManager()
   mgr.alert_auto_merge_success('test.patch', {'overall': 0.96})
   "
   ```

**Blockers**: None  
**Blocks**: None

---

## 🔧 OPTIONAL ENHANCEMENTS (Phase 3)

### TODO-008: Implement Real Security Scanning
**Priority**: MEDIUM  
**Time**: 12 hours  
**Owner**: Security/Developer

**Tasks**:
- [ ] Integrate pip-audit for dependency scanning
- [ ] Add bandit for Python code security
- [ ] Create security policy for blocking critical CVEs
- [ ] Update confidence scoring to include security score
- [ ] Add security scan results to PR descriptions

**File to Update**: `error/automation/patch_applier.py`

**Implementation Skeleton**:
```python
def _run_security_scan(self, patch_path: Path) -> float:
    """Run pip-audit and bandit on patched code.
    
    Returns:
        float: 0.0-1.0 security score
    """
    # pip-audit for dependencies
    # bandit for code security
    # Block on CRITICAL findings
    pass
```

**Blockers**: None  
**Blocks**: None

---

### TODO-009: Add Comprehensive Test Suite
**Priority**: MEDIUM  
**Time**: 16 hours  
**Owner**: Developer

**Tests Needed**:
```bash
tests/error/automation/
├── test_patch_applier.py
│   ├── test_validate_patch_high_confidence
│   ├── test_validate_patch_medium_confidence
│   ├── test_validate_patch_low_confidence
│   ├── test_confidence_scoring
│   └── test_decision_routing
├── test_pr_creator.py
│   ├── test_github_token_validation
│   ├── test_repo_access_check
│   ├── test_pr_body_generation
│   ├── test_auto_merge_enablement
│   └── test_graceful_fallback
├── test_queue_processor.py
│   ├── test_add_to_queue
│   ├── test_update_status_atomic
│   ├── test_list_pending
│   ├── test_get_metrics
│   └── test_health_calculation
├── test_alerting.py
│   ├── test_file_logging
│   ├── test_slack_optional
│   ├── test_alert_types
│   └── test_non_blocking_failures
└── test_metrics.py
    ├── test_time_based_aggregation
    ├── test_queue_age_tracking
    └── test_confidence_analytics
```

**Target**: 80%+ code coverage

**Run Tests**:
```bash
pytest tests/error/automation/ -v --cov=error.automation --cov-report=html
```

**Blockers**: None  
**Blocks**: None

---

### TODO-010: Implement Retry Logic
**Priority**: LOW  
**Time**: 8 hours  
**Owner**: Developer

**Scenarios**:
- GitHub API rate limiting
- Network timeouts
- Transient CI failures
- Temporary Slack outages

**Pattern**: Exponential backoff with circuit breaker

**File to Update**: `error/automation/pr_creator.py`, `error/automation/alerting.py`

**Implementation**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def _create_pr_with_retry(self, ...):
    # PR creation logic with automatic retries
    pass
```

**Blockers**: None  
**Blocks**: None

---

### TODO-011: Add Real Coverage Checks
**Priority**: LOW  
**Time**: 4 hours  
**Owner**: Developer

**Tasks**:
- [ ] Integrate pytest-cov
- [ ] Calculate coverage delta (before/after patch)
- [ ] Set minimum coverage threshold (e.g., 80%)
- [ ] Block patches that reduce coverage
- [ ] Include coverage in confidence score

**File to Update**: `error/automation/patch_applier.py`

**Implementation**:
```python
def _check_coverage(self, patch_path: Path) -> float:
    """Calculate coverage delta from patch.
    
    Returns:
        float: 1.0 if coverage maintained/improved, 0.0-1.0 if reduced
    """
    # Run pytest --cov before patch
    # Apply patch
    # Run pytest --cov after patch
    # Compare coverage percentages
    pass
```

**Blockers**: TODO-009  
**Blocks**: None

---

## 📋 DOCUMENTATION TASKS

### TODO-012: Create Onboarding Guide for New Team Members
**Priority**: LOW  
**Time**: 2 hours  
**Owner**: Team Lead

**Contents**:
- Overview of error automation system
- How confidence scoring works
- When to approve/reject manual reviews
- How to tune thresholds
- Troubleshooting common issues
- FAQ

**File**: `error/automation/ONBOARDING.md`

**Blockers**: TODO-005 (need real-world data)  
**Blocks**: None

---

### TODO-013: Create Runbook for Common Issues
**Priority**: LOW  
**Time**: 2 hours  
**Owner**: Developer

**Scenarios to Document**:
- Queue backlog growing too large
- PR creation failing
- Slack alerts not sending
- GitHub token expired
- False positive auto-merges
- Confidence scores too low

**File**: `error/automation/RUNBOOK.md`

**Blockers**: TODO-005 (need real-world issues)  
**Blocks**: None

---

### TODO-014: Create Metrics Dashboard
**Priority**: LOW  
**Time**: 8 hours  
**Owner**: Developer/Data Team

**Options**:
1. **Simple**: Grafana + JSON logs
2. **Medium**: Custom Flask dashboard
3. **Advanced**: Integrate with existing monitoring (Datadog, etc.)

**Metrics to Display**:
- Patches processed (daily/weekly/monthly)
- Confidence score distribution
- Auto-merge vs PR vs manual review %
- Queue health over time
- Time saved estimation
- Alert frequency

**Blockers**: TODO-005 (need baseline data)  
**Blocks**: None

---

## 🚀 FUTURE ROADMAP

### TODO-015: Multi-Repository Support
**Priority**: LOW  
**Time**: 16 hours  
**Owner**: Developer

**Features**:
- Support multiple repos in single instance
- Repo-specific configuration
- Shared queue or per-repo queues
- Aggregate metrics across repos

**Blockers**: TODO-005 (validate single-repo first)  
**Blocks**: None

---

### TODO-016: ML-Based Confidence Scoring
**Priority**: LOW  
**Time**: 40+ hours  
**Owner**: ML Engineer/Developer

**Idea**: Train model on historical patches to predict success

**Features**:
- Learn from approved/rejected patches
- Improve confidence scoring accuracy
- Reduce manual review burden over time
- Adaptive thresholds

**Blockers**: TODO-005 (need training data)  
**Blocks**: None

---

### TODO-017: Integration with Error Detection
**Priority**: LOW  
**Time**: 20 hours  
**Owner**: Developer

**Goal**: Close the loop from error detection → patch generation → auto-apply

**Tasks**:
- [ ] Hook into existing error detection pipeline
- [ ] Automatic patch generation (if not already)
- [ ] Trigger automation from CI failures
- [ ] End-to-end automated recovery

**Blockers**: None (but requires Phase 6 error recovery to exist)  
**Blocks**: None

---

## 📊 SUCCESS METRICS TO TRACK

### TODO-018: Establish Baseline Metrics
**Priority**: HIGH  
**Time**: 1 hour  
**Owner**: Team Lead

**Metrics to Capture (First 2 Weeks)**:
```bash
# Daily log template
Date: YYYY-MM-DD

Manual interventions: X
Time spent on patch review: X hours
Patches auto-merged: X
Patches via PR: X
Patches rejected: X
False positives: X
False negatives: X

Total time saved estimate: X hours
```

**Store in**: `DEVELOPMENT_TEMP_DOCS/METRICS_BASELINE_YYYYMM.md`

**Blockers**: TODO-004  
**Blocks**: TODO-019

---

### TODO-019: Monthly ROI Report
**Priority**: MEDIUM  
**Time**: 1 hour/month  
**Owner**: Team Lead

**Template**:
```markdown
# Error Automation - Monthly ROI Report

**Month**: YYYY-MM

## Metrics
- Patches processed: X
- Auto-merged: X (Y%)
- PR created: X (Y%)
- Manual review: X (Y%)

## Time Savings
- Estimated manual time: X hours
- Actual intervention time: X hours
- Net time saved: X hours

## Financial Impact
- Developer rate: $X/hour
- Team size: X developers
- Monthly value: $X,XXX

## Issues
- False positives: X
- False negatives: X
- System downtime: X hours

## Recommendations
- [Any threshold adjustments needed]
- [Process improvements]
- [Feature requests]
```

**Blockers**: TODO-018  
**Blocks**: None

---

## 🎯 PRIORITY MATRIX

### This Week (CRITICAL)
1. ⚡ TODO-001: Set up environment variables (15 min)
2. ⚡ TODO-002: Install dependencies (5 min)
3. ⚡ TODO-003: Test with sample patch (30 min)
4. ⚡ TODO-004: Set up monitoring (30 min)

**Total Time**: ~1.5 hours  
**Blockers**: None  
**Impact**: CRITICAL - System not operational without these

---

### Week 1-2 (HIGH)
5. 📊 TODO-005: Monitor real-world usage (1-2 hours/week)
6. 🔧 TODO-006: Tune thresholds (2 hours)
7. 💬 TODO-007: Create Slack channel (30 min)
8. 📊 TODO-018: Establish baseline metrics (1 hour)

**Total Time**: ~4-5 hours  
**Impact**: HIGH - Optimization and observability

---

### Month 1-2 (MEDIUM)
9. 🔒 TODO-008: Security scanning (12 hours)
10. ✅ TODO-009: Test suite (16 hours)
11. 📚 TODO-012: Onboarding guide (2 hours)
12. 📚 TODO-013: Runbook (2 hours)
13. 📊 TODO-019: Monthly ROI report (1 hour/month)

**Total Time**: ~33 hours  
**Impact**: MEDIUM - Quality and sustainability

---

### Future (LOW)
14. 🔄 TODO-010: Retry logic (8 hours)
15. 📊 TODO-011: Coverage checks (4 hours)
16. 📊 TODO-014: Metrics dashboard (8 hours)
17. 🚀 TODO-015: Multi-repo support (16 hours)
18. 🤖 TODO-016: ML confidence scoring (40+ hours)
19. 🔗 TODO-017: Integration with error detection (20 hours)

**Total Time**: ~96+ hours  
**Impact**: LOW - Nice-to-have enhancements

---

## 📝 QUICK START CHECKLIST

**Copy this to your task tracker:**

```markdown
## Error Automation - Deployment Checklist

### Week 0 (This Week) - CRITICAL ⚡
- [ ] TODO-001: Set GITHUB_TOKEN and SLACK_WEBHOOK_URL env vars
- [ ] TODO-002: Run `pip install -r requirements.txt`
- [ ] TODO-002: Install and authenticate `gh` CLI
- [ ] TODO-003: Test with sample patch
- [ ] TODO-003: Verify queue operations
- [ ] TODO-003: Check metrics display
- [ ] TODO-004: Add monitoring to cron/GitHub Actions
- [ ] TODO-004: Verify monitoring alerts work

### Week 1-2 - HIGH 📊
- [ ] TODO-005: Daily review of alerts.jsonl
- [ ] TODO-005: Weekly review of manual queue
- [ ] TODO-005: Track time saved (manual log)
- [ ] TODO-005: Collect team feedback
- [ ] TODO-006: Analyze confidence score distribution
- [ ] TODO-006: Adjust thresholds if needed
- [ ] TODO-007: Set up Slack channel and webhook
- [ ] TODO-018: Document baseline metrics

### Month 1 - MEDIUM 🔧
- [ ] TODO-008: Implement security scanning (optional)
- [ ] TODO-009: Write test suite (optional)
- [ ] TODO-012: Create onboarding guide
- [ ] TODO-013: Create runbook
- [ ] TODO-019: Generate first monthly ROI report

### Ongoing
- [ ] Weekly queue review
- [ ] Monthly ROI reporting
- [ ] Continuous threshold tuning
- [ ] Team feedback collection
```

---

## 🚨 KNOWN ISSUES & MITIGATIONS

### Issue 1: PyGithub Not Installed
**Symptom**: ImportError when running PR creator  
**Mitigation**: Run `pip install PyGithub>=2.1.1`  
**Prevention**: Add to requirements.txt ✅ (already done)

### Issue 2: GitHub Token Missing
**Symptom**: ValueError: "GITHUB_TOKEN environment variable required"  
**Mitigation**: Set environment variable (TODO-001)  
**Prevention**: Document in deployment guide ✅ (already done)

### Issue 3: gh CLI Not Authenticated
**Symptom**: Auto-merge fails silently, PR still created  
**Mitigation**: Run `gh auth login`  
**Prevention**: Include in setup checklist (TODO-002)

### Issue 4: Slack Webhook Optional
**Symptom**: Alerts only logged to file, no Slack notifications  
**Mitigation**: This is expected behavior (graceful degradation)  
**Prevention**: Set SLACK_WEBHOOK_URL if notifications desired (TODO-007)

### Issue 5: Queue Growing Too Large
**Symptom**: Many patches queued for manual review  
**Mitigation**: Lower PR threshold or increase team review cadence  
**Prevention**: Monitoring alerts (TODO-004) + threshold tuning (TODO-006)

---

## 📞 SUPPORT & CONTACTS

**For Implementation Help**:
- See: `error/automation/README.md`
- See: `DEVELOPMENT_TEMP_DOCS/ERROR_AUTOMATION_COMPLETE_SUMMARY.md`

**For Issues**:
- Check: `.state/alerts.jsonl` for error patterns
- Check: `DEVELOPMENT_TEMP_DOCS/ERROR_AUTOMATION_GAP_ANALYSIS.md` for architecture

**For Questions**:
- Review: PHASE_1_EXECUTION_SUMMARY.md
- Review: PHASE_2_EXECUTION_SUMMARY.md

---

## ✅ COMPLETION CRITERIA

**System is "Production Ready" when**:
- [x] All Phase 1 & 2 code committed ✅
- [ ] TODO-001: Environment variables set
- [ ] TODO-002: Dependencies installed
- [ ] TODO-003: System tested with real patch
- [ ] TODO-004: Monitoring automated
- [ ] TODO-005: Metrics tracked for 2 weeks
- [ ] TODO-006: Thresholds tuned

**System is "Fully Operational" when**:
- [ ] All "Production Ready" criteria met
- [ ] Team trained on system
- [ ] Runbook created
- [ ] ROI demonstrated (first month)
- [ ] Team satisfied with automation level

**System is "Optimized" when**:
- [ ] All "Fully Operational" criteria met
- [ ] Test coverage > 80%
- [ ] Security scanning integrated
- [ ] Retry logic implemented
- [ ] 3+ months of stable operation

---

## 🎯 FINAL NOTES

**Estimated Timeline**:
- Week 0 (Deploy): 1.5 hours
- Week 1-2 (Monitor & Tune): 4-5 hours
- Month 1-2 (Optimize): 33 hours (optional)
- Future: 96+ hours (optional enhancements)

**Minimum Viable Deployment**: Complete TODO-001 through TODO-004 (~1.5 hours)

**Recommended Path**: Complete TODO-001 through TODO-007 + TODO-018 (~5 hours)

**Full Enhancement**: Complete all Phase 3 items (~128 hours total)

---

**Status**: Ready for execution  
**Created**: 2025-12-06  
**Last Updated**: 2025-12-06  
**Next Review**: After TODO-005 (Week 2)

---

*End of TODO List*
