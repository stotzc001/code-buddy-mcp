"""Generate missing workflow stub files efficiently."""
from pathlib import Path

# Define all missing workflows with their metadata
MISSING_WORKFLOWS = {
    "architecture": [
        ("distributed_systems_patterns", "arc-004", "HIGH", "Complex", "60-120 minutes",
         "Design patterns for building distributed systems",
         "`architecture` `distributed-systems` `patterns` `scalability` `reliability`"),
        ("event_driven_architecture", "arc-005", "HIGH", "Complex", "60-120 minutes",
         "Designing event-driven architectures with messaging",
         "`architecture` `event-driven` `messaging` `asynchronous` `decoupling`"),
        ("microservices_patterns", "arc-006", "HIGH", "Complex", "60-120 minutes",
         "Patterns for designing and implementing microservices",
         "`architecture` `microservices` `patterns` `service-mesh` `distributed`"),
        ("scalability_patterns", "arc-007", "HIGH", "Complex", "60-120 minutes",
         "Patterns for building scalable systems",
         "`architecture` `scalability` `patterns` `performance` `high-availability`"),
        ("system_architecture_design", "arc-008", "HIGH", "Complex", "60-120 minutes",
         "Comprehensive system architecture design workflow",
         "`architecture` `system-design` `patterns` `trade-offs` `best-practices`"),
        ("architecture_decision_records", "arc-009", "MEDIUM", "Moderate", "30-60 minutes",
         "Creating and maintaining Architecture Decision Records (ADRs)",
         "`architecture` `adr` `documentation` `decision-making` `governance`"),
    ],
}

STUB_TEMPLATE = """# {title}

**ID:** {id}  
**Category:** {category}  
**Priority:** {priority}  
**Complexity:** {complexity}  
**Estimated Time:** {time}  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** {purpose}

**Why:** {purpose} improves system quality and development efficiency

**When to use:**
- Working on {title_lower} tasks
- Setting up new projects
- Improving existing processes

---

## Prerequisites

**Required:**
- [ ] [Tool/Knowledge 1]
- [ ] [Tool/Knowledge 2]

**Check before starting:**
```bash
# Verification commands
```

---

## Implementation Steps

### Step 1: [Step Name]

**What:** [Brief description]

**How:**
[Detailed instructions]

**Code/Commands:**
```bash
# Example commands
```

**Verification:**
- [ ] [Check 1]
- [ ] [Check 2]

**If This Fails:**
→ [Troubleshooting]

---

### Step 2: [Step Name]

[Additional steps to be filled in]

---

## Verification Checklist

After completing this workflow:

- [ ] [Primary goal achieved]
- [ ] All tests pass
- [ ] No new errors introduced
- [ ] Documentation updated
- [ ] Changes committed

---

## Common Issues & Solutions

### Issue: [Problem Description]

**Symptoms:**
- [Symptom 1]

**Solution:**
[Step-by-step fix]

**Prevention:**
[How to avoid]

---

## Examples

### Example 1: [Scenario Name]

**Context:** [Situation]

**Execution:**
```bash
# Commands
```

**Result:** [Outcome]

---

## Best Practices

### DO:
✅ [Best practice 1]
✅ [Best practice 2]

### DON'T:
❌ [Anti-pattern 1]
❌ [Anti-pattern 2]

---

## Related Workflows

**Prerequisites:**
- [To be determined based on detailed analysis]

**Next Steps:**
- [To be determined based on detailed analysis]

**Alternatives:**
- [To be determined based on detailed analysis]

---

## Tags
{tags}
"""

def filename_to_title(filename):
    """Convert filename to human-readable title."""
    return filename.replace('_', ' ').title()

def generate_stubs():
    """Generate all missing workflow stub files."""
    base_path = Path("C:/Repos/code_buddy_mcp/workflows")
    total_created = 0
    
    for category, workflows in MISSING_WORKFLOWS.items():
        category_path = base_path / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{category.upper()} ({len(workflows)} workflows)")
        print("-" * 60)
        
        for filename, wf_id, priority, complexity, time, purpose, tags in workflows:
            title = filename_to_title(filename)
            title_lower = title.lower()
            cat_title = category.replace('-', ' ').title()
            
            content = STUB_TEMPLATE.format(
                title=title,
                id=wf_id,
                category=cat_title,
                priority=priority,
                complexity=complexity,
                time=time,
                purpose=purpose,
                title_lower=title_lower,
                tags=tags
            )
            
            file_path = category_path / f"{filename}.md"
            file_path.write_text(content, encoding='utf-8')
            
            print(f"  ✅ Created: {filename}.md")
            total_created += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully created {total_created} workflow stub files!")
    print(f"{'='*60}")

if __name__ == "__main__":
    generate_stubs()
