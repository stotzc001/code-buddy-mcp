"""
Generate stub files for the 25 missing workflows.
"""
from pathlib import Path
from datetime import datetime

# Workflow definitions with proper metadata from inventory
MISSING_WORKFLOWS = {
    # Development (12 missing)
    "development": [
        {
            "filename": "add_secrets_github_cli.md",
            "id": "dev-021",
            "title": "Add Secrets via GitHub CLI",
            "priority": "MEDIUM",
            "complexity": "Simple",
            "time": "15-30 minutes",
            "tags": ["development", "security", "secrets", "github", "automation"],
        },
        {
            "filename": "application_settings.md",
            "id": "dev-015",
            "title": "Application Settings Configuration",
            "priority": "MEDIUM",
            "complexity": "Simple",
            "time": "15-30 minutes",
            "tags": ["development", "configuration", "settings", "environment"],
        },
        {
            "filename": "breaking_api_changes.md",
            "id": "dev-026",
            "title": "Breaking API Changes",
            "priority": "HIGH",
            "complexity": "Complex",
            "time": "1-2 hours",
            "tags": ["development", "api-design", "versioning", "migration"],
        },
        {
            "filename": "code_review_response.md",
            "id": "dev-030",
            "title": "Code Review Response Workflow",
            "priority": "MEDIUM",
            "complexity": "Moderate",
            "time": "30-60 minutes",
            "tags": ["development", "code-review", "collaboration", "feedback"],
        },
        {
            "filename": "if_project_has_formatter.md",
            "id": "dev-017",
            "title": "If Project Has Formatter",
            "priority": "LOW",
            "complexity": "Simple",
            "time": "15-30 minutes",
            "tags": ["development", "formatting", "code-style", "automation"],
        },
        {
            "filename": "install_vercel_cli.md",
            "id": "dev-020",
            "title": "Install Vercel CLI",
            "priority": "LOW",
            "complexity": "Simple",
            "time": "15-30 minutes",
            "tags": ["development", "deployment", "vercel", "cli-tools"],
        },
        {
            "filename": "legacy_code_integration.md",
            "id": "dev-028",
            "title": "Legacy Code Integration",
            "priority": "HIGH",
            "complexity": "Complex",
            "time": "1-2 hours",
            "tags": ["development", "refactoring", "migration", "technical-debt"],
        },
        {
            "filename": "module_creation_headers.md",
            "id": "dev-014",
            "title": "Module Creation with Headers",
            "priority": "MEDIUM",
            "complexity": "Simple",
            "time": "15-30 minutes",
            "tags": ["development", "python", "code-organization", "standards"],
        },
        {
            "filename": "pydantic_settings.md",
            "id": "dev-016",
            "title": "Pydantic Settings Configuration",
            "priority": "MEDIUM",
            "complexity": "Moderate",
            "time": "30-60 minutes",
            "tags": ["development", "python", "pydantic", "configuration", "type-safety"],
        },
        {
            "filename": "run_tests_coverage.md",
            "id": "dev-019",
            "title": "Run Tests with Coverage",
            "priority": "HIGH",
            "complexity": "Simple",
            "time": "15-30 minutes",
            "tags": ["development", "testing", "coverage", "quality-assurance"],
        },
        {
            "filename": "spike-research-workflow.md",
            "id": "dev-029",
            "title": "Spike Research Workflow",
            "priority": "MEDIUM",
            "complexity": "Moderate",
            "time": "30-60 minutes",
            "tags": ["development", "research", "discovery", "prototyping"],
        },
        {
            "filename": "system_logs_config.md",
            "id": "dev-018",
            "title": "System Logs Configuration",
            "priority": "MEDIUM",
            "complexity": "Moderate",
            "time": "30-60 minutes",
            "tags": ["development", "logging", "monitoring", "debugging"],
        },
    ],
    # Configuration Management (4 missing)
    "configuration-management": [
        {
            "filename": "application_settings.md",
            "id": "cfg-001",
            "title": "Application Settings",
            "priority": "MEDIUM",
            "complexity": "Simple",
            "time": "15-30 minutes",
            "tags": ["configuration", "settings", "environment", "config-management"],
        },
        {
            "filename": "project_formatter_setup.md",
            "id": "cfg-003",
            "title": "Project Formatter Setup",
            "priority": "LOW",
            "complexity": "Simple",
            "time": "15-30 minutes",
            "tags": ["configuration", "formatting", "code-style", "black", "prettier"],
        },
        {
            "filename": "pydantic_settings_config.md",
            "id": "cfg-002",
            "title": "Pydantic Settings Configuration",
            "priority": "MEDIUM",
            "complexity": "Moderate",
            "time": "30-60 minutes",
            "tags": ["configuration", "pydantic", "python", "type-safety", "validation"],
        },
        {
            "filename": "system_logs_config.md",
            "id": "cfg-004",
            "title": "System Logs Configuration",
            "priority": "MEDIUM",
            "complexity": "Moderate",
            "time": "30-60 minutes",
            "tags": ["configuration", "logging", "monitoring", "debugging", "observability"],
        },
    ],
    # Data Engineering (2 missing)
    "data-engineering": [
        {
            "filename": "big_data_processing_spark.md",
            "id": "dat-001",
            "title": "Big Data Processing with Spark",
            "priority": "HIGH",
            "complexity": "Complex",
            "time": "1-2 hours",
            "tags": ["data-engineering", "spark", "big-data", "distributed-computing"],
        },
        {
            "filename": "ml_experiment_setup.md",
            "id": "dat-012",
            "title": "ML Experiment Setup",
            "priority": "MEDIUM",
            "complexity": "Moderate",
            "time": "30-60 minutes",
            "tags": ["data-engineering", "ml", "experiments", "data-science", "tracking"],
        },
    ],
    # Security (2 missing)
    "security": [
        {
            "filename": "anthropic_key_rotation.md",
            "id": "sec-005",
            "title": "Anthropic Claude Key Rotation",
            "priority": "HIGH",
            "complexity": "Simple",
            "time": "15-30 minutes",
            "tags": ["security", "api-keys", "rotation", "anthropic", "automation"],
        },
        {
            "filename": "openai_key_rotation.md",
            "id": "sec-006",
            "title": "OpenAI Key Rotation",
            "priority": "HIGH",
            "complexity": "Simple",
            "time": "15-30 minutes",
            "tags": ["security", "api-keys", "rotation", "openai", "automation"],
        },
    ],
    # DevOps (1 missing)
    "devops": [
        {
            "filename": "rollback_procedure.md",
            "id": "dvo-015",
            "title": "Rollback Procedure",
            "priority": "CRITICAL",
            "complexity": "Moderate",
            "time": "30-60 minutes",
            "tags": ["devops", "deployment", "rollback", "recovery"],
        },
    ],
    # Frontend Development (1 missing)
    "frontend-development": [
        {
            "filename": "frontend_build_deployment.md",
            "id": "fro-011",
            "title": "Frontend Build & Deployment",
            "priority": "HIGH",
            "complexity": "Moderate",
            "time": "30-60 minutes",
            "tags": ["frontend", "build", "deployment", "ci-cd", "optimization"],
        },
    ],
    # Version Control (1 missing)
    "version-control": [
        {
            "filename": "version_release_tagging.md",
            "id": "ver-004",
            "title": "Version Release & Tagging",
            "priority": "MEDIUM",
            "complexity": "Moderate",
            "time": "30-60 minutes",
            "tags": ["version-control", "git", "releases", "tagging", "semantic-versioning"],
        },
    ],
    # Testing (1 missing)
    "testing": [
        {
            "filename": "test_writing.md",
            "id": "tes-005",
            "title": "Test Writing",
            "priority": "HIGH",
            "complexity": "Moderate",
            "time": "30-60 minutes",
            "tags": ["testing", "unit-tests", "tdd", "quality-assurance", "best-practices"],
        },
    ],
    # Discovery (1 missing)
    "discovery": [
        {
            "filename": "spike_research_workflow.md",
            "id": "dis-001",
            "title": "Spike/Research Workflow",
            "priority": "MEDIUM",
            "complexity": "Moderate",
            "time": "30-60 minutes",
            "tags": ["discovery", "research", "spikes", "prototyping", "investigation"],
        },
    ],
}

STUB_TEMPLATE = """# {title}

**ID:** {id}  
**Category:** {category}  
**Priority:** {priority}  
**Complexity:** {complexity}  
**Estimated Time:** {time}  
**Last Updated:** {date}

---

## Purpose

**What:** {purpose_what}

**Why:** {purpose_why}

**When to use:**
{when_to_use}

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

def generate_purpose(title):
    """Generate purpose text based on title."""
    title_lower = title.lower()
    
    what = f"Systematic workflow for {title_lower}"
    
    if 'test' in title_lower:
        why = "Testing ensures code quality and catches bugs early"
    elif 'deploy' in title_lower or 'build' in title_lower:
        why = "Automated deployment reduces errors and speeds up releases"
    elif 'monitor' in title_lower or 'log' in title_lower:
        why = "Monitoring provides visibility into system health and performance"
    elif 'security' in title_lower or 'secret' in title_lower or 'key' in title_lower:
        why = "Security practices protect systems and data from threats"
    elif 'api' in title_lower:
        why = "Well-designed APIs improve developer experience and system integration"
    elif 'configuration' in title_lower or 'settings' in title_lower:
        why = "Proper configuration management ensures consistency across environments"
    else:
        why = "This workflow improves development efficiency and code quality"
    
    return what, why

def generate_when_to_use(title):
    """Generate when to use section."""
    title_lower = title.lower()
    items = [
        f"- Working on {title_lower} tasks",
        "- Setting up new projects or features",
        "- Improving existing processes and workflows",
    ]
    return '\n'.join(items)

# Generate stubs
workflows_dir = Path(r"C:\Repos\code_buddy_mcp\workflows")
date = datetime.now().strftime('%Y-%m-%d')
created_count = 0

for category, workflows in MISSING_WORKFLOWS.items():
    category_dir = workflows_dir / category
    category_dir.mkdir(parents=True, exist_ok=True)
    
    for wf in workflows:
        filepath = category_dir / wf['filename']
        
        # Generate content
        purpose_what, purpose_why = generate_purpose(wf['title'])
        when_to_use = generate_when_to_use(wf['title'])
        tags_str = ' '.join(f'`{tag}`' for tag in wf['tags'])
        
        # Format category name
        category_name = category.replace('-', ' ').title()
        
        content = STUB_TEMPLATE.format(
            title=wf['title'],
            id=wf['id'],
            category=category_name,
            priority=wf['priority'],
            complexity=wf['complexity'],
            time=wf['time'],
            date=date,
            purpose_what=purpose_what,
            purpose_why=purpose_why,
            when_to_use=when_to_use,
            tags=tags_str,
        )
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        created_count += 1
        print(f"✅ Created: {category}/{wf['filename']} ({wf['id']})")

print(f"\n{'='*80}")
print(f"COMPLETE: Created {created_count} workflow stub files")
print(f"{'='*80}")
