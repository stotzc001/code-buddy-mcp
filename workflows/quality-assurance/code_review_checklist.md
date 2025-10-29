# Code Review Checklist

**ID:** qua-001  
**Category:** Quality Assurance  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 30-60 minutes (per review)  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Comprehensive, systematic checklist for conducting thorough and effective code reviews that catch bugs, improve code quality, and facilitate knowledge sharing across the team.

**Why:** Code reviews are one of the most effective ways to improve code quality, catch bugs early, share knowledge, and maintain consistency across a codebase. A structured checklist ensures reviews are thorough, consistent, and focused on the most important aspects. Studies show code reviews can catch 60-90% of defects before they reach production.

**When to use:**
- Reviewing pull requests before merging
- Conducting pair programming sessions
- Performing security audits
- Mentoring junior developers
- Establishing code review culture
- Ensuring coding standards compliance
- Pre-release quality gates

---

## Prerequisites

**Required:**
- [ ] Access to code repository and PR tool (GitHub, GitLab, Bitbucket)
- [ ] Understanding of project coding standards
- [ ] Familiarity with the codebase
- [ ] Development environment set up for testing
- [ ] CI/CD pipeline results available

**Check before starting:**
```bash
# Clone/update repository
git fetch origin
git checkout <branch-name>

# Verify PR details
gh pr view <pr-number>

# Check CI/CD status
gh pr checks <pr-number>

# Review changed files
git diff main...<branch-name> --stat

# Set up development environment
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

---

## Implementation Steps

### Step 1: Understand Context and Requirements

**What:** Review the PR description, linked issues, and understand what problem the code is solving before diving into implementation details.

**How:**

**Read PR description:**
```markdown
# Check for required information:
- [ ] Clear title describing the change
- [ ] Description of what changed and why
- [ ] Link to related issue/ticket
- [ ] Screenshots/videos for UI changes
- [ ] Breaking changes documented
- [ ] Migration steps if needed
- [ ] Testing instructions
```

**Review linked issues:**
```bash
# View GitHub issue
gh issue view <issue-number>

# Check for:
- Acceptance criteria
- Design decisions
- Edge cases discussed
- Performance requirements
- Security considerations
```

**Understand scope:**
```bash
# Check files changed
git diff --name-status main...<branch-name>

# Count changes
git diff --stat main...<branch-name>

# Categorize changes:
# - New features
# - Bug fixes
# - Refactoring
# - Documentation
# - Tests
```

**Context questions to answer:**
```markdown
✓ What problem does this solve?
✓ Why was this approach chosen?
✓ What are the alternatives?
✓ What could go wrong?
✓ Who are the users affected?
✓ What is the performance impact?
✓ Are there security implications?
```

**Verification:**
- [ ] PR description is clear and complete
- [ ] Requirements are understood
- [ ] Scope is appropriate (not too large)
- [ ] Related issues/docs reviewed
- [ ] Questions documented for author

**If This Fails:**
→ Request clarification from author before continuing review
→ If PR is too large (>500 lines), suggest breaking into smaller PRs
→ If context is missing, ask author to update description

---

### Step 2: Check Automated Tests and CI/CD Status

**What:** Verify all automated checks pass before doing manual review.

**How:**

**Check CI/CD pipeline:**
```bash
# View all checks
gh pr checks <pr-number>

# Expected passing checks:
# ✅ Build successful
# ✅ Unit tests passed
# ✅ Integration tests passed
# ✅ Linting passed (ruff, pylint)
# ✅ Type checking passed (mypy)
# ✅ Security scan passed
# ✅ Code coverage maintained/improved
```

**Review test coverage:**
```bash
# Check coverage report
pytest --cov=. --cov-report=term --cov-report=html

# Coverage requirements:
# - Overall coverage >= 80%
# - New code coverage >= 90%
# - No decrease in coverage
```

**Verify tests exist:**
```bash
# Count test files
find . -name "test_*.py" -o -name "*_test.py" | wc -l

# Check for new tests
git diff main...<branch-name> --name-only | grep test

# Test categories to check:
# ✓ Unit tests for new functions
# ✓ Integration tests for new features
# ✓ Edge case tests
# ✓ Error handling tests
# ✓ Performance tests (if needed)
```

**Run tests locally:**
```bash
# Run full test suite
pytest -v

# Run only tests for changed files
pytest tests/test_changed_module.py -v

# Run with different scenarios
pytest -v --runslow  # Include slow tests
pytest -v --runintegration  # Integration tests
```

**Verification:**
- [ ] All CI/CD checks passing
- [ ] Test coverage maintained or improved
- [ ] New functionality has tests
- [ ] Tests are meaningful (not just for coverage)
- [ ] Tests run quickly (< 1 second per test)
- [ ] Tests are independent and don't share state

**If This Fails:**
→ Request author to fix failing tests before review
→ If coverage decreased, request additional tests
→ If tests are flaky, identify and fix before merging

---

### Step 3: Review Code Structure and Design

**What:** Evaluate the overall architecture, design patterns, and code organization.

**How:**

**Architecture review:**
```markdown
## Check for:
✓ Follows existing patterns in codebase
✓ Separation of concerns (SRP)
✓ Proper abstraction levels
✓ Appropriate use of design patterns
✓ Avoids premature optimization
✓ No circular dependencies

## Red flags:
❌ God objects (classes doing too much)
❌ Tight coupling between modules
❌ Hardcoded configuration
❌ Mixing business logic and presentation
❌ Overly complex inheritance hierarchies
❌ Violation of SOLID principles
```

**Code organization:**
```python
# Good: Clear separation
class UserService:
    """Handles user business logic."""
    
    def create_user(self, data: UserCreate) -> User:
        """Create new user with validation."""
        # Business logic here
        pass

class UserRepository:
    """Handles user data access."""
    
    def save(self, user: User) -> User:
        """Persist user to database."""
        # Database operations here
        pass

# Bad: Mixed concerns
class UserManager:
    """Does everything related to users."""
    
    def create_user(self, data: dict) -> dict:
        # Validation
        # Business logic
        # Database access
        # Email sending
        # All in one place!
        pass
```

**Design patterns:**
```python
# Check for appropriate pattern usage:

# ✅ Good: Factory pattern
class ReportFactory:
    @staticmethod
    def create_report(report_type: str) -> Report:
        if report_type == "pdf":
            return PDFReport()
        elif report_type == "excel":
            return ExcelReport()
        raise ValueError(f"Unknown report type: {report_type}")

# ✅ Good: Strategy pattern
class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def process(self, amount: float) -> bool:
        return self.strategy.execute(amount)

# ❌ Bad: Overengineering
class SimpleCounter:
    """Just needs to count, but uses complex patterns unnecessarily."""
    def __init__(self):
        self.factory = CounterFactory()
        self.strategy = CountingStrategy()
        self.observer = CounterObserver()
```

**Modularity check:**
```bash
# Check module dependencies
pydeps src/ --max-bacon=2

# Analyze coupling
radon cc src/ -a -nb

# Look for:
# - Low coupling
# - High cohesion
# - Clear interfaces
# - Minimal dependencies
```

**Verification:**
- [ ] Code follows SOLID principles
- [ ] Design patterns used appropriately
- [ ] No unnecessary complexity
- [ ] Clear separation of concerns
- [ ] Dependencies are minimal and clear
- [ ] Modules are cohesive
- [ ] No circular dependencies

**If This Fails:**
→ Suggest refactoring for better structure
→ Provide specific examples of better patterns
→ Discuss in comments or synchronously if major issues

---

### Step 4: Review Code Quality and Readability

**What:** Examine code for clarity, maintainability, and adherence to coding standards.

**How:**

**Naming conventions:**
```python
# ✅ Good: Clear, descriptive names
def calculate_monthly_revenue(transactions: List[Transaction]) -> Decimal:
    """Calculate total revenue for the current month."""
    return sum(t.amount for t in transactions if t.is_current_month())

# ❌ Bad: Unclear, abbreviated names
def calc_rev(txns: List) -> float:
    """Do stuff with money."""
    return sum(t.amt for t in txns if t.chk())

# Checklist:
# ✓ Variables: noun_phrase (user_account, total_price)
# ✓ Functions: verb_phrase (get_user, calculate_total)
# ✓ Classes: PascalCase nouns (UserAccount, PaymentProcessor)
# ✓ Constants: UPPER_SNAKE_CASE (MAX_RETRY_COUNT)
# ✓ Boolean variables: is_/has_/can_ prefix (is_active, has_permission)
```

**Function quality:**
```python
# ✅ Good: Single responsibility, short, clear
def validate_email(email: str) -> bool:
    """Check if email address is valid format."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def send_welcome_email(user: User) -> None:
    """Send welcome email to new user."""
    if not validate_email(user.email):
        raise ValueError(f"Invalid email: {user.email}")
    
    email_service.send(
        to=user.email,
        subject="Welcome!",
        template="welcome",
        context={"name": user.name}
    )

# ❌ Bad: Does too much, too long, unclear
def process_user(email: str, name: str, age: int, addr: str) -> dict:
    """Do user stuff."""
    # 100+ lines of validation, database access, email sending,
    # logging, error handling all mixed together
    pass

# Function quality checklist:
# ✓ < 50 lines (ideally < 20)
# ✓ Single responsibility
# ✓ < 5 parameters
# ✓ No nested functions > 3 levels
# ✓ Early returns for edge cases
# ✓ Clear, descriptive name
```

**Code smells:**
```python
# ❌ Magic numbers
if age > 18:  # Why 18?
    allow_access()

# ✅ Named constants
MINIMUM_AGE = 18  # Legal adult age

if age >= MINIMUM_AGE:
    allow_access()

# ❌ Long parameter lists
def create_user(name, email, phone, address, city, state, zip, country, age, gender):
    pass

# ✅ Use data classes
@dataclass
class UserData:
    name: str
    email: str
    phone: str
    address: Address
    demographics: Demographics

def create_user(data: UserData):
    pass

# ❌ Nested conditionals
if user:
    if user.is_active:
        if user.has_permission:
            if not user.is_banned:
                return True
return False

# ✅ Guard clauses
if not user or not user.is_active:
    return False
if not user.has_permission or user.is_banned:
    return False
return True
```

**Code complexity:**
```bash
# Check cyclomatic complexity
radon cc src/ -s -a

# Target values:
# A (1-5): Low risk - Simple code
# B (6-10): Moderate - Acceptable
# C (11-20): High - Consider refactoring
# D-F (21+): Very high - Must refactor

# Check cognitive complexity
# Measures how difficult code is to understand
# Target: < 15 for most functions
```

**Verification:**
- [ ] Names are clear and descriptive
- [ ] Functions are short and focused
- [ ] No code smells detected
- [ ] Complexity metrics acceptable
- [ ] Code is self-documenting
- [ ] No unnecessary comments (code speaks for itself)
- [ ] Complex logic has explanatory comments

**If This Fails:**
→ Request specific refactorings
→ Suggest better names with examples
→ Provide links to style guide
→ Pair with author to improve code

---

### Step 5: Review Error Handling and Edge Cases

**What:** Ensure code handles errors gracefully and covers edge cases.

**How:**

**Error handling checklist:**
```python
# ✅ Good: Specific exceptions, informative messages
def divide_numbers(a: float, b: float) -> float:
    """Divide two numbers with proper error handling."""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError(f"Both arguments must be numbers, got {type(a)} and {type(b)}")
    
    if b == 0:
        raise ValueError("Cannot divide by zero")
    
    return a / b

# ❌ Bad: Generic exceptions, no context
def divide_numbers(a, b):
    try:
        return a / b
    except:  # Catches everything!
        return None  # No information about what went wrong

# Error handling principles:
# ✓ Use specific exception types
# ✓ Provide informative error messages
# ✓ Include context (values, state)
# ✓ Don't catch exceptions you can't handle
# ✓ Log errors before re-raising
# ✓ Don't use exceptions for control flow
```

**Edge cases to check:**
```python
# ✅ Good: Handles all edge cases
def get_first_element(items: List[Any]) -> Any:
    """Get first element of list."""
    if not items:  # Empty list
        raise ValueError("Cannot get first element of empty list")
    return items[0]

def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage."""
    if total == 0:  # Division by zero
        return 0.0
    if part < 0 or total < 0:  # Negative numbers
        raise ValueError("Values must be non-negative")
    return (part / total) * 100

# Edge cases checklist:
# ✓ Empty collections ([], {}, "")
# ✓ None/null values
# ✓ Zero values
# ✓ Negative numbers (when unexpected)
# ✓ Very large numbers (overflow)
# ✓ Very small numbers (underflow)
# ✓ Boundary values (0, 1, MAX, MIN)
# ✓ Invalid input types
# ✓ Concurrent access
# ✓ Network failures
# ✓ Database errors
```

**Resource management:**
```python
# ✅ Good: Context managers
def process_file(filename: str) -> str:
    """Process file with proper resource management."""
    with open(filename, 'r') as f:
        return f.read().upper()

# ✅ Good: Try-finally for cleanup
def make_api_call():
    connection = create_connection()
    try:
        return connection.fetch_data()
    finally:
        connection.close()  # Always closes

# ❌ Bad: No cleanup
def process_file(filename):
    f = open(filename)
    data = f.read()
    # What if error happens here? File never closed!
    return data.upper()
```

**Validation:**
```python
# ✅ Good: Input validation
def create_user(email: str, age: int) -> User:
    """Create user with validation."""
    # Validate email format
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        raise ValueError(f"Invalid email format: {email}")
    
    # Validate age range
    if not 13 <= age <= 120:
        raise ValueError(f"Invalid age: {age}")
    
    return User(email=email, age=age)

# Validation checklist:
# ✓ Input format validation
# ✓ Range checks
# ✓ Type validation
# ✓ Required fields present
# ✓ Data consistency
# ✓ Business rule validation
```

**Verification:**
- [ ] All errors handled appropriately
- [ ] Specific exception types used
- [ ] Error messages are informative
- [ ] Edge cases covered
- [ ] Resources properly cleaned up
- [ ] Input validation thorough
- [ ] Tests cover error scenarios

**If This Fails:**
→ Request additional error handling
→ Suggest specific edge cases to test
→ Add tests for error scenarios

---

### Step 6: Review Security and Performance

**What:** Check for security vulnerabilities and performance issues.

**How:**

**Security checklist:**
```python
# ✅ Good: Parameterized queries
def get_user(user_id: int) -> User:
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))

# ❌ Bad: SQL injection vulnerability
def get_user(user_id: str) -> User:
    query = f"SELECT * FROM users WHERE id = {user_id}"  # DANGEROUS!
    cursor.execute(query)

# ✅ Good: Input sanitization
from html import escape

def display_user_input(text: str) -> str:
    return escape(text)  # Prevents XSS

# ❌ Bad: Unsanitized output
def display_user_input(text: str) -> str:
    return text  # XSS vulnerability!

# Security review points:
# ✓ No SQL injection (use parameterized queries)
# ✓ No XSS (sanitize output)
# ✓ No hardcoded secrets/passwords
# ✓ Sensitive data encrypted
# ✓ Authentication/authorization checks
# ✓ CSRF protection
# ✓ Rate limiting
# ✓ Input validation
# ✓ Secure random number generation
# ✓ No eval() or exec() with user input
```

**Secrets management:**
```python
# ✅ Good: Environment variables
import os

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")

# ❌ Bad: Hardcoded secrets
API_KEY = "sk-1234567890abcdef"  # NEVER DO THIS!

# Check for:
# ✓ No secrets in code
# ✓ No secrets in comments
# ✓ No secrets in test data
# ✓ .env files in .gitignore
```

**Performance review:**
```python
# ✅ Good: Efficient query
def get_active_users() -> List[User]:
    # Single query with filtering
    return User.objects.filter(is_active=True).select_related('profile')

# ❌ Bad: N+1 query problem
def get_active_users() -> List[User]:
    users = User.objects.all()
    return [u for u in users if u.is_active]  # Queries for each user!

# ✅ Good: Caching
@cache_result(ttl=3600)
def get_expensive_data():
    return slow_database_query()

# ❌ Bad: No caching
def get_expensive_data():
    return slow_database_query()  # Called repeatedly!

# Performance checklist:
# ✓ No N+1 query problems
# ✓ Appropriate indexes on database
# ✓ Caching for expensive operations
# ✓ Pagination for large result sets
# ✓ Async for I/O-bound operations
# ✓ Batch operations when possible
# ✓ Avoid unnecessary loops
# ✓ Use appropriate data structures
```

**Check for common vulnerabilities:**
```bash
# Run security scanner
bandit -r src/

# Check dependencies for vulnerabilities
safety check

# Review changes for:
# - Exposed secrets
# - Insecure deserialization
# - Path traversal
# - Command injection
# - XML external entities
# - Insecure direct object references
```

**Verification:**
- [ ] No security vulnerabilities
- [ ] No hardcoded secrets
- [ ] Input properly validated and sanitized
- [ ] SQL queries parameterized
- [ ] No obvious performance issues
- [ ] Appropriate caching used
- [ ] Database queries optimized
- [ ] Security scan passed

**If This Fails:**
→ Request immediate fix for security issues
→ Block PR until critical issues resolved
→ Suggest performance optimizations
→ Run load tests if concerned

---

### Step 7: Review Documentation and Tests

**What:** Ensure code is well-documented and thoroughly tested.

**How:**

**Documentation review:**
```python
# ✅ Good: Clear docstrings
def calculate_compound_interest(
    principal: Decimal,
    rate: Decimal,
    years: int,
    compounds_per_year: int = 12
) -> Decimal:
    """Calculate compound interest.
    
    Args:
        principal: Initial investment amount
        rate: Annual interest rate (as decimal, e.g., 0.05 for 5%)
        years: Number of years to compound
        compounds_per_year: Compounding frequency (default: monthly)
    
    Returns:
        Final amount after compounding
    
    Raises:
        ValueError: If principal or rate is negative, or years is not positive
    
    Example:
        >>> calculate_compound_interest(Decimal('1000'), Decimal('0.05'), 10)
        Decimal('1647.01')
    """
    if principal < 0 or rate < 0:
        raise ValueError("Principal and rate must be non-negative")
    if years <= 0:
        raise ValueError("Years must be positive")
    
    return principal * (1 + rate / compounds_per_year) ** (compounds_per_year * years)

# ❌ Bad: No documentation
def calc(p, r, y, c=12):
    return p * (1 + r / c) ** (c * y)

# Documentation checklist:
# ✓ Public functions have docstrings
# ✓ Complex logic has comments
# ✓ Parameters documented
# ✓ Return values documented
# ✓ Exceptions documented
# ✓ Examples provided
# ✓ README updated if needed
# ✓ API docs updated
```

**Test quality:**
```python
# ✅ Good: Clear, comprehensive tests
def test_calculate_compound_interest_basic():
    """Test basic compound interest calculation."""
    result = calculate_compound_interest(
        principal=Decimal('1000'),
        rate=Decimal('0.05'),
        years=1,
        compounds_per_year=12
    )
    assert result == pytest.approx(Decimal('1051.16'), rel=0.01)

def test_calculate_compound_interest_zero_rate():
    """Test with zero interest rate."""
    result = calculate_compound_interest(
        principal=Decimal('1000'),
        rate=Decimal('0'),
        years=10
    )
    assert result == Decimal('1000')

def test_calculate_compound_interest_negative_principal():
    """Test that negative principal raises ValueError."""
    with pytest.raises(ValueError, match="must be non-negative"):
        calculate_compound_interest(
            principal=Decimal('-1000'),
            rate=Decimal('0.05'),
            years=1
        )

# Test quality checklist:
# ✓ Tests have clear names
# ✓ One assertion per test (usually)
# ✓ Arrange-Act-Assert pattern
# ✓ Test edge cases
# ✓ Test error conditions
# ✓ Tests are independent
# ✓ No flaky tests
# ✓ Fast execution (< 1s per test)
```

**Code examples in documentation:**
```markdown
# ✅ Good: Working examples
## Usage

\`\`\`python
from myapp import UserService

# Create a new user
service = UserService()
user = service.create_user(
    email="user@example.com",
    name="John Doe"
)

# Update user profile
user.update_profile(bio="Software engineer")
\`\`\`

# ❌ Bad: Outdated or broken examples
## Usage
\`\`\`python
user = create_user()  # This function doesn't exist anymore!
\`\`\`
```

**Verification:**
- [ ] All public APIs documented
- [ ] Docstrings follow format (Google/NumPy style)
- [ ] Complex logic has explanatory comments
- [ ] README updated if needed
- [ ] Tests are comprehensive
- [ ] Tests cover edge cases and errors
- [ ] Tests are clear and maintainable
- [ ] Examples in docs work

**If This Fails:**
→ Request documentation for public APIs
→ Suggest specific areas needing tests
→ Provide test examples
→ Update README if needed

---

### Step 8: Provide Constructive Feedback and Approve

**What:** Summarize findings and provide actionable feedback.

**How:**

**Feedback guidelines:**
```markdown
## Review feedback structure:

### Positive feedback first
"Great job on implementing the caching layer! The performance improvement is significant."

### Specific, actionable suggestions
❌ Bad: "This code is messy"
✅ Good: "Consider extracting lines 45-60 into a separate function called `validate_input()` for better readability"

### Explain the "why"
"We should use parameterized queries here to prevent SQL injection attacks"

### Offer solutions
"Instead of nested if statements, consider using guard clauses:
\`\`\`python
if not user:
    return None
if not user.is_active:
    return None
return user
\`\`\`"

### Categorize issues
🔴 **Blocking:** Must fix before merge (security, bugs)
🟡 **Important:** Should fix (design, performance)
🟢 **Nit:** Nice to have (style, naming)
```

**Comment types:**
```bash
# 🔴 Blocking comment
"""
🔴 **Security Issue:** This SQL query is vulnerable to injection.
Use parameterized queries instead:

```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```
"""

# 🟡 Suggestion
"""
🟡 **Suggestion:** Consider using a constant for the magic number:
```python
MAX_RETRIES = 3  # Maximum retry attempts
```
This makes the code more maintainable.
"""

# 🟢 Nit
"""
🟢 **Nit:** Variable name could be more descriptive:
`user_list` → `active_users`
"""

# ✅ Praise
"""
✅ Excellent error handling here! The error messages are very informative.
"""
```

**Review decision:**
```markdown
## Approve ✅
- All checks passed
- Code quality excellent
- Tests comprehensive
- Documentation complete
- No blocking issues

## Request Changes 🔴
- [Blocking] Security vulnerability in line 45
- [Blocking] Failing tests must be fixed
- [Important] Performance issue with database query
- [Nit] Consider better variable names

## Comment/Discuss 💬
- Need clarification on design decision
- Want to discuss alternative approaches
- Requesting additional context
```

**Follow-up:**
```bash
# Add PR comment with summary
gh pr comment <pr-number> --body "
## Review Summary

### ✅ Strengths
- Well-structured code
- Comprehensive tests
- Good error handling

### 🔴 Required Changes
1. Fix SQL injection vulnerability (line 45)
2. Add tests for edge cases

### 🟡 Suggestions
1. Consider extracting validation logic
2. Add caching for expensive operation

### Next Steps
Please address the blocking issues. Happy to discuss synchronously if needed!
"

# Or approve
gh pr review <pr-number> --approve --body "LGTM! 🚀"
```

**Verification:**
- [ ] Feedback is specific and actionable
- [ ] Positive aspects acknowledged
- [ ] Blocking issues clearly marked
- [ ] Suggestions include examples
- [ ] Tone is constructive and respectful
- [ ] Review decision made (approve/request changes)
- [ ] Author knows next steps

**If This Fails:**
→ Review your own feedback for clarity
→ Discuss complex issues synchronously
→ Be available for questions

---

## Verification Checklist

After completing code review:

- [ ] Context and requirements understood
- [ ] All CI/CD checks reviewed
- [ ] Code structure evaluated
- [ ] Code quality assessed
- [ ] Error handling verified
- [ ] Security reviewed
- [ ] Performance checked
- [ ] Documentation reviewed
- [ ] Tests evaluated
- [ ] Constructive feedback provided
- [ ] Review decision made (approve/request changes)
- [ ] Follow-up plan established

---

## Common Issues & Solutions

### Issue: Review Taking Too Long

**Symptoms:**
- Review taking > 1 hour
- Getting lost in details
- Analysis paralysis

**Solution:**
```markdown
Time management:
1. Set time limit (30-60 min max)
2. Focus on critical issues first:
   - Security
   - Correctness
   - Tests
3. Defer minor nits to follow-up PR
4. If too large, suggest splitting PR

Large PR strategy:
- Review architectural changes first
- Then review critical paths
- Leave detailed nits for later
```

**Prevention:**
- Establish PR size limits (< 400 lines)
- Request PRs to be broken up
- Use automated tools for style issues

---

### Issue: Uncertain About Code Quality

**Symptoms:**
- Not sure if code is "good enough"
- Uncertain about suggestions
- Lack of confidence in review

**Solution:**
```markdown
When uncertain:
1. Ask questions rather than demand changes
   "Have you considered X approach?"
   
2. Discuss with another reviewer
   "Hey, can you take a look at this?"
   
3. Test the code locally
   Actually run it to understand behavior
   
4. Check similar code in codebase
   Consistency matters
   
5. Consult team standards
   Follow established patterns
```

**Prevention:**
- Establish clear coding standards
- Create review checklist
- Pair review with senior dev
- Document common patterns

---

### Issue: Author Defensive About Feedback

**Symptoms:**
- Author pushback on suggestions
- Defensive comments
- Tension in discussion

**Solution:**
```markdown
De-escalation strategies:
1. Acknowledge the author's work
   "I see what you're trying to do here..."
   
2. Ask questions instead of demanding
   "What do you think about X approach?"
   
3. Explain the "why"
   "We use this pattern because..."
   
4. Offer to pair program
   "Want to hop on a call to discuss?"
   
5. Remember: review the code, not the person
   "This function" not "You wrote a function"
```

**Prevention:**
- Establish review culture early
- Lead by example (accept feedback gracefully)
- Frame as collaborative improvement
- Praise good work publicly

---

## Best Practices

### DO:
✅ **Review promptly** - Within 24 hours of PR creation  
✅ **Test the code** - Actually run it, don't just read  
✅ **Be specific** - Point to exact lines and suggest fixes  
✅ **Explain reasoning** - Help author learn  
✅ **Praise good code** - Acknowledge what's done well  
✅ **Ask questions** - When unsure, ask for clarification  
✅ **Focus on important issues** - Don't bikeshed minor details  
✅ **Be constructive** - Suggest improvements, don't just criticize

### DON'T:
❌ **Nitpick excessively** - Focus on substance over style  
❌ **Be vague** - "This is bad" → "Consider extracting this into..."  
❌ **Review your own PR** - Get fresh eyes  
❌ **Rubber stamp** - Actually review, don't just approve  
❌ **Block on minor issues** - Distinguish blocking vs. nice-to-have  
❌ **Be condescending** - Respect the author's effort  
❌ **Skip testing** - Code that looks good may not work  
❌ **Review when tired/rushed** - Quality matters

---

## Related Workflows

**Prerequisites:**
- [Test Writing](../development/test_writing.md) - Understanding test quality
- [Refactoring Strategy](../development/refactoring_strategy.md) - Recognizing when code needs refactoring
- [CI/CD Workflow](../development/ci_cd_workflow.md) - Understanding automated checks

**Next Steps:**
- [PR Creation and Review](./pr_creation_review.md) - Creating PRs that get approved quickly
- [Complexity Reduction](./complexity_reduction.md) - Simplifying complex code
- [Ruff Error Resolution](./ruff_error_resolution.md) - Fixing linting issues

**Related:**
- [Security Audit](../security/security_audit_logging.md) - Security review considerations
- [Performance Tuning](../devops/performance_tuning.md) - Performance optimization

---

## Tags
`quality-assurance` `code-review` `pull-requests` `best-practices` `teamwork` `mentoring` `quality`
