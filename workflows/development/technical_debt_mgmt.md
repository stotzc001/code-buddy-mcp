# Technical Debt Management

**ID:** dev-018  
**Category:** Development  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** Ongoing (15-20% of sprint capacity)  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Execute and manage technical debt remediation in a sustainable way that balances feature development with code health improvements.

**Why:** Technical debt doesn't pay itself down. Without active management, debt accumulates faster than it's resolved, eventually crippling development velocity and increasing bug rates. Systematic management ensures continuous improvement without halting feature work.

**When to use:**
- During sprint planning to allocate debt work
- When prioritizing remediation efforts
- Managing ongoing debt reduction initiatives
- Communicating debt status to stakeholders
- Making build-vs-fix tradeoff decisions

---

## Prerequisites

**Required:**
- [ ] Technical debt items identified and documented (see [Technical Debt Identification](./technical_debt_identification.md))
- [ ] Debt items prioritized with effort/impact scores
- [ ] Team buy-in on dedicating time to debt reduction
- [ ] Version control and CI/CD pipeline functional

**Recommended:**
- [ ] Project management tool (Jira, Linear, GitHub Projects)
- [ ] Metrics dashboard for tracking progress
- [ ] Automated testing in place
- [ ] Code review process established

**Check before starting:**
```bash
# Verify you have debt tracking in place
ls TECHNICAL_DEBT.md || echo "⚠️ No debt tracking file found"

# Check if there are tracked debt items
gh issue list --label "tech-debt" --limit 5

# Verify test suite is functional
pytest --collect-only | grep "test session starts"

# Check current coverage baseline
pytest --cov=src --cov-report=term | tail -n 1
```

---

## Implementation Steps

### Step 1: Integrate Debt Work Into Sprint Planning

**What:** Allocate dedicated capacity for technical debt work in each sprint, treating it as first-class work alongside features.

**How:** Reserve a percentage of sprint capacity specifically for debt reduction, with the allocation increasing based on debt severity and velocity impact.

**Code/Commands:**
```python
# scripts/calculate_debt_capacity.py
"""Calculate recommended debt allocation for sprint."""

def calculate_debt_allocation(
    total_capacity_points: int,
    velocity_trend: float,  # -1.0 to 1.0, negative = slowing
    debt_severity_score: int,  # 0-100, higher = worse
    upcoming_major_features: bool = False
) -> dict:
    """
    Recommend percentage of sprint to allocate to technical debt.
    
    Returns:
        dict with 'percentage', 'points', and 'reasoning'
    """
    # Base allocation
    base_allocation = 0.15  # Start with 15%
    
    # Adjust based on velocity trend
    if velocity_trend < -0.2:  # Velocity dropping significantly
        base_allocation += 0.10
    elif velocity_trend < 0:
        base_allocation += 0.05
    
    # Adjust based on debt severity
    if debt_severity_score > 70:  # Critical debt level
        base_allocation += 0.10
    elif debt_severity_score > 50:  # High debt level
        base_allocation += 0.05
    
    # Reduce if major feature work planned
    if upcoming_major_features:
        base_allocation = max(0.10, base_allocation - 0.05)
    
    # Cap at reasonable limits
    allocation_pct = min(0.35, max(0.10, base_allocation))
    allocation_points = int(total_capacity_points * allocation_pct)
    
    # Build reasoning
    reasons = []
    if velocity_trend < -0.2:
        reasons.append("Velocity declining significantly (-20%+)")
    if debt_severity_score > 70:
        reasons.append("Critical debt levels detected")
    if upcoming_major_features:
        reasons.append("Major features planned (reduced allocation)")
    
    return {
        'percentage': allocation_pct,
        'points': allocation_points,
        'reasoning': reasons or ["Standard allocation for healthy codebase"]
    }

# Example usage
result = calculate_debt_allocation(
    total_capacity_points=40,
    velocity_trend=-0.15,  # Velocity down 15%
    debt_severity_score=65,
    upcoming_major_features=False
)

print(f"Recommended Debt Allocation: {result['percentage']*100:.0f}%")
print(f"Sprint Points for Debt: {result['points']}")
print(f"Reasoning: {', '.join(result['reasoning'])}")
```

**Sprint Planning Template:**
```markdown
# Sprint X Planning - Debt Allocation

## Capacity Calculation
- Total Sprint Points: 40
- Team Size: 4 developers
- Expected Capacity: 38 points (accounting for meetings, etc.)

## Debt Allocation
- **Reserved for Debt:** 8 points (20%)
- **Available for Features:** 30 points (80%)

## Rationale
- Velocity declined 10% last 3 sprints
- 12 high-severity debt items in backlog
- No major feature launches this sprint

## Selected Debt Items (8 points total)
1. [TD-023] Add tests to payment module (3 points) - HIGH severity
2. [TD-015] Fix circular import in auth (2 points) - MEDIUM severity  
3. [TD-042] Type hints for core models (3 points) - HIGH severity

## Feature Work (30 points)
[Standard feature planning...]

## Commitment
Team commits to completing both debt AND feature work. Debt items are not 
"stretch goals" - they are core sprint commitments.
```

**Verification:**
- [ ] Debt allocation percentage decided and documented
- [ ] Specific debt items selected for sprint
- [ ] Debt work has story points/time estimates
- [ ] Team capacity calculated with debt work included
- [ ] Debt items added to sprint board

**If This Fails:**
→ If no time allocated: Start with 10%, demonstrate ROI, gradually increase
→ If team resists: Frame as "investment in velocity" not "time away from features"
→ If allocation ignored: Make debt items visible on sprint board, track in velocity

---

### Step 2: Prioritize Debt Items for Current Sprint

**What:** Select specific debt items for the sprint based on priority, dependencies, and available capacity.

**How:** Use a scoring model that balances ROI, team skills, and strategic goals to choose the right debt items.

**Code/Commands:**
```python
# scripts/select_sprint_debt.py
"""Intelligently select debt items for sprint based on multiple factors."""

from dataclasses import dataclass
from typing import List
import json

@dataclass
class DebtItem:
    id: str
    title: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    effort_points: int
    impact_score: int  # 1-10
    risk_score: int  # 1-10
    category: str
    dependencies: List[str]  # Other debt items that must be done first
    required_skills: List[str]  # e.g., ["python", "database"]

def calculate_sprint_readiness(item: DebtItem, completed_items: set) -> float:
    """Score how ready an item is to be worked on (0-1)."""
    # Check if dependencies are met
    unmet_deps = set(item.dependencies) - completed_items
    if unmet_deps:
        return 0.0  # Not ready
    
    # Items with no dependencies are most ready
    if not item.dependencies:
        return 1.0
    
    return 0.8  # Dependencies met, ready to go

def calculate_roi_score(item: DebtItem) -> float:
    """Calculate return on investment (higher = better ROI)."""
    impact = item.impact_score + item.risk_score
    effort = max(item.effort_points, 0.5)
    return impact / effort

def select_sprint_debt(
    debt_items: List[DebtItem],
    available_points: int,
    team_skills: List[str],
    completed_items: set,
    strategic_category: str = None
) -> List[DebtItem]:
    """
    Select optimal set of debt items for sprint.
    
    Args:
        debt_items: All available debt items
        available_points: Sprint capacity allocated for debt
        team_skills: Skills available in current sprint
        completed_items: Set of debt item IDs already resolved
        strategic_category: Prioritize this category if specified
    
    Returns:
        Selected debt items that fit in capacity
    """
    # Score each item
    scored_items = []
    for item in debt_items:
        # Skip if already completed or dependencies not met
        readiness = calculate_sprint_readiness(item, completed_items)
        if readiness == 0:
            continue
        
        # Check if team has required skills
        skill_match = len(set(item.required_skills) & set(team_skills)) / max(len(item.required_skills), 1)
        if skill_match < 0.5:  # Team doesn't have enough skills
            continue
        
        # Calculate scores
        roi = calculate_roi_score(item)
        
        # Severity weight
        severity_weight = {
            'CRITICAL': 10,
            'HIGH': 7,
            'MEDIUM': 4,
            'LOW': 2
        }[item.severity]
        
        # Strategic category bonus
        category_bonus = 2 if strategic_category == item.category else 0
        
        # Final score
        score = (roi * severity_weight * readiness * skill_match) + category_bonus
        
        scored_items.append((score, item))
    
    # Sort by score (descending)
    scored_items.sort(reverse=True)
    
    # Greedy knapsack: select items that fit in capacity
    selected = []
    used_points = 0
    
    for score, item in scored_items:
        if used_points + item.effort_points <= available_points:
            selected.append(item)
            used_points += item.effort_points
    
    return selected

# Example usage
debt_backlog = [
    DebtItem('TD-001', 'Add payment tests', 'HIGH', 3, 9, 8, 'Testing', [], ['python', 'pytest']),
    DebtItem('TD-002', 'Fix circular imports', 'MEDIUM', 2, 6, 5, 'Architecture', [], ['python']),
    DebtItem('TD-003', 'Upgrade deprecated API', 'CRITICAL', 5, 8, 9, 'Dependencies', [], ['python', 'api']),
    DebtItem('TD-004', 'Add type hints', 'HIGH', 3, 7, 4, 'Code Quality', ['TD-002'], ['python', 'typing']),
]

selected = select_sprint_debt(
    debt_items=debt_backlog,
    available_points=8,
    team_skills=['python', 'pytest', 'typing', 'api'],
    completed_items=set(),
    strategic_category='Testing'
)

print(f"Selected {len(selected)} debt items for sprint:")
for item in selected:
    print(f"- {item.id}: {item.title} ({item.effort_points} points)")
```

**Manual Selection Checklist:**
```markdown
# Debt Item Selection Criteria

For each debt item being considered:

## Must Have
- [ ] No unmet dependencies
- [ ] Team has required skills
- [ ] Fits within allocated capacity
- [ ] Clear acceptance criteria defined

## Should Have (Score +1 each)
- [ ] Quick win (≤2 days effort)
- [ ] Blocks feature work
- [ ] Affects customer-facing code
- [ ] Team familiar with affected code
- [ ] Can be independently tested

## Nice to Have
- [ ] Related to other sprint work
- [ ] Educational value for team
- [ ] Improves developer experience

## Anti-Patterns (Avoid)
- [ ] ❌ No clear owner
- [ ] ❌ Requires external dependencies
- [ ] ❌ Touches critical path without safety net
- [ ] ❌ "While we're at it" scope creep
```

**Verification:**
- [ ] Selected items total ≤ allocated capacity
- [ ] All dependencies for selected items are met
- [ ] Each item has clear definition of done
- [ ] Team members assigned as owners
- [ ] Items added to sprint board/backlog

**If This Fails:**
→ If can't find enough items: Look for quick wins or splitting larger items
→ If dependencies blocking: Start dependency resolution in this sprint
→ If skill mismatch: Pair junior/senior developers or defer to future sprint

---

### Step 3: Execute Debt Remediation with Quality

**What:** Work on debt items with the same rigor as feature work, including testing, review, and documentation.

**How:** Follow standard development practices while focusing on not introducing new debt during remediation.

**Code/Commands:**
```bash
# Standard workflow for debt remediation

# 1. Create feature branch
git checkout -b debt/TD-042-add-type-hints
git push -u origin debt/TD-042-add-type-hints

# 2. Set up tracking
gh issue edit TD-042 \
  --add-label "in-progress" \
  --add-assignee @me

# 3. Make incremental changes with tests
# Example: Adding type hints incrementally

# First, add types to one module
cat > src/models.py << 'EOF'
from typing import Optional, List
from datetime import datetime

class User:
    def __init__(
        self,
        id: int,
        email: str,
        created_at: datetime,
        roles: Optional[List[str]] = None
    ) -> None:
        self.id = id
        self.email = email
        self.created_at = created_at
        self.roles = roles or []
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role."""
        return role in self.roles
EOF

# 4. Verify types pass mypy
mypy src/models.py --strict

# 5. Run full test suite
pytest tests/ -v

# 6. Check for regression
pytest tests/ --cov=src --cov-report=term-missing

# 7. Update documentation
cat >> CHANGELOG.md << 'EOF'
## [Technical Debt] - 2025-10-25

### Added
- Type annotations to User model (TD-042)
- Strict mypy checking enabled for models.py

### Fixed
- Resolved circular import between auth and models modules
EOF

# 8. Commit with debt reference
git add src/models.py CHANGELOG.md
git commit -m "[TD-042] Add type annotations to User model

- Added type hints to __init__ and has_role methods
- Enabled mypy strict mode for models.py
- All tests passing with 100% coverage on changes

Closes #TD-042"

# 9. Push and create PR
git push
gh pr create \
  --title "[TECH DEBT] Add type annotations to User model" \
  --body "## Technical Debt Item: TD-042

### Changes
- Added comprehensive type hints to User model
- Enabled mypy strict checking
- Updated documentation

### Testing
- All existing tests pass
- mypy --strict validation successful
- Coverage maintained at 95%+

### Checklist
- [x] Tests pass
- [x] Type checking passes
- [x] Documentation updated
- [x] No new warnings introduced
- [x] Changelog updated" \
  --label "tech-debt"
```

**Quality Checklist for Debt Work:**
```markdown
# Debt Remediation Quality Checklist

## Before Starting
- [ ] Read and understand the debt item description
- [ ] Review affected code areas
- [ ] Check for related issues or recent changes
- [ ] Set up local development environment
- [ ] Create feature branch with descriptive name

## During Development
- [ ] Make small, atomic commits
- [ ] Write tests for changes (or improve existing tests)
- [ ] Run tests frequently during development
- [ ] Use linters and type checkers continuously
- [ ] Document non-obvious decisions in comments
- [ ] Keep scope limited to debt item (avoid scope creep)

## Before PR
- [ ] All tests pass locally
- [ ] Code passes linting (ruff check)
- [ ] Type checking passes (mypy --strict)
- [ ] Coverage not decreased
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated
- [ ] Self-review of changes

## PR Description
- [ ] Link to original debt item
- [ ] Explain what changed and why
- [ ] Highlight any risks or trade-offs
- [ ] Include testing details
- [ ] Add screenshots/logs if relevant

## After Merge
- [ ] Close debt item with reference to PR
- [ ] Update debt tracking metrics
- [ ] Notify team in standup/chat
- [ ] Monitor for any issues in production
```

**Verification:**
- [ ] Changes merged to main branch
- [ ] All CI/CD checks pass
- [ ] No new bugs introduced (monitor for 48 hours)
- [ ] Debt item marked as complete
- [ ] Team aware of changes

**If This Fails:**
→ If tests fail: Don't skip tests to "save time" - fix or update them
→ If scope grows: Create new debt items for discovered issues
→ If blocked: Document blocker, move to next item, escalate if needed

---

### Step 4: Track Progress and Measure Impact

**What:** Monitor debt reduction efforts and measure their impact on velocity, quality, and team satisfaction.

**How:** Establish metrics dashboards and regular reviews to ensure debt work is delivering value.

**Code/Commands:**
```python
# scripts/debt_metrics.py
"""Calculate and track technical debt metrics over time."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import subprocess

class DebtMetricsTracker:
    def __init__(self, metrics_file='debt_metrics.json'):
        self.metrics_file = metrics_file
        self.load_history()
    
    def load_history(self):
        """Load historical metrics."""
        if Path(self.metrics_file).exists():
            with open(self.metrics_file) as f:
                self.history = json.load(f)
        else:
            self.history = []
    
    def calculate_current_metrics(self) -> Dict:
        """Calculate current debt metrics."""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'total_debt_items': self._count_debt_items(),
            'debt_by_severity': self._count_by_severity(),
            'debt_by_category': self._count_by_category(),
            'avg_age_days': self._calculate_avg_age(),
            'code_quality': self._analyze_code_quality(),
            'test_coverage': self._get_test_coverage(),
            'velocity_trend': self._calculate_velocity_trend()
        }
        return metrics
    
    def _count_debt_items(self) -> int:
        """Count open debt items."""
        result = subprocess.run(
            ['gh', 'issue', 'list', '--label', 'tech-debt', '--state', 'open', '--json', 'number'],
            capture_output=True,
            text=True
        )
        issues = json.loads(result.stdout)
        return len(issues)
    
    def _count_by_severity(self) -> Dict[str, int]:
        """Count debt items by severity."""
        result = subprocess.run(
            ['gh', 'issue', 'list', '--label', 'tech-debt', '--state', 'open', '--json', 'labels'],
            capture_output=True,
            text=True
        )
        issues = json.loads(result.stdout)
        
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for issue in issues:
            for label in issue['labels']:
                if label['name'] in severity_counts:
                    severity_counts[label['name']] += 1
        
        return severity_counts
    
    def _get_test_coverage(self) -> float:
        """Get current test coverage percentage."""
        result = subprocess.run(
            ['pytest', '--cov=src', '--cov-report=json'],
            capture_output=True,
            text=True
        )
        
        if Path('.coverage.json').exists():
            with open('.coverage.json') as f:
                coverage_data = json.load(f)
                return coverage_data['totals']['percent_covered']
        return 0.0
    
    def _analyze_code_quality(self) -> Dict:
        """Run static analysis and return quality scores."""
        # Run ruff
        ruff_result = subprocess.run(
            ['ruff', 'check', 'src/', '--statistics'],
            capture_output=True,
            text=True
        )
        
        # Extract issue count
        # Format: "XXX E501 [*] Line too long"
        lines = ruff_result.stdout.strip().split('\n')
        total_issues = sum(int(line.split()[0]) for line in lines if line)
        
        # Run radon for complexity
        radon_result = subprocess.run(
            ['radon', 'cc', 'src/', '-a', '-j'],
            capture_output=True,
            text=True
        )
        complexity_data = json.loads(radon_result.stdout)
        avg_complexity = sum(func['complexity'] for file_data in complexity_data.values() 
                            for func in file_data) / max(len(complexity_data), 1)
        
        return {
            'total_linting_issues': total_issues,
            'avg_complexity': avg_complexity
        }
    
    def record_snapshot(self):
        """Record current metrics to history."""
        current = self.calculate_current_metrics()
        self.history.append(current)
        
        with open(self.metrics_file, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        return current
    
    def generate_report(self, days=30) -> str:
        """Generate markdown report of debt trends."""
        if len(self.history) < 2:
            return "Not enough historical data for trend analysis."
        
        current = self.history[-1]
        past = self.history[-min(len(self.history), days)]
        
        report = f"""# Technical Debt Metrics Report

**Period:** Last {days} days  
**Generated:** {datetime.now().strftime('%Y-%m-%d')}

## Current Status

- **Total Debt Items:** {current['total_debt_items']}
- **Critical:** {current['debt_by_severity']['CRITICAL']}
- **High:** {current['debt_by_severity']['HIGH']}
- **Medium:** {current['debt_by_severity']['MEDIUM']}
- **Low:** {current['debt_by_severity']['LOW']}

- **Test Coverage:** {current['test_coverage']:.1f}%
- **Avg Complexity:** {current['code_quality']['avg_complexity']:.2f}
- **Linting Issues:** {current['code_quality']['total_linting_issues']}

## Trends

"""
        # Calculate deltas
        debt_delta = current['total_debt_items'] - past['total_debt_items']
        coverage_delta = current['test_coverage'] - past['test_coverage']
        
        report += f"- Debt items: {debt_delta:+d} ({'📈' if debt_delta > 0 else '📉'})\n"
        report += f"- Coverage: {coverage_delta:+.1f}% ({'📈' if coverage_delta > 0 else '📉'})\n"
        
        return report

# Usage
tracker = DebtMetricsTracker()
tracker.record_snapshot()
print(tracker.generate_report(days=30))
```

**Create Metrics Dashboard:**
```bash
# Set up automated metrics collection (run daily via cron/Actions)

# .github/workflows/debt-metrics.yml
cat > .github/workflows/debt-metrics.yml << 'EOF'
name: Track Technical Debt Metrics

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  collect-metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov ruff radon
          pip install -r requirements.txt
      
      - name: Collect metrics
        env:
          GH_TOKEN: ${{ github.token }}
        run: python scripts/debt_metrics.py
      
      - name: Generate report
        run: python scripts/debt_metrics.py --report > DEBT_REPORT.md
      
      - name: Commit metrics
        run: |
          git config user.name "Debt Tracker Bot"
          git config user.email "bot@example.com"
          git add debt_metrics.json DEBT_REPORT.md
          git commit -m "📊 Update debt metrics [skip ci]" || echo "No changes"
          git push
EOF
```

**Verification:**
- [ ] Metrics dashboard accessible to team
- [ ] Historical data tracked (at least 2 weeks)
- [ ] Trends visible (debt increasing/decreasing)
- [ ] Coverage and quality metrics included
- [ ] Team reviews metrics weekly

**If This Fails:**
→ If metrics not updating: Check automation (cron job, GitHub Actions)
→ If trends unclear: Add more data points, visualize with charts
→ If team ignores metrics: Present in standups, link to velocity impact

---

### Step 5: Communicate Progress to Stakeholders

**What:** Regularly update stakeholders on debt reduction efforts and their business impact.

**How:** Translate technical metrics into business outcomes that stakeholders care about.

**Code/Commands:**
```markdown
# Template: Monthly Technical Health Report

# Technical Health Report - October 2025

**To:** Product & Engineering Leadership  
**From:** Engineering Team  
**Date:** 2025-10-31

---

## Executive Summary

This month we made significant progress on technical debt reduction while 
delivering all planned features. Our investment in code health is paying off:
- **Velocity improved 12%** due to reduced debugging time
- **Production bugs down 30%** from improved test coverage
- **Deploy time reduced from 45min to 25min** via CI/CD improvements

---

## Debt Reduction Highlights

### Completed This Month (8 items)
1. ✅ **Payment Module Testing** - Added comprehensive test suite
   - *Business Impact:* Prevents $50K+ revenue loss from payment bugs
   - *Effort:* 3 days
   
2. ✅ **API Rate Limiting** - Implemented proper rate limiting
   - *Business Impact:* Prevents service degradation during traffic spikes
   - *Effort:* 2 days
   
3. ✅ **Type Safety** - Added type annotations to core modules
   - *Business Impact:* Catches bugs before production (caught 12 this month)
   - *Effort:* 4 days

[... 5 more items ...]

### Metrics

| Metric | Last Month | This Month | Change |
|--------|------------|------------|--------|
| Open Debt Items | 45 | 39 | ↓ 13% |
| Test Coverage | 72% | 81% | ↑ 9% |
| Critical Items | 8 | 3 | ↓ 62% |
| Avg Deploy Time | 45min | 25min | ↓ 44% |
| Production Bugs | 23 | 16 | ↓ 30% |

---

## Investment vs. Return

**Time Invested:** 22 engineering days (18% of sprint capacity)  
**Returns:**
- Prevented estimated 4-6 production incidents
- Reduced debugging time by ~15 hours/week across team
- Enabled faster feature development (12% velocity increase)

**ROI:** For every 1 day invested in debt, we save ~2.5 days in future work

---

## Priorities for Next Month

1. **Database Performance** (5 days) - Optimize slow queries affecting UX
2. **Security Hardening** (3 days) - Address 2 remaining security vulnerabilities  
3. **Documentation** (2 days) - Complete API documentation for partners

---

## Recommendations

1. **Maintain 15-20% debt allocation** - Current level is optimal for our situation
2. **Approve security audit** - Found 2 HIGH severity issues needing external review
3. **Invest in monitoring** - Better observability will help prevent future debt

---

Questions? Contact @engineering-leads
```

**Stakeholder Communication Checklist:**
```markdown
## When Communicating About Technical Debt:

### DO:
✅ **Translate to business impact** - "Prevents $X in losses" not "Fixed circular import"
✅ **Show velocity improvements** - "Team 12% faster after debt reduction"
✅ **Quantify risk reduction** - "Decreased security vulnerabilities by 60%"
✅ **Celebrate wins** - Highlight completed debt items and their impact
✅ **Use analogies** - "Like maintaining a car - regular service prevents breakdowns"
✅ **Tie to OKRs** - Connect debt work to company objectives
✅ **Show ROI** - Investment (time) vs returns (prevented bugs, faster velocity)

### DON'T:
❌ **Use jargon** - Avoid "cyclomatic complexity", "coupling", "refactoring"
❌ **Only report problems** - Balance concerns with progress and plans
❌ **Blame** - Focus on systemic improvements, not individuals
❌ **Apologize excessively** - Frame as proactive maintenance, not failure
❌ **Request open-ended time** - Always tie to specific outcomes and timeframes
```

**Verification:**
- [ ] Monthly report sent to stakeholders
- [ ] Business impact clearly articulated
- [ ] Progress visible and celebrated
- [ ] Future plans communicated
- [ ] Stakeholders understand ROI of debt work

**If This Fails:**
→ If stakeholders don't see value: Show correlation between debt and incidents/velocity
→ If push back on time allocation: Demonstrate cost of not fixing (outages, delays)
→ If communication ignored: Present in person, use visuals, tell stories

---

### Step 6: Prevent New Debt Accumulation

**What:** Establish processes and practices to prevent new technical debt from being introduced.

**How:** Implement quality gates, code review standards, and team practices that catch debt early.

**Code/Commands:**
```bash
# Comprehensive pre-commit hooks to prevent debt

cat > .pre-commit-config.yaml << 'EOF'
# Pre-commit hooks for debt prevention
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
  
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.5
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        args: [--strict]
        additional_dependencies: [types-requests]
  
  - repo: local
    hooks:
      - id: complexity-check
        name: Check code complexity
        entry: bash -c 'radon cc src/ --min C && radon mi src/ --min B'
        language: system
        pass_filenames: false
      
      - id: test-coverage
        name: Ensure test coverage
        entry: bash -c 'pytest --cov=src --cov-fail-under=80 --cov-report=term-missing'
        language: system
        pass_filenames: false
      
      - id: no-untracked-debt
        name: Check for TODO/FIXME without issues
        entry: bash -c '! git diff --cached | grep -E "^\+.*TODO|FIXME" | grep -v "github.com"'
        language: system
        pass_filenames: false
EOF

# Install hooks
pre-commit install
pre-commit run --all-files
```

**Code Review Checklist (Debt Prevention):**
```markdown
# Code Review Checklist - Technical Debt Prevention

## Reviewer: Check for Technical Debt Red Flags

### Code Quality
- [ ] Functions <50 lines (extract if longer)
- [ ] Cyclomatic complexity <10 (refactor if higher)
- [ ] No duplicated code blocks
- [ ] Meaningful variable/function names (not x, tmp, data)
- [ ] No commented-out code (delete or explain why)

### Testing
- [ ] New code has unit tests
- [ ] Tests actually test something (not just "doesn't crash")
- [ ] Critical paths have integration tests
- [ ] Tests don't rely on external services without mocks
- [ ] Coverage not decreased by this PR

### Architecture
- [ ] Changes aligned with existing patterns
- [ ] No new circular dependencies introduced
- [ ] Proper error handling (not bare try/except)
- [ ] No hardcoded values (use config)
- [ ] Dependencies flow correctly (inner ← outer)

### Security
- [ ] No secrets in code
- [ ] Input validation present
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (escaped output)
- [ ] Authentication/authorization checks

### Documentation
- [ ] Public APIs have docstrings
- [ ] Complex logic has explanatory comments
- [ ] README updated if needed
- [ ] Breaking changes noted in CHANGELOG

### Debt Indicators (Flag for discussion)
- [ ] ⚠️ TODO/FIXME comments (create issue instead)
- [ ] ⚠️ Type: ignore comments (explain why necessary)
- [ ] ⚠️ Disabled linter rules (temporary or permanent?)
- [ ] ⚠️ Skipped tests (when will they be fixed?)
- [ ] ⚠️ "Quick fix" or "temporary" in commit message

## Decision: Approve or Request Changes?

**Approve if:**
- No debt red flags OR
- Minor debt clearly documented and tracked

**Request changes if:**
- Introduces significant untracked debt
- Violates team standards without justification
- Creates technical risk without mitigation plan
```

**Team Practices:**
```markdown
# Team Practices for Debt Prevention

## Definition of Done (DoD)
Every story must meet DoD before marking complete:
- [ ] Code reviewed and approved
- [ ] All tests passing (unit + integration)
- [ ] Coverage ≥80% on new code
- [ ] No linter errors or warnings
- [ ] Type checking passes (mypy --strict)
- [ ] Documentation updated
- [ ] No new TODO comments without linked issues
- [ ] Security checklist reviewed
- [ ] Deployed to staging and verified

## Boy Scout Rule
"Leave code better than you found it"
- Fix small issues you encounter (typos, formatting)
- Add tests to untested code you modify
- Refactor confusing code while working on it
- Document unclear behavior
- BUT: Don't expand PR scope significantly

## Spike Protocol
For uncertain technical work:
1. Time-box investigation (2-4 hours max)
2. Document findings in ticket
3. Create debt items for shortcuts taken
4. Review with team before implementing

## Knowledge Sharing
- Pair on complex/risky changes
- Brown bag sessions on new patterns
- Architecture Decision Records (ADRs)
- Internal wiki with patterns/anti-patterns
```

**Verification:**
- [ ] Pre-commit hooks installed and running
- [ ] Code review checklist adopted by team
- [ ] Definition of Done enforced
- [ ] Team practices documented and visible
- [ ] New debt creation rate decreased

**If This Fails:**
→ If hooks too strict: Make some checks warnings initially, tighten gradually
→ If team bypasses checks: Make quality gates mandatory in CI, can't merge without passing
→ If DoD ignored: Discuss in retro, adjust DoD to be realistic

---

### Step 7: Balance Debt Work with Feature Development

**What:** Make strategic tradeoff decisions between addressing debt and shipping features.

**How:** Use frameworks to evaluate when to take on debt vs. when to pay it down.

**Code/Commands:**
```python
# Decision framework for debt vs. feature tradeoffs

from enum import Enum
from dataclasses import dataclass

class Decision(Enum):
    FIX_NOW = "Fix debt immediately"
    FIX_SOON = "Fix within 2 sprints"
    TRACK_AND_DEFER = "Track but defer to later"
    ACCEPTABLE = "Accept as strategic tradeoff"

@dataclass
class TradeoffContext:
    debt_severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    feature_priority: str  # P0, P1, P2, P3
    timeline_pressure: bool  # Is there a hard deadline?
    affects_customers: bool  # Does debt impact customer experience?
    affects_team: bool  # Does debt slow down team?
    cost_to_fix_now: int  # Days of effort
    cost_if_deferred: int  # Estimated future cost in days

def evaluate_tradeoff(context: TradeoffContext) -> tuple[Decision, str]:
    """
    Decide whether to fix debt now or defer.
    
    Returns:
        (Decision, reasoning)
    """
    # Critical debt blocking features → fix now
    if context.debt_severity == 'CRITICAL':
        return (
            Decision.FIX_NOW,
            "Critical debt must be resolved before additional features"
        )
    
    # High severity debt affecting customers → fix soon
    if context.debt_severity == 'HIGH' and context.affects_customers:
        if context.timeline_pressure and context.feature_priority == 'P0':
            return (
                Decision.FIX_SOON,
                "Fix after P0 feature launch (within 2 sprints)"
            )
        else:
            return (
                Decision.FIX_NOW,
                "Customer-affecting debt should be prioritized"
            )
    
    # Debt significantly slowing team → fix before more features
    if context.affects_team and context.cost_to_fix_now < context.cost_if_deferred * 0.5:
        return (
            Decision.FIX_NOW,
            "Fixing now is 2x+ cheaper than deferring"
        )
    
    # P0 feature with timeline → defer non-critical debt
    if context.feature_priority == 'P0' and context.timeline_pressure:
        if context.debt_severity in ['MEDIUM', 'LOW']:
            return (
                Decision.TRACK_AND_DEFER,
                "P0 deadline takes precedence, track debt for later"
            )
    
    # Small fix that prevents accumulation → fix now (boy scout rule)
    if context.cost_to_fix_now <= 0.5:  # Half day or less
        return (
            Decision.FIX_NOW,
            "Quick fix - apply boy scout rule"
        )
    
    # Low severity, not blocking → defer
    if context.debt_severity == 'LOW' and not context.affects_customers:
        return (
            Decision.ACCEPTABLE,
            "Low-priority debt - acceptable in current state"
        )
    
    # Default: track and fix within 2 sprints
    return (
        Decision.FIX_SOON,
        "Address in next sprint or two to prevent accumulation"
    )

# Example usage
context = TradeoffContext(
    debt_severity='HIGH',
    feature_priority='P0',
    timeline_pressure=True,
    affects_customers=False,
    affects_team=True,
    cost_to_fix_now=2,
    cost_if_deferred=8
)

decision, reasoning = evaluate_tradeoff(context)
print(f"Decision: {decision.value}")
print(f"Reasoning: {reasoning}")
```

**Decision Matrix:**
```markdown
# Debt vs. Feature Decision Matrix

|  | P0 Feature (Hard Deadline) | P1 Feature (Flexible) | No Feature Pressure |
|---|---|---|---|
| **Critical Debt (Blocks Work)** | Fix → Ship | Fix → Ship | Fix Now |
| **High Debt (Impacts Customers)** | Ship → Fix ASAP | Fix → Ship | Fix Now |
| **High Debt (Impacts Team)** | Evaluate ROI* | Fix → Ship | Fix Now |
| **Medium Debt** | Ship → Track | Consider fixing | Fix if quick |
| **Low Debt** | Ship → Defer | Ship → Defer | Defer |

*ROI Evaluation: If `cost_to_fix_now` < `cost_if_deferred * 0.5`, fix first.

## Guidelines:
1. **Never defer CRITICAL debt** - It will bite you
2. **Customer-facing debt** takes precedence over internal
3. **Quick fixes** (<4 hours) should just be done
4. **Document all deferrals** - Create tracked debt items
5. **Review deferrals** monthly - Don't let them accumulate
```

**Verification:**
- [ ] Decision framework documented and shared
- [ ] Team uses framework during planning
- [ ] Deferrals are explicitly tracked, not forgotten
- [ ] Tradeoffs reviewed in retrospectives
- [ ] Stakeholders understand tradeoff decisions

**If This Fails:**
→ If always deferring debt: Show long-term cost (velocity decline, outages)
→ If always fixing debt: Adjust severity thresholds, accept some debt
→ If framework too complex: Simplify to 3 categories (fix now, fix soon, defer)

---

### Step 8: Review and Refine Debt Management Process

**What:** Regularly assess the effectiveness of your debt management process and make improvements.

**How:** Conduct quarterly reviews of debt metrics, process effectiveness, and team satisfaction.

**Code/Commands:**
```markdown
# Quarterly Technical Debt Review - Template

# Q4 2025 Technical Debt Review

**Date:** 2025-10-31  
**Attendees:** Engineering Team + Tech Lead + Product Manager

---

## Review Period: July 1 - Sept 30, 2025

### Key Metrics

| Metric | Q3 Start | Q3 End | Change | Target |
|--------|----------|--------|--------|--------|
| Total Debt Items | 52 | 39 | ↓ 25% | ↓ 30% |
| Critical Items | 8 | 3 | ↓ 62% | < 5 |
| Test Coverage | 68% | 81% | ↑ 13% | 80%+ |
| Velocity (story points) | 32 | 36 | ↑ 12% | stable |
| Production Incidents | 18 | 11 | ↓ 39% | < 12 |
| Deploy Frequency | 8/month | 15/month | ↑ 87% | 12+/month |

**Summary:** Strong progress on all metrics. Exceeded targets except total debt reduction 
(25% vs 30% target).

---

## What Worked Well ✅

1. **Dedicated Debt Allocation (20%)** 
   - Consistent time each sprint
   - Team knew debt work was "real work"
   - Completed 13 debt items

2. **Automated Metrics Dashboard**
   - Visibility drove action
   - Early warning on trends
   - Stakeholders engaged

3. **Pre-commit Hooks**
   - Caught 40+ issues before they became debt
   - Team adapted to stricter checks
   - New debt creation rate ↓ 60%

4. **Monthly Stakeholder Reports**
   - Gained support for debt work
   - Celebrated wins publicly
   - Connected debt to business outcomes

---

## What Didn't Work ❌

1. **Debt Item Documentation**
   - Still too verbose and slow
   - Team skips documentation for "small" items
   - **Action:** Create quick-capture template

2. **Severity Assignment**
   - Inconsistent between team members
   - Some disagreement on HIGH vs MEDIUM
   - **Action:** Run calibration session

3. **Long-lived Branches**
   - Some debt fixes sat in branches 2+ weeks
   - Delayed showing progress
   - **Action:** Break large debt items into smaller chunks

4. **Skills Mismatch**
   - Some debt items required specialized skills
   - Blocked progress when those people unavailable
   - **Action:** Pair programming, knowledge sharing

---

## Process Improvements for Q4

### Changes to Make:

1. **Simplify Debt Capture**
   - New quick template: Title, Impact, Effort, Owner
   - Detailed docs optional for complex items

2. **Pair on High-Risk Debt**
   - Mandatory pairing for CRITICAL and HIGH items
   - Knowledge sharing benefit

3. **Debt Sprint Every Quarter**
   - One sprint per quarter dedicated 80% to debt
   - Tackle 5-10 accumulated items intensively
   - Book time with specialized skills in advance

4. **Better Visibility**
   - Add debt board column to main kanban
   - Debt work visible in standups
   - Celebrate completions in team chat

5. **Preventive Investment**
   - Upgrade testing framework (4 days)
   - Implement feature flags (3 days)
   - These investments will prevent future debt

---

## Updated Goals for Q4

1. **Reduce debt items by 35%** (from 39 to 25)
2. **Maintain 0 critical items**
3. **Increase coverage to 85%+**
4. **Decrease new debt creation by 40%**
5. **Improve velocity by additional 5%**

---

## Action Items

- [ ] @tech-lead: Schedule debt calibration session (by Oct 10)
- [ ] @team: Create simplified debt capture template (by Oct 15)
- [ ] @product: Schedule Q4 debt sprint for December (by Nov 1)
- [ ] @devops: Upgrade testing framework (Sprint 23)
- [ ] @everyone: Implement pairing protocol for HIGH+ debt (immediately)

---

## Conclusion

Strong quarter for debt management. Process is working, with minor improvements needed.
Team morale improved - developers report feeling less "frustrated by the codebase."
Continue current allocation (20%) with process refinements.

**Next Review:** End of Q4 2025
```

**Retrospective Questions:**
```markdown
# Retro: Technical Debt Management

## Collect Feedback Anonymously

### What's Working?
- What aspects of our debt management are effective?
- What practices should we keep?

### What's Not Working?
- What's frustrating about current debt process?
- What's slowing us down?

### Ideas for Improvement
- What would make debt management easier?
- What tools or processes would help?

### Questions
- Are we allocating right amount of time?
- Are we working on the right debt items?
- Do stakeholders understand the value?

## Discuss and Prioritize
1. Group similar themes
2. Vote on top 3 improvements
3. Assign owners and deadlines
4. Track improvements as action items
```

**Verification:**
- [ ] Quarterly review conducted with team
- [ ] Metrics reviewed and trends analyzed
- [ ] Process improvements identified and prioritized
- [ ] Action items assigned with deadlines
- [ ] Next review scheduled

**If This Fails:**
→ If no time for reviews: Make them 30 minutes, focus on top issues
→ If same problems recur: Deep dive on root causes, not symptoms
→ If team disengaged: Change format, use retrospective games, bring snacks!

---

## Verification Checklist

After implementing technical debt management:

- [ ] Debt work integrated into sprint planning (10-20% capacity)
- [ ] Debt items prioritized by ROI and tracked systematically
- [ ] Team follows quality standards during debt remediation
- [ ] Progress metrics tracked and reviewed regularly
- [ ] Stakeholders receive regular updates with business impact
- [ ] Prevention measures in place (hooks, gates, reviews)
- [ ] Tradeoff decisions made transparently using framework
- [ ] Quarterly reviews conducted with continuous improvement
- [ ] Team satisfaction with codebase improving over time
- [ ] Velocity trending upward or stable (not declining)

---

## Best Practices

### DO:
✅ **Reserve dedicated time for debt** - Make it non-negotiable
✅ **Measure and communicate impact** - Show ROI to stakeholders
✅ **Prevent as much as fix** - Quality gates are cheaper than remediation
✅ **Celebrate debt reduction** - Make it visible and rewarding
✅ **Balance quick wins and strategic fixes** - Mix for sustained progress
✅ **Make tradeoffs explicit** - Document deferrals and reasoning
✅ **Pair on risky debt** - Share knowledge and reduce mistakes
✅ **Review process regularly** - Continuous improvement
✅ **Connect to business outcomes** - Always explain "why this matters"

### DON'T:
❌ **Don't treat debt as optional** - It compounds like financial debt
❌ **Don't wait for "perfect time"** - There never is one
❌ **Don't fix without tests** - You'll create new debt
❌ **Don't scope creep debt work** - Stay focused on original issue
❌ **Don't let perfection block progress** - 80% solution now > 100% never
❌ **Don't defer critical items** - They only get more expensive
❌ **Don't work in isolation** - Review and communicate
❌ **Don't give up** - Debt management is a marathon, not sprint

---

## Common Issues & Solutions

### Issue: Team Can't Sustain Debt Allocation

**Symptoms:**
- Debt capacity frequently reallocated to features
- Pressure to "skip debt this sprint"
- Debt items chronically pushed to next sprint

**Solution:**
1. Protect allocation like you protect prod on-call time
2. Show correlation: debt reduction → velocity increase
3. Make it leadership commitment, not just team decision
4. Start smaller (10%) and demonstrate value before increasing

**Prevention:**
Establish debt allocation as baseline capacity planning, not extra time.

---

### Issue: Debt Work Takes Longer Than Estimated

**Symptoms:**
- Debt items consistently spill over sprints
- Estimates off by 2-3x
- Discovery of more debt while fixing original issue

**Solution:**
1. Add 50% buffer to debt estimates initially
2. Break large items into smaller incremental fixes
3. Time-box investigation phase before committing to fix
4. Document discovered debt as separate items

**Prevention:**
Use relative sizing (S/M/L) instead of precise hours for debt work.

---

### Issue: Same Debt Types Keep Recurring

**Symptoms:**
- Repeatedly fixing similar issues (missing tests, type errors)
- New debt created as fast as old debt resolved
- Prevention measures not effective

**Solution:**
1. Root cause analysis - why does this debt keep appearing?
2. Invest in better prevention (better linting, templates, training)
3. Make problematic patterns harder to introduce (enforce in CI)
4. Pair programming or code review focus areas

**Prevention:**
Treat recurring debt as process problem, not individual mistakes.

---

### Issue: Stakeholders Don't Support Debt Work

**Symptoms:**
- Push back on allocating time
- "Why aren't we building features?"
- Debt work deprioritized in planning

**Solution:**
1. Show data: velocity decline, incident rate, customer impact
2. Translate to business terms: "Prevents $X in losses"
3. Demonstrate success: "After fixing X, Y improved by Z%"
4. Make visible: Include in sprint demos and reports

**Prevention:**
Build trust by consistently delivering while managing debt.

---

## Related Workflows

**Prerequisites:**
- [Technical Debt Identification](./technical_debt_identification.md) - Identify debt before managing
- [Test Writing](./test_writing.md) - Tests are crucial for safe debt remediation
- [Refactoring Strategy](./refactoring_strategy.md) - Safely refactor during debt work

**Next Steps:**
- [Code Review Checklist](../quality-assurance/code_review_checklist.md) - Prevent new debt
- [CI/CD Pipeline](./ci_cd_workflow.md) - Automate quality gates
- [Sprint Planning](../project-management/progress_tracking.md) - Integrate debt into planning

**Related:**
- [Complexity Reduction](../quality-assurance/complexity_reduction.md) - Reduce complexity debt
- [Type Annotation Addition](./type_annotation_addition.md) - Address type debt
- [Developer Onboarding](./developer_onboarding.md) - Debt impacts new developer experience

---

## Tags
`development` `technical-debt` `project-management` `process` `metrics` `communication` `leadership`
