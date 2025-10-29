---
id: dev-019
title: Third Party API Integration
category: Development
subcategory: Integration
tags:
  - api
  - integration
  - rest
  - http
  - authentication
  - testing
  - error-handling
prerequisites:
  - dev-003  # Environment Initialization
  - sec-001  # Secret Management
related_workflows:
  - dev-002  # Test Writing
  - sec-002  # API Key Management
  - dvo-014  # Monitoring Setup
complexity: intermediate
estimated_time: 2-4 hours
last_updated: 2025-10-25
---

# Third Party API Integration

## Overview

**What:** Complete workflow for integrating external third-party APIs into your application with proper authentication, error handling, rate limiting, and monitoring.

**Why:** Third-party APIs enable powerful functionality without building from scratch. Proper integration ensures reliability, security, and maintainability while preventing common issues like rate limiting, auth failures, and data inconsistencies.

**When to use:**
- Integrating payment providers (Stripe, PayPal)
- Adding authentication (OAuth, Auth0)
- Using cloud services (AWS, GCP, Azure)
- Integrating communication (Twilio, SendGrid)
- Adding analytics or monitoring (Google Analytics, Datadog)
- Connecting to business tools (Salesforce, HubSpot)

---

## Prerequisites

**Required:**
- [ ] API documentation URL
- [ ] API credentials (key, secret, etc.)
- [ ] Understanding of API authentication method
- [ ] Rate limits and quotas known
- [ ] Testing environment/sandbox available

**Required Tools:**
- [ ] Python with requests library
- [ ] Environment variable management (.env)
- [ ] Test framework (pytest)

**Check before starting:**
```bash
# Install required packages
pip install requests python-dotenv pydantic tenacity

# Verify API credentials are available
echo $API_KEY  # Should not be empty

# Test network connectivity
curl -I https://api.example.com
```

---

## Implementation Steps

### Step 1: Research and Plan API Integration

**What:** Understand API capabilities, limitations, authentication, and data structures before writing code.

**Review API documentation:**
```markdown
# Create API Research Document

## API Overview
- **Provider:** Stripe
- **Purpose:** Payment processing
- **Documentation:** https://stripe.com/docs/api
- **Status Page:** https://status.stripe.com

## Authentication
- **Method:** Bearer token (API key)
- **Location:** Header: `Authorization: Bearer sk_test_...`
- **Key Types:** Test keys (sk_test_) and Live keys (sk_live_)

## Key Endpoints We'll Use
1. POST /v1/customers - Create customer
2. POST /v1/payment_intents - Create payment
3. GET /v1/payment_intents/:id - Retrieve payment status

## Rate Limits
- 100 requests/second per key
- Exponential backoff on 429 responses

## Quotas
- Test mode: Unlimited
- Live mode: Based on plan

## Error Responses
- 400: Bad request (invalid parameters)
- 401: Authentication failed
- 429: Rate limit exceeded
- 500: Server error

## Webhooks
- Available for payment events
- Signature verification required
```

**Create integration plan:**
```python
# docs/stripe_integration_plan.md
"""
## Phase 1: Basic Setup (This workflow)
- [ ] Set up authentication
- [ ] Create API client class
- [ ] Test connection
- [ ] Implement basic operations

## Phase 2: Core Features
- [ ] Customer creation
- [ ] Payment processing
- [ ] Webhook handling

## Phase 3: Production Ready
- [ ] Error handling
- [ ] Retry logic
- [ ] Rate limiting
- [ ] Monitoring
"""
```

**Verification:**
- [ ] API documentation reviewed
- [ ] Authentication method understood
- [ ] Rate limits documented
- [ ] Key endpoints identified
- [ ] Integration plan created

---

### Step 2: Set Up Authentication and Configuration

**What:** Securely configure API credentials and create configuration classes.

**Store credentials securely:**
```bash
# .env file (never commit!)
STRIPE_API_KEY=sk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
STRIPE_API_VERSION=2023-10-16

# .env.example (commit this)
STRIPE_API_KEY=sk_test_YOUR_KEY_HERE_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
STRIPE_API_VERSION=2023-10-16
```

**Create configuration class:**
```python
# src/integrations/stripe_config.py
from pydantic_settings import BaseSettings
from typing import Optional


class StripeConfig(BaseSettings):
    """Stripe API configuration."""
    
    api_key: str
    webhook_secret: str
    api_version: str = "2023-10-16"
    timeout: int = 30
    max_retries: int = 3
    
    # Optional: Different keys for test/live
    use_test_mode: bool = True
    
    class Config:
        env_prefix = "STRIPE_"
        env_file = ".env"
    
    @property
    def base_url(self) -> str:
        return "https://api.stripe.com/v1"
    
    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Stripe-Version": self.api_version,
            "Content-Type": "application/json",
        }


# Usage
config = StripeConfig()
```

**Verification:**
- [ ] Credentials stored in .env
- [ ] .env in .gitignore
- [ ] Configuration class created
- [ ] Can load configuration: `config = StripeConfig()`

---

### Step 3: Create API Client Class

**What:** Build reusable client class with proper error handling and retry logic.

**Basic API client:**
```python
# src/integrations/stripe_client.py
import requests
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from .stripe_config import StripeConfig

logger = logging.getLogger(__name__)


class StripeAPIError(Exception):
    """Base exception for Stripe API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class StripeClient:
    """Client for Stripe API integration."""
    
    def __init__(self, config: Optional[StripeConfig] = None):
        self.config = config or StripeConfig()
        self.session = requests.Session()
        self.session.headers.update(self.config.headers)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            # Handle specific HTTP errors
            status_code = e.response.status_code
            error_data = e.response.json() if e.response.content else {}
            
            if status_code == 401:
                raise StripeAPIError("Authentication failed - check API key", status_code, error_data)
            elif status_code == 429:
                raise StripeAPIError("Rate limit exceeded", status_code, error_data)
            elif status_code >= 500:
                raise StripeAPIError(f"Server error: {status_code}", status_code, error_data)
            else:
                raise StripeAPIError(f"HTTP {status_code}: {error_data}", status_code, error_data)
        
        except requests.exceptions.Timeout:
            raise StripeAPIError(f"Request timeout after {self.config.timeout}s")
        except requests.exceptions.RequestException as e:
            raise StripeAPIError(f"Request failed: {str(e)}")
    
    def create_customer(self, email: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new customer."""
        data = {"email": email}
        if name:
            data["name"] = name
        
        logger.info(f"Creating customer: {email}")
        return self._request("POST", "customers", data=data)
    
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve customer by ID."""
        logger.info(f"Retrieving customer: {customer_id}")
        return self._request("GET", f"customers/{customer_id}")
    
    def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a payment intent."""
        data = {
            "amount": amount,
            "currency": currency,
        }
        if customer_id:
            data["customer"] = customer_id
        
        logger.info(f"Creating payment intent: {amount} {currency}")
        return self._request("POST", "payment_intents", data=data)
```

**Verification:**
- [ ] Client class created
- [ ] Authentication headers set
- [ ] Retry logic implemented
- [ ] Error handling comprehensive
- [ ] Logging added

---

### Step 4: Write Comprehensive Tests

**What:** Create unit and integration tests for API client.

**Unit tests (mocked):**
```python
# tests/unit/test_stripe_client.py
import pytest
from unittest.mock import Mock, patch
from src.integrations.stripe_client import StripeClient, StripeAPIError


@pytest.fixture
def stripe_client():
    """Provide Stripe client with test config."""
    with patch('src.integrations.stripe_config.StripeConfig') as mock_config:
        mock_config.return_value.api_key = "sk_test_YOUR_KEY_HERE"
        mock_config.return_value.base_url = "https://api.stripe.com/v1"
        mock_config.return_value.timeout = 30
        client = StripeClient()
        return client


def test_create_customer_success(stripe_client):
    """Test successful customer creation."""
    # Mock response
    with patch.object(stripe_client.session, 'request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "cus_test123",
            "email": "test@example.com"
        }
        mock_request.return_value = mock_response
        
        # Call method
        result = stripe_client.create_customer("test@example.com")
        
        # Verify
        assert result["id"] == "cus_test123"
        assert result["email"] == "test@example.com"
        mock_request.assert_called_once()


def test_authentication_error(stripe_client):
    """Test handling of authentication error."""
    with patch.object(stripe_client.session, 'request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_request.return_value = mock_response
        
        with pytest.raises(StripeAPIError) as exc_info:
            stripe_client.create_customer("test@example.com")
        
        assert "Authentication failed" in str(exc_info.value)
```

**Integration tests (real API):**
```python
# tests/integration/test_stripe_integration.py
import pytest
from src.integrations.stripe_client import StripeClient


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("STRIPE_API_KEY"), reason="API key not set")
def test_create_and_retrieve_customer():
    """Test full customer lifecycle with real API."""
    client = StripeClient()
    
    # Create customer
    customer = client.create_customer(
        email="integration-test@example.com",
        name="Test User"
    )
    
    assert customer["id"].startswith("cus_")
    assert customer["email"] == "integration-test@example.com"
    
    # Retrieve customer
    retrieved = client.get_customer(customer["id"])
    assert retrieved["id"] == customer["id"]
    assert retrieved["email"] == customer["email"]
```

**Verification:**
- [ ] Unit tests written and passing
- [ ] Integration tests created
- [ ] Error cases tested
- [ ] Retry logic tested
- [ ] All tests can run independently

---

### Step 5: Implement Rate Limiting and Circuit Breaker

**What:** Add protection against rate limits and service outages.

**Rate limiter:**
```python
# src/integrations/rate_limiter.py
import time
from threading import Lock
from collections import deque


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, requests_per_second: int):
        self.requests_per_second = requests_per_second
        self.tokens = requests_per_second
        self.last_update = time.time()
        self.lock = Lock()
    
    def acquire(self) -> bool:
        """Acquire a token, blocking if necessary."""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Refill tokens
            self.tokens = min(
                self.requests_per_second,
                self.tokens + elapsed * self.requests_per_second
            )
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            
            # Wait for token
            wait_time = (1 - self.tokens) / self.requests_per_second
            time.sleep(wait_time)
            self.tokens = 0
            return True


# Add to client
class StripeClient:
    def __init__(self, config: Optional[StripeConfig] = None):
        self.config = config or StripeConfig()
        self.session = requests.Session()
        self.session.headers.update(self.config.headers)
        self.rate_limiter = RateLimiter(requests_per_second=100)
    
    def _request(self, method: str, endpoint: str, **kwargs):
        """Make request with rate limiting."""
        self.rate_limiter.acquire()
        # ... rest of request logic
```

**Verification:**
- [ ] Rate limiter implemented
- [ ] Rate limiter tested
- [ ] Client respects rate limits
- [ ] No 429 errors in logs

---

### Step 6: Add Monitoring and Logging

**What:** Instrument API client for observability.

**Enhanced logging:**
```python
# src/integrations/stripe_client.py
import logging
import time

logger = logging.getLogger(__name__)


class StripeClient:
    def _request(self, method: str, endpoint: str, **kwargs):
        """Make request with comprehensive logging."""
        start_time = time.time()
        
        logger.info(f"Stripe API: {method} {endpoint}", extra={
            "method": method,
            "endpoint": endpoint,
            "params": kwargs.get("params"),
        })
        
        try:
            response = self.session.request(...)
            duration = time.time() - start_time
            
            logger.info(f"Stripe API success: {method} {endpoint} ({duration:.2f}s)", extra={
                "method": method,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "duration": duration,
            })
            
            return response.json()
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Stripe API error: {method} {endpoint} ({duration:.2f}s)", extra={
                "method": method,
                "endpoint": endpoint,
                "error": str(e),
                "duration": duration,
            }, exc_info=True)
            raise
```

**Verification:**
- [ ] Logging added to all API calls
- [ ] Metrics collected (duration, errors)
- [ ] Errors logged with context
- [ ] Can trace requests in logs

---

### Step 7: Document Integration

**What:** Create comprehensive documentation for API integration.

**Create docs:**
```python
# docs/stripe_integration.md
"""
# Stripe Integration Guide

## Setup

```python
from src.integrations.stripe_client import StripeClient

client = StripeClient()
```

## Usage Examples

### Create Customer
```python
customer = client.create_customer(
    email="user@example.com",
    name="John Doe"
)
```

### Process Payment
```python
payment = client.create_payment_intent(
    amount=2000,  # $20.00 in cents
    currency="usd",
    customer_id=customer["id"]
)
```

## Error Handling

All API errors raise `StripeAPIError`:
```python
try:
    customer = client.create_customer(email="test@example.com")
except StripeAPIError as e:
    logger.error(f"Failed to create customer: {e}")
```

## Rate Limits

Client automatically handles rate limiting (100 req/sec).

## Testing

Run tests:
```bash
# Unit tests (mocked)
pytest tests/unit/test_stripe_client.py

# Integration tests (requires API key)
STRIPE_API_KEY=sk_test_YOUR_KEY_HERE pytest tests/integration/
```
"""
```

**Verification:**
- [ ] Documentation created
- [ ] Usage examples provided
- [ ] Error handling documented
- [ ] Testing instructions included

---

### Step 8: Deploy and Monitor

**What:** Deploy integration and monitor in production.

**Pre-deployment checklist:**
```markdown
- [ ] All tests passing
- [ ] Using live API keys (not test)
- [ ] Rate limiting configured
- [ ] Error handling tested
- [ ] Logging configured
- [ ] Monitoring alerts set up
- [ ] Rollback plan ready
```

**Monitor in production:**
```python
# Monitor key metrics:
# - API request count
# - Error rate
# - Response time (p50, p95, p99)
# - Rate limit hits
# - Timeout rate

# Set up alerts:
# - Error rate > 5%
# - Response time > 5s
# - Multiple auth failures
```

**Verification:**
- [ ] Deployed successfully
- [ ] No errors in production logs
- [ ] Monitoring dashboards show healthy metrics
- [ ] Alerts configured

---

## Verification Checklist

- [ ] API documentation reviewed
- [ ] Authentication configured
- [ ] API client created
- [ ] Error handling implemented
- [ ] Rate limiting added
- [ ] Tests written and passing
- [ ] Monitoring configured
- [ ] Documentation complete

---

## Best Practices

### DO:
✅ Read API documentation thoroughly
✅ Use test/sandbox environment first
✅ Implement retry logic with exponential backoff
✅ Handle rate limiting gracefully
✅ Log all API interactions
✅ Use type hints and validation (Pydantic)
✅ Write both unit and integration tests
✅ Monitor API health and errors
✅ Keep API keys in environment variables
✅ Version API requests when possible
✅ Implement circuit breaker for reliability
✅ Cache responses when appropriate

### DON'T:
❌ Hardcode API keys in code
❌ Skip error handling
❌ Ignore rate limits
❌ Skip testing before production
❌ Make unthrottled requests
❌ Expose API keys in logs
❌ Skip retry logic
❌ Ignore timeout settings
❌ Use synchronous requests for slow APIs
❌ Skip monitoring and alerts

---

## Common Patterns

### Pattern 1: Async API Client (for high throughput)
```python
import asyncio
import aiohttp

class AsyncStripeClient:
    async def create_customer(self, email: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.config.base_url}/customers",
                json={"email": email},
                headers=self.config.headers
            ) as response:
                return await response.json()
```

### Pattern 2: Webhook Handler
```python
from flask import request
import hmac

@app.route("/webhooks/stripe", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhooks."""
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    
    # Verify signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400
    
    # Handle event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        handle_successful_payment(payment_intent)
    
    return "Success", 200
```

---

## Troubleshooting

### Issue: Authentication failures

**Solution:**
```python
# Verify API key format
assert config.api_key.startswith("sk_")

# Test with curl
curl https://api.stripe.com/v1/customers \
  -u sk_test_YOUR_KEY_HERE: \
  -X GET

# Check key is for correct environment (test vs live)
```

### Issue: Rate limit errors (429)

**Solution:**
```python
# Implement exponential backoff
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=4, max=60)
)
def make_request():
    # ... request logic
```

### Issue: Timeout errors

**Solution:**
```python
# Increase timeout
config.timeout = 60

# Use async for slow endpoints
async def slow_operation():
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)):
        # ... async request
```

---

## Related Workflows

**Prerequisites:**
- [[dev-003]] Environment Initialization
- [[sec-001]] Secret Management

**Next Steps:**
- [[dev-002]] Test Writing
- [[dvo-014]] Monitoring Setup

**Related:**
- [[sec-002]] API Security
- [[dvo-015]] Error Tracking

---

## Tags
`development` `api` `integration` `rest` `http` `authentication` `testing` `error-handling` `rate-limiting` `monitoring`
