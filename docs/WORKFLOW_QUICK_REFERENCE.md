# Workflow Structure Quick Reference

## 📋 Complete Workflow Template

```markdown
# [Workflow Name]

**ID:** [category]-[number]
**Category:** [Category Name]
**Priority:** [CRITICAL|HIGH|MEDIUM|LOW]
**Complexity:** [Simple|Moderate|Complex|Expert]
**Estimated Time:** [X minutes/hours]
**Last Updated:** YYYY-MM-DD

---

## Purpose

**What:** [One sentence - what it does]
**Why:** [One sentence - why it matters]
**When to use:**
- [Trigger/situation 1]
- [Trigger/situation 2]

---

## Prerequisites

**Required:**
- [ ] [Tool/knowledge 1]
- [ ] [Tool/knowledge 2]

**Check before starting:**
```bash
# Verification commands
```

---

## Implementation Steps

### Step 1: [Action Name]
**What:** [Brief description]
**How:**
[Instructions]

```bash
# Code/commands
```

**Verification:**
- [ ] Check 1
- [ ] Check 2

**If This Fails:**
→ [Troubleshooting]

---

### Step 2: [Action Name]
[Repeat...]

---

## Verification Checklist
- [ ] Main outcome achieved
- [ ] Tests pass
- [ ] No errors introduced

---

## Common Issues

### Issue: [Problem]
**Symptoms:** [What you see]
**Solution:** [How to fix]

---

## Examples

### Example: [Scenario]
**Context:** [Situation]
**Code:**
```bash
# Commands
```
**Result:** [Outcome]

---

## Best Practices

### DO:
✅ [Good practice 1]
✅ [Good practice 2]

### DON'T:
❌ [Bad practice 1]
❌ [Bad practice 2]

---

## Related Workflows
- [[id]](path) - Before this
- [[id]](path) - After this

---

## Tags
`tag1` `tag2` `tag3`
```

---

## 🎯 Priority Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| **CRITICAL** | System breaks without it | Security patches, production incidents |
| **HIGH** | Blocks development | CI/CD setup, environment config |
| **MEDIUM** | Important but not blocking | Refactoring, optimization |
| **LOW** | Nice to have | Documentation updates, cleanup |

---

## 🔧 Complexity Levels

| Level | Characteristics | Typical Time | Prerequisites |
|-------|----------------|--------------|---------------|
| **Simple** | 3-5 steps, single tool | 5-15 min | Minimal |
| **Moderate** | 5-10 steps, 2-3 tools | 15-45 min | Some experience |
| **Complex** | 10+ steps, multiple systems | 1-3 hours | Good understanding |
| **Expert** | Deep integration, critical | 3+ hours | Expert knowledge |

---

## 📝 Section Checklist

### 🔴 REQUIRED (Must Include)
- [ ] Title & ID
- [ ] Purpose (What/Why/When)
- [ ] Prerequisites
- [ ] Implementation Steps (3+ steps)
- [ ] Verification Checklist
- [ ] Tags

### 🟡 HIGHLY RECOMMENDED
- [ ] Common Issues & Solutions
- [ ] Examples (2+ scenarios)
- [ ] Best Practices (DO/DON'T)
- [ ] Related Workflows

### 🟢 OPTIONAL (Enhances Quality)
- [ ] Decision Trees
- [ ] Patterns & Variations
- [ ] Version History
- [ ] Specialized sections

---

## 🏷️ Tag Categories

### Technology Tags
`python` `docker` `kubernetes` `react` `fastapi` `postgres` `aws`

### Category Tags
`development` `devops` `frontend` `backend` `data-engineering` `ml` `security`

### Activity Tags
`setup` `deployment` `testing` `refactoring` `debugging` `monitoring`

### Complexity Tags
`beginner` `intermediate` `advanced` `expert`

### Use Case Tags
`ci-cd` `api-design` `database` `performance` `automation` `quality`

**Rule:** 5-8 tags per workflow, mix categories

---

## 📏 Step Structure Template

```markdown
### Step X: [Verb] [Object]

**What:** [One sentence - what this step accomplishes]

**Why:** [Optional - why this step matters]

**How:**
1. [Detailed instruction 1]
2. [Detailed instruction 2]

**Code/Commands:**
```language
# Actual runnable code
command --option value
```

**Expected Result:**
[What you should see/get]

**Verification:**
- [ ] [Check item 1]
- [ ] [Check item 2]

**If This Fails:**
→ [What to try] or → See [[workflow-id]](path)
```

---

## 🎨 Formatting Quick Tips

### Headers
```markdown
# H1 - Title only
## H2 - Major sections
### H3 - Subsections
#### H4 - Minor points
```

### Emphasis
```markdown
**Bold** - Important terms
*Italic* - Definitions
`code` - Commands/functions
> Quote - Important notes
```

### Lists
```markdown
- Bullet point
  - Nested point
- [ ] Checkbox unchecked
- [x] Checkbox checked

1. Numbered item
2. Numbered item
```

### Code Blocks
````markdown
```python
# Python code
def example():
    pass
```

```bash
# Shell commands
npm install
```

```yaml
# Config files
key: value
```
````

### Links
```markdown
[Text](https://url.com)
[[workflow-id]](../category/file.md)
```

---

## ⚡ Common Sections Quick Copy

### Prerequisites Section
```markdown
## Prerequisites

**Required Tools:**
- [ ] Tool 1 (version X.X+)
- [ ] Tool 2 with access to Y

**Required Knowledge:**
- [ ] Understanding of concept A
- [ ] Familiarity with system B

**Required Files:**
- [ ] [path/to/file.ext] - Purpose

**Verification:**
```bash
tool1 --version  # Should show X.X+
tool2 check      # Should return OK
```
```

### Verification Checklist
```markdown
## Verification Checklist

After completing this workflow:

- [ ] Primary goal achieved
- [ ] All tests pass
- [ ] No new errors introduced
- [ ] Documentation updated
- [ ] Changes committed
- [ ] Team notified (if needed)
```

### Common Issues
```markdown
## Common Issues & Solutions

### Issue: [Problem Description]
**Symptoms:**
- [Symptom 1]
- Error: `error message`

**Cause:**
[Root cause explanation]

**Solution:**
```bash
# Step-by-step fix
command1
command2
```

**Prevention:**
[How to avoid in future]
```

### Examples Section
```markdown
## Examples

### Example 1: [Common Scenario]
**Context:** [When this happens]

**Setup:**
[Starting state]

**Execution:**
```bash
command --flag value
```

**Result:**
[What should happen]
```

### Best Practices
```markdown
## Best Practices

### DO:
✅ Action 1 with reason
✅ Action 2 with reason
✅ Action 3 with reason

### DON'T:
❌ Anti-pattern 1 with reason
❌ Anti-pattern 2 with reason
❌ Anti-pattern 3 with reason
```

---

## 🔗 Workflow Relationships

### Before/After Links
```markdown
## Related Workflows

**Prerequisites (do first):**
- [[setup-001]](../setup/environment.md) - Sets up dev environment
- [[dev-002]](../development/config.md) - Configures project

**Next Steps (do after):**
- [[test-001]](../testing/unit_tests.md) - Write tests for new code
- [[quality-001]](../quality/code_review.md) - Submit for review

**Alternatives (instead of this):**
- [[dev-003]](../development/alternative.md) - Use when condition X
```

---

## 🎯 Quality Checklist

Before submitting a workflow:

### Content Quality
- [ ] Purpose clearly stated
- [ ] All steps tested and work
- [ ] Code examples are runnable
- [ ] Links are valid
- [ ] No spelling/grammar errors

### Structure Quality
- [ ] Follows template
- [ ] Logical flow
- [ ] Consistent formatting
- [ ] Proper markdown syntax

### Metadata Quality
- [ ] ID is unique and follows pattern
- [ ] Tags are relevant
- [ ] Time estimate is realistic
- [ ] Complexity level is accurate

### Completeness
- [ ] Has all required sections
- [ ] Has verification checklist
- [ ] Has at least 1 example
- [ ] Has common issues (if applicable)

---

## 📊 Example Workflows by Complexity

### Simple Workflow Example
```markdown
# Run Tests with Coverage

**ID:** test-001
**Complexity:** Simple
**Time:** 5 minutes

## Purpose
Run test suite with coverage reporting

## Steps
1. Install pytest-cov
2. Run tests with coverage
3. View report

[3 simple steps total]
```

### Moderate Workflow Example
```markdown
# FastAPI Endpoint Creation

**ID:** dev-010
**Complexity:** Moderate
**Time:** 30 minutes

## Purpose
Create new REST API endpoint

## Steps
1. Define Pydantic models
2. Create route handler
3. Add validation
4. Write tests
5. Update OpenAPI docs

[5-7 steps with examples]
```

### Complex Workflow Example
```markdown
# Kubernetes Production Deployment

**ID:** devops-015
**Complexity:** Complex
**Time:** 3 hours

## Purpose
Deploy application to production K8s cluster

## Steps
1. Build container image
2. Push to registry
3. Update K8s manifests
4. Apply staging deployment
5. Run smoke tests
6. Deploy to production
7. Monitor rollout
8. Verify health checks
9. Setup alerts
10. Document changes

[10+ steps, multiple examples, extensive troubleshooting]
```

---

## 💡 Pro Tips

### Writing Steps
1. **Use action verbs** - "Configure", "Deploy", "Test"
2. **Be specific** - "Install Python 3.11+" not "Install Python"
3. **Show examples** - Don't just describe, demonstrate
4. **Include output** - Show what success looks like
5. **Handle errors** - Tell users what to do when things fail

### Writing Examples
1. **Start simple** - Basic case first
2. **Progress to complex** - Build on simple example
3. **Show real commands** - Actual copy-paste-able code
4. **Explain the result** - What should happen
5. **Use realistic data** - Not foo/bar but actual domain data

### Organizing Content
1. **Most important first** - Common case before edge cases
2. **Group related items** - Keep prerequisites together
3. **Use white space** - Don't wall of text
4. **Consistent structure** - Follow template
5. **Link liberally** - Connect to related workflows

---

## 🚀 Quick Start: Create a New Workflow

```bash
# 1. Copy template
cp workflows/templates/_workflow_template.md workflows/[category]/[name].md

# 2. Fill in metadata
# - Choose unique ID
# - Set priority/complexity
# - Estimate time

# 3. Write purpose
# - What it does (1 sentence)
# - Why it matters (1 sentence)  
# - When to use (2-3 bullets)

# 4. List prerequisites
# - Required tools/knowledge
# - Verification commands

# 5. Write steps
# - 3-10 steps
# - Code examples
# - Verification for each

# 6. Add verification checklist
# - Final checks
# - Success criteria

# 7. Add examples (2+)
# - Simple case
# - Complex case

# 8. Add common issues (3+)
# - Problem/solution pairs

# 9. Link related workflows
# - Before/after/alternatives

# 10. Tag appropriately
# - 5-8 relevant tags
```

---

## 📚 Resources

- **Full Structure Guide:** [WORKFLOW_FILE_STRUCTURE.md](./WORKFLOW_FILE_STRUCTURE.md)
- **Template File:** [workflows/templates/_workflow_template.md](../workflows/templates/_workflow_template.md)
- **Example Workflows:** See any workflow in `workflows/*/` directories
- **Markdown Guide:** [CommonMark Spec](https://commonmark.org/)

---

**Remember:** A good workflow is clear, complete, and actionable. When in doubt, test it yourself!
