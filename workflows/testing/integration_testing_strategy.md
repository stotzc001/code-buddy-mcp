# Integration Testing Strategy

**ID:** tes-001  
**Category:** Testing  
**Complexity:** Intermediate  
**Estimated Time:** 2-4 hours (setup), 30 minutes per test suite  
**Prerequisites:** Understanding of system components, unit testing basics  

---

## Overview

Integration testing verifies that different parts of your system work together correctly. This workflow helps you design and implement effective integration tests that catch issues unit tests miss while remaining faster and more reliable than end-to-end tests.

**When to Use:**
- Testing interactions between components/services
- Verifying API contracts
- Testing database operations
- Validating third-party integrations
- Ensuring correct data flow between layers

**Integration vs Unit vs E2E:**
```markdown
| Type | Scope | Speed | Reliability | Cost | When to Use |
|------|-------|-------|-------------|------|-------------|
| Unit | Single function/class | Fast | High | Low | Logic, calculations |
| Integration | Multiple components | Medium | Medium | Medium | Component interactions |
| E2E | Full system | Slow | Low | High | Critical user flows |
```

---

## Quick Start

```python
# Example: Testing API endpoint with database
import pytest
from app import create_app
from database import db

@pytest.fixture
def client():
    app = create_app(config='testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_create_user_integration(client):
    # POST to API
    response = client.post('/api/users', json={
        'name': 'John Doe',
        'email': 'john@example.com'
    })
    
    assert response.status_code == 201
    
    # Verify in database
    user = db.session.query(User).filter_by(email='john@example.com').first()
    assert user is not None
    assert user.name == 'John Doe'
```

---

## Testing Pyramid Strategy

```
        /\
       /  \       E2E Tests (10%)
      /----\      Few, slow, expensive
     /      \     Critical user journeys
    /--------\    
   /          \   Integration Tests (30%)
  /------------\  Component interactions
 /              \ API endpoints, databases
/----------------\
                  Unit Tests (60%)
                  Many, fast, cheap
                  Business logic, utilities
```

---

## Step-by-Step Guide

### Phase 1: Identify Integration Boundaries (30 minutes)

**Map Your System:**

```markdown
## Example: E-commerce System

**Integration Points:**
1. API ↔ Database
   - User CRUD operations
   - Order processing
   - Product catalog

2. API ↔ Payment Service (Stripe)
   - Payment processing
   - Webhook handling
   - Refund processing

3. API ↔ Email Service
   - Order confirmations
   - Password resets
   - Notifications

4. Frontend ↔ API
   - Authentication flow
   - Shopping cart
   - Checkout process

5. Message Queue ↔ Workers
   - Order fulfillment
   - Inventory updates
   - Report generation

**Priority for Integration Tests:**
1. Payment processing (critical, external)
2. Order flow (critical, multi-component)
3. Authentication (critical, security)
4. Email notifications (important, external)
5. Report generation (nice-to-have, async)
```

---

### Phase 2: Set Up Test Infrastructure (1-2 hours)

**Test Database Setup:**

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Order, Product

@pytest.fixture(scope='session')
def test_db():
    """Create test database for entire test session."""
    engine = create_engine('postgresql://localhost/test_db')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope='function')
def db_session(test_db):
    """Create a new database session for each test."""
    connection = test_db.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_data(db_session):
    """Seed database with test data."""
    user = User(name='Test User', email='test@example.com')
    product = Product(name='Test Product', price=99.99)
    db_session.add(user)
    db_session.add(product)
    db_session.commit()
    
    return {'user': user, 'product': product}
```

**Test API Client:**

```python
# tests/conftest.py (continued)
from app import create_app

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app({
        'TESTING': True,
        'DATABASE_URL': 'postgresql://localhost/test_db',
        'WTF_CSRF_ENABLED': False
    })
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def auth_client(client, sample_data):
    """Create authenticated test client."""
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = response.json['token']
    
    # Create client with auth header
    class AuthClient:
        def __init__(self, client, token):
            self.client = client
            self.token = token
        
        def get(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['Authorization'] = f'Bearer {self.token}'
            return self.client.get(*args, **kwargs)
        
        def post(self, *args, **kwargs):
            kwargs.setdefault('headers', {})['Authorization'] = f'Bearer {self.token}'
            return self.client.post(*args, **kwargs)
    
    return AuthClient(client, token)
```

**External Service Mocking:**

```python
# tests/conftest.py (continued)
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_stripe():
    """Mock Stripe API calls."""
    with patch('stripe.PaymentIntent') as mock_payment:
        mock_payment.create.return_value = Mock(
            id='pi_test_123',
            status='succeeded',
            amount=9999
        )
        yield mock_payment

@pytest.fixture
def mock_email():
    """Mock email service."""
    with patch('app.services.email.send_email') as mock_send:
        yield mock_send
```

---

### Phase 3: Write Integration Tests (ongoing)

**API + Database Integration:**

```python
# tests/integration/test_orders.py

def test_create_order_integration(auth_client, db_session, sample_data):
    """Test complete order creation flow."""
    
    # 1. Create order via API
    response = auth_client.post('/api/orders', json={
        'product_id': sample_data['product'].id,
        'quantity': 2
    })
    
    assert response.status_code == 201
    order_id = response.json['id']
    
    # 2. Verify order in database
    order = db_session.query(Order).get(order_id)
    assert order is not None
    assert order.user_id == sample_data['user'].id
    assert order.product_id == sample_data['product'].id
    assert order.quantity == 2
    assert order.total == 199.98  # 2 * 99.99
    
    # 3. Verify inventory updated
    product = db_session.query(Product).get(sample_data['product'].id)
    assert product.stock == sample_data['product'].stock - 2
    
    # 4. Verify order status
    assert order.status == 'pending'

def test_order_with_payment_integration(
    auth_client, db_session, sample_data, mock_stripe, mock_email
):
    """Test order creation with payment processing."""
    
    # 1. Create and pay for order
    response = auth_client.post('/api/orders', json={
        'product_id': sample_data['product'].id,
        'quantity': 1,
        'payment_method': 'pm_test_123'
    })
    
    assert response.status_code == 201
    order_id = response.json['id']
    
    # 2. Verify Stripe was called
    mock_stripe.create.assert_called_once()
    call_args = mock_stripe.create.call_args
    assert call_args[1]['amount'] == 9999
    assert call_args[1]['currency'] == 'usd'
    
    # 3. Verify order status updated
    order = db_session.query(Order).get(order_id)
    assert order.status == 'paid'
    assert order.payment_id == 'pi_test_123'
    
    # 4. Verify confirmation email sent
    mock_email.assert_called_once()
    assert 'Order Confirmation' in mock_email.call_args[0][1]
```

**Service-to-Service Integration:**

```python
# tests/integration/test_inventory_service.py

def test_inventory_update_via_message_queue(
    db_session, sample_data, message_queue
):
    """Test inventory updates via message queue."""
    
    # 1. Send inventory update message
    message_queue.publish('inventory.update', {
        'product_id': sample_data['product'].id,
        'quantity': -5,
        'reason': 'sale'
    })
    
    # 2. Wait for message to be processed
    message_queue.wait_for_processing()
    
    # 3. Verify database updated
    db_session.refresh(sample_data['product'])
    assert sample_data['product'].stock == sample_data['product'].stock - 5
    
    # 4. Verify audit log created
    audit = db_session.query(InventoryAudit).filter_by(
        product_id=sample_data['product'].id
    ).first()
    assert audit is not None
    assert audit.quantity_change == -5
    assert audit.reason == 'sale'
```

**Third-Party Integration:**

```python
# tests/integration/test_stripe_integration.py

def test_stripe_webhook_handling(client, db_session, sample_data):
    """Test handling of Stripe webhooks."""
    
    # 1. Create pending order
    order = Order(
        user_id=sample_data['user'].id,
        product_id=sample_data['product'].id,
        total=99.99,
        status='pending',
        payment_id='pi_test_123'
    )
    db_session.add(order)
    db_session.commit()
    
    # 2. Simulate Stripe webhook
    webhook_payload = {
        'type': 'payment_intent.succeeded',
        'data': {
            'object': {
                'id': 'pi_test_123',
                'status': 'succeeded',
                'amount': 9999
            }
        }
    }
    
    response = client.post(
        '/api/webhooks/stripe',
        json=webhook_payload,
        headers={'Stripe-Signature': 'test_signature'}
    )
    
    assert response.status_code == 200
    
    # 3. Verify order updated
    db_session.refresh(order)
    assert order.status == 'paid'
    
    # 4. Verify fulfillment triggered
    fulfillment = db_session.query(Fulfillment).filter_by(
        order_id=order.id
    ).first()
    assert fulfillment is not None
    assert fulfillment.status == 'pending'
```

---

### Phase 4: Test Data Management

**Test Data Builders:**

```python
# tests/builders.py

class UserBuilder:
    """Builder for creating test users."""
    
    def __init__(self):
        self.name = 'Test User'
        self.email = 'test@example.com'
        self.is_admin = False
    
    def with_name(self, name):
        self.name = name
        return self
    
    def with_email(self, email):
        self.email = email
        return self
    
    def as_admin(self):
        self.is_admin = True
        return self
    
    def build(self, db_session):
        user = User(
            name=self.name,
            email=self.email,
            is_admin=self.is_admin
        )
        db_session.add(user)
        db_session.commit()
        return user

# Usage
user = UserBuilder().with_name('Admin User').as_admin().build(db_session)
```

**Fixtures with Factories:**

```python
# tests/conftest.py
import factory
from app.models import User, Product, Order

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db_session
    
    name = factory.Faker('name')
    email = factory.Faker('email')
    created_at = factory.Faker('date_time')

class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Product
        sqlalchemy_session = db_session
    
    name = factory.Faker('word')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2)
    stock = factory.Faker('random_int', min=0, max=1000)

# Usage in tests
def test_bulk_order(db_session):
    users = UserFactory.create_batch(5)
    products = ProductFactory.create_batch(10)
    
    for user in users:
        order = Order(user_id=user.id, product_id=products[0].id)
        db_session.add(order)
    
    db_session.commit()
```

---

## Best Practices

### DO:
✅ **Test realistic scenarios** - Use cases that mirror production  
✅ **Isolate between tests** - Each test starts with clean state  
✅ **Mock external services** - Don't depend on third-party availability  
✅ **Test error paths** - Not just happy path  
✅ **Keep tests fast** - Use transactions, avoid unnecessary waits  
✅ **Test data flow** - Verify data moves correctly between layers  

### DON'T:
❌ **Test implementation details** - Focus on behavior  
❌ **Share state between tests** - Leads to flaky tests  
❌ **Hit real external APIs** - Use mocks/stubs  
❌ **Make tests too complex** - Each test should test one thing  
❌ **Ignore test data** - Good fixtures make tests readable  
❌ **Skip cleanup** - Clean up after tests  

---

## Common Patterns

### Testing Async Operations

```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_async_order_processing(db_session, sample_data):
    """Test asynchronous order processing."""
    
    # Create order
    order = Order(user_id=sample_data['user'].id, status='pending')
    db_session.add(order)
    db_session.commit()
    
    # Trigger async processing
    await process_order(order.id)
    
    # Wait for completion (with timeout)
    await asyncio.wait_for(
        wait_for_order_status(order.id, 'completed'),
        timeout=5.0
    )
    
    # Verify result
    db_session.refresh(order)
    assert order.status == 'completed'
```

### Contract Testing

```python
def test_api_contract_users_endpoint(client):
    """Test that API contract is maintained."""
    
    response = client.get('/api/users/1')
    
    # Verify response structure
    assert response.status_code == 200
    data = response.json
    
    # Required fields
    assert 'id' in data
    assert 'name' in data
    assert 'email' in data
    assert 'created_at' in data
    
    # Field types
    assert isinstance(data['id'], int)
    assert isinstance(data['name'], str)
    assert isinstance(data['email'], str)
    assert isinstance(data['created_at'], str)
    
    # Format validation
    assert '@' in data['email']
    assert len(data['created_at']) > 0
```

---

## Troubleshooting

### Issue: Flaky Tests

**Symptoms:**
- Tests pass sometimes, fail others
- Different results on different machines
- Race conditions

**Solution:**
```python
# Use explicit waits
import time
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def wait_for_order_completion(order_id):
    order = db.session.query(Order).get(order_id)
    if order.status != 'completed':
        raise Exception("Order not completed yet")
    return order

# Reset state between tests
@pytest.fixture(autouse=True)
def reset_state(db_session):
    yield
    db_session.rollback()
    db_session.remove()
```

---

## Related Workflows

**Prerequisites:**
- `dev-xxx_test_writing.md` - Unit testing basics
- `qa-xxx_test_failure_investigation.md` - Debugging tests

**Next Steps:**
- `frontend-xxx_e2e_testing_workflow.md` - End-to-end testing
- `qa-xxx_production_testing.md` - Testing in production

---

## Tags

`testing` `integration-testing` `api-testing` `database-testing` `test-automation` `quality-assurance` `ci-cd`
