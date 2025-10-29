# Legacy Code Integration

**ID:** dev-028  
**Category:** Development  
**Priority:** HIGH  
**Complexity:** Complex  
**Estimated Time:** Varies (days to weeks)  
**Frequency:** As needed  
**Last Updated:** 2025-10-27  
**Status:** ✅ Complete

---

## Purpose

**What:** Strategies and techniques for integrating modern code with legacy codebases while minimizing risk, maintaining functionality, and gradually improving code quality.

**Why:** Legacy systems often contain critical business logic that can't be replaced overnight. Successful integration allows incremental modernization, reduces risk of breaking changes, and enables teams to deliver value while improving code quality.

**When to use:**
- Adding new features to legacy systems
- Migrating from legacy technology stack
- Refactoring legacy code incrementally
- Integrating third-party legacy systems
- Modernizing monolithic applications
- When complete rewrite is not feasible

---

## Prerequisites

**Required Knowledge:**
- [ ] Understanding of both legacy and modern codebases
- [ ] Familiarity with design patterns (Adapter, Facade, Strangler Fig)
- [ ] Testing strategies (characterization tests, integration tests)
- [ ] Version control and branching strategies

**Required Tools:**
- [ ] Comprehensive test suite (or ability to create one)
- [ ] Code analysis tools
- [ ] Monitoring and logging capabilities
- [ ] Feature flags/toggles (recommended)

---

## Implementation Steps

### Step 1: Understand the Legacy Code

**What:** Analyze and document the legacy system before making changes

**How:**

1. **Map the System:**
   ```bash
   # Analyze dependencies
   # Python
   pip install pydeps
   pydeps src --max-bacon=3 --show-deps
   
   # JavaScript
   npm install -g madge
   madge --image graph.svg src/
   ```

2. **Identify Key Components:**
   - Critical business logic
   - External dependencies
   - Database interactions
   - API contracts
   - Data flow patterns

3. **Document Current Behavior:**
   ```python
   # Create characterization tests that describe existing behavior
   def test_legacy_payment_processor_behavior():
       """Document how legacy payment system currently works."""
       processor = LegacyPaymentProcessor()
       result = processor.process_payment(amount=100, currency="USD")
       # Document actual behavior, even if it seems wrong
       assert result.status == "pending"  # Not "success" as expected
       assert result.transaction_id is None  # Bug: no ID generated
   ```

**Verification:**
- [ ] System architecture documented
- [ ] Critical paths identified
- [ ] Dependencies mapped
- [ ] Current behavior captured in tests

---

### Step 2: Create Safety Net (Comprehensive Testing)

**What:** Build test coverage before making any changes

**How:**

**Characterization Tests:**
```python
"""
Characterization tests capture existing behavior,
including bugs, for regression detection.
"""

def test_legacy_tax_calculation():
    """
    Legacy tax calculation behavior.
    Bug: rounds down instead of standard rounding.
    """
    calculator = LegacyTaxCalculator()
    # Document the actual behavior
    assert calculator.calculate_tax(99.95, rate=0.08) == 7.99  # Should be 8.00
    assert calculator.calculate_tax(100.00, rate=0.08) == 8.00
```

**Integration Tests:**
```python
def test_legacy_order_processing_e2e():
    """End-to-end test of legacy order processing."""
    order = create_test_order()
    result = LegacyOrderProcessor().process(order)
    
    assert result.status == "completed"
    assert result.email_sent is True
    assert result.inventory_updated is True
```

**Verification:**
- [ ] Critical paths have test coverage
- [ ] Tests pass with current behavior
- [ ] Can detect regressions
- [ ] Tests run quickly enough for TDD

---

### Step 3: Choose Integration Strategy

**What:** Select the appropriate pattern based on your situation

**Strategy Options:**

#### A. Strangler Fig Pattern (Recommended for Major Rewrites)
```
Legacy System          New System
     â"‚                     â"‚
     â"œâ"€â"€â"€â" Routing â"Œâ"€â"€â"€â"€â"¤
     â"‚         Logic     â"‚
     â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
     
Gradually route traffic to new system
```

```python
class OrderRouter:
    """Route orders to legacy or new system based on feature flag."""
    
    def process_order(self, order):
        if feature_flag.is_enabled("new_order_system"):
            return NewOrderProcessor().process(order)
        return LegacyOrderProcessor().process(order)
```

#### B. Adapter Pattern (For API Compatibility)
```python
class LegacyPaymentAdapter:
    """Adapt legacy payment API to modern interface."""
    
    def __init__(self, legacy_processor):
        self.legacy = legacy_processor
    
    def process_payment(self, payment: PaymentRequest) -> PaymentResponse:
        """Modern interface."""
        # Convert modern request to legacy format
        legacy_request = self._to_legacy_format(payment)
        
        # Call legacy system
        legacy_response = self.legacy.process_payment_legacy(legacy_request)
        
        # Convert legacy response to modern format
        return self._from_legacy_format(legacy_response)
```

#### C. Facade Pattern (Simplify Complex Legacy APIs)
```python
class SimplifiedLegacyFacade:
    """Provide simple interface to complex legacy system."""
    
    def __init__(self):
        self.subsystem_a = LegacySubsystemA()
        self.subsystem_b = LegacySubsystemB()
        self.subsystem_c = LegacySubsystemC()
    
    def execute_workflow(self, data):
        """Simple method that orchestrates complex legacy operations."""
        step1_result = self.subsystem_a.complex_operation_1(data)
        step2_result = self.subsystem_b.complex_operation_2(step1_result)
        return self.subsystem_c.complex_operation_3(step2_result)
```

**Verification:**
- [ ] Strategy chosen based on project needs
- [ ] Team understands the approach
- [ ] Migration path is clear

---

### Step 4: Implement Anti-Corruption Layer

**What:** Create boundary that prevents legacy code from polluting new code

**How:**

```python
"""
Anti-corruption layer isolates new code from legacy complexity.
"""

# Domain models (clean, modern)
@dataclass
class Order:
    id: str
    customer_id: str
    items: List[OrderItem]
    total: Decimal
    status: OrderStatus

# Anti-corruption layer
class OrderTranslator:
    """Translate between legacy and modern domain models."""
    
    @staticmethod
    def to_modern(legacy_order: LegacyOrderDict) -> Order:
        """Convert legacy dict to modern domain object."""
        return Order(
            id=str(legacy_order["order_num"]),  # Rename fields
            customer_id=legacy_order["cust_id"],
            items=OrderTranslator._parse_items(legacy_order["items_csv"]),
            total=Decimal(legacy_order["amt"]) / 100,  # Convert cents to dollars
            status=OrderTranslator._convert_status(legacy_order["stat"])
        )
    
    @staticmethod
    def to_legacy(order: Order) -> LegacyOrderDict:
        """Convert modern object back to legacy format."""
        return {
            "order_num": int(order.id),
            "cust_id": order.customer_id,
            "items_csv": OrderTranslator._format_items(order.items),
            "amt": int(order.total * 100),  # Convert to cents
            "stat": OrderTranslator._convert_status_legacy(order.status)
        }

# Service layer (only works with modern models)
class OrderService:
    def __init__(self, legacy_repo: LegacyOrderRepository):
        self.translator = OrderTranslator()
        self.legacy_repo = legacy_repo
    
    def get_order(self, order_id: str) -> Order:
        """Clean interface returns modern domain model."""
        legacy_order = self.legacy_repo.find_by_id(order_id)
        return self.translator.to_modern(legacy_order)
```

**Verification:**
- [ ] Legacy concepts don't leak into new code
- [ ] Clear boundary between systems
- [ ] Easy to test new code in isolation

---

### Step 5: Gradual Migration with Feature Flags

**What:** Use feature flags to safely roll out changes

**How:**

```python
from feature_flags import FeatureFlags

class UserService:
    def __init__(self):
        self.flags = FeatureFlags()
    
    def create_user(self, user_data):
        if self.flags.is_enabled("new_user_system"):
            # New implementation
            return self._create_user_v2(user_data)
        else:
            # Legacy implementation
            return self._create_user_legacy(user_data)
    
    def _create_user_v2(self, user_data):
        """New, improved implementation."""
        # Modern code here
        pass
    
    def _create_user_legacy(self, user_data):
        """Existing legacy code."""
        # Keep legacy code working
        pass
```

**Rollout Strategy:**
```python
# Phase 1: Deploy with flag OFF (0% traffic)
# - Deploy code
# - Monitor for issues
# - Verify deployment

# Phase 2: Enable for internal users (1% traffic)
if user.is_internal or random.random() < 0.01:
    use_new_system = True

# Phase 3: Gradual rollout (5%, 10%, 25%, 50%, 100%)
rollout_percentage = config.get("new_system_rollout", 0)
use_new_system = random.random() * 100 < rollout_percentage

# Phase 4: Remove feature flag and legacy code
# Once new system is stable at 100%
```

**Verification:**
- [ ] Can toggle between old and new
- [ ] Rollback is instant (disable flag)
- [ ] Monitoring shows both systems

---

### Step 6: Maintain Parallel Systems During Migration

**What:** Run old and new systems simultaneously to verify correctness

**How:**

```python
class DualWriteService:
    """Write to both legacy and new systems, compare results."""
    
    def __init__(self):
        self.legacy = LegacyService()
        self.new = NewService()
        self.logger = logging.getLogger(__name__)
    
    def process(self, data):
        # Always use legacy as source of truth (safe)
        legacy_result = self.legacy.process(data)
        
        # Try new system in shadow mode
        try:
            new_result = self.new.process(data)
            
            # Compare results
            if legacy_result != new_result:
                self.logger.warning(
                    "Result mismatch",
                    extra={
                        "legacy": legacy_result,
                        "new": new_result,
                        "data": data
                    }
                )
        except Exception as e:
            self.logger.error(f"New system error: {e}")
        
        # Always return legacy result (safe)
        return legacy_result
```

**Verification:**
- [ ] Both systems receiving same inputs
- [ ] Results compared automatically
- [ ] Discrepancies logged and investigated
- [ ] No user impact from new system errors

---

## Verification Checklist

Throughout integration:

- [ ] Legacy system remains functional
- [ ] New code has comprehensive tests
- [ ] Monitoring in place for both systems
- [ ] Rollback plan defined and tested
- [ ] Team trained on both codebases
- [ ] Documentation updated
- [ ] Performance metrics tracked
- [ ] User experience unchanged (or improved)

---

## Common Issues & Solutions

### Issue 1: Legacy Code Has Hidden Dependencies

**Symptoms:**
- Unexpected failures in seemingly unrelated areas
- "Magic" behavior that's not documented

**Solution:**
```python
# Use dependency injection to make dependencies explicit
class ModernService:
    def __init__(
        self,
        legacy_database: LegacyDatabase,
        legacy_cache: LegacyCache,
        legacy_email: LegacyEmailService  # Now explicit!
    ):
        self.db = legacy_database
        self.cache = legacy_cache
        self.email = legacy_email

# Document discovered dependencies
"""
IMPORTANT: This service secretly depends on:
- Global config loaded at startup
- Singleton database connection
- Thread-local request context
See LEGACY_DEPENDENCIES.md for details
"""
```

---

### Issue 2: No Tests, Can't Safely Change

**Symptoms:**
- Fear of making any changes
- No way to verify behavior

**Solution:**
```python
# Create approval/snapshot tests
def test_legacy_report_generation():
    """Approval test: captures current output."""
    report = LegacyReportGenerator().generate(test_data)
    
    # First run: creates baseline
    # Future runs: compares against baseline
    verify(report)  # pytest-approve or similar

# Record and replay for complex interactions
import vcr

@vcr.use_cassette('fixtures/legacy_api_call.yaml')
def test_legacy_api_integration():
    """Records real API responses for replay."""
    result = legacy_api.fetch_data()
    assert result.status_code == 200
```

---

## Best Practices

### DO:
✅ Start with comprehensive testing  
✅ Use feature flags for gradual rollout  
✅ Create clear boundaries (anti-corruption layers)  
✅ Run systems in parallel initially  
✅ Monitor everything during migration  
✅ Document legacy behavior (including bugs)  
✅ Plan for rollback at every step  
✅ Migrate incrementally, not all at once

### DON'T:
❌ Assume you understand legacy without testing  
❌ Make multiple changes simultaneously  
❌ Skip the safety net (tests)  
❌ Let legacy patterns leak into new code  
❌ Rush the migration  
❌ Ignore monitoring and metrics  
❌ Forget to remove feature flags after migration  
❌ Try to fix legacy bugs during integration

---

## Related Workflows

**Before This Workflow:**
- [[dev-001]](technical_debt_identification.md) - Identify technical debt
- [[dev-013]](refactoring_strategy.md) - Plan refactoring approach

**After This Workflow:**
- [[tes-005]](../testing/test_writing.md) - Write comprehensive tests
- [[qua-001]](../quality-assurance/code_review_checklist.md) - Review integration code

**Complementary Workflows:**
- [[dvo-015]](../devops/rollback_procedure.md) - Rollback if needed
- [[dvo-001]](../devops/application_monitoring_setup.md) - Monitor both systems

---

## Tags

`legacy-code` `refactoring` `integration` `migration` `technical-debt` `strangler-fig` `adapter-pattern` `testing` `feature-flags`
