# Complexity Reduction

**ID:** qua-002  
**Category:** Quality Assurance  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 1-4 hours (per complex function)  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic approach to identifying and reducing code complexity through refactoring, simplification, and better design patterns, making code more maintainable and less error-prone.

**Why:** Complex code is harder to understand, test, and maintain. Studies show functions with cyclomatic complexity >10 have 2-3x more bugs than simpler functions. Code with complexity >20 is nearly impossible to test thoroughly. Reducing complexity improves code quality, reduces bugs, speeds up development, and makes onboarding easier.

**When to use:**
- Code review flags high complexity
- Function has cyclomatic complexity >10
- Code is difficult to test
- Bugs keep appearing in same area
- New developers struggle with code
- Before major refactoring
- Performance optimization needed

---

## Prerequisites

**Required:**
- [ ] Access to codebase
- [ ] Complexity analysis tools (radon, flake8-complexity)
- [ ] Test suite for affected code
- [ ] Understanding of refactoring patterns

**Check before starting:**
```bash
# Install complexity tools
pip install radon flake8-mccabe

# Check complexity of codebase
radon cc src/ -a -s

# Find complex functions (>10)
radon cc src/ -n B

# Example output:
# src/processor.py
#   M 45:4 process_data - C (15)
#   M 89:4 validate_input - D (22)
```

---

## Implementation Steps

### Step 1: Measure and Identify Complex Code

**What:** Use tools to identify functions with high cyclomatic complexity.

**How:**

**Run complexity analysis:**
```bash
# Radon complexity check
radon cc src/ -a -s

# Output example:
# src/app.py
#   C 23:0 MainClass - A (3)
#   M 45:4 process_data - C (12)
#   M 67:4 complex_function - D (18)
#   M 89:4 monster_function - F (35)
# Average complexity: A (5.2)

# Complexity grades:
# A: 1-5   (simple)
# B: 6-10  (acceptable)
# C: 11-20 (high - consider refactoring)
# D: 21-30 (very high - should refactor)
# E: 31-40 (extreme - must refactor)
# F: 41+   (unmaintainable)
```

**Find specific complex functions:**
```bash
# Show only functions with complexity >10
radon cc src/ -n C

# Show functions >20
radon cc src/ -n D

# Sort by complexity
radon cc src/ -s -n B | sort -t '(' -k2 -n

# Generate JSON report
radon cc src/ -j > complexity-report.json
```

**Calculate cognitive complexity:**
```bash
# Cognitive complexity measures understandability
# Often more useful than cyclomatic complexity

# With flake8
flake8 --max-complexity=10 src/

# Example output:
# src/processor.py:45:1: C901 'process_data' is too complex (15)
```

**Visualize complexity:**
```python
# complexity_report.py
import json
import matplotlib.pyplot as plt

with open('complexity-report.json') as f:
    data = json.load(f)

complexities = []
names = []

for module in data.values():
    for item in module:
        if item['type'] == 'method':
            complexities.append(item['complexity'])
            names.append(item['name'])

# Plot
plt.figure(figsize=(12, 6))
plt.bar(range(len(complexities)), sorted(complexities, reverse=True))
plt.axhline(y=10, color='r', linestyle='--', label='Threshold (10)')
plt.ylabel('Complexity')
plt.title('Function Complexity')
plt.legend()
plt.savefig('complexity-chart.png')
```

**Verification:**
- [ ] Complexity analysis complete
- [ ] Complex functions identified (>10)
- [ ] Critical complex code noted (>20)
- [ ] Report generated

**If This Fails:**
→ If tools not installed: `pip install radon`
→ If no complex code found: Great! No action needed
→ If everything is complex: Start with highest complexity first

---

### Step 2: Understand Why Code Is Complex

**What:** Analyze complex functions to understand root causes before refactoring.

**How:**

**Common causes of complexity:**

**1. Deep nesting (if/for/while):**
```python
# Example: Complexity from nesting
def process_user(user_data):
    if user_data:
        if 'email' in user_data:
            if validate_email(user_data['email']):
                if user_data.get('age'):
                    if user_data['age'] >= 18:
                        if user_data.get('country') == 'US':
                            return create_us_adult_user(user_data)
    return None
# Complexity: ~7 just from nesting
```

**2. Long functions (>50 lines):**
```python
def process_order(order_data):
    # 150 lines of code doing:
    # - Validation
    # - Price calculation
    # - Discount application
    # - Tax calculation
    # - Inventory check
    # - Payment processing
    # - Email notification
    # - Logging
    pass
# Each responsibility adds complexity
```

**3. Multiple responsibilities:**
```python
def process_and_save_and_notify(data):
    # Validates data
    # Transforms data
    # Saves to database
    # Sends email
    # Updates cache
    # Logs activity
    pass
# Violates Single Responsibility Principle
```

**4. Complex conditionals:**
```python
if (user.is_premium and user.age > 25 and 
    user.country in ['US', 'CA', 'UK'] and
    not user.is_banned and user.email_verified and
    user.account_age > 365 and user.orders_count > 10):
    # ...
# Many conditions = high complexity
```

**5. Error handling:**
```python
def process():
    try:
        result = step1()
    except Error1:
        try:
            result = fallback1()
        except Error2:
            try:
                result = fallback2()
            except Error3:
                return None
# Nested error handling adds complexity
```

**Analyze specific function:**
```python
# Read the function carefully
# Ask:
# 1. What does it do? (should be one thing)
# 2. How many decision points? (if/for/while)
# 3. Can it be split into smaller functions?
# 4. Are there repeated patterns?
# 5. Is the logic clear or confusing?

# Example analysis:
def validate_and_process_payment(order):
    # Decision points:
    # - if order is None: +1
    # - if not order.items: +1
    # - for item in order.items: +1
    #   - if item.price < 0: +1
    # - if order.total > limit: +1
    # - if payment fails: +1
    #   - for retry in retries: +1
    #     - if retry succeeds: +1
    # Total: 8 decision points
    # Complexity: ~9
    pass
```

**Verification:**
- [ ] Root causes identified
- [ ] Nesting depth noted
- [ ] Multiple responsibilities found
- [ ] Refactoring approach clear

**If This Fails:**
→ If cause unclear, discuss with code author
→ If too complex to analyze, break into smaller parts
→ If multiple causes, address most impactful first

---

### Step 3: Apply Refactoring Patterns

**What:** Use proven refactoring techniques to reduce complexity.

**How:**

**Pattern 1: Extract Method**
```python
# Before: One big function (complexity: 15)
def process_order(order_data):
    # Validate
    if not order_data:
        return None
    if 'items' not in order_data:
        return None
    if not order_data['items']:
        return None
    
    # Calculate total
    total = 0
    for item in order_data['items']:
        if item.get('price'):
            total += item['price'] * item.get('quantity', 1)
    
    # Apply discount
    if order_data.get('discount_code'):
        discount = get_discount(order_data['discount_code'])
        if discount:
            total = total * (1 - discount.percentage / 100)
    
    # Calculate tax
    tax_rate = get_tax_rate(order_data.get('state'))
    total = total * (1 + tax_rate)
    
    return total

# After: Extracted methods (complexity: 3, 2, 2, 2)
def process_order(order_data: Dict) -> Optional[Decimal]:
    if not is_valid_order(order_data):
        return None
    
    subtotal = calculate_subtotal(order_data['items'])
    total = apply_discount(subtotal, order_data.get('discount_code'))
    total = add_tax(total, order_data.get('state'))
    
    return total

def is_valid_order(order_data: Dict) -> bool:
    return (order_data and 
            'items' in order_data and 
            order_data['items'])

def calculate_subtotal(items: List[Dict]) -> Decimal:
    return sum(
        item['price'] * item.get('quantity', 1)
        for item in items
        if item.get('price')
    )

def apply_discount(total: Decimal, code: Optional[str]) -> Decimal:
    if code:
        discount = get_discount(code)
        if discount:
            return total * (1 - discount.percentage / 100)
    return total

def add_tax(total: Decimal, state: Optional[str]) -> Decimal:
    tax_rate = get_tax_rate(state)
    return total * (1 + tax_rate)
```

**Pattern 2: Replace Nested Conditionals with Guard Clauses**
```python
# Before: Deep nesting (complexity: 7)
def process_user(user_data):
    if user_data:
        if 'email' in user_data:
            if validate_email(user_data['email']):
                if user_data.get('age'):
                    if user_data['age'] >= 18:
                        if user_data.get('country') == 'US':
                            return create_us_adult_user(user_data)
    return None

# After: Guard clauses (complexity: 3)
def process_user(user_data: Dict) -> Optional[User]:
    if not user_data:
        return None
    if 'email' not in user_data:
        return None
    if not validate_email(user_data['email']):
        return None
    if not user_data.get('age') or user_data['age'] < 18:
        return None
    if user_data.get('country') != 'US':
        return None
    
    return create_us_adult_user(user_data)
```

**Pattern 3: Replace Complex Conditionals with Strategy Pattern**
```python
# Before: Complex conditional (complexity: 8)
def calculate_shipping(order, method):
    if method == 'standard':
        if order.total < 50:
            return 5.99
        else:
            return 0
    elif method == 'express':
        if order.weight < 5:
            return 12.99
        else:
            return 19.99
    elif method == 'overnight':
        if order.distance < 100:
            return 29.99
        else:
            return 49.99

# After: Strategy pattern (complexity: 1 each)
from abc import ABC, abstractmethod

class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, order: Order) -> Decimal:
        pass

class StandardShipping(ShippingStrategy):
    def calculate(self, order: Order) -> Decimal:
        return Decimal('0') if order.total >= 50 else Decimal('5.99')

class ExpressShipping(ShippingStrategy):
    def calculate(self, order: Order) -> Decimal:
        return Decimal('12.99') if order.weight < 5 else Decimal('19.99')

class OvernightShipping(ShippingStrategy):
    def calculate(self, order: Order) -> Decimal:
        return Decimal('29.99') if order.distance < 100 else Decimal('49.99')

SHIPPING_STRATEGIES = {
    'standard': StandardShipping(),
    'express': ExpressShipping(),
    'overnight': OvernightShipping(),
}

def calculate_shipping(order: Order, method: str) -> Decimal:
    strategy = SHIPPING_STRATEGIES.get(method)
    if not strategy:
        raise ValueError(f"Unknown shipping method: {method}")
    return strategy.calculate(order)
```

**Pattern 4: Extract Complex Loops**
```python
# Before: Complex loop (complexity: 6)
def process_items(items):
    results = []
    for item in items:
        if item.is_valid():
            if item.price > 0:
                if item.in_stock:
                    processed = transform(item)
                    results.append(processed)
    return results

# After: Simplified (complexity: 2, 2)
def process_items(items: List[Item]) -> List[ProcessedItem]:
    valid_items = filter_valid_items(items)
    return [transform(item) for item in valid_items]

def filter_valid_items(items: List[Item]) -> List[Item]:
    return [
        item for item in items
        if item.is_valid() and item.price > 0 and item.in_stock
    ]
```

**Pattern 5: Decompose Complex Class**
```python
# Before: God class (complexity distributed across many methods)
class OrderProcessor:
    def validate_order(self): pass  # Complex
    def calculate_total(self): pass  # Complex
    def process_payment(self): pass  # Complex
    def send_confirmation(self): pass  # Complex
    def update_inventory(self): pass  # Complex

# After: Separate responsibilities
class OrderValidator:
    def validate(self, order: Order) -> bool:
        pass  # Simple validation

class PriceCalculator:
    def calculate_total(self, order: Order) -> Decimal:
        pass  # Simple calculation

class PaymentProcessor:
    def process(self, order: Order) -> PaymentResult:
        pass  # Simple payment

class NotificationService:
    def send_confirmation(self, order: Order) -> None:
        pass  # Simple notification

class InventoryManager:
    def update(self, order: Order) -> None:
        pass  # Simple update
```

**Verification:**
- [ ] Functions extracted
- [ ] Nesting reduced
- [ ] Conditionals simplified
- [ ] Responsibilities separated
- [ ] Complexity reduced

**If This Fails:**
→ If refactoring breaks tests, fix incrementally
→ If unsure about pattern, start with extract method
→ If too risky, create new code alongside old

---

### Step 4: Verify Improvements

**What:** Ensure refactoring reduced complexity without breaking functionality.

**How:**

**Measure new complexity:**
```bash
# Run radon again
radon cc src/app.py

# Before:
# M 45:4 process_order - D (18)

# After:
# M 45:4 process_order - A (3)
# M 67:4 calculate_subtotal - A (2)
# M 78:4 apply_discount - A (2)
# M 89:4 add_tax - A (1)
#
# Total: 8 (vs 18) ✅
```

**Run tests:**
```bash
# Ensure refactoring didn't break anything
pytest tests/test_order.py -v

# All tests should pass
# If not, fix or revert

# Add new tests for extracted functions
pytest tests/test_order.py::test_calculate_subtotal
pytest tests/test_order.py::test_apply_discount
```

**Check code coverage:**
```bash
# Coverage should be same or better
pytest --cov=src.order --cov-report=term

# Before: 85%
# After: 92% (easier to test simple functions)
```

**Performance check:**
```python
# Verify no performance regression
import timeit

# Before refactoring: 0.05s
# After refactoring: 0.05s (same) ✅

# If slower, profile and optimize
```

**Code review:**
```markdown
Review refactored code:
- [ ] More readable?
- [ ] Easier to understand?
- [ ] Simpler to test?
- [ ] Functions have single responsibility?
- [ ] Names are clear?
- [ ] Complexity reduced?
```

**Verification:**
- [ ] Complexity reduced by 50%+
- [ ] All tests pass
- [ ] Coverage maintained/improved
- [ ] No performance regression
- [ ] Code more readable

**If This Fails:**
→ If tests fail, fix refactored code
→ If complexity not reduced enough, apply more patterns
→ If performance worse, profile and optimize

---

### Step 5: Prevent Future Complexity

**What:** Establish guardrails to prevent complexity from creeping back.

**How:**

**Add complexity checks to CI:**
```yaml
# .github/workflows/complexity.yml

name: Complexity Check

on: [pull_request]

jobs:
  radon:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      
      - name: Install radon
        run: pip install radon
      
      - name: Check complexity
        run: |
          radon cc src/ -n C --total-average
          # Fails if any function >10 complexity
```

**Configure flake8:**
```ini
# .flake8 or setup.cfg

[flake8]
max-complexity = 10
# Fail build if complexity >10
```

**Pre-commit hook:**
```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/PyCQA/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-complexity=10]
```

**Code review checklist:**
```markdown
## Complexity Review

- [ ] Functions < 20 lines
- [ ] Cyclomatic complexity < 10
- [ ] Max nesting depth: 3
- [ ] Single responsibility per function
- [ ] Clear function names
- [ ] No "god" functions
```

**Team guidelines:**
```markdown
# Complexity Guidelines

## Maximum Limits:
- Function length: 20 lines (50 max)
- Cyclomatic complexity: 5 (10 max)
- Nesting depth: 3 levels
- Parameters: 4 (6 max)

## When Function Gets Complex:
1. Extract smaller functions
2. Use guard clauses
3. Apply design patterns
4. Get code review

## Red Flags:
- "and" in function name
- Need to scroll to see whole function
- Can't understand function in 30 seconds
```

**Verification:**
- [ ] CI checks complexity
- [ ] Pre-commit hook configured
- [ ] Code review includes complexity
- [ ] Team trained on limits

**If This Fails:**
→ If CI too strict, adjust thresholds
→ If team resists, show examples of bugs in complex code
→ If limits unclear, start with high limits and decrease

---

## Verification Checklist

- [ ] Complex code identified
- [ ] Root causes understood
- [ ] Refactoring patterns applied
- [ ] Complexity reduced 50%+
- [ ] Tests pass
- [ ] Prevention measures in place
- [ ] Team aware of limits

---

## Common Issues & Solutions

### Issue: Tests Break After Refactoring

**Symptoms:**
- Reduced complexity
- Tests fail
- Behavior changed

**Solution:**
```python
# Always refactor incrementally

# Step 1: Extract method
def process_order(order):
    # ... old code ...
    pass

def calculate_subtotal(items):  # New extracted method
    return sum(i['price'] for i in items)

# Step 2: Test extracted method
def test_calculate_subtotal():
    assert calculate_subtotal([{'price': 10}]) == 10

# Step 3: Replace in original
def process_order(order):
    subtotal = calculate_subtotal(order['items'])  # Use new method
    # ... rest of code ...

# Step 4: Test still passes? Good, continue
```

**Prevention:**
- Refactor one pattern at a time
- Test after each change
- Keep commits small

---

### Issue: Complexity Still High After Refactoring

**Symptoms:**
- Applied patterns
- Complexity reduced but still >10
- Not clear what else to do

**Solution:**
```python
# Look for:
# 1. Multiple responsibilities
# 2. Hidden complexity in extracted functions
# 3. Business logic that's genuinely complex

# If genuinely complex, document it
def complex_tax_calculation(order):
    """
    Calculate tax based on state, local, and special rules.
    
    Complexity is inherent to tax code requirements.
    Cannot simplify further without losing correctness.
    """
    # ... complex but necessary logic ...
    pass
```

---

## Examples

### Example 1: Reducing Nested Conditionals

**Context:** Function with complexity 15 from nesting

**Before:**
```python
def process_payment(order):
    if order:
        if order.total > 0:
            if order.user:
                if order.user.payment_method:
                    if not order.user.is_blocked:
                        return charge_payment(order)
    return None
```

**After:**
```python
def process_payment(order: Order) -> Optional[PaymentResult]:
    if not order or order.total <= 0:
        return None
    if not order.user or not order.user.payment_method:
        return None
    if order.user.is_blocked:
        return None
    
    return charge_payment(order)
```

**Result:** Complexity reduced from 15 to 4

---

### Example 2: Extracting Methods

**Context:** 150-line function with complexity 25

**Before:**
```python
def process_order(order_data):
    # 150 lines doing everything
    pass  # Complexity: 25
```

**After:**
```python
def process_order(order_data):
    validate_order(order_data)  # Complexity: 3
    total = calculate_total(order_data)  # Complexity: 4
    process_payment(total, order_data)  # Complexity: 5
    send_notification(order_data)  # Complexity: 2
    # Complexity: 3
```

**Result:** One complex function → 5 simple functions

---

## Best Practices

### DO:
✅ **Measure before refactoring** - Know the baseline
✅ **Refactor incrementally** - Small steps
✅ **Test after each change** - Catch breaks early
✅ **Extract methods liberally** - Small functions are good
✅ **Use guard clauses** - Reduce nesting
✅ **Apply design patterns** - Strategy, factory, etc.
✅ **Set complexity limits** - Enforce in CI
✅ **Review for simplicity** - Part of code review

### DON'T:
❌ **Refactor without tests** - Too risky
❌ **Optimize too early** - Focus on clarity first
❌ **Make it worse** - Verify improvements
❌ **Ignore root cause** - Understand why it's complex
❌ **Over-engineer** - Don't add unnecessary abstractions
❌ **Rush it** - Take time to do it right
❌ **Forget to document** - Explain complex logic
❌ **Let complexity creep back** - Maintain limits

---

## Related Workflows

**Prerequisites:**
- [Refactoring Strategy](../development/refactoring_strategy.md)
- [Test Writing](../development/test_writing.md)

**Next Steps:**
- [Code Review Checklist](./code_review_checklist.md)
- [Quality Gate Execution](./quality_gate_execution.md)

**Related:**
- [Technical Debt Management](../development/technical_debt_mgmt.md)

---

## Tags
`quality-assurance` `refactoring` `complexity` `code-quality` `maintainability` `best-practices`
