# Test Data Generation

**ID:** tes-004  
**Category:** Testing  
**Priority:** MEDIUM  
**Complexity:** Intermediate  
**Estimated Time:** 30-60 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Generate realistic, diverse test data programmatically for thorough testing

**Why:** Manual test data creation is time-consuming and incomplete. Generated test data provides comprehensive coverage, edge cases, and scales to thousands of test scenarios, catching bugs that handwritten examples miss

**When to use:**
- Populating test databases with realistic data
- Testing data pipelines and transformations
- Performance testing with large datasets
- Generating user input variations
- Creating fixtures for integration tests
- Testing data validation and parsing
- Seeding development/staging environments

---

## Prerequisites

**Required:**
- [ ] Programming language and test framework installed
- [ ] Data generation library (Faker, Factory Boy, etc.)
- [ ] Understanding of data model and constraints
- [ ] Database/storage for generated data (if applicable)

**Check before starting:**
```bash
# Python
pip show faker factory-boy

# JavaScript
npm list faker @faker-js/faker

# Java
# Check for JavaFaker in Maven/Gradle

# Test basic generation
python -c "from faker import Faker; print(Faker().name())"
```

---

## Implementation Steps

### Step 1: Choose Data Generation Strategy

**What:** Select the appropriate approach for generating test data

**How:**

**Strategy Options:**

| Strategy | Use Case | Tools | Pros/Cons |
|----------|----------|-------|-----------|
| **Random Faker** | Independent entities | Faker, Chance.js | ✅ Quick, varied ❌ No relationships |
| **Factory Pattern** | Related objects | Factory Boy, Fishery | ✅ Relationships ❌ More setup |
| **Fixtures** | Fixed scenarios | JSON/YAML files | ✅ Reproducible ❌ Manual work |
| **Snapshot Testing** | Known good states | Test framework | ✅ Catches regressions ❌ Brittle |
| **Property-Based** | Input variations | Hypothesis, fast-check | ✅ Edge cases ❌ Complex |
| **Synthetic Data** | ML training | SDV, Mockaroo | ✅ Privacy-safe ❌ Specialized |

**Decision Matrix:**

```
Need reproducible data for debugging?
├─ Yes → Use fixtures or seeded random generation
└─ No → Use random generation

Need relationships between entities?
├─ Yes → Use factory pattern
└─ No → Use simple faker

Need realistic data that matches production patterns?
├─ Yes → Sample from production or use ML-based synthetic data
└─ No → Random generation is fine

Need huge volumes (>100k records)?
├─ Yes → Use bulk generation with batching
└─ No → Simple generation works
```

**Code/Commands:**
```python
# Random independent data
from faker import Faker
fake = Faker()
user = {
    'name': fake.name(),
    'email': fake.email(),
    'address': fake.address()
}

# Factory pattern with relationships
import factory
class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    name = factory.Faker('name')
    posts = factory.RelatedFactory(PostFactory, 'author')

# Fixed fixtures
# tests/fixtures/users.json
{
    "test_user": {
        "name": "Test User",
        "email": "test@example.com"
    }
}

# Property-based generation
from hypothesis import strategies as st
user_strategy = st.builds(
    User,
    name=st.text(min_size=1),
    email=st.emails()
)
```

**Verification:**
- [ ] Strategy matches test needs
- [ ] Can generate required data types
- [ ] Performance is acceptable
- [ ] Generated data is realistic enough

**If This Fails:**
→ Start with simple Faker for quick wins
→ Add factory pattern as relationships grow
→ Combine strategies (factories + faker)

---

### Step 2: Install and Configure Data Generation Library

**What:** Set up the data generation tools for your stack

**How:**

**Python (Faker + Factory Boy):**
```bash
pip install faker factory-boy
```

**Configuration:**
```python
# conftest.py or test setup
from faker import Faker
import factory

# Configure locale for specific formats
fake = Faker('en_US')  # American English
# or multiple locales
fake = Faker(['en_US', 'ja_JP', 'fr_FR'])

# Custom providers
from faker.providers import BaseProvider

class CustomProvider(BaseProvider):
    def product_id(self):
        return f"PRD-{self.random_int(10000, 99999)}"

fake.add_provider(CustomProvider)
```

**JavaScript (Faker):**
```bash
npm install --save-dev @faker-js/faker
```

**Configuration:**
```javascript
// test-utils.js
import { faker } from '@faker-js/faker';

// Set seed for reproducibility
faker.seed(12345);

// Custom generators
export const generateUser = () => ({
  id: faker.string.uuid(),
  name: faker.person.fullName(),
  email: faker.internet.email(),
  avatar: faker.image.avatar(),
  createdAt: faker.date.past()
});
```

**Java (JavaFaker):**
```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.github.javafaker</groupId>
    <artifactId>javafaker</artifactId>
    <version>1.0.2</version>
    <scope>test</scope>
</dependency>
```

```java
import com.github.javafaker.Faker;

public class TestDataGenerator {
    private static final Faker faker = new Faker();
    
    public static User createUser() {
        return new User(
            faker.name().fullName(),
            faker.internet().emailAddress(),
            faker.number().numberBetween(18, 80)
        );
    }
}
```

**Verification:**
- [ ] Libraries installed successfully
- [ ] Can generate basic data types
- [ ] Locale/format settings work
- [ ] Custom providers function correctly

**If This Fails:**
→ Check version compatibility
→ Clear cache and reinstall
→ Try alternative libraries (Casual.js, Chance.js)

---

### Step 3: Create Data Generation Functions

**What:** Build reusable functions to generate test data

**How:**

**Basic Generators:**

```python
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

def generate_user(role='user'):
    """Generate a user with realistic data"""
    return {
        'id': fake.uuid4(),
        'username': fake.user_name(),
        'email': fake.email(),
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'phone': fake.phone_number(),
        'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=80),
        'role': role,
        'is_active': True,
        'created_at': fake.date_time_between(start_date='-2y', end_date='now'),
        'address': {
            'street': fake.street_address(),
            'city': fake.city(),
            'state': fake.state(),
            'zip': fake.zipcode(),
            'country': 'US'
        }
    }

def generate_product():
    """Generate a product with pricing"""
    name = fake.catch_phrase()
    return {
        'id': fake.uuid4(),
        'name': name,
        'slug': name.lower().replace(' ', '-'),
        'description': fake.text(max_nb_chars=200),
        'price': round(random.uniform(9.99, 999.99), 2),
        'stock': random.randint(0, 1000),
        'category': random.choice(['Electronics', 'Clothing', 'Home', 'Sports']),
        'tags': random.sample(['popular', 'sale', 'new', 'limited'], k=random.randint(0, 3)),
        'created_at': fake.date_time_between(start_date='-1y', end_date='now')
    }

def generate_order(user_id=None, num_items=None):
    """Generate an order with line items"""
    if num_items is None:
        num_items = random.randint(1, 5)
    
    items = [
        {
            'product_id': fake.uuid4(),
            'quantity': random.randint(1, 3),
            'price': round(random.uniform(10, 200), 2)
        }
        for _ in range(num_items)
    ]
    
    subtotal = sum(item['quantity'] * item['price'] for item in items)
    
    return {
        'id': fake.uuid4(),
        'user_id': user_id or fake.uuid4(),
        'items': items,
        'subtotal': round(subtotal, 2),
        'tax': round(subtotal * 0.08, 2),
        'total': round(subtotal * 1.08, 2),
        'status': random.choice(['pending', 'processing', 'shipped', 'delivered']),
        'created_at': fake.date_time_between(start_date='-30d', end_date='now')
    }
```

**JavaScript:**

```javascript
import { faker } from '@faker-js/faker';

export function generateUser(role = 'user') {
  return {
    id: faker.string.uuid(),
    username: faker.internet.userName(),
    email: faker.internet.email(),
    firstName: faker.person.firstName(),
    lastName: faker.person.lastName(),
    phone: faker.phone.number(),
    dateOfBirth: faker.date.birthdate({ min: 18, max: 80, mode: 'age' }),
    role: role,
    isActive: true,
    createdAt: faker.date.past({ years: 2 }),
    address: {
      street: faker.location.streetAddress(),
      city: faker.location.city(),
      state: faker.location.state(),
      zip: faker.location.zipCode(),
      country: 'US'
    }
  };
}

export function generateProduct() {
  const name = faker.commerce.productName();
  return {
    id: faker.string.uuid(),
    name: name,
    slug: name.toLowerCase().replace(/\s+/g, '-'),
    description: faker.commerce.productDescription(),
    price: parseFloat(faker.commerce.price({ min: 10, max: 1000 })),
    stock: faker.number.int({ min: 0, max: 1000 }),
    category: faker.helpers.arrayElement(['Electronics', 'Clothing', 'Home', 'Sports']),
    tags: faker.helpers.arrayElements(['popular', 'sale', 'new', 'limited'], { min: 0, max: 3 }),
    createdAt: faker.date.past({ years: 1 })
  };
}

export function generateOrder(userId = null, numItems = null) {
  const itemCount = numItems ?? faker.number.int({ min: 1, max: 5 });
  
  const items = Array.from({ length: itemCount }, () => ({
    productId: faker.string.uuid(),
    quantity: faker.number.int({ min: 1, max: 3 }),
    price: parseFloat(faker.commerce.price({ min: 10, max: 200 }))
  }));
  
  const subtotal = items.reduce((sum, item) => sum + item.quantity * item.price, 0);
  
  return {
    id: faker.string.uuid(),
    userId: userId ?? faker.string.uuid(),
    items: items,
    subtotal: Math.round(subtotal * 100) / 100,
    tax: Math.round(subtotal * 8) / 100,
    total: Math.round(subtotal * 108) / 100,
    status: faker.helpers.arrayElement(['pending', 'processing', 'shipped', 'delivered']),
    createdAt: faker.date.recent({ days: 30 })
  };
}
```

**Verification:**
- [ ] Generators produce valid data
- [ ] Data matches expected schema
- [ ] Relationships between entities work
- [ ] Edge cases can be generated

**If This Fails:**
→ Test generators in isolation first
→ Add validation to generator output
→ Start simple, add complexity incrementally

---

### Step 4: Implement Factory Pattern for Related Data

**What:** Create factories that handle relationships and dependencies

**How:**

**Python (Factory Boy):**

```python
import factory
from factory.faker import Faker as FactoryFaker
from datetime import datetime

class UserFactory(factory.Factory):
    class Meta:
        model = dict  # or your User model
    
    id = factory.Sequence(lambda n: n)
    username = factory.LazyAttribute(
        lambda obj: f"{obj.first_name.lower()}.{obj.last_name.lower()}"
    )
    first_name = FactoryFaker('first_name')
    last_name = FactoryFaker('last_name')
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    is_admin = False
    created_at = FactoryFaker('date_time_between', start_date='-2y', end_date='now')

class AdminUserFactory(UserFactory):
    """Specialized factory for admin users"""
    is_admin = True
    email = factory.LazyAttribute(lambda obj: f"admin.{obj.username}@example.com")

class PostFactory(factory.Factory):
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n)
    title = FactoryFaker('sentence', nb_words=6)
    content = FactoryFaker('text', max_nb_chars=500)
    author = factory.SubFactory(UserFactory)  # Creates related user
    published_at = FactoryFaker('date_time_between', start_date='-1y', end_date='now')
    
    @factory.lazy_attribute
    def slug(self):
        return self.title.lower().replace(' ', '-')

class CommentFactory(factory.Factory):
    class Meta:
        model = dict
    
    id = factory.Sequence(lambda n: n)
    content = FactoryFaker('text', max_nb_chars=200)
    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    created_at = factory.LazyAttribute(
        lambda obj: obj.post.published_at + timedelta(days=random.randint(0, 30))
    )

# Usage in tests
def test_with_factories():
    # Create a user
    user = UserFactory()
    
    # Create an admin
    admin = AdminUserFactory()
    
    # Create post with its author
    post = PostFactory()
    
    # Create post with specific author
    post = PostFactory(author=user)
    
    # Create multiple instances
    users = UserFactory.create_batch(10)
    
    # Create related data
    post_with_comments = PostFactory(
        comments=CommentFactory.create_batch(5)
    )
```

**JavaScript (Fishery):**

```javascript
import { Factory } from 'fishery';
import { faker } from '@faker-js/faker';

const userFactory = Factory.define(({ sequence }) => ({
  id: sequence,
  username: faker.internet.userName(),
  email: faker.internet.email(),
  firstName: faker.person.firstName(),
  lastName: faker.person.lastName(),
  isAdmin: false,
  createdAt: faker.date.past({ years: 2 })
}));

const adminUserFactory = userFactory.params({
  isAdmin: true
});

const postFactory = Factory.define(({ sequence, associations }) => ({
  id: sequence,
  title: faker.lorem.sentence(),
  content: faker.lorem.paragraphs(3),
  slug: faker.helpers.slugify(faker.lorem.sentence()),
  author: associations.author || userFactory.build(),
  publishedAt: faker.date.past({ years: 1 })
}));

const commentFactory = Factory.define(({ sequence, associations }) => ({
  id: sequence,
  content: faker.lorem.paragraph(),
  post: associations.post || postFactory.build(),
  author: associations.author || userFactory.build(),
  createdAt: faker.date.recent({ days: 30 })
}));

// Usage in tests
describe('Blog', () => {
  it('creates related data', () => {
    // Create a user
    const user = userFactory.build();
    
    // Create post with specific author
    const post = postFactory.build({ author: user });
    
    // Create multiple posts
    const posts = postFactory.buildList(5);
    
    // Create comment with post and author
    const comment = commentFactory.build({
      post: post,
      author: user
    });
  });
});
```

**Traits and States:**

```python
class UserFactory(factory.Factory):
    class Meta:
        model = dict
    
    username = FactoryFaker('user_name')
    email = FactoryFaker('email')
    status = 'active'
    
    class Params:
        # Traits that modify the factory
        admin = factory.Trait(
            role='admin',
            permissions=['all']
        )
        
        suspended = factory.Trait(
            status='suspended',
            suspended_at=FactoryFaker('date_time_this_year')
        )
        
        with_posts = factory.Trait(
            posts=factory.RelatedFactoryList(PostFactory, 'author', size=5)
        )

# Usage
admin_user = UserFactory(admin=True)
suspended_user = UserFactory(suspended=True)
active_blogger = UserFactory(with_posts=True)
```

**Verification:**
- [ ] Factories create valid instances
- [ ] Relationships work correctly
- [ ] Traits and variations work
- [ ] Batch creation succeeds

**If This Fails:**
→ Check factory meta configuration
→ Ensure SubFactory references are correct
→ Test factories individually before combining

---

### Step 5: Generate Bulk Data for Performance Testing

**What:** Create large datasets efficiently for performance and load testing

**How:**

**Batch Generation:**

```python
def generate_bulk_users(count=10000):
    """Generate users in batches for memory efficiency"""
    batch_size = 1000
    users = []
    
    for i in range(0, count, batch_size):
        batch = [
            generate_user()
            for _ in range(min(batch_size, count - i))
        ]
        users.extend(batch)
        
        # Optionally write to file/db to free memory
        if len(users) >= 5000:
            save_to_database(users)
            users = []
    
    return users

def generate_time_series_data(days=365, points_per_day=24):
    """Generate time-series data efficiently"""
    from datetime import timedelta
    
    start_date = datetime.now() - timedelta(days=days)
    data = []
    
    for day in range(days):
        date = start_date + timedelta(days=day)
        for hour in range(points_per_day):
            timestamp = date + timedelta(hours=hour)
            data.append({
                'timestamp': timestamp,
                'value': random.gauss(100, 15),  # Normal distribution
                'sensor_id': random.randint(1, 10)
            })
    
    return data  # 365 * 24 = 8,760 data points
```

**Database Bulk Insert:**

```python
# PostgreSQL with psycopg2
import psycopg2.extras

def bulk_insert_users(users, conn):
    """Fast bulk insert using execute_values"""
    with conn.cursor() as cur:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO users (username, email, first_name, last_name)
            VALUES %s
            """,
            [(u['username'], u['email'], u['first_name'], u['last_name']) 
             for u in users],
            page_size=1000
        )
    conn.commit()

# SQLAlchemy bulk operations
from sqlalchemy.orm import Session

def bulk_insert_sqlalchemy(users, session: Session):
    """Efficient SQLAlchemy bulk insert"""
    session.bulk_insert_mappings(User, users)
    session.commit()
```

**File Generation:**

```python
import csv
import json

def generate_csv_dataset(filename, num_rows=100000):
    """Generate large CSV file"""
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'id', 'name', 'email', 'created_at'
        ])
        writer.writeheader()
        
        for i in range(num_rows):
            writer.writerow({
                'id': i,
                'name': fake.name(),
                'email': fake.email(),
                'created_at': fake.date_time().isoformat()
            })
            
            # Progress indicator
            if i % 10000 == 0:
                print(f"Generated {i} rows...")

def generate_json_lines(filename, num_records=50000):
    """Generate JSON Lines file for big data testing"""
    with open(filename, 'w') as f:
        for i in range(num_records):
            record = {
                'id': i,
                'user': generate_user(),
                'order': generate_order()
            }
            f.write(json.dumps(record) + '\n')
```

**Verification:**
- [ ] Large datasets generate without memory errors
- [ ] Generation completes in reasonable time
- [ ] Data is properly saved/committed
- [ ] Can query and use generated data

**If This Fails:**
→ Reduce batch size
→ Use streaming/generators instead of lists
→ Add progress monitoring
→ Split into multiple files

---

### Step 6: Add Constraints and Validation

**What:** Ensure generated data meets business rules and constraints

**How:**

**Data Validation:**

```python
from pydantic import BaseModel, EmailStr, validator
from typing import List

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    age: int
    roles: List[str]
    
    @validator('username')
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError('Username too short')
        return v.lower()
    
    @validator('age')
    def age_valid(cls, v):
        if not 18 <= v <= 120:
            raise ValueError('Invalid age')
        return v

def generate_valid_user():
    """Generate user that passes validation"""
    while True:
        try:
            data = generate_user()
            user = User(**data)  # Validates on creation
            return user.dict()
        except ValueError:
            continue  # Generate new one if validation fails
```

**Constrained Generation:**

```python
def generate_user_with_constraints(
    min_age=18,
    max_age=80,
    required_roles=None,
    email_domain='example.com'
):
    """Generate user with specific constraints"""
    user = {
        'id': fake.uuid4(),
        'username': fake.user_name(),
        'email': f"{fake.user_name()}@{email_domain}",
        'age': random.randint(min_age, max_age),
        'roles': required_roles or ['user'],
        'created_at': fake.date_time_between(start_date='-2y')
    }
    return user

def generate_order_with_total(min_total=50, max_total=500):
    """Generate order with specific total value"""
    target_total = random.uniform(min_total, max_total)
    num_items = random.randint(1, 5)
    price_per_item = target_total / num_items
    
    items = [
        {
            'product_id': fake.uuid4(),
            'quantity': 1,
            'price': round(price_per_item + random.uniform(-10, 10), 2)
        }
        for _ in range(num_items)
    ]
    
    actual_total = sum(item['price'] * item['quantity'] for item in items)
    
    return {
        'id': fake.uuid4(),
        'items': items,
        'subtotal': round(actual_total, 2),
        'tax': round(actual_total * 0.08, 2),
        'total': round(actual_total * 1.08, 2)
    }
```

**Custom Constraints:**

```python
def generate_unique_usernames(count=100):
    """Generate guaranteed unique usernames"""
    usernames = set()
    
    while len(usernames) < count:
        username = fake.user_name()
        usernames.add(username)
    
    return list(usernames)

def generate_realistic_distribution():
    """Generate data with realistic statistical distribution"""
    # 70% regular users, 20% premium, 10% admin
    role_distribution = ['user'] * 70 + ['premium'] * 20 + ['admin'] * 10
    
    users = []
    for _ in range(100):
        user = generate_user()
        user['role'] = random.choice(role_distribution)
        users.append(user)
    
    return users
```

**Verification:**
- [ ] Generated data passes validation
- [ ] Constraints are enforced
- [ ] Distributions match requirements
- [ ] Unique constraints maintained

**If This Fails:**
→ Add retry logic for constraint violations
→ Generate more data than needed, filter down
→ Use constraint-aware generation from start

---

## Verification Checklist

After completing this workflow:

- [ ] Data generation libraries installed and configured
- [ ] Generator functions created for all data types
- [ ] Factory pattern implemented for related data
- [ ] Bulk generation works efficiently
- [ ] Data meets validation rules and constraints
- [ ] Generated data is realistic and useful
- [ ] Reproducibility through seeds when needed
- [ ] Documentation for how to generate test data

---

## Common Issues & Solutions

### Issue: Generated data is not realistic

**Symptoms:**
- Data looks obviously fake
- Doesn't match production patterns
- Tests pass but bugs still occur in production

**Solution:**
```python
# BAD - Unrealistic
def generate_user_bad():
    return {
        'name': 'Test User',
        'email': 'test@test.com',
        'age': 25
    }

# GOOD - Realistic patterns
def generate_user_good():
    # Use actual name patterns
    first = fake.first_name()
    last = fake.last_name()
    
    # Realistic email patterns
    email_patterns = [
        f"{first.lower()}.{last.lower()}@example.com",
        f"{first[0].lower()}{last.lower()}@example.com",
        f"{first.lower()}{random.randint(1, 99)}@example.com"
    ]
    
    # Age distribution matching real users
    age_distribution = (
        [random.randint(18, 25)] * 20 +  # 20% young adults
        [random.randint(26, 40)] * 45 +  # 45% working age
        [random.randint(41, 65)] * 30 +  # 30% middle age
        [random.randint(66, 80)] * 5      # 5% seniors
    )
    
    return {
        'first_name': first,
        'last_name': last,
        'email': random.choice(email_patterns),
        'age': random.choice(age_distribution)
    }

# BETTER - Sample from production data (anonymized)
def generate_from_production_sample():
    """Use anonymized production patterns"""
    # Load patterns from real data analysis
    common_names = load_name_distribution()
    email_domains = load_email_domains()
    
    return {
        'name': random.choice(common_names),
        'email': f"{fake.user_name()}@{random.choice(email_domains)}",
        'age': np.random.normal(loc=35, scale=12)  # From real distribution
    }
```

**Prevention:**
- Analyze production data patterns
- Use locale-specific generators
- Match real distributions and correlations

---

### Issue: Performance is too slow

**Symptoms:**
- Test setup takes minutes
- Memory usage explodes
- Can't generate enough data for performance tests

**Solution:**
```python
# BAD - Inefficient generation
def generate_slow():
    users = []
    for i in range(100000):
        user = generate_user()  # Lots of function calls
        users.append(user)
    return users

# GOOD - Batch with generators
def generate_efficient():
    """Use generator for memory efficiency"""
    for i in range(100000):
        yield generate_user()

# BETTER - Pre-compute and reuse
class CachedFaker:
    def __init__(self):
        self.fake = Faker()
        # Pre-generate common values
        self.names = [self.fake.name() for _ in range(1000)]
        self.emails = [self.fake.email() for _ in range(1000)]
    
    def get_user(self):
        return {
            'name': random.choice(self.names),
            'email': random.choice(self.emails)
        }

cached = CachedFaker()
users = [cached.get_user() for _ in range(100000)]
```

**Prevention:**
- Use generators for large datasets
- Cache commonly used values
- Use bulk insert operations
- Consider using pre-generated fixtures

---

### Issue: Data doesn't maintain referential integrity

**Symptoms:**
- Foreign key violations
- Orphaned records
- Broken relationships

**Solution:**
```python
# BAD - Broken relationships
def generate_comment_bad():
    return {
        'id': 1,
        'post_id': random.randint(1, 1000),  # Might not exist!
        'author_id': random.randint(1, 1000)  # Might not exist!
    }

# GOOD - Maintain references
class DataGenerator:
    def __init__(self):
        self.users = []
        self.posts = []
    
    def generate_user(self):
        user = {'id': len(self.users) + 1, 'name': fake.name()}
        self.users.append(user)
        return user
    
    def generate_post(self):
        author = random.choice(self.users)
        post = {
            'id': len(self.posts) + 1,
            'author_id': author['id'],
            'title': fake.sentence()
        }
        self.posts.append(post)
        return post
    
    def generate_comment(self):
        post = random.choice(self.posts)
        author = random.choice(self.users)
        return {
            'post_id': post['id'],
            'author_id': author['id'],
            'content': fake.text()
        }

# Usage
gen = DataGenerator()
users = [gen.generate_user() for _ in range(100)]
posts = [gen.generate_post() for _ in range(500)]
comments = [gen.generate_comment() for _ in range(2000)]
```

**Prevention:**
- Use factory pattern with SubFactory
- Track generated IDs
- Generate in dependency order (users → posts → comments)

---

## Examples

### Example 1: E-commerce Test Data

**Context:** Generate complete e-commerce dataset with users, products, orders

**Implementation:**
```python
class EcommerceDataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.users = []
        self.products = []
        self.orders = []
    
    def generate_dataset(self, num_users=100, num_products=50, orders_per_user=3):
        """Generate complete e-commerce dataset"""
        # Generate users
        for _ in range(num_users):
            self.users.append(self.generate_user())
        
        # Generate products
        for _ in range(num_products):
            self.products.append(self.generate_product())
        
        # Generate orders
        for user in self.users:
            for _ in range(random.randint(0, orders_per_user)):
                self.orders.append(self.generate_order(user['id']))
        
        return {
            'users': self.users,
            'products': self.products,
            'orders': self.orders
        }
    
    def generate_user(self):
        return {
            'id': len(self.users) + 1,
            'email': self.fake.email(),
            'name': self.fake.name(),
            'address': self.fake.address(),
            'created_at': self.fake.date_time_between(start_date='-2y')
        }
    
    def generate_product(self):
        return {
            'id': len(self.products) + 1,
            'name': self.fake.catch_phrase(),
            'price': round(random.uniform(10, 500), 2),
            'stock': random.randint(0, 100),
            'category': random.choice(['Electronics', 'Books', 'Clothing'])
        }
    
    def generate_order(self, user_id):
        num_items = random.randint(1, 5)
        items = random.sample(self.products, min(num_items, len(self.products)))
        
        order_items = [
            {
                'product_id': product['id'],
                'quantity': random.randint(1, 3),
                'price': product['price']
            }
            for product in items
        ]
        
        total = sum(item['quantity'] * item['price'] for item in order_items)
        
        return {
            'id': len(self.orders) + 1,
            'user_id': user_id,
            'items': order_items,
            'total': round(total, 2),
            'status': random.choice(['pending', 'shipped', 'delivered']),
            'created_at': self.fake.date_time_between(start_date='-90d')
        }

# Usage
generator = EcommerceDataGenerator()
dataset = generator.generate_dataset(num_users=1000, num_products=200)

# Save to database
save_to_db(dataset['users'], 'users')
save_to_db(dataset['products'], 'products')
save_to_db(dataset['orders'], 'orders')
```

**Result:** Complete relational dataset for testing

---

### Example 2: Time-Series Sensor Data

**Context:** Generate IoT sensor data for testing data pipeline

**Implementation:**
```python
import pandas as pd
import numpy as np

def generate_sensor_data(
    num_sensors=10,
    days=30,
    frequency='1H',  # One reading per hour
    anomaly_rate=0.05
):
    """Generate realistic sensor time-series data"""
    
    start_date = datetime.now() - timedelta(days=days)
    timestamps = pd.date_range(start=start_date, periods=days*24, freq=frequency)
    
    data = []
    
    for sensor_id in range(1, num_sensors + 1):
        # Each sensor has its own baseline and pattern
        baseline = random.uniform(50, 150)
        
        for i, timestamp in enumerate(timestamps):
            # Daily pattern (higher during day)
            hour = timestamp.hour
            daily_factor = 1 + 0.3 * np.sin((hour - 6) * np.pi / 12)
            
            # Weekly pattern (lower on weekends)
            weekly_factor = 0.8 if timestamp.weekday() >= 5 else 1.0
            
            # Random noise
            noise = np.random.normal(0, 5)
            
            # Occasional anomalies
            is_anomaly = random.random() < anomaly_rate
            anomaly = random.uniform(-50, 50) if is_anomaly else 0
            
            value = baseline * daily_factor * weekly_factor + noise + anomaly
            
            data.append({
                'sensor_id': sensor_id,
                'timestamp': timestamp,
                'value': round(value, 2),
                'is_anomaly': is_anomaly
            })
    
    return pd.DataFrame(data)

# Generate and save
df = generate_sensor_data(num_sensors=20, days=90)
df.to_csv('sensor_data.csv', index=False)
df.to_parquet('sensor_data.parquet')
```

**Result:** Realistic time-series data with patterns and anomalies

---

## Best Practices

### DO:
✅ Use libraries (Faker, Factory Boy) instead of manual generation
✅ Make data generation reproducible with seeds
✅ Generate realistic data that matches production patterns
✅ Create reusable generator functions and factories
✅ Maintain referential integrity between related entities
✅ Use batch generation for large datasets
✅ Validate generated data against schemas
✅ Document generation strategies and constraints
✅ Consider privacy when using production data patterns
✅ Balance realism with test execution speed

### DON'T:
❌ Hardcode test data (use generation instead)
❌ Ignore referential integrity
❌ Generate unrealistic data (all ages=25)
❌ Create massive datasets when small ones suffice
❌ Forget to clean up generated test data
❌ Use production data directly (privacy risk)
❌ Make every test generate new data (use fixtures too)
❌ Ignore performance of data generation
❌ Generate random data without constraints
❌ Skip validation of generated data

---

## Related Workflows

**Prerequisites:**
- `dev-008`: Unit Testing Setup - Testing infrastructure
- `dev-010`: Test Fixtures and Mocks - Understanding test data patterns

**Next Steps:**
- `tes-002`: Property Based Testing - Using generated inputs systematically
- `tes-003`: Mocking Strategy - Combining mocks with generated data
- `qa-008`: Integration Testing - Using generated data in integration tests

**Alternatives:**
- `dev-010`: Test Fixtures - Static test data files
- `tes-002`: Property Based Testing - Framework-generated test inputs
- Snapshot testing - Using recorded real data

---

## Tags
`testing` `test-data` `data-generation` `faker` `factory-pattern` `test-fixtures` `synthetic-data` `bulk-data` `test-automation` `factory-boy`
