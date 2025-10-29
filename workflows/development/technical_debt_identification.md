# Technical Debt Identification

**ID:** dev-017  
**Category:** Development  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 1-2 hours  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Systematically identify, categorize, and document technical debt in a codebase to inform prioritization and remediation planning.

**Why:** Unmanaged technical debt compounds over time, slowing development velocity, increasing bug rates, and making refactoring more expensive. Systematic identification enables informed decision-making about when and how to address debt.

**When to use:**
- Beginning of a new sprint or planning cycle
- After major feature releases
- When velocity starts decreasing unexpectedly
- During onboarding to understand codebase health
- Quarterly or monthly code health reviews
- Before major refactoring initiatives

---

## Prerequisites

**Required:**
- [ ] Access to codebase and version control history
- [ ] Static analysis tools (Ruff, mypy, SonarQube, etc.)
- [ ] Understanding of code quality metrics
- [ ] Familiarity with the project architecture

**Optional:**
- [ ] Code coverage tools (pytest-cov, coverage.py)
- [ ] Dependency analysis tools (pip-audit, safety)
- [ ] Documentation system (Confluence, Notion, GitHub Wiki)

**Check before starting:**
```bash
# Verify tools are installed
ruff --version
mypy --version
git --version

# Check test coverage baseline
pytest --cov=src --cov-report=term-missing

# Verify you have read access to repository
git log --oneline -10
```

---

## Implementation Steps

### Step 1: Set Up Technical Debt Tracking

**What:** Create a centralized system for documenting and tracking technical debt items.

**How:** Establish a structured approach to record debt with consistent categorization and metadata.

**Code/Commands:**
```markdown
# Create TECHNICAL_DEBT.md in repository root

# Technical Debt Register

## Active Debt Items

### [TD-001] Missing Test Coverage in Payment Module
**Category:** Testing  
**Severity:** HIGH  
**Impact:** High risk of production bugs  
**Effort:** 3 days  
**Identified:** 2025-10-25  
**Owner:** @backend-team  
**Related Code:** `src/payments/processor.py`

**Description:**
Payment processing module has only 45% test coverage, with no integration tests
for refund workflows.

**Consequences:**
- 3 production bugs in last 2 months
- Difficult to refactor without breaking changes
- Team afraid to modify code

**Proposed Solution:**
Add comprehensive unit and integration tests, aiming for 85%+ coverage.

---

### [TD-002] Deprecated API Version Still in Use
**Category:** Dependencies  
**Severity:** MEDIUM  
...
```

**Alternative - Use GitHub Issues with Labels:**
```bash
# Create technical debt label
gh label create "tech-debt" --description "Technical debt items" --color "FFA500"

# Create debt categories
gh label create "tech-debt:testing" --description "Testing debt" --color "FFD700"
gh label create "tech-debt:architecture" --description "Architecture debt" --color "FF8C00"
gh label create "tech-debt:security" --description "Security debt" --color "FF0000"
gh label create "tech-debt:performance" --description "Performance debt" --color "FFA500"
gh label create "tech-debt:docs" --description "Documentation debt" --color "FFE4B5"

# Template for creating debt issue
gh issue create \
  --title "[TECH DEBT] Missing type annotations in core modules" \
  --label "tech-debt,tech-debt:quality" \
  --body "**Impact:** High - Reduces IDE assistance and catches fewer bugs
**Effort:** 2 days
**Modules Affected:** auth.py, database.py, utils.py
**Proposed Fix:** Add comprehensive type hints using mypy strict mode"
```

**Verification:**
- [ ] Tracking system is accessible to all team members
- [ ] Template is clear and provides all necessary fields
- [ ] Team agrees on categories and severity levels
- [ ] Process for adding new items is documented

**If This Fails:**
→ If team doesn't use tracking system: Make it low-friction (use existing tools like Jira/GitHub)
→ If categories unclear: Start with simple High/Medium/Low and refine over time
→ If no buy-in: Present data on velocity impact to demonstrate value

---

### Step 2: Run Automated Code Quality Analysis

**What:** Use static analysis tools to automatically identify quality issues, code smells, and violations.

**How:** Configure and run multiple analysis tools to get comprehensive coverage of different debt types.

**Code/Commands:**
```bash
# Run comprehensive linting with Ruff
ruff check . --output-format=json > reports/ruff_report.json
ruff check . --statistics

# Run type checking with mypy
mypy src/ --strict --html-report reports/mypy/ --txt-report reports/
mypy src/ --strict --any-exprs-report reports/

# Check for security vulnerabilities
pip-audit --format json --output reports/security_audit.json

# Analyze code complexity
radon cc src/ -a -s > reports/complexity.txt
radon mi src/ -s > reports/maintainability.txt

# Check for duplicate code
pylint src/ --disable=all --enable=duplicate-code > reports/duplicates.txt

# Measure test coverage
pytest --cov=src --cov-report=html:reports/coverage --cov-report=term-missing
```

**Python script for aggregating results:**
```python
# scripts/aggregate_debt.py
import json
from pathlib import Path
from collections import defaultdict

def analyze_ruff_report(report_path):
    """Extract high-priority issues from Ruff report."""
    with open(report_path) as f:
        issues = json.load(f)
    
    debt_items = defaultdict(list)
    for issue in issues:
        if issue.get('code', '').startswith(('E501', 'F401', 'C90')):
            category = categorize_ruff_code(issue['code'])
            debt_items[category].append({
                'file': issue['filename'],
                'line': issue['location']['row'],
                'message': issue['message'],
                'code': issue['code']
            })
    
    return debt_items

def categorize_ruff_code(code):
    """Map Ruff codes to debt categories."""
    mapping = {
        'E': 'code-style',
        'F': 'code-quality',
        'C': 'complexity',
        'N': 'naming',
        'D': 'documentation',
        'S': 'security'
    }
    return mapping.get(code[0], 'other')

def generate_report(debt_items, output_path):
    """Generate markdown report of technical debt."""
    with open(output_path, 'w') as f:
        f.write("# Technical Debt Analysis Report\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        
        for category, items in sorted(debt_items.items()):
            f.write(f"## {category.title()} ({len(items)} items)\n\n")
            for item in items[:10]:  # Top 10 per category
                f.write(f"- `{item['file']}:{item['line']}` - {item['message']}\n")
            f.write("\n")

if __name__ == "__main__":
    debt_items = analyze_ruff_report("reports/ruff_report.json")
    generate_report(debt_items, "DEBT_ANALYSIS.md")
```

**Verification:**
- [ ] All analysis tools completed successfully
- [ ] Reports generated in `reports/` directory
- [ ] No critical security vulnerabilities found
- [ ] Baseline metrics documented (coverage %, complexity scores)

**If This Fails:**
→ If tools not installed: `pip install ruff mypy pip-audit radon pylint pytest-cov`
→ If too many errors: Start with `--select` for specific rules, gradually expand
→ If mypy fails: Use `--no-strict-optional` initially, tighten incrementally

---

### Step 3: Analyze Code Metrics and Hotspots

**What:** Identify code areas with high change frequency, complexity, or defect density as debt indicators.

**How:** Use version control history and complexity metrics to find problematic areas.

**Code/Commands:**
```bash
# Find most frequently changed files (potential hotspots)
git log --format=format: --name-only | \
  grep -v '^$' | \
  sort | \
  uniq -c | \
  sort -rn | \
  head -20 > reports/change_frequency.txt

# Find files with most bug fixes
git log --all --grep="fix\|bug\|hotfix" --name-only --pretty=format: | \
  grep -v '^$' | \
  sort | \
  uniq -c | \
  sort -rn | \
  head -20 > reports/bug_hotspots.txt

# Find largest files (potential god objects)
find src -name "*.py" -exec wc -l {} \; | \
  sort -rn | \
  head -20 > reports/large_files.txt

# Analyze commit patterns (abandoned areas)
git log --all --since="6 months ago" --pretty=format:"%ad %an" --date=short | \
  awk '{print $1}' | \
  sort | \
  uniq -c > reports/commit_activity.txt
```

**Python script for hotspot analysis:**
```python
# scripts/analyze_hotspots.py
import subprocess
from pathlib import Path
from collections import Counter
import json

def get_file_complexity(file_path):
    """Get cyclomatic complexity for a file."""
    result = subprocess.run(
        ['radon', 'cc', file_path, '-j'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def get_change_frequency(file_path, since="6 months ago"):
    """Count commits touching this file."""
    result = subprocess.run(
        ['git', 'log', '--oneline', '--since', since, '--', file_path],
        capture_output=True,
        text=True
    )
    return len(result.stdout.strip().split('\n'))

def identify_hotspots(src_dir='src'):
    """Identify high-risk files based on complexity + change frequency."""
    hotspots = []
    
    for py_file in Path(src_dir).rglob('*.py'):
        complexity = get_file_complexity(py_file)
        changes = get_change_frequency(py_file)
        
        # Calculate risk score (complexity * change frequency)
        avg_complexity = sum(func['complexity'] for file_data in complexity.values() 
                           for func in file_data) / max(len(complexity), 1)
        risk_score = avg_complexity * changes
        
        if risk_score > 50:  # Threshold for hotspot
            hotspots.append({
                'file': str(py_file),
                'complexity': avg_complexity,
                'changes': changes,
                'risk_score': risk_score
            })
    
    # Sort by risk score
    hotspots.sort(key=lambda x: x['risk_score'], reverse=True)
    return hotspots

def generate_hotspot_report(hotspots):
    """Generate technical debt entries for hotspots."""
    print("# Code Hotspots Requiring Attention\n")
    
    for idx, hotspot in enumerate(hotspots[:10], 1):
        print(f"## [{idx}] {hotspot['file']}")
        print(f"**Risk Score:** {hotspot['risk_score']:.1f}")
        print(f"**Complexity:** {hotspot['complexity']:.1f}")
        print(f"**Recent Changes:** {hotspot['changes']}")
        print(f"\n**Recommended Action:** Refactor to reduce complexity and improve testability\n")

if __name__ == "__main__":
    hotspots = identify_hotspots()
    generate_hotspot_report(hotspots)
```

**Verification:**
- [ ] Hotspot analysis completed
- [ ] Top 10 high-risk files identified
- [ ] Change frequency data collected
- [ ] Patterns in bug-prone areas documented

**If This Fails:**
→ If git history too large: Limit analysis to `--since="3 months ago"`
→ If radon errors: Install with `pip install radon`
→ If false positives: Adjust risk score thresholds based on your codebase

---

### Step 4: Review Architecture and Design Patterns

**What:** Identify architectural debt through manual review of design patterns, dependencies, and structure.

**How:** Systematically review key architectural decisions and identify areas that violate best practices.

**Code/Commands:**
```python
# scripts/analyze_architecture.py
"""Identify architectural debt through dependency analysis."""

import ast
from pathlib import Path
from collections import defaultdict
import networkx as nx

def analyze_imports(file_path):
    """Extract import statements from a Python file."""
    with open(file_path) as f:
        tree = ast.parse(f.read())
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    return imports

def build_dependency_graph(src_dir='src'):
    """Build directed graph of module dependencies."""
    graph = nx.DiGraph()
    
    for py_file in Path(src_dir).rglob('*.py'):
        module = str(py_file.relative_to(src_dir)).replace('/', '.').replace('.py', '')
        imports = analyze_imports(py_file)
        
        for imp in imports:
            if imp.startswith('src.'):  # Internal imports only
                graph.add_edge(module, imp)
    
    return graph

def detect_circular_dependencies(graph):
    """Find circular dependencies in the codebase."""
    try:
        cycles = list(nx.simple_cycles(graph))
        return cycles
    except:
        return []

def detect_god_modules(graph, threshold=20):
    """Find modules with too many dependencies."""
    god_modules = []
    
    for node in graph.nodes():
        in_degree = graph.in_degree(node)  # How many depend on this
        out_degree = graph.out_degree(node)  # How many this depends on
        
        if in_degree > threshold or out_degree > threshold:
            god_modules.append({
                'module': node,
                'dependents': in_degree,
                'dependencies': out_degree
            })
    
    return god_modules

def generate_architecture_report():
    """Generate report of architectural debt."""
    graph = build_dependency_graph()
    cycles = detect_circular_dependencies(graph)
    god_modules = detect_god_modules(graph)
    
    print("# Architectural Debt Report\n")
    
    if cycles:
        print("## ⚠️ Circular Dependencies\n")
        for idx, cycle in enumerate(cycles, 1):
            print(f"{idx}. {' → '.join(cycle)}")
        print()
    
    if god_modules:
        print("## ⚠️ God Modules (High Coupling)\n")
        for mod in god_modules:
            print(f"- `{mod['module']}`")
            print(f"  - {mod['dependents']} modules depend on this")
            print(f"  - Depends on {mod['dependencies']} other modules")
        print()

if __name__ == "__main__":
    generate_architecture_report()
```

**Manual Review Checklist:**
```markdown
# Architectural Debt Review

## Layering & Separation of Concerns
- [ ] Clear separation between business logic and infrastructure
- [ ] No domain logic in controllers/views
- [ ] Database queries isolated in repository layer
- [ ] External API calls abstracted behind interfaces

## Dependency Management
- [ ] No circular dependencies between modules
- [ ] Dependencies flow from outer to inner layers
- [ ] Core business logic depends on abstractions, not implementations
- [ ] Test dependencies not leaking into production code

## Design Patterns
- [ ] Consistent error handling strategy
- [ ] Configuration management pattern in place
- [ ] Logging strategy consistently applied
- [ ] Authentication/authorization properly abstracted

## Code Organization
- [ ] Related functionality grouped together
- [ ] No "utils" dumping ground modules
- [ ] Clear module boundaries and responsibilities
- [ ] File/folder structure matches domain concepts
```

**Verification:**
- [ ] Dependency graph generated
- [ ] Circular dependencies identified (if any)
- [ ] God modules/classes documented
- [ ] Layering violations noted

**If This Fails:**
→ If dependency analysis slow: Use `--max-depth=3` to limit recursion
→ If too many false positives: Adjust thresholds for your codebase size
→ If unclear violations: Document examples and get team consensus

---

### Step 5: Assess Test Quality and Coverage

**What:** Identify testing debt by analyzing test coverage, quality, and effectiveness.

**How:** Review test suite comprehensiveness, identify gaps, and assess test maintainability.

**Code/Commands:**
```bash
# Generate detailed coverage report
pytest --cov=src --cov-report=html:reports/coverage \
       --cov-report=term-missing \
       --cov-report=json:reports/coverage.json

# Find uncovered critical paths
pytest --cov=src --cov-report=term-missing | grep "0%"

# Identify slow tests (performance debt)
pytest --durations=20 > reports/slow_tests.txt

# Check test isolation (look for test interdependencies)
pytest --random-order --random-order-seed=42

# Measure test code quality
ruff check tests/
mypy tests/ --strict
```

**Python script for test debt analysis:**
```python
# scripts/analyze_test_debt.py
import json
from pathlib import Path

def analyze_coverage(coverage_file='reports/coverage.json'):
    """Identify modules with insufficient coverage."""
    with open(coverage_file) as f:
        data = json.load(f)
    
    low_coverage = []
    for file, metrics in data['files'].items():
        coverage = metrics['summary']['percent_covered']
        if coverage < 80 and 'test' not in file:
            low_coverage.append({
                'file': file,
                'coverage': coverage,
                'missing_lines': metrics['summary']['num_statements'] - 
                                metrics['summary']['covered_lines']
            })
    
    # Sort by missing lines (impact)
    low_coverage.sort(key=lambda x: x['missing_lines'], reverse=True)
    return low_coverage

def identify_untested_modules(src_dir='src', test_dir='tests'):
    """Find source files with no corresponding test file."""
    src_files = set(Path(src_dir).rglob('*.py'))
    test_files = set(Path(test_dir).rglob('test_*.py'))
    
    # Map test files to source files
    tested_modules = set()
    for test_file in test_files:
        # Assume test_module.py tests module.py
        module_name = test_file.name.replace('test_', '')
        tested_modules.add(module_name)
    
    untested = []
    for src_file in src_files:
        if src_file.name not in tested_modules and '__init__' not in src_file.name:
            untested.append(str(src_file))
    
    return untested

def generate_test_debt_report():
    """Generate comprehensive test debt report."""
    print("# Test Debt Analysis\n")
    
    # Coverage gaps
    low_coverage = analyze_coverage()
    if low_coverage:
        print("## Low Coverage Modules\n")
        for item in low_coverage[:10]:
            print(f"- `{item['file']}` - {item['coverage']:.1f}% coverage, "
                  f"{item['missing_lines']} lines uncovered")
        print()
    
    # Untested modules
    untested = identify_untested_modules()
    if untested:
        print("## Modules Without Tests\n")
        for module in untested[:15]:
            print(f"- `{module}`")
        print()
    
    # Test quality issues
    print("## Test Quality Issues\n")
    print("- [ ] Review slow tests (>1s) for optimization opportunities")
    print("- [ ] Check for test interdependencies causing flakiness")
    print("- [ ] Identify tests that mock too much (unit vs integration balance)")
    print("- [ ] Look for assertion-free tests (just checking for no exceptions)")

if __name__ == "__main__":
    generate_test_debt_report()
```

**Verification:**
- [ ] Coverage report generated and reviewed
- [ ] Critical uncovered paths identified
- [ ] Modules without any tests documented
- [ ] Slow tests identified (>1 second)
- [ ] Test quality issues noted

**If This Fails:**
→ If coverage too low to be useful: Focus on new code and critical paths first
→ If tests too slow: Identify database/network calls that should be mocked
→ If flaky tests: Run with `--lf` (last failed) to reproduce issues

---

### Step 6: Document Technical Debt Items

**What:** Convert findings from analysis into actionable technical debt items with clear metadata.

**How:** Use consistent format to document each debt item with impact, effort, and prioritization data.

**Code/Commands:**
```markdown
# Template for Technical Debt Item

## [TD-XXX] [Concise Title]

**Category:** [Testing | Architecture | Security | Performance | Documentation | Dependencies]  
**Severity:** [CRITICAL | HIGH | MEDIUM | LOW]  
**Effort:** [Hours/Days estimate]  
**Impact:** [Qualitative description of consequences]  
**Identified:** [YYYY-MM-DD]  
**Owner:** [@team or @person]  
**Related Code:** [File paths or module names]

### Description
[2-3 sentences explaining what the debt is and how it arose]

### Current Consequences
- [Specific impact 1 - e.g., "3 production bugs in last month"]
- [Specific impact 2 - e.g., "Deployment time increased 40%"]
- [Specific impact 3 - e.g., "Developer onboarding takes 2 extra days"]

### Proposed Solution
[Specific steps or approach to resolve the debt]

### Alternatives Considered
- [Alternative 1 and why not chosen]
- [Alternative 2 and why not chosen]

### Acceptance Criteria
- [ ] [Specific measurable outcome 1]
- [ ] [Specific measurable outcome 2]
- [ ] [Specific measurable outcome 3]

### Priority Justification
[Explain why this priority level is appropriate based on risk and cost]

### Related Items
- Blocks: [TD-XXX]
- Related to: [TD-XXX, TD-XXX]
```

**Example - Real Technical Debt Item:**
```markdown
## [TD-042] Missing Type Annotations in Core Business Logic

**Category:** Code Quality  
**Severity:** HIGH  
**Effort:** 3 days  
**Impact:** Reduced IDE assistance, runtime errors not caught at development time  
**Identified:** 2025-10-25  
**Owner:** @backend-team  
**Related Code:** `src/core/business_logic.py`, `src/core/models.py`, `src/core/validators.py`

### Description
Core business logic modules (15,000+ lines) have no type annotations. This was
initially built before team adopted type checking, and hasn't been retrofitted.

### Current Consequences
- 8 AttributeError bugs in production last quarter that types would have caught
- New developers struggle with unclear function contracts
- Refactoring is risky without type safety
- mypy excluded from these modules, creating blind spots

### Proposed Solution
1. Add type annotations incrementally, starting with public APIs
2. Enable mypy strict mode for these modules
3. Add py.typed marker to package
4. Document complex types in separate types.py module

### Alternatives Considered
- Stubs (.pyi files): Decided against - prefer inline annotations for maintainability
- Skip annotations: Unacceptable - debt is actively causing bugs

### Acceptance Criteria
- [ ] 100% of public functions have type annotations
- [ ] 80%+ of internal functions have type annotations
- [ ] mypy --strict passes with no errors
- [ ] No type: ignore comments without explanatory notes
- [ ] CI pipeline includes type checking

### Priority Justification
HIGH because actively causing production bugs and impeding refactoring efforts.
Cost of fixing will only increase as codebase grows.

### Related Items
- Blocks: TD-043 (Refactor payment module - needs types first)
- Related to: TD-015 (Adopt mypy in CI pipeline)
```

**Verification:**
- [ ] Each debt item has unique ID
- [ ] Category and severity assigned consistently
- [ ] Effort estimates include team's input
- [ ] Impact quantified where possible (not just "bad")
- [ ] Proposed solutions are specific and actionable

**If This Fails:**
→ If effort estimates vary wildly: Do relative sizing (t-shirt sizes) first
→ If severity unclear: Use impact × likelihood matrix
→ If too many items: Start with top 20 by severity/effort ratio

---

### Step 7: Prioritize and Create Remediation Plan

**What:** Rank technical debt items by ROI (impact/effort) and create a realistic remediation plan.

**How:** Use quantitative scoring to prioritize and balance debt work with feature development.

**Code/Commands:**
```python
# scripts/prioritize_debt.py
"""Calculate technical debt priority scores."""

from dataclasses import dataclass
from typing import List
import pandas as pd

@dataclass
class DebtItem:
    id: str
    title: str
    category: str
    severity: str
    effort_days: float
    impact_score: int  # 1-10
    risk_score: int  # 1-10
    
    def priority_score(self) -> float:
        """Calculate priority score (higher = more urgent)."""
        # Severity weight
        severity_weight = {
            'CRITICAL': 4.0,
            'HIGH': 3.0,
            'MEDIUM': 2.0,
            'LOW': 1.0
        }[self.severity]
        
        # ROI calculation: (impact + risk) / effort
        roi = (self.impact_score + self.risk_score) / max(self.effort_days, 0.5)
        
        return severity_weight * roi

# Example debt items
debt_items = [
    DebtItem('TD-001', 'Missing payment tests', 'Testing', 'HIGH', 3, 9, 8),
    DebtItem('TD-002', 'Deprecated API version', 'Dependencies', 'MEDIUM', 1, 6, 4),
    DebtItem('TD-003', 'Circular dependencies', 'Architecture', 'CRITICAL', 5, 8, 9),
    DebtItem('TD-004', 'No API rate limiting', 'Security', 'HIGH', 2, 7, 8),
    # ... add all your debt items
]

# Calculate priorities
for item in debt_items:
    item.priority = item.priority_score()

# Sort by priority
debt_items.sort(key=lambda x: x.priority, reverse=True)

# Generate prioritized report
print("# Technical Debt Prioritization\n")
print("## Top Priority Items (Recommended Order)\n")

for idx, item in enumerate(debt_items[:10], 1):
    print(f"{idx}. **{item.id}** - {item.title}")
    print(f"   - Category: {item.category} | Severity: {item.severity}")
    print(f"   - Effort: {item.effort_days} days | Priority Score: {item.priority:.2f}")
    print(f"   - Impact: {item.impact_score}/10 | Risk: {item.risk_score}/10")
    print()
```

**Create Remediation Roadmap:**
```markdown
# Technical Debt Remediation Roadmap

## Sprint 1 (Next 2 weeks)
**Theme:** Critical Security & Stability

1. [TD-004] Implement API rate limiting (2 days)
2. [TD-001] Add payment module tests (3 days)
3. [TD-012] Fix authentication vulnerabilities (2 days)

**Expected Impact:** Reduce security risk by 60%, prevent payment bugs

---

## Sprint 2 (Weeks 3-4)
**Theme:** Architecture Improvements

1. [TD-003] Resolve circular dependencies (5 days)
2. [TD-018] Extract god class into services (3 days)

**Expected Impact:** Improve maintainability, enable parallel development

---

## Sprint 3 (Weeks 5-6)
**Theme:** Code Quality Foundation

1. [TD-042] Add type annotations to core modules (3 days)
2. [TD-025] Refactor duplicate authentication logic (2 days)
3. [TD-031] Document API contracts (2 days)

**Expected Impact:** Catch bugs earlier, improve developer experience

---

## Ongoing (Weekly allocation)
- Reserve 20% of sprint capacity for debt reduction
- Refactor code touched during feature work (Boy Scout Rule)
- Pay down one small debt item per sprint
```

**Verification:**
- [ ] All debt items have priority scores
- [ ] Top 10 items align with team consensus
- [ ] Remediation plan has realistic timelines
- [ ] Balance of quick wins and strategic improvements
- [ ] Dependencies between items identified

**If This Fails:**
→ If team disagrees with priorities: Run prioritization workshop together
→ If effort estimates too uncertain: Do spike investigations for top items
→ If can't allocate time: Start with 10% of sprint capacity, demonstrate value

---

### Step 8: Establish Monitoring and Prevention

**What:** Set up processes to track debt trends and prevent accumulation of new debt.

**How:** Implement metrics, quality gates, and team practices to maintain code health.

**Code/Commands:**
```bash
# Create pre-commit hook to prevent new debt
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to prevent common technical debt patterns

echo "Running technical debt checks..."

# Check for missing type annotations in new/modified Python files
MODIFIED_PY=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -n "$MODIFIED_PY" ]; then
    echo "Checking type annotations..."
    for file in $MODIFIED_PY; do
        # Count function definitions without type annotations
        untyped=$(grep -E '^\s*def \w+\([^)]*\)\s*:' "$file" | \
                  grep -v '-> ' | \
                  wc -l)
        
        if [ "$untyped" -gt 0 ]; then
            echo "⚠️  $file has $untyped functions without return type annotations"
            echo "   Consider adding type hints before committing"
        fi
    done
    
    # Run mypy on changed files
    echo "Running mypy on changed files..."
    mypy $MODIFIED_PY || {
        echo "❌ Type checking failed. Fix errors or use # type: ignore with justification"
        exit 1
    }
fi

# Check for TODO/FIXME comments that should be tracked
TODOS=$(git diff --cached | grep -E '^\+.*TODO|FIXME' | wc -l)
if [ "$TODOS" -gt 0 ]; then
    echo "⚠️  Found $TODOS new TODO/FIXME comments"
    echo "   Consider creating technical debt items instead"
fi

# Check complexity of new functions
echo "Checking code complexity..."
radon cc --min C $(echo $MODIFIED_PY) || {
    echo "⚠️  High complexity detected. Consider refactoring before committing"
}

echo "✅ Pre-commit checks complete"
EOF

chmod +x .git/hooks/pre-commit
```

**Configure CI/CD Quality Gates:**
```yaml
# .github/workflows/quality-gates.yml
name: Code Quality Gates

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install ruff mypy radon pytest pytest-cov
          pip install -r requirements.txt
      
      - name: Check code complexity
        run: |
          radon cc src/ --min C --show-complexity
          radon mi src/ --min B
      
      - name: Type checking
        run: mypy src/ --strict
      
      - name: Lint with Ruff
        run: ruff check src/
      
      - name: Test coverage
        run: |
          pytest --cov=src --cov-report=term-missing --cov-fail-under=80
      
      - name: Check for security issues
        run: pip-audit
      
      - name: Generate debt metrics
        run: |
          python scripts/aggregate_debt.py
          python scripts/debt_metrics.py --output metrics.json
      
      - name: Comment on PR with metrics
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const metrics = JSON.parse(fs.readFileSync('metrics.json'));
            
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## Code Quality Metrics\n\n` +
                    `- Coverage: ${metrics.coverage}%\n` +
                    `- Complexity: ${metrics.avg_complexity}\n` +
                    `- Type Coverage: ${metrics.type_coverage}%\n`
            });
```

**Team Process - Debt Review Meeting:**
```markdown
# Weekly Debt Review Meeting (15 minutes)

## Agenda:
1. Review debt metrics dashboard (5 min)
   - Trend in total debt count
   - Trend in debt by category
   - Items completed vs. added this week

2. Discuss new debt items (5 min)
   - Triage newly identified items
   - Assign categories and severity
   - Quick prioritization

3. Plan next actions (5 min)
   - Commit to debt items for next sprint
   - Identify quick wins
   - Assign owners

## Metrics to Track:
- Total active debt items
- Debt items by category (pie chart)
- Age distribution (histogram)
- Debt resolved per sprint (trend line)
- New debt added per sprint (trend line)
```

**Verification:**
- [ ] Quality gates configured in CI/CD
- [ ] Pre-commit hooks installed and functional
- [ ] Debt tracking integrated into sprint planning
- [ ] Team has visibility into debt metrics
- [ ] Process for triaging new debt established

**If This Fails:**
→ If hooks too strict: Make them warnings initially, gradually enforce
→ If team ignores metrics: Connect debt to actual bugs/incidents
→ If no time for debt work: Show cost of not addressing (outages, slowdowns)

---

## Verification Checklist

After completing this workflow:

- [ ] Technical debt tracking system is operational
- [ ] Automated analysis tools configured and running
- [ ] At least 20 debt items documented with metadata
- [ ] Debt items prioritized by ROI
- [ ] Remediation roadmap created for next 3 sprints
- [ ] Quality gates prevent new debt accumulation
- [ ] Team understands debt categories and severity levels
- [ ] Metrics dashboard shows baseline and trends

---

## Best Practices

### DO:
✅ **Quantify impact with data** - "3 prod bugs last month" beats "unstable"
✅ **Track debt age** - Old debt gets stale and harder to fix
✅ **Balance quick wins with strategic refactoring** - Show early progress
✅ **Make debt visible** - Display on team dashboard, discuss in standups
✅ **Link debt to business impact** - Connect to customer issues, velocity
✅ **Review debt during sprint planning** - Reserve capacity for cleanup
✅ **Use "Boy Scout Rule"** - Improve code you touch during feature work
✅ **Celebrate debt reduction** - Track and publicize improvements
✅ **Automate debt detection** - Don't rely on manual discovery

### DON'T:
❌ **Don't let perfect be the enemy of good** - Start with imperfect tracking
❌ **Don't prioritize solely by severity** - Consider effort and ROI
❌ **Don't create debt backlog and ignore it** - Review and update regularly
❌ **Don't treat all debt equally** - Some debt is acceptable/strategic
❌ **Don't stop feature work for debt** - Find sustainable balance
❌ **Don't blame individuals** - Focus on systemic improvements
❌ **Don't accumulate "TODO" comments** - Convert to tracked items
❌ **Don't skip prevention** - Quality gates are cheaper than remediation

---

## Common Issues & Solutions

### Issue: Too Many Debt Items, Team Overwhelmed

**Symptoms:**
- Hundreds of items in backlog
- Team doesn't know where to start
- Debt items never get addressed

**Solution:**
1. Create tiers: P0 (must fix), P1 (should fix), P2 (nice to fix)
2. Archive P2 items that are >6 months old
3. Focus on top 10-20 items only
4. Set quarterly debt reduction goals

**Prevention:**
Implement quality gates to prevent low-priority debt from accumulating.

---

### Issue: Disagreement on Severity/Priority

**Symptoms:**
- Arguments about what constitutes "high" severity
- Different team members prioritize differently
- Inconsistent categorization

**Solution:**
1. Create rubric with examples for each severity level
2. Run calibration session where team rates sample items together
3. Document reasoning for disputed items
4. Review and adjust rubric quarterly

**Prevention:**
Use objective criteria (impact × likelihood) and make prioritization transparent.

---

### Issue: Debt Never Gets Fixed

**Symptoms:**
- Debt backlog only grows
- No sprint capacity for cleanup
- Team demoralized by growing debt

**Solution:**
1. Reserve fixed percentage of sprint capacity (start with 10%)
2. Link debt to features ("can't build X without fixing Y")
3. Show cost of not fixing (outages, slow velocity)
4. Make debt fixes count toward velocity

**Prevention:**
Make debt work visible and celebrate improvements. Track debt reduction as a KPI.

---

### Issue: New Code Adds More Debt

**Symptoms:**
- Debt items increase faster than resolved
- Quality gates bypassed or ignored
- Team under pressure to deliver quickly

**Solution:**
1. Make quality gates mandatory (can't merge without passing)
2. Include debt impact in story estimation
3. Code review checklist includes debt prevention
4. Pair programming on complex features

**Prevention:**
Build quality into development process, not as afterthought. Make it easy to do the right thing.

---

## Related Workflows

**Prerequisites:**
- [Code Review Checklist](../quality-assurance/code_review_checklist.md) - Establish quality standards
- [Test Writing Best Practices](./test_writing.md) - Understand testing debt

**Next Steps:**
- [Technical Debt Management](./technical_debt_mgmt.md) - Execute remediation plans
- [Refactoring Strategy](./refactoring_strategy.md) - Safely reduce debt
- [PR Creation & Review](../quality-assurance/pr_creation_review.md) - Prevent new debt

**Related:**
- [Complexity Reduction](../quality-assurance/complexity_reduction.md) - Address complexity debt
- [Type Annotation Addition](./type_annotation_addition.md) - Fix missing types
- [Dependency Upgrade](./dependency_upgrade.md) - Manage dependency debt

---

## Tags
`development` `technical-debt` `code-quality` `refactoring` `maintenance` `metrics` `static-analysis`
