# Example: Type Annotation Addition - Parsed Structure

## Token Efficiency Comparison

### OLD STRUCTURE (Current)
```
Single workflow file: type_annotation_addition.md
Size: 17,412 bytes
Estimated tokens: ~4,350 tokens

Loading entire workflow for ANY query about type hints = 4,350 tokens
```

### NEW STRUCTURE (Proposed)

#### 1. Workflow Overview (~400 tokens)
```yaml
workflow:
  id: 1
  name: type_annotation_addition
  title: Type Annotation Addition
  overview: |
    Systematically add Python type hints to untyped code to enable 
    static type checking and improve code quality.
    
    Benefits: Catch bugs before runtime, improve IDE support, 
    serve as documentation, make refactoring safer.
    
    Use when: Working with untyped Python code, preparing for 
    mypy validation, improving maintainability.
  
  category: Development
  tags: [python, typing, type-hints, mypy]
  complexity: moderate
  estimated_time_minutes: 30
```

#### 2. Individual Tasks (~300-500 tokens each)

**Task 1: Assess Current State**
```yaml
task:
  id: 101
  workflow_id: 1
  step_number: 1
  name: assess_current_state
  title: Assess Current State
  content: |
    ## What
    Understand current typing situation in your codebase.
    
    ## How
    1. Run mypy for coverage: `mypy src/`
    2. Generate report: `mypy --html-report mypy-coverage src/`
    3. Count untyped functions
    
    ## Commands
    ```bash
    mypy --install-types --non-interactive src/
    grep -rn "^def " src/ | grep -v " -> " | wc -l
    ```
    
    ## Verify
    - Mypy runs successfully
    - Coverage report generated
    - Priority modules identified
  
  prerequisites: [Python 3.8+, mypy installed]
  verification_checks:
    - Mypy runs without crashing
    - Coverage report generated
  estimated_time_minutes: 10
```
**Tokens: ~350**

**Task 2: Configure Type Checking**
```yaml
task:
  id: 102
  workflow_id: 1
  step_number: 2
  content: |
    ## What
    Set up mypy.ini for gradual typing adoption.
    
    ## How
    Create mypy.ini with:
    ```ini
    [mypy]
    python_version = 3.8
    warn_return_any = True
    disallow_untyped_defs = False
    check_untyped_defs = True
    ```
    
    ## Verify
    Run: `mypy --config-file=mypy.ini src/`
  
  estimated_time_minutes: 5
```
**Tokens: ~250**

**Task 3: Add Simple Function Types**
```yaml
task:
  id: 103
  workflow_id: 1
  step_number: 3
  content: |
    ## What
    Add types to straightforward functions.
    
    ## Example
    Before:
    ```python
    def calculate_total(items, tax_rate):
        return sum(item['price'] for item in items) * (1 + tax_rate)
    ```
    
    After:
    ```python
    def calculate_total(items: List[Dict[str, Any]], tax_rate: float) -> float:
        return sum(item['price'] for item in items) * (1 + tax_rate)
    ```
    
    ## Verify
    - Parameters have types
    - Return type specified
    - Mypy validates
  
  estimated_time_minutes: 15
```
**Tokens: ~300**

**Task 4-7:** Handle Complex Types, Add Class Annotations, Run Mypy, Document Decisions
**Tokens per task: ~300-500**

---

#### 3. Reusable Skills (~200-300 tokens each)

**Skill: Using TypedDict**
```yaml
skill:
  id: 201
  name: using_typeddict
  title: Using TypedDict for Structured Data
  content: |
    Define structured dictionary types instead of Dict[str, Any].
    
    ```python
    from typing import TypedDict
    
    class Item(TypedDict):
        name: str
        price: float
        quantity: int
    
    def calculate_total(items: List[Item]) -> float:
        return sum(item['price'] * item['quantity'] for item in items)
    ```
    
    Result: Type-safe dictionary access with full IDE support.
  
  category: Python
  tags: [python, typing, typeddict]
  use_cases: [Structured data, API responses, Config objects]
```
**Tokens: ~250**

**Skill: Generic Types Pattern**
```yaml
skill:
  id: 202
  name: generic_types_pattern
  content: |
    Use TypeVar for generic functions.
    
    ```python
    from typing import TypeVar, List, Optional
    
    T = TypeVar('T')
    
    def first_or_none(items: List[T]) -> Optional[T]:
        return items[0] if items else None
    
    # Works with any type
    first_num = first_or_none([1, 2, 3])  # int
    first_str = first_or_none(['a', 'b'])  # str
    ```
```
**Tokens: ~200**

**Skill: Protocol for Structural Typing**
```yaml
skill:
  id: 203
  name: protocol_structural_typing
  content: |
    Use Protocol for duck typing.
    
    ```python
    from typing import Protocol
    
    class Drawable(Protocol):
        def draw(self) -> None: ...
    
    def render(obj: Drawable) -> None:
        obj.draw()  # Works with anything with draw()
    ```
```
**Tokens: ~150**

---

## Query Examples with New Structure

### Query: "How do I add type hints to Python?"

**OLD:** Load entire workflow = **4,350 tokens**

**NEW:** Return workflow overview + first 2 tasks = **~1,000 tokens**
- Workflow overview: 400 tokens
- Task 1 (Assess): 350 tokens  
- Task 2 (Configure): 250 tokens

**Savings: 77% ⬇️**

---

### Query: "How to use TypedDict?"

**OLD:** Load entire workflow = **4,350 tokens**

**NEW:** Return specific skill = **~250 tokens**
- Skill: Using TypedDict

**Savings: 94% ⬇️**

---

### Query: "Configure mypy for gradual typing"

**OLD:** Load entire workflow = **4,350 tokens**

**NEW:** Return specific task = **~250 tokens**
- Task 2: Configure Type Checking

**Savings: 94% ⬇️**

---

### Query: "Show me complete type annotation workflow"

**OLD:** Load entire workflow = **4,350 tokens**

**NEW:** Return overview + task list (no content) = **~600 tokens**
- Overview: 400 tokens
- Task list (7 tasks × ~25 tokens): 175 tokens
- Related skills list: 25 tokens

User can then ask for specific tasks: "Show me step 3"

**Savings: 86% ⬇️**

---

## Database Storage Comparison

### OLD
```
workflows table:
- 121 workflows × 17KB average = 2,057KB total
- 121 embeddings × 1024 dimensions = 124 embeddings
```

### NEW
```
workflows table:
- 121 workflows × 2KB overview = 242KB
- 121 embeddings

tasks table:
- 121 workflows × 6 tasks avg × 2KB = 1,452KB
- 726 tasks × embeddings = 726 embeddings

skills table:
- ~200 unique skills × 1.5KB = 300KB
- 200 embeddings

Total: 1,994KB (similar storage)
Total embeddings: 1,047 (better search granularity)
```

---

## Search Results Format

### When user asks: "How to rotate API keys?"

**Search returns:**
```json
{
  "type": "task",
  "workflow": "Secret Management (Solo)",
  "task": "Step 4: Rotate Secrets Regularly",
  "relevance": 0.94,
  "content": "...", 
  "tokens": 450,
  "related_skills": ["Key Rotation Pattern"],
  "full_workflow_link": "workflow_id:4"
}
```

User gets exactly what they need, not 4,300 tokens of unrelated content.

---

## Summary

| Metric | OLD | NEW | Improvement |
|--------|-----|-----|-------------|
| Avg query tokens | 4,350 | 400-600 | **85-90% ⬇️** |
| Specific task query | 4,350 | 250-500 | **88-94% ⬇️** |
| Skill pattern query | 4,350 | 150-300 | **93-97% ⬇️** |
| Search granularity | 121 workflows | 726 tasks + 200 skills | **8x better** |
| Relevance | Medium | High | Much better targeting |

**Result: 10x more efficient while being more useful!** 🚀
