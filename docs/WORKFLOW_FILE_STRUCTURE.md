# Workflow/Skill File Structure Reference

## Complete Information Architecture

Every workflow/skill file should contain the following sections and information:

---

## 1. HEADER METADATA (Required)

```markdown
# [Workflow Name]

**ID:** [category]-[number]  (e.g., dev-005, devops-004)
**Category:** [Category Name]
**Priority:** [CRITICAL | HIGH | MEDIUM | LOW]
**Complexity:** [Simple | Moderate | Complex | Expert]
**Estimated Time:** [X minutes/hours]
**Frequency:** [Once | Per Project | Monthly | As Needed]
**Last Updated:** YYYY-MM-DD
**Status:** [✅ Complete | 🔧 Built | 📝 Implied | ⭐ TODO]
```

**Purpose:** Quick reference metadata for searching, sorting, and understanding scope

---

## 2. PURPOSE SECTION (Required)

```markdown
## Purpose

**What:** [1-2 sentence description of what this workflow does]

**Why:** [Why this workflow matters, benefits it provides]

**When to use:**
- [Trigger phrase 1]
- [Situation 1]
- [Use case 1]
```

**Purpose:** Helps users and AI assistants understand when to apply this workflow

---

## 3. PREREQUISITES (Required)

```markdown
## Prerequisites

**Required Knowledge:**
- [ ] [Knowledge item 1]
- [ ] [Knowledge item 2]

**Required Tools/Access:**
- [ ] [Tool 1] - Version X.X+
- [ ] [Access/Permission 2]

**Required Files:**
- [ ] [File path 1] - [Purpose]
- [ ] [File path 2] - [Purpose]

**Check before starting:**
```bash
# Verification commands
command --version
```
```

**Purpose:** Ensures user has everything needed before starting

---

## 4. DEPENDENCIES (Optional but Recommended)

```markdown
## Dependencies

**Auto-Load These Workflows:**
- [[workflow-id]](../path/to/workflow.md) - [Why this is needed first]

**Auto-Load These Files:**
- [config/file.yaml] - [Configuration needed]

**Called By These Workflows:**
- [[workflow-id]](../path/to/workflow.md) - [Context of usage]

**Related Workflows:**
- [[workflow-id]](path) - [Before/After/Alternative]
```

**Purpose:** Maps workflow relationships for intelligent chaining

---

## 5. IMPLEMENTATION STEPS (Required)

```markdown
## Implementation Steps / Procedure

### Step 1: [Step Name]

**What:** [Brief description of what this step accomplishes]

**Why:** [Why this step is important]

**How:**
[Detailed instructions]

**Commands/Code:**
```bash
# Example commands with comments
command --option value
```

```python
# Python code examples
def example():
    pass
```

**Expected Result:**
[What should happen when this step succeeds]

**Verification:**
- [ ] Check 1
- [ ] Check 2

**If This Fails:**
→ [Troubleshooting guidance or link to related workflow]

---

### Step 2: [Step Name]
[Repeat pattern for each step]
```

**Purpose:** Step-by-step executable instructions

**Key Elements:**
- **Sequential numbering** - Clear progression
- **Action-oriented headers** - "Set up environment", "Configure database"
- **Code examples** - Real, runnable commands
- **Verification checks** - How to confirm success
- **Failure handling** - What to do if it breaks

---

## 6. VERIFICATION CHECKLIST (Required)

```markdown
## Verification Checklist

After completing this workflow, verify:

- [ ] [Verification item 1]
- [ ] [Verification item 2]
- [ ] No new errors introduced
- [ ] Tests passing
- [ ] Documentation updated (if applicable)
- [ ] Code committed and pushed (if applicable)
```

**Purpose:** Confirms workflow completion and quality

---

## 7. COMMON ISSUES & SOLUTIONS (Highly Recommended)

```markdown
## Common Issues & Solutions

### Issue 1: [Problem Description]

**Symptoms:**
- [Symptom 1]
- [Error message example]

**Cause:**
[Why this happens]

**Solution:**
[Step-by-step fix]

**Prevention:**
[How to avoid this in the future]

---

### Issue 2: [Problem Description]
[Repeat pattern for each common issue]
```

**Purpose:** Anticipates and solves common problems

---

## 8. EXAMPLES (Highly Recommended)

```markdown
## Examples

### Example 1: [Scenario Name]

**Context:** [Real-world situation]

**Setup:**
[Initial state]

**Execution:**
```bash
# Commands used
command arg1 arg2
```

**Result:**
[Outcome and what user should see]

---

### Example 2: [Scenario Name]
[Repeat for different scenarios]
```

**Purpose:** Demonstrates real-world application

**Types of Examples:**
- **Simple case** - Basic usage
- **Complex case** - Advanced usage with edge cases
- **Common scenario** - Typical real-world situation
- **Integration example** - How it works with other workflows

---

## 9. BEST PRACTICES (Recommended)

```markdown
## Best Practices

### DO:
✅ [Best practice 1]
✅ [Best practice 2]
✅ [Best practice 3]

### DON'T:
❌ [Anti-pattern 1]
❌ [Anti-pattern 2]
❌ [Anti-pattern 3]
```

**Purpose:** Guides users toward optimal usage

---

## 10. DECISION TREES (Optional - for Complex Workflows)

```markdown
## Decision Trees

### Which approach should I use?
```
Question?
├─ Condition A
│   ├─ Sub-condition 1 → Solution 1
│   └─ Sub-condition 2 → Solution 2
├─ Condition B
│   └─ Solution 3
└─ Default → Solution 4
```
```

**Purpose:** Helps users navigate complex choices

---

## 11. PATTERNS & VARIATIONS (Optional)

```markdown
## Common Patterns

### Pattern 1: [Pattern Name]
**When to use:** [Situation]
**Implementation:**
```language
# Code example
```

### Pattern 2: [Pattern Name]
[Repeat pattern]
```

**Purpose:** Shows different ways to apply the workflow

---

## 12. RELATED WORKFLOWS (Required)

```markdown
## Related Workflows

**Before This Workflow:**
- [[workflow-id]](path) - [Should be done first because...]

**After This Workflow:**
- [[workflow-id]](path) - [Natural next step because...]

**Alternative Workflows:**
- [[workflow-id]](path) - [Use instead when...]

**Complementary Workflows:**
- [[workflow-id]](path) - [Use together for...]
```

**Purpose:** Creates workflow graph for intelligent navigation

---

## 13. NOTES (Optional)

```markdown
## Notes

### For Code Buddy (AI Assistant)
[Special instructions for AI executing this workflow]
- Always verify X before Y
- Never skip step 3
- Check file exists before modifying

### For Humans
[Context, rationale, historical notes]
- This approach was chosen because...
- Previous version did X but we changed to Y because...

### Deviation Protocol
[When/how to safely deviate from this workflow]
- Can skip step X if condition Y is true
- Alternative approach available for edge case Z
```

**Purpose:** Additional context for execution

---

## 14. VERSION HISTORY (Optional)

```markdown
## Version History

- **v1.0** (2025-01-15): Initial creation - [Author]
- **v1.1** (2025-03-20): Added Docker support - [Author]
- **v2.0** (2025-06-10): Complete rewrite for Python 3.11+ - [Author]
```

**Purpose:** Track evolution and changes

---

## 15. TAGS & METADATA (Required)

```markdown
## Tags
`primary-tag` `secondary-tag` `technology` `category` `use-case`

## Additional Metadata
**Automation Potential:** [None | Partial | Full]
**Risk Level:** [Low | Medium | High]
**Team Size:** [Solo | Small (2-5) | Large (6+)]
**Environment:** [Local | CI/CD | Production]
**Last Reviewed:** YYYY-MM-DD
**Next Review Due:** YYYY-MM-DD
```

**Purpose:** Enables advanced search and filtering

---

## SPECIAL SECTIONS (Workflow-Specific)

Depending on the workflow type, include relevant specialized sections:

### For DevOps Workflows:
```markdown
## Platform-Specific Instructions
- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI

## Deployment Strategies
- Blue-Green
- Canary
- Rolling

## Monitoring & Alerts
[Metrics to track]
```

### For Development Workflows:
```markdown
## Code Examples
[Before/After comparisons]

## Testing Strategy
[How to verify the changes]

## Performance Considerations
[Impact on performance]
```

### For Security Workflows:
```markdown
## Security Considerations
[Risks and mitigations]

## Compliance Requirements
[Regulatory considerations]

## Incident Response
[What to do if things go wrong]
```

### For Data Workflows:
```markdown
## Data Schema
[Input/output formats]

## Performance Tuning
[Optimization strategies]

## Data Quality Checks
[Validation rules]
```

---

## QUALITY STANDARDS

### Content Quality
- **Clear and concise** - No fluff, get to the point
- **Action-oriented** - Use verbs, be directive
- **Complete** - Include all necessary information
- **Accurate** - Test all commands and examples
- **Up-to-date** - Reflect current best practices

### Code Examples
- **Runnable** - Should work as-is when copied
- **Commented** - Explain non-obvious parts
- **Safe** - Include error handling
- **Complete** - Don't leave out imports or setup

### Organization
- **Logical flow** - Natural progression
- **Consistent structure** - Follow template
- **Easy scanning** - Use headers, bullets, formatting
- **Searchable** - Include relevant keywords

---

## MINIMUM VIABLE WORKFLOW

At minimum, a workflow must have:

1. ✅ **Title and ID**
2. ✅ **Purpose** (What/Why/When)
3. ✅ **Prerequisites**
4. ✅ **Implementation Steps** (at least 3 steps)
5. ✅ **Verification Checklist**
6. ✅ **Tags**

**Everything else enhances but is not strictly required.**

---

## WORKFLOW SIZE GUIDELINES

### Simple Workflow (5-10 min)
- 3-5 steps
- Minimal prerequisites
- Few examples
- Focus on common case

### Moderate Workflow (10-30 min)
- 5-10 steps
- Multiple examples
- Common issues section
- Decision points

### Complex Workflow (30+ min)
- 10+ steps
- Comprehensive examples
- Decision trees
- Multiple patterns
- Extensive troubleshooting

### Expert Workflow (multi-hour)
- Multiple sub-sections
- Advanced patterns
- Integration with other systems
- Performance tuning
- Security considerations

---

## FILE NAMING CONVENTIONS

```
[category_name]/[workflow_name].md

Examples:
- development/type_annotation_addition.md
- devops/cicd_pipeline_setup.md
- frontend-development/react_component_creation.md
- machine-learning/model_training_evaluation.md
```

**Rules:**
- Use lowercase
- Use underscores (not hyphens) for multi-word names
- Keep names descriptive but concise
- Match the category directory structure

---

## LINKING CONVENTIONS

### Internal Links (to other workflows)
```markdown
[[workflow-id]](../category/workflow_file.md)
Example: [[dev-005]](../development/type_annotation_addition.md)
```

### External Links
```markdown
[Link Text](https://example.com)
Example: [Python Typing Docs](https://docs.python.org/3/library/typing.html)
```

### File References
```markdown
[config/settings.py]
[.github/workflows/ci.yml]
```

---

## MARKDOWN FORMATTING STANDARDS

### Headers
```markdown
# Main Title (H1) - Only once at top
## Major Sections (H2)
### Subsections (H3)
#### Minor Subsections (H4)
```

### Code Blocks
````markdown
```python
# Python code with language specified
def example():
    pass
```

```bash
# Shell commands
command --option value
```

```yaml
# Configuration files
key: value
```
````

### Lists
```markdown
- Unordered item
- Unordered item
  - Nested item
  - Nested item

1. Ordered item
2. Ordered item
   1. Nested ordered
   2. Nested ordered
```

### Emphasis
```markdown
**Bold** for emphasis
*Italic* for terms
`code` for inline code
> Blockquote for important notes
```

### Tables
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
```

### Checkboxes
```markdown
- [ ] Incomplete item
- [x] Complete item
```

---

## TESTING YOUR WORKFLOW

Before submitting a workflow, verify:

1. ✅ **Follows template structure**
2. ✅ **All code examples tested**
3. ✅ **Links work correctly**
4. ✅ **Markdown renders properly**
5. ✅ **Commands execute successfully**
6. ✅ **Verification checklist is accurate**
7. ✅ **No spelling/grammar errors**
8. ✅ **Tags are relevant**
9. ✅ **Metadata is complete**
10. ✅ **Fresh eyes review (if possible)**

---

## SUMMARY: ESSENTIAL COMPONENTS

```
🔴 CRITICAL (Must Have):
- Title & ID
- Purpose (What/Why/When)
- Prerequisites
- Implementation Steps
- Verification Checklist
- Tags

🟡 IMPORTANT (Should Have):
- Common Issues & Solutions
- Examples
- Best Practices
- Related Workflows

🟢 NICE TO HAVE:
- Decision Trees
- Patterns & Variations
- Version History
- Specialized sections
```

---

This structure ensures workflows are:
- **Discoverable** - Easy to find via search
- **Understandable** - Clear purpose and context
- **Executable** - Step-by-step instructions
- **Verifiable** - Checkpoints and validation
- **Maintainable** - Version tracking and updates
- **Connected** - Linked to related workflows
