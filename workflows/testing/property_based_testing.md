# Property Based Testing

**ID:** tes-002  
**Category:** Testing  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 45-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Implement property-based testing to validate code behavior across a wide range of inputs

**Why:** Property-based testing catches edge cases that example-based tests miss by automatically generating hundreds of test cases, finding bugs that would take weeks to discover manually

**When to use:**
- Testing functions with multiple input combinations
- Validating data transformations and invariants
- Ensuring algorithm correctness across edge cases
- Testing parsers, serializers, and codecs
- Validating API contracts and data models
- When refactoring critical business logic

---

## Prerequisites

**Required:**
- [ ] Testing framework installed (pytest, unittest, etc.)
- [ ] Property-based testing library (Hypothesis for Python, fast-check for JS, QuickCheck for Haskell)
- [ ] Understanding of function properties and invariants
- [ ] Code to test with clear input/output specifications

**Check before starting:**
```bash
# Python with Hypothesis
pip show hypothesis

# JavaScript with fast-check
npm list fast-check

# Verify test runner works
pytest --version
# or
npm test -- --version
```

---

## Implementation Steps

### Step 1: Identify Properties and Invariants

**What:** Define the mathematical or logical properties that should always hold true

**How:**
Think about what should ALWAYS be true regardless of input:
- **Invariants:** Properties that never change (e.g., sort output is always sorted)
- **Symmetry:** Reversible operations (encode/decode, serialize/deserialize)
- **Idempotence:** Running operation twice gives same result as once
- **Commutativity:** Order doesn't matter (a + b = b + a)
- **Composition:** Combining operations (sort(sort(x)) = sort(x))

**Common Properties:**
```python
# Invariant property
"sorted list always has same length as input"
"JSON decode(encode(x)) always equals x"

# Relationship property  
"filter then map = map then filter (for independent operations)"
"processing all items = sum of processing each item"

# Error conditions
"invalid input always raises specific exception"
"function never returns null for valid input"
```

**Verification:**
- [ ] Listed all properties that should hold
- [ ] Properties are specific and testable
- [ ] Properties cover success and error cases
- [ ] Properties don't just restate implementation

**If This Fails:**
→ Start simple: "output is valid JSON", "result is non-negative"
→ Look at existing example tests for patterns
→ Ask: "What would make this function wrong?"

---

### Step 2: Set Up Property-Based Testing Framework

**What:** Install and configure the testing library

**How:**

**For Python (Hypothesis):**
```bash
pip install hypothesis
```

**For JavaScript (fast-check):**
```bash
npm install --save-dev fast-check
```

**For Java (jqwik):**
```xml
<dependency>
    <groupId>net.jqwik</groupId>
    <artifactId>jqwik</artifactId>
    <version>1.7.4</version>
    <scope>test</scope>
</dependency>
```

**Basic Setup:**
```python
# Python - test_my_module.py
from hypothesis import given, strategies as st
import pytest

# JavaScript - my_module.test.js
import fc from 'fast-check';
import { describe, it, expect } from '@jest/globals';
```

**Verification:**
- [ ] Library installed successfully
- [ ] Can import in test files
- [ ] Example test runs
- [ ] IDE shows autocomplete for strategies

**If This Fails:**
→ Check Python/Node version compatibility
→ Clear pip/npm cache and reinstall
→ Use virtual environment for Python

---

### Step 3: Write Property-Based Tests

**What:** Create tests that verify properties across generated inputs

**How:**

**Structure:**
1. Define input strategy (how to generate test data)
2. Write property assertion (what should be true)
3. Let framework generate test cases
4. Handle edge cases and constraints

**Python Example (Hypothesis):**
```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_invariants(numbers):
    """Sorting should preserve length and maintain order"""
    result = sorted(numbers)
    
    # Property 1: Length is preserved
    assert len(result) == len(numbers)
    
    # Property 2: Output is sorted
    assert all(result[i] <= result[i+1] for i in range(len(result)-1))
    
    # Property 3: Contains same elements
    assert sorted(result) == sorted(numbers)

@given(st.text(), st.text())
def test_string_concatenation_associative(a, b):
    """String concatenation is associative"""
    c = "test"
    assert (a + b) + c == a + (b + c)

@given(st.dictionaries(st.text(), st.integers()))
def test_json_roundtrip(data):
    """JSON encode/decode is identity function"""
    import json
    encoded = json.dumps(data)
    decoded = json.loads(encoded)
    assert decoded == data
```

**JavaScript Example (fast-check):**
```javascript
import fc from 'fast-check';

describe('Array operations', () => {
  it('reverse is involutive', () => {
    fc.assert(
      fc.property(fc.array(fc.integer()), (arr) => {
        const reversed = arr.reverse();
        const doubleReversed = reversed.reverse();
        expect(doubleReversed).toEqual(arr);
      })
    );
  });

  it('map preserves length', () => {
    fc.assert(
      fc.property(
        fc.array(fc.integer()),
        fc.func(fc.integer()),
        (arr, fn) => {
          expect(arr.map(fn)).toHaveLength(arr.length);
        }
      )
    );
  });
});
```

**Advanced: Custom Strategies:**
```python
from hypothesis import strategies as st

# Custom domain model
@st.composite
def user_strategy(draw):
    return {
        'id': draw(st.integers(min_value=1, max_value=999999)),
        'email': draw(st.emails()),
        'age': draw(st.integers(min_value=18, max_value=120)),
        'name': draw(st.text(min_size=1, max_size=50))
    }

@given(user_strategy())
def test_user_validation(user):
    result = validate_user(user)
    assert result['is_valid'] is True
    assert result['errors'] == []
```

**Verification:**
- [ ] Tests run and generate multiple examples
- [ ] Properties are being verified
- [ ] Tests fail on broken code
- [ ] Shrinking works (finds minimal failing case)

**If This Fails:**
→ Start with simple strategies (integers, strings)
→ Add `.example()` to see what's being generated
→ Check for timeout issues (reduce max_examples)

---

### Step 4: Handle Edge Cases and Constraints

**What:** Add constraints and filters to generate realistic test data

**How:**

**Using assume() for constraints:**
```python
from hypothesis import given, assume, strategies as st

@given(st.integers(), st.integers())
def test_division(a, b):
    assume(b != 0)  # Skip cases where b is zero
    result = a / b
    assert result * b == pytest.approx(a)

@given(st.lists(st.integers(), min_size=1))
def test_max_element(numbers):
    """Max is always >= all elements"""
    max_val = max(numbers)
    assert all(max_val >= n for n in numbers)
```

**Filtering strategies:**
```python
# Instead of assume (more efficient)
@given(st.integers(min_value=1))  # Only positive
@given(st.text(min_size=1))  # Non-empty strings
@given(st.lists(st.integers()).filter(lambda x: len(x) > 0))

# Complex constraints
@given(st.integers(min_value=0, max_value=100).filter(lambda x: x % 2 == 0))
def test_even_numbers(n):
    assert n % 2 == 0
```

**Example expectations:**
```python
@given(st.integers())
def test_with_examples(n):
    # Add specific cases to always test
    pass

test_with_examples = example(0)(example(-1)(example(1)(test_with_examples)))
```

**JavaScript constraints:**
```javascript
fc.assert(
  fc.property(
    fc.integer({ min: 1, max: 100 }),
    fc.string({ minLength: 1 }),
    (age, name) => {
      // Test with constrained inputs
      const user = createUser(age, name);
      expect(user).toBeDefined();
    }
  )
);
```

**Verification:**
- [ ] Constraints properly limit input space
- [ ] Tests don't have excessive assumes (< 10% rejection rate)
- [ ] Edge cases are covered (empty, max, min values)
- [ ] Invalid inputs raise expected exceptions

**If This Fails:**
→ Replace `assume()` with filtered strategies
→ Check if constraints are too restrictive
→ Use `@example()` to test specific edge cases

---

### Step 5: Configure Test Execution

**What:** Optimize test runs with appropriate settings

**How:**

**Hypothesis Configuration:**
```python
from hypothesis import settings, Verbosity

# Global configuration
settings.register_profile("dev", max_examples=50)
settings.register_profile("ci", max_examples=1000, verbosity=Verbosity.verbose)
settings.load_profile("dev")

# Per-test configuration
@settings(max_examples=500, deadline=None)
@given(st.integers())
def test_expensive_operation(n):
    # More thorough testing for critical function
    pass
```

**Common Settings:**
- `max_examples`: Number of test cases (default: 100)
- `deadline`: Time limit per test (default: 200ms)
- `verbosity`: Output detail level
- `suppress_health_check`: Skip certain warnings

**fast-check Configuration:**
```javascript
fc.assert(
  fc.property(fc.integer(), (n) => {
    // test code
  }),
  { 
    numRuns: 1000,  // Number of test cases
    verbose: true,   // Show all failures
    seed: 42         // Reproducible tests
  }
);
```

**CI/CD Integration:**
```yaml
# .github/workflows/test.yml
- name: Run property tests
  run: |
    pytest --hypothesis-profile=ci tests/
  env:
    HYPOTHESIS_VERBOSITY: verbose
```

**Verification:**
- [ ] Tests complete in reasonable time
- [ ] CI runs more examples than local dev
- [ ] Verbose mode shows useful output
- [ ] Seed value makes failures reproducible

**If This Fails:**
→ Reduce max_examples for slow tests
→ Increase deadline for complex operations
→ Use database strategies for stateful testing

---

### Step 6: Debug and Shrink Failures

**What:** Analyze minimal failing examples when property tests fail

**How:**

**Understanding Shrinking:**
When a property test fails, the framework automatically finds the smallest input that causes failure.

**Example failure output:**
```python
# Hypothesis will show:
Falsifying example: test_division(a=1, b=0)

# It found this after trying:
# Initially failed with: a=582749, b=0
# Shrunk to minimal: a=1, b=0
```

**Debugging techniques:**
```python
@given(st.integers())
def test_with_debug(n):
    print(f"Testing with: {n}")  # See what's being tested
    result = my_function(n)
    assert result > 0

# Add explicit examples for debugging
@example(0)
@example(-1)
@example(sys.maxsize)
@given(st.integers())
def test_with_examples(n):
    pass
```

**Reproduce specific failure:**
```python
from hypothesis import reproduce_failure

@reproduce_failure('6.0.0', b'AAEC...')  # Paste from failure output
@given(st.integers())
def test_reproduce(n):
    # Runs with exact failing input
    pass
```

**JavaScript debugging:**
```javascript
fc.assert(
  fc.property(fc.integer(), (n) => {
    console.log('Testing:', n);
    // test code
  }),
  { 
    seed: 1234567890,  // Use seed from failure
    path: "0:0:0"      // Use path from failure
  }
);
```

**Verification:**
- [ ] Minimal failing case is clear
- [ ] Can reproduce failure consistently  
- [ ] Root cause identified
- [ ] Fix addresses the property violation

**If This Fails:**
→ Add print statements to see generated values
→ Reduce max_examples to make debugging easier
→ Use `.example()` to test specific cases first

---

## Verification Checklist

After completing this workflow:

- [ ] Properties clearly defined and documented
- [ ] Tests generate diverse inputs automatically
- [ ] Edge cases discovered and handled
- [ ] Shrinking provides minimal failing examples
- [ ] Tests run in CI/CD pipeline
- [ ] Coverage complements example-based tests
- [ ] Performance acceptable for test suite
- [ ] Team understands property-based approach

---

## Common Issues & Solutions

### Issue: Tests are too slow

**Symptoms:**
- Test suite takes > 5 minutes locally
- CI times out on property tests
- Developers skip running tests

**Solution:**
```python
# Reduce examples for fast feedback
@settings(max_examples=20)  # Down from default 100
@given(st.integers())
def test_quick_check(n):
    pass

# Or use profiles
settings.register_profile("dev", max_examples=20)
settings.register_profile("ci", max_examples=500)
```

**Prevention:**
- Use smaller max_examples for dev, larger for CI
- Mock expensive operations (DB, network)
- Use `@settings(deadline=None)` for legitimately slow tests

---

### Issue: Too many invalid inputs generated

**Symptoms:**
- Tests spend time filtering out invalid inputs
- "Unable to satisfy assumptions" warnings
- > 10% of inputs rejected

**Solution:**
```python
# BAD: Too many assumes
@given(st.integers())
def test_bad(n):
    assume(n > 0)
    assume(n < 100)
    assume(n % 2 == 0)

# GOOD: Constrained strategy
@given(st.integers(min_value=2, max_value=98).filter(lambda x: x % 2 == 0))
def test_good(n):
    pass

# BETTER: Custom strategy
@st.composite
def even_small_integers(draw):
    return draw(st.integers(min_value=1, max_value=49)) * 2
```

**Prevention:**
- Design strategies that generate valid data
- Use strategy combinators (builds, tuples, etc.)
- Reject early in strategy, not in test

---

### Issue: Properties are too weak

**Symptoms:**
- Tests always pass, even with bugs
- Properties just restate the implementation
- No edge cases found

**Solution:**
```python
# WEAK: Just restates implementation
@given(st.lists(st.integers()))
def test_weak(numbers):
    result = my_sort(numbers)
    assert result == sorted(numbers)  # Circular reasoning

# STRONG: Tests actual properties
@given(st.lists(st.integers()))
def test_strong(numbers):
    result = my_sort(numbers)
    # Independent properties
    assert len(result) == len(numbers)
    assert all(result[i] <= result[i+1] for i in range(len(result)-1))
    assert set(result) == set(numbers)
```

**Prevention:**
- Think about mathematical properties
- Test relationships, not equality to known implementation
- Use oracle testing (compare to trusted alternative)

---

### Issue: Non-deterministic failures

**Symptoms:**
- Tests fail randomly
- Can't reproduce failures
- Different results on different machines

**Solution:**
```python
# Use seed for reproducibility
@settings(
    max_examples=100,
    derandomize=True  # Uses deterministic randomness
)
@given(st.integers())
def test_reproducible(n):
    pass

# Or set global seed
from hypothesis import seed
seed(12345)
```

**Prevention:**
- Always use framework's random generators, not `random.randint()`
- Avoid time-dependent behavior in tests
- Use deterministic mode in CI

---

## Examples

### Example 1: Testing a URL Parser

**Context:** Validating URL parsing handles all edge cases

**Implementation:**
```python
from hypothesis import given, strategies as st
from urllib.parse import urlparse, urlunparse

# Strategy for valid URLs
url_strategy = st.builds(
    lambda scheme, host, path: f"{scheme}://{host}{path}",
    scheme=st.sampled_from(['http', 'https', 'ftp']),
    host=st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789.-', min_size=1, max_size=50),
    path=st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789/-_', max_size=100)
)

@given(url_strategy)
def test_url_roundtrip(url):
    """Parsing and reconstructing URL should be identity"""
    parsed = urlparse(url)
    reconstructed = urlunparse(parsed)
    # May not be exact match but should be equivalent
    assert urlparse(reconstructed) == parsed

@given(url_strategy)
def test_url_parts_are_strings(url):
    """All parsed components should be strings"""
    parsed = urlparse(url)
    assert isinstance(parsed.scheme, str)
    assert isinstance(parsed.netloc, str)
    assert isinstance(parsed.path, str)
```

**Result:** Found edge case where paths with consecutive slashes were normalized differently

---

### Example 2: Testing JSON Serialization

**Context:** Ensuring data survives JSON encode/decode cycle

**Implementation:**
```python
import json
from hypothesis import given, strategies as st

# JSON-compatible data strategy
json_value = st.recursive(
    st.one_of(
        st.none(),
        st.booleans(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(),
    ),
    lambda children: st.one_of(
        st.lists(children),
        st.dictionaries(st.text(), children)
    ),
    max_leaves=50
)

@given(json_value)
def test_json_roundtrip(value):
    """JSON encode/decode should be identity for JSON-safe types"""
    encoded = json.dumps(value)
    decoded = json.loads(encoded)
    assert decoded == value

@given(st.dictionaries(st.text(), st.integers()))
def test_json_preserves_keys(data):
    """All keys should survive JSON serialization"""
    encoded = json.dumps(data)
    decoded = json.loads(encoded)
    assert set(decoded.keys()) == set(data.keys())
```

**Result:** Discovered that float NaN and Infinity broke serialization

---

### Example 3: Testing State Machine

**Context:** Validating a shopping cart's state transitions

**Implementation:**
```python
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
from hypothesis import strategies as st

class ShoppingCartStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.cart = ShoppingCart()
        self.items = set()
    
    @rule(item=st.text(min_size=1), quantity=st.integers(min_value=1, max_value=10))
    def add_item(self, item, quantity):
        self.cart.add(item, quantity)
        self.items.add(item)
    
    @rule(item=st.text())
    def remove_item(self, item):
        if item in self.items:
            self.cart.remove(item)
            self.items.remove(item)
    
    @invariant()
    def cart_items_match_tracking(self):
        """Cart should only contain items we've added"""
        assert set(self.cart.items.keys()) == self.items
    
    @invariant()
    def all_quantities_positive(self):
        """All quantities should be positive"""
        assert all(q > 0 for q in self.cart.items.values())

TestShoppingCart = ShoppingCartStateMachine.TestCase
```

**Result:** Found race condition when removing items that were just added

---

## Best Practices

### DO:
✅ Start with simple properties before complex ones
✅ Test properties, not equality to reference implementation  
✅ Use constrained strategies instead of excessive assumes
✅ Run more examples in CI than locally (50 local, 1000 CI)
✅ Keep shrinking fast by using simple strategies
✅ Complement property tests with example-based tests
✅ Document what properties you're testing
✅ Use custom strategies for domain models
✅ Test both success and error paths
✅ Make tests deterministic with seeds

### DON'T:
❌ Write properties that just restate the code
❌ Use assume() when you could use filtered strategies
❌ Ignore shrinking output - it shows minimal bug case
❌ Test only happy paths - include error conditions
❌ Make strategies generate mostly invalid data
❌ Use property tests for everything - they're not always best
❌ Let tests run too long (> 5 min locally)
❌ Forget to test edge cases explicitly with @example()
❌ Skip documentation on what properties mean
❌ Test implementation details instead of behavior

---

## Related Workflows

**Prerequisites:**
- `dev-008`: Unit Testing Setup - Basic testing infrastructure
- `dev-010`: Test Fixtures and Mocks - Understanding test data patterns

**Next Steps:**
- `tes-004`: Test Data Generation - Advanced data generation strategies
- `qa-009`: Regression Test Suite - Incorporating found bugs into regression suite
- `qa-007`: Test Coverage Analysis - Measuring property test effectiveness

**Alternatives:**
- `tes-003`: Mocking Strategy - For testing with external dependencies
- `dev-009`: Mutation Testing - Alternative approach to find weak tests
- Fuzz testing - Similar concept, focuses on security/crashes

---

## Tags
`testing` `property-based-testing` `hypothesis` `fast-check` `quickcheck` `automated-testing` `test-generation` `edge-cases` `quality-assurance`
