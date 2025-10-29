---
id: dev-009
title: Refactoring Strategy
category: Development
subcategory: Code Quality
tags:
  - refactoring
  - code-quality
  - technical-debt
  - clean-code
  - maintainability
prerequisites:
  - dev-002  # Test Writing
  - qa-001   # Code Review Checklist
related_workflows:
  - dev-016  # Technical Debt Identification
  - qa-008   # Complexity Reduction
  - dev-017  # CI/CD Pipeline
complexity: intermediate
estimated_time: 45-60 minutes
last_updated: 2025-10-25
---

# Refactoring Strategy

## Overview

**What:** Systematic approach to improving code structure, readability, and maintainability without changing external behavior.

**Why:** Refactoring reduces technical debt, makes code easier to understand and modify, prevents bugs, and improves team velocity. Good code is cheaper to maintain and extend.

**When to use:**
- Before adding new features to messy code
- After identifying code smells during reviews
- When tests become difficult to write
- After multiple bug fixes in the same area
- When code has grown organically without design
- During "boy scout rule" cleanups (leave code better than you found it)

---

## Prerequisites

**Required:**
- [ ] Comprehensive test suite (or ability to write tests)
- [ ] Version control (Git)
- [ ] Understanding of the code to be refactored
- [ ] Time allocation for refactoring (not rushed)

**Optional but recommended:**
- [ ] Code review culture
- [ ] Static analysis tools (ruff, mypy, pylint)
- [ ] CI/CD pipeline with automated tests

**Check before starting:**
```bash
# Verify you have good test coverage
pytest --cov=src --cov-report=term-missing
# Aim for >70% coverage before major refactoring

# Ensure all tests pass
pytest

# Create a backup branch
git checkout -b refactor/improve-user-service

# Check for uncommitted changes
git status

# Run linting to see current issues
ruff check src/
mypy src/
```

---

## Implementation Steps

### Step 1: Identify Refactoring Candidates

**What:** Systematically find code that needs refactoring using code smells, metrics, and tooling.

**How:** Use static analysis tools and code review to identify problems before starting work.

**Common code smells to look for:**

1. **Long Functions/Methods** (> 50 lines)
2. **Large Classes** (> 300 lines, too many responsibilities)
3. **Duplicated Code** (copy-pasted logic)
4. **Long Parameter Lists** (> 4 parameters)
5. **Complex Conditionals** (deeply nested if/else)
6. **Magic Numbers** (unexplained constants)
7. **Dead Code** (unused functions/classes)
8. **Poor Naming** (unclear variable/function names)
9. **God Objects** (classes that do everything)
10. **Feature Envy** (method uses another class more than its own)

**Tools to identify issues:**

```bash
# Complexity analysis
pip install radon
radon cc src/ -a -nb  # Cyclomatic complexity
radon mi src/ -nb     # Maintainability index

# Find duplicates
pip install pylint
pylint src/ --disable=all --enable=duplicate-code

# Code metrics
pip install flake8 flake8-cognitive-complexity
flake8 --max-complexity=10 src/

# Type checking (finds architectural issues)
mypy src/ --strict
```

**Example analysis:**

```python
# BEFORE (code smell: long method, too many responsibilities)
def process_order(order_data):
    """Process an order (BAD: does too much)."""
    # Validate (responsibility 1)
    if not order_data.get('customer_id'):
        raise ValueError("Missing customer")
    if not order_data.get('items'):
        raise ValueError("No items")
    
    # Calculate total (responsibility 2)
    total = 0
    for item in order_data['items']:
        total += item['price'] * item['quantity']
    
    # Apply discount (responsibility 3)
    if order_data.get('discount_code'):
        discount = get_discount(order_data['discount_code'])
        total *= (1 - discount)
    
    # Save to database (responsibility 4)
    db.execute(
        "INSERT INTO orders (customer_id, total, items) VALUES (%s, %s, %s)",
        (order_data['customer_id'], total, json.dumps(order_data['items']))
    )
    
    # Send email (responsibility 5)
    send_email(
        to=get_customer_email(order_data['customer_id']),
        subject="Order confirmed",
        body=f"Your order for ${total} is confirmed"
    )
    
    return total
```

**Create refactoring checklist:**

```markdown
## Refactoring Targets (Priority Order)

1. **process_order() function** - Too many responsibilities
   - Complexity: 15 (high)
   - Lines: 30
   - Issues: Violates Single Responsibility Principle
   
2. **UserService class** - God object (500 lines)
   - Too many methods (23)
   - Handles authentication, validation, emails, database
   
3. **calculate_price()** - Complex conditionals
   - Nested depth: 4
   - Duplicated logic in 3 places
```

**Verification:**
- [ ] Identified specific code smells with tools
- [ ] Prioritized issues by impact and effort
- [ ] Have concrete examples of problems
- [ ] Team agrees on refactoring targets

**If This Fails:**
→ Start with most obvious issues (duplication, long functions)
→ Ask for code review feedback on problem areas
→ Use metrics as guide, not absolute rules
→ Focus on pain points causing actual bugs

---

### Step 2: Write Tests Before Refactoring

**What:** Ensure comprehensive test coverage before making any changes to lock in current behavior.

**How:** Write tests for the existing functionality, even if it's imperfect, to prevent regressions.

**Critical rule:** **Never refactor without tests!**

```python
# Example: Testing the messy code BEFORE refactoring

# tests/test_order_processing.py
import pytest
from unittest.mock import Mock, patch
from src.orders import process_order


class TestProcessOrder:
    """Tests for existing process_order function (before refactoring)."""
    
    @patch('src.orders.db')
    @patch('src.orders.send_email')
    @patch('src.orders.get_customer_email')
    @patch('src.orders.get_discount')
    def test_process_order_success(
        self, 
        mock_discount, 
        mock_email, 
        mock_send, 
        mock_db
    ):
        """Test successful order processing (characterization test)."""
        # Arrange
        mock_discount.return_value = 0.1  # 10% discount
        mock_email.return_value = "customer@example.com"
        
        order_data = {
            'customer_id': 123,
            'items': [
                {'price': 10.0, 'quantity': 2},  # $20
                {'price': 5.0, 'quantity': 3},   # $15
            ],
            'discount_code': 'SAVE10'
        }
        
        # Act
        total = process_order(order_data)
        
        # Assert
        assert total == 31.5  # (20 + 15) * 0.9 = 31.5
        mock_db.execute.assert_called_once()
        mock_send.assert_called_once()
    
    def test_process_order_missing_customer(self):
        """Test validation: missing customer raises error."""
        with pytest.raises(ValueError, match="Missing customer"):
            process_order({'items': [{'price': 10, 'quantity': 1}]})
    
    def test_process_order_no_items(self):
        """Test validation: no items raises error."""
        with pytest.raises(ValueError, match="No items"):
            process_order({'customer_id': 123, 'items': []})
    
    @patch('src.orders.db')
    @patch('src.orders.send_email')
    def test_process_order_no_discount(self, mock_send, mock_db):
        """Test order without discount code."""
        order_data = {
            'customer_id': 123,
            'items': [{'price': 10.0, 'quantity': 1}]
        }
        
        total = process_order(order_data)
        
        assert total == 10.0  # No discount applied
```

**Run tests and ensure 100% pass:**

```bash
# Run tests
pytest tests/test_order_processing.py -v

# Check coverage
pytest --cov=src.orders --cov-report=term-missing

# Ensure all pass before refactoring
pytest --tb=short
```

**Verification:**
- [ ] All existing tests pass
- [ ] Coverage of code to be refactored is >= 80%
- [ ] Tests are fast (< 1 second total)
- [ ] Tests document current behavior (even if imperfect)
- [ ] Can run tests easily and frequently

**If This Fails:**
→ Write more tests until you have confidence
→ Start with happy path, then add edge cases
→ Use mocks to isolate the code being tested
→ Don't refactor if you can't write tests - fix that first

---

### Step 3: Make Small, Incremental Changes

**What:** Refactor in tiny steps, running tests after each change to ensure nothing breaks.

**How:** Follow the "red-green-refactor" cycle: make one small improvement, test it, commit it.

**Refactoring techniques (small steps):**

**1. Extract Method** - Break long function into smaller functions

```python
# BEFORE: Long method
def process_order(order_data):
    # Validate
    if not order_data.get('customer_id'):
        raise ValueError("Missing customer")
    if not order_data.get('items'):
        raise ValueError("No items")
    
    # Calculate
    total = sum(item['price'] * item['quantity'] for item in order_data['items'])
    
    # ... rest of function ...

# AFTER Step 1: Extract validation
def validate_order(order_data):
    """Validate order data."""
    if not order_data.get('customer_id'):
        raise ValueError("Missing customer")
    if not order_data.get('items'):
        raise ValueError("No items")

def process_order(order_data):
    validate_order(order_data)  # Extracted!
    
    total = sum(item['price'] * item['quantity'] for item in order_data['items'])
    # ... rest of function ...

# ✅ Run tests: pytest
# ✅ Commit: git commit -m "refactor: extract order validation"
```

**2. Extract Variable** - Name complex expressions

```python
# BEFORE: Magic number and unclear expression
def calculate_shipping(weight):
    return weight * 0.5 + 2.99 if weight > 10 else 5.99

# AFTER: Named constants and variables
def calculate_shipping(weight):
    COST_PER_POUND = 0.5
    HEAVY_BASE_FEE = 2.99
    LIGHT_FLAT_FEE = 5.99
    HEAVY_THRESHOLD = 10
    
    is_heavy = weight > HEAVY_THRESHOLD
    
    if is_heavy:
        return weight * COST_PER_POUND + HEAVY_BASE_FEE
    else:
        return LIGHT_FLAT_FEE

# ✅ Run tests
# ✅ Commit
```

**3. Introduce Parameter Object** - Replace long parameter lists

```python
# BEFORE: Too many parameters
def create_user(username, email, first_name, last_name, age, country, city):
    # ... implementation ...

# AFTER Step 1: Create data class
from dataclasses import dataclass

@dataclass
class UserData:
    username: str
    email: str
    first_name: str
    last_name: str
    age: int
    country: str
    city: str

def create_user(user_data: UserData):
    # ... implementation ...

# ✅ Run tests
# ✅ Commit
```

**4. Replace Conditional with Polymorphism**

```python
# BEFORE: Type checking
def calculate_area(shape):
    if shape['type'] == 'circle':
        return 3.14 * shape['radius'] ** 2
    elif shape['type'] == 'rectangle':
        return shape['width'] * shape['height']
    elif shape['type'] == 'triangle':
        return 0.5 * shape['base'] * shape['height']

# AFTER: Use classes
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius
    
    def area(self) -> float:
        return 3.14 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    
    def area(self) -> float:
        return self.width * self.height

# ✅ Run tests
# ✅ Commit
```

**The golden rule:**
```bash
# After EVERY small change:
pytest  # All tests must pass
git add .
git commit -m "refactor: <describe small change>"
```

**Verification:**
- [ ] Each change is small (< 20 lines modified)
- [ ] Tests pass after every change
- [ ] Each commit has a single purpose
- [ ] Can easily revert if something breaks
- [ ] Progress is steady and measurable

**If This Fails:**
→ Make even smaller changes (1-2 line edits)
→ If tests fail, immediately revert: `git checkout .`
→ Don't continue if tests are red
→ Take breaks between changes to maintain focus

---

### Step 4: Apply SOLID Principles

**What:** Refactor code to follow SOLID design principles for better maintainability.

**How:** Systematically apply each principle to improve code structure.

**S - Single Responsibility Principle**
*A class should have only one reason to change*

```python
# BEFORE: Multiple responsibilities
class UserManager:
    def create_user(self, data):
        # Validate
        if not data.get('email'):
            raise ValueError("Email required")
        
        # Save to database
        db.execute("INSERT INTO users ...")
        
        # Send welcome email
        send_email(data['email'], "Welcome!")
        
        # Log activity
        logger.info(f"User created: {data['email']}")

# AFTER: Separated responsibilities
class UserValidator:
    """Responsible only for validation."""
    def validate(self, data):
        if not data.get('email'):
            raise ValueError("Email required")

class UserRepository:
    """Responsible only for database operations."""
    def save(self, user):
        db.execute("INSERT INTO users ...", user)

class EmailService:
    """Responsible only for emails."""
    def send_welcome_email(self, email):
        send_email(email, "Welcome!")

class UserService:
    """Orchestrates user creation."""
    def __init__(self):
        self.validator = UserValidator()
        self.repository = UserRepository()
        self.email_service = EmailService()
    
    def create_user(self, data):
        self.validator.validate(data)
        user = self.repository.save(data)
        self.email_service.send_welcome_email(data['email'])
        return user
```

**O - Open/Closed Principle**
*Open for extension, closed for modification*

```python
# BEFORE: Must modify for new payment types
class PaymentProcessor:
    def process(self, payment_type, amount):
        if payment_type == 'credit_card':
            return self._process_credit_card(amount)
        elif payment_type == 'paypal':
            return self._process_paypal(amount)
        # Must modify this method for each new type!

# AFTER: Extensible without modification
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def process(self, amount: float) -> bool:
        pass

class CreditCardPayment(PaymentMethod):
    def process(self, amount: float) -> bool:
        # Credit card logic
        return True

class PayPalPayment(PaymentMethod):
    def process(self, amount: float) -> bool:
        # PayPal logic
        return True

class PaymentProcessor:
    def process(self, payment_method: PaymentMethod, amount: float):
        return payment_method.process(amount)

# Add new payment type WITHOUT modifying existing code
class BitcoinPayment(PaymentMethod):
    def process(self, amount: float) -> bool:
        # Bitcoin logic
        return True
```

**L - Liskov Substitution Principle**
*Subclasses should be substitutable for their base classes*

```python
# BEFORE: Violates LSP
class Rectangle:
    def set_width(self, width):
        self.width = width
    
    def set_height(self, height):
        self.height = height

class Square(Rectangle):
    def set_width(self, width):
        self.width = width
        self.height = width  # Violates expectation!
    
    def set_height(self, height):
        self.width = height
        self.height = height

# This breaks:
def test_rectangle(rect: Rectangle):
    rect.set_width(5)
    rect.set_height(10)
    assert rect.width * rect.height == 50  # Fails for Square!

# AFTER: Proper abstraction
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    
    def area(self) -> float:
        return self.width * self.height

class Square(Shape):
    def __init__(self, side: float):
        self.side = side
    
    def area(self) -> float:
        return self.side * self.side
```

**I - Interface Segregation Principle**
*Clients shouldn't depend on interfaces they don't use*

```python
# BEFORE: Fat interface
class Worker(ABC):
    @abstractmethod
    def work(self): pass
    
    @abstractmethod
    def eat(self): pass
    
    @abstractmethod
    def sleep(self): pass

class Robot(Worker):
    def work(self): return "Working"
    def eat(self): raise NotImplementedError("Robots don't eat!")
    def sleep(self): raise NotImplementedError("Robots don't sleep!")

# AFTER: Segregated interfaces
class Workable(ABC):
    @abstractmethod
    def work(self): pass

class Eatable(ABC):
    @abstractmethod
    def eat(self): pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self): pass

class Human(Workable, Eatable, Sleepable):
    def work(self): return "Working"
    def eat(self): return "Eating"
    def sleep(self): return "Sleeping"

class Robot(Workable):  # Only implements what it needs
    def work(self): return "Working"
```

**D - Dependency Inversion Principle**
*Depend on abstractions, not concretions*

```python
# BEFORE: Tight coupling to concrete implementations
class EmailService:
    def send(self, to, message):
        # Sends via Gmail
        gmail_api.send(to, message)

class UserService:
    def __init__(self):
        self.email_service = EmailService()  # Tight coupling!
    
    def notify_user(self, user, message):
        self.email_service.send(user.email, message)

# AFTER: Dependency injection with abstractions
from abc import ABC, abstractmethod

class MessageSender(ABC):
    @abstractmethod
    def send(self, to: str, message: str): pass

class EmailSender(MessageSender):
    def send(self, to: str, message: str):
        # Gmail implementation
        pass

class SMSSender(MessageSender):
    def send(self, to: str, message: str):
        # SMS implementation
        pass

class UserService:
    def __init__(self, message_sender: MessageSender):
        self.message_sender = message_sender  # Injected dependency
    
    def notify_user(self, user, message):
        self.message_sender.send(user.contact, message)

# Easy to test with mocks
def test_user_notification():
    mock_sender = Mock(spec=MessageSender)
    service = UserService(mock_sender)
    service.notify_user(user, "Hello")
    mock_sender.send.assert_called_once()
```

**Verification:**
- [ ] Classes have single, clear responsibilities
- [ ] Can add new functionality without modifying existing code
- [ ] Subclasses are truly interchangeable
- [ ] Interfaces are minimal and focused
- [ ] Dependencies are injected, not hardcoded

**If This Fails:**
→ Apply one principle at a time
→ Start with Single Responsibility (easiest)
→ Don't over-engineer - SOLID is a guide, not a law
→ Focus on making code testable and readable

---

### Step 5: Improve Names and Readability

**What:** Refactor names, formatting, and structure to make code self-documenting.

**How:** Apply consistent naming conventions and simplify complex expressions.

**Naming improvements:**

```python
# BEFORE: Poor names
def f(x, y):
    return x * y * 0.2

def proc_usr_dat(d):
    return {'id': d[0], 'n': d[1], 'em': d[2]}

# AFTER: Clear names
def calculate_discount(original_price: float, discount_rate: float) -> float:
    """Calculate discounted price with 20% cap."""
    MAXIMUM_DISCOUNT_RATE = 0.2
    effective_rate = min(discount_rate, MAXIMUM_DISCOUNT_RATE)
    return original_price * effective_rate

def parse_user_data(raw_data: tuple) -> dict:
    """Convert raw database tuple to user dictionary."""
    user_id, name, email = raw_data
    return {
        'id': user_id,
        'name': name,
        'email': email
    }
```

**Remove magic numbers:**

```python
# BEFORE: Magic numbers
def is_valid_age(age):
    return age >= 18 and age <= 120

def calculate_fee(amount):
    if amount > 100:
        return amount * 0.05
    return 2.50

# AFTER: Named constants
MIN_ADULT_AGE = 18
MAX_REASONABLE_AGE = 120
HIGH_AMOUNT_THRESHOLD = 100
HIGH_AMOUNT_FEE_RATE = 0.05
LOW_AMOUNT_FLAT_FEE = 2.50

def is_valid_age(age: int) -> bool:
    """Check if age is within valid adult range."""
    return MIN_ADULT_AGE <= age <= MAX_REASONABLE_AGE

def calculate_fee(amount: float) -> float:
    """Calculate transaction fee based on amount."""
    if amount > HIGH_AMOUNT_THRESHOLD:
        return amount * HIGH_AMOUNT_FEE_RATE
    return LOW_AMOUNT_FLAT_FEE
```

**Simplify boolean logic:**

```python
# BEFORE: Complex boolean expressions
if not (user.is_active and user.email_verified) or user.banned:
    return False
if user.subscription_type == 'premium' or user.subscription_type == 'enterprise':
    return True
return False

# AFTER: Extracted methods with clear names
def can_access_feature(user: User) -> bool:
    """Check if user can access premium feature."""
    if not is_user_in_good_standing(user):
        return False
    
    return has_premium_subscription(user)

def is_user_in_good_standing(user: User) -> bool:
    """Check if user account is active and valid."""
    return user.is_active and user.email_verified and not user.banned

def has_premium_subscription(user: User) -> bool:
    """Check if user has a premium subscription."""
    premium_tiers = {'premium', 'enterprise'}
    return user.subscription_type in premium_tiers
```

**Add type hints:**

```python
# BEFORE: No type information
def process_items(items, config):
    results = []
    for item in items:
        result = transform(item, config)
        results.append(result)
    return results

# AFTER: Type hints document interface
from typing import List, Dict, Any

def process_items(
    items: List[Dict[str, Any]], 
    config: ProcessingConfig
) -> List[ProcessedItem]:
    """Transform raw items using configuration.
    
    Args:
        items: List of raw item dictionaries
        config: Processing configuration
        
    Returns:
        List of processed item objects
    """
    results: List[ProcessedItem] = []
    
    for item in items:
        result = transform(item, config)
        results.append(result)
    
    return results
```

**Verification:**
- [ ] Variable/function names describe purpose
- [ ] No magic numbers (all constants named)
- [ ] Type hints on all public functions
- [ ] Complex logic is broken into named functions
- [ ] Code reads like prose

**If This Fails:**
→ Use linter rules to enforce naming (ruff/pylint)
→ Ask "would a new developer understand this?"
→ Read code aloud - awkward reading means unclear code
→ Use IDE refactoring tools (rename symbol)

---

### Step 6: Remove Duplication

**What:** Identify and eliminate duplicated code through extraction and abstraction.

**How:** Use the DRY (Don't Repeat Yourself) principle to create reusable components.

**Find duplication:**

```bash
# Use pylint to find duplicates
pylint src/ --disable=all --enable=duplicate-code --min-similarity-lines=4

# Manual inspection
grep -r "def calculate" src/  # Find similar function names
```

**Pattern 1: Extract common function**

```python
# BEFORE: Duplicated validation logic
class UserController:
    def create_user(self, data):
        if not data.get('email'):
            raise ValueError("Email required")
        if not '@' in data['email']:
            raise ValueError("Invalid email")
        # ... create user ...
    
    def update_email(self, user_id, email):
        if not email:
            raise ValueError("Email required")
        if not '@' in email:
            raise ValueError("Invalid email")
        # ... update email ...

# AFTER: Extracted validation
class UserController:
    def _validate_email(self, email: str) -> None:
        """Validate email format."""
        if not email:
            raise ValueError("Email required")
        if '@' not in email:
            raise ValueError("Invalid email")
    
    def create_user(self, data):
        self._validate_email(data.get('email', ''))
        # ... create user ...
    
    def update_email(self, user_id, email):
        self._validate_email(email)
        # ... update email ...
```

**Pattern 2: Template method pattern**

```python
# BEFORE: Duplicated structure
class PremiumReport:
    def generate(self):
        print("Fetching premium data...")
        data = fetch_premium_data()
        print("Processing premium data...")
        processed = process_data(data)
        print("Formatting premium report...")
        return format_report(processed)

class BasicReport:
    def generate(self):
        print("Fetching basic data...")
        data = fetch_basic_data()
        print("Processing basic data...")
        processed = process_data(data)
        print("Formatting basic report...")
        return format_report(processed)

# AFTER: Template method (DRY)
from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    """Template for report generation."""
    
    def generate(self):
        """Generate report following standard steps."""
        print(f"Fetching {self.report_type} data...")
        data = self.fetch_data()
        
        print(f"Processing {self.report_type} data...")
        processed = self.process_data(data)
        
        print(f"Formatting {self.report_type} report...")
        return self.format_report(processed)
    
    @property
    @abstractmethod
    def report_type(self) -> str:
        pass
    
    @abstractmethod
    def fetch_data(self):
        pass
    
    def process_data(self, data):
        # Common processing
        return data
    
    def format_report(self, data):
        # Common formatting
        return f"Report: {data}"

class PremiumReport(ReportGenerator):
    report_type = "premium"
    
    def fetch_data(self):
        return fetch_premium_data()

class BasicReport(ReportGenerator):
    report_type = "basic"
    
    def fetch_data(self):
        return fetch_basic_data()
```

**Pattern 3: Configuration over duplication**

```python
# BEFORE: Copy-pasted similar functions
def send_welcome_email(email):
    send_email(
        to=email,
        subject="Welcome!",
        template="welcome.html",
        from_address="noreply@example.com"
    )

def send_reset_email(email):
    send_email(
        to=email,
        subject="Password Reset",
        template="reset.html",
        from_address="noreply@example.com"
    )

def send_notification_email(email):
    send_email(
        to=email,
        subject="Notification",
        template="notification.html",
        from_address="noreply@example.com"
    )

# AFTER: Configuration-driven
from enum import Enum
from dataclasses import dataclass

class EmailType(Enum):
    WELCOME = "welcome"
    RESET = "reset"
    NOTIFICATION = "notification"

@dataclass
class EmailConfig:
    subject: str
    template: str
    from_address: str = "noreply@example.com"

EMAIL_CONFIGS = {
    EmailType.WELCOME: EmailConfig(
        subject="Welcome!",
        template="welcome.html"
    ),
    EmailType.RESET: EmailConfig(
        subject="Password Reset",
        template="reset.html"
    ),
    EmailType.NOTIFICATION: EmailConfig(
        subject="Notification",
        template="notification.html"
    ),
}

def send_templated_email(email: str, email_type: EmailType):
    """Send email using configuration."""
    config = EMAIL_CONFIGS[email_type]
    
    send_email(
        to=email,
        subject=config.subject,
        template=config.template,
        from_address=config.from_address
    )
```

**Verification:**
- [ ] No duplicated code blocks > 3 lines
- [ ] Common patterns extracted to utilities
- [ ] Configuration used instead of code duplication
- [ ] Tests verify extracted code works correctly

**If This Fails:**
→ Use copy-paste detector tools
→ Start with most duplicated code first
→ Don't over-DRY (some duplication is okay if abstraction is unclear)
→ Extract after 3rd use, not 2nd (Rule of Three)

---

### Step 7: Run Full Test Suite and Quality Checks

**What:** Verify all refactoring hasn't broken anything and improved code quality metrics.

**How:** Run comprehensive tests, linting, and static analysis to validate improvements.

**Full verification:**

```bash
# 1. Run all tests
pytest -v

# 2. Check coverage hasn't decreased
pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# 3. Run linting
ruff check src/

# 4. Type checking
mypy src/ --strict

# 5. Security scan
bandit -r src/

# 6. Complexity analysis
radon cc src/ -a -nb
radon mi src/ -nb

# 7. Check for common issues
pylint src/

# 8. Format code
black src/
isort src/
```

**Compare metrics before/after:**

```bash
# Before refactoring:
# Complexity: 15 (high)
# Maintainability: 45/100 (low)
# Coverage: 65%
# Duplicated code: 15%

# After refactoring:
# Complexity: 8 (moderate)
# Maintainability: 72/100 (good)
# Coverage: 82%
# Duplicated code: 2%
```

**Integration testing:**

```bash
# Run integration tests
pytest -m integration

# Run full system tests if available
pytest tests/e2e/

# Manual smoke testing
python -m src.main  # Does it still start?
curl localhost:8000/health  # Does API respond?
```

**Performance check:**

```python
# Ensure refactoring didn't slow things down
import time

def test_performance_unchanged():
    """Verify refactored code isn't slower."""
    import time
    from src.orders import process_order
    
    start = time.time()
    for _ in range(1000):
        process_order(sample_order_data)
    duration = time.time() - start
    
    # Should complete in reasonable time
    assert duration < 5.0, f"Too slow: {duration}s"
```

**Verification:**
- [ ] All tests pass (100%)
- [ ] Coverage maintained or improved
- [ ] No new linting errors
- [ ] Type checking passes
- [ ] Complexity reduced
- [ ] No performance regression
- [ ] Manual smoke test passes

**If This Fails:**
→ Review each failing test individually
→ Use git bisect to find problem commit: `git bisect start`
→ Roll back problematic changes: `git revert <commit>`
→ Fix issues incrementally, not all at once

---

### Step 8: Document and Review

**What:** Document changes, update relevant documentation, and get code review.

**How:** Create comprehensive pull request with clear explanations of refactoring.

**Update documentation:**

```python
# Add docstrings to refactored code
class UserService:
    """Service for user management operations.
    
    This service handles user creation, validation, and email notifications.
    It coordinates between UserRepository, EmailService, and validation logic.
    
    Example:
        >>> service = UserService(db_repo, email_service)
        >>> user = service.create_user({'email': 'user@example.com'})
    """
    
    def create_user(self, user_data: dict) -> User:
        """Create a new user account.
        
        Args:
            user_data: Dictionary containing user information.
                Required keys: 'email', 'username'
        
        Returns:
            Created User object
            
        Raises:
            ValueError: If validation fails
            DatabaseError: If save operation fails
        """
        pass
```

**Update README/docs:**

```markdown
# Architecture Changes (2025-10-25)

## Refactoring: User Management Module

### Changes Made:
- Split `UserManager` into separate responsibilities:
  - `UserValidator`: Input validation
  - `UserRepository`: Database operations
  - `EmailService`: Email notifications
  - `UserService`: Orchestration

### Benefits:
- Each class now has single responsibility
- Easier to test (can mock dependencies)
- Easier to extend (add new notification channels)
- Reduced complexity from 15 → 7 per class

### Migration Guide:
```python
# Old way:
manager = UserManager()
user = manager.create_user(data)

# New way:
repository = UserRepository(db)
email_service = EmailService(smtp_config)
service = UserService(repository, email_service)
user = service.create_user(data)
```
```

**Create detailed PR:**

```markdown
## Pull Request: Refactor User Management Module

### Summary
Refactored `UserManager` to follow Single Responsibility Principle, 
reducing complexity and improving testability.

### Motivation
- Original class was 500 lines, doing too much
- Difficulty writing tests due to tight coupling
- Hard to extend with new features

### Changes
1. **Extracted UserValidator** - Handles all input validation
2. **Extracted UserRepository** - Database operations only
3. **Extracted EmailService** - Email sending logic
4. **Created UserService** - Orchestrates above services

### Metrics Improved
- Complexity: 15 → 7 (per class)
- Test coverage: 65% → 85%
- Duplicated code: 12% → 2%

### Testing
- ✅ All existing tests pass
- ✅ Added 15 new unit tests
- ✅ Integration tests updated
- ✅ Manual smoke testing completed

### Breaking Changes
⚠️ API interface changed (see migration guide above)

### Checklist
- [x] Tests pass
- [x] Documentation updated
- [x] No performance regression
- [x] Code reviewed by team
- [x] Migration guide provided
```

**Request code review:**

```bash
# Push refactoring branch
git push origin refactor/user-management

# Create PR on GitHub/GitLab
# Request review from team members
# Address feedback
```

**Verification:**
- [ ] All code is documented
- [ ] README reflects changes
- [ ] Migration guide provided (if API changed)
- [ ] PR description is comprehensive
- [ ] Code review completed
- [ ] Team approves changes

**If This Fails:**
→ Break large PR into smaller, focused PRs
→ Provide more context in descriptions
→ Pair program on complex changes
→ Schedule team walkthrough for major refactors

---

## Verification Checklist

After completing this workflow:

- [ ] All tests pass after refactoring
- [ ] Code complexity reduced (measurable)
- [ ] Test coverage maintained or improved
- [ ] No duplicated code remains
- [ ] SOLID principles followed
- [ ] Code is more readable
- [ ] Documentation updated
- [ ] Team reviewed and approved changes
- [ ] No performance regressions
- [ ] Changes deployed successfully

---

## Best Practices

### DO:
✅ Write tests BEFORE refactoring (safety net)
✅ Make small, incremental changes
✅ Run tests after every change
✅ Commit frequently with clear messages
✅ Focus on one smell at a time
✅ Keep the interface stable (avoid breaking changes)
✅ Measure improvements with metrics
✅ Get code review on large refactorings
✅ Document architectural decisions
✅ Leave code better than you found it (Boy Scout Rule)
✅ Timebox refactoring (don't perfect forever)

### DON'T:
❌ Refactor without tests
❌ Mix refactoring with feature development
❌ Make large changes all at once
❌ Change behavior during refactoring
❌ Ignore test failures
❌ Refactor in production on Friday afternoon
❌ Over-engineer solutions
❌ Argue about perfection (good enough is good enough)
❌ Skip code review for "minor" refactorings
❌ Refactor code you don't understand

---

## Common Patterns

### Pattern 1: Strangler Fig (Gradual Replacement)
```python
# Gradually replace old code without breaking system

# Step 1: Create new implementation
class NewUserService:
    def create_user(self, data):
        # New, better implementation
        pass

# Step 2: Add feature flag
USE_NEW_SERVICE = os.getenv('USE_NEW_USER_SERVICE', 'false') == 'true'

def create_user(data):
    if USE_NEW_SERVICE:
        return NewUserService().create_user(data)
    else:
        return OldUserManager().create_user(data)

# Step 3: Gradually roll out
# Step 4: Remove old implementation when confident
```

### Pattern 2: Branch by Abstraction
```python
# Refactor behind interface, switch implementations

from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount): pass

class OldPaymentGateway(PaymentGateway):
    def charge(self, amount):
        # Old implementation
        pass

class NewPaymentGateway(PaymentGateway):
    def charge(self, amount):
        # New refactored implementation
        pass

# Configure which implementation to use
def get_payment_gateway() -> PaymentGateway:
    if os.getenv('USE_NEW_GATEWAY'):
        return NewPaymentGateway()
    return OldPaymentGateway()
```

### Pattern 3: Parallel Run (Verification)
```python
# Run both old and new code, compare results

def process_order(order_data):
    # Old implementation
    old_result = old_process_order(order_data)
    
    # New implementation
    try:
        new_result = new_process_order(order_data)
        
        # Compare results
        if old_result != new_result:
            logger.warning(f"Results differ: {old_result} vs {new_result}")
    except Exception as e:
        logger.error(f"New implementation failed: {e}")
    
    # Always return old result (safe)
    return old_result

# Once confident, switch to new_result
```

---

## Troubleshooting

### Issue: Tests fail after refactoring

**Symptoms:**
- Tests that passed before now fail
- Unclear which change broke tests
- Too many failing tests to fix

**Solutions:**
```bash
# 1. Revert to last working state
git log --oneline  # Find last good commit
git reset --hard <commit>

# 2. Reapply changes incrementally
git cherry-pick <commit>  # One at a time
pytest  # After each

# 3. Use git bisect to find problem
git bisect start
git bisect bad  # Current broken state
git bisect good <last-working-commit>
# Git will checkout commits for you to test
pytest && git bisect good || git bisect bad

# 4. Fix incrementally
pytest --lf  # Run only last failed
pytest -x  # Stop at first failure
```

**Prevention:**
- Commit after every passing test run
- Make smaller changes
- Use feature branches for experiments

---

### Issue: Performance degraded

**Symptoms:**
- Tests take longer to run
- Application is slower
- Requests timeout

**Solutions:**
```python
# 1. Profile the code
import cProfile
import pstats

cProfile.run('slow_function()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(10)

# 2. Find specific bottleneck
import time

def timed_function(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.time() - start:.2f}s")
        return result
    return wrapper

# 3. Compare before/after with benchmarks
import pytest

@pytest.mark.benchmark
def test_performance():
    result = expensive_operation()
    # Track timing across commits
```

**Prevention:**
- Run performance tests as part of CI
- Profile before major refactoring
- Keep performance benchmarks

---

### Issue: Too many changes to review

**Symptoms:**
- PR has 1000+ lines changed
- Reviewers confused by scope
- PR sits unreviewed

**Solutions:**
```bash
# 1. Break into smaller PRs
git log --oneline  # Review commits
git rebase -i HEAD~10  # Split commits

# Create multiple PRs:
# PR 1: Extract validation logic
# PR 2: Extract database layer
# PR 3: Extract email service
# PR 4: Wire everything together

# 2. Use stacked PRs
git checkout main
git checkout -b refactor-step-1
# Make changes, create PR

git checkout -b refactor-step-2
# Make changes, create PR (based on step-1)

# 3. Provide detailed context
# Use PR templates
# Add diagrams
# Record video walkthrough
```

**Prevention:**
- Plan refactoring in stages
- Create tracking issue with checklist
- Commit and PR frequently

---

## Related Workflows

**Prerequisites:**
- [[test_writing]] - Need tests before refactoring safely
- [[code_review_checklist]] - Learn what good code looks like

**Next Steps:**
- [[technical_debt_identification]] - Find more refactoring opportunities
- [[complexity_reduction]] - Specific techniques for simplification
- [[ci_cd_workflow]] - Automate quality checks

**Related:**
- [[type_annotation_addition]] - Improve type safety during refactoring
- [[performance_tuning]] - Optimize while refactoring
- [[developer_onboarding]] - Teach new developers clean code

---

## Tags
`development` `refactoring` `code-quality` `technical-debt` `clean-code` `maintainability` `solid-principles` `testing` `best-practices`
