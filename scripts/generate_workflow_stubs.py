"""
Workflow Stub Generator

Run this script locally to:
1. Scan all source workflows
2. Generate stub files in proper categories
3. Assign sequential IDs
4. Create relationship mappings

Usage:
    python generate_workflow_stubs.py
"""

import os
import re
from pathlib import Path
from datetime import datetime

# === CONFIGURATION ===

SOURCE_WORKFLOWS = {
    "development": [
        "technical_debt_identification.md",
        "test_writing.md",
        "third_party_api_integration.md",
        "type_annotation_addition.md",
    ],
    "devops": [
        "application_monitoring_setup.md",
        "auto_scaling_configuration.md",
        "backup_disaster_recovery.md",
        "cicd_pipeline_setup.md",
        "cloud_provider_setup.md",
        "docker_compose_multi_service.md",
        "docker_container_creation.md",
        "incident_response_workflow.md",
        "infrastructure_as_code_terraform.md",
        "kubernetes_deployment.md",
        "log_aggregation_elk.md",
        "performance_tuning.md",
    ],
    "frontend": [
        "accessibility_workflow.md",
        "api_integration_patterns.md",
        "build_deployment.md",
        "component_testing_strategy.md",
        "e2e_testing_workflow.md",
        "form_handling_validation.md",
        "performance_optimization.md",
        "react_component_creation.md",
        "responsive_design_implementation.md",
        "state_management_setup.md",
    ],
    "git": [
        "branch_strategy.md",
        "commit_message_correction.md",
        "merge_conflict_resolution.md",
    ],
    "maintenance": [
        "dependency_update_strategy.md",
        "dependency_upgrade.md",
        "log_analysis.md",
        "maint-011_cross_repo_changes.md",
        "refactoring_strategy.md",
        "rollback_procedure.md",
        "technical_debt_mgmt.md",
        "version_release_tagging.md",
    ],
    "ml": [
        "ab_testing_models.md",
        "automl_hyperparameter_optimization.md",
        "data_preprocessing_pipelines.md",
        "deep_learning_pytorch_tensorflow.md",
        "feature_engineering_selection.md",
        "mlops_pipeline_setup.md",
        "model_deployment_strategies.md",
        "model_monitoring_observability.md",
        "model_training_evaluation.md",
    ],
    "ml_ai": [
        "ml_experiment_setup.md",
    ],
    "people": [
        "ai_assisted_session.md",
        "developer_onboarding.md",
        "pair_programming_ai.md",
        "pair_programming_with_ai.md",
    ],
    "quality": [
        "code_review_checklist.md",
        "complexity_reduction.md",
        "coverage_gap_analysis.md",
        "deviation_protocol.md",
        "graduation_lite_to_strict.md",
        "mypy_type_fixing.md",
        "pr_creation_review.md",
        "quality_gate_execution.md",
        "ruff_error_resolution.md",
        "test_failure_investigation.md",
    ],
    "security": [
        "code_buddy_secret_rules.md",
        "git_history_cleanup_solo.md",
        "secret_incident_solo.md",
        "secret_management_solo.md",
    ],
    "session": [
        "knowledge_transfer.md",
        "progress_tracking.md",
        "startup_resume.md",
        "token_management_handoff.md",
    ],
    "setup": [
        "ci_cd_workflow.md",
        "environment_initialization.md",
        "new_repo_scaffolding.md",
        "pre_commit_hooks.md",
    ],
    "testing": [
        "performance_regression_investigation.md",
        "property_based_testing.md",
        "test-002_mocking_strategy.md",
        "test_data_generation.md",
    ],
    "emergency": [
        "emergency_hotfix.md",
        "incident_response.md",
    ],
}

# Category mapping
CATEGORY_MAP = {
    "development": "development",
    "devops": "devops",
    "frontend": "frontend-development",
    "git": "version-control",
    "maintenance": "development",
    "ml": "machine-learning",
    "ml_ai": "machine-learning",
    "people": "development",
    "quality": "quality-assurance",
    "security": "security",
    "session": "project-management",
    "setup": "development",
    "testing": "testing",
    "emergency": "devops",
}

# Target directory
TARGET_DIR = r"C:\Repos\code_buddy_mcp\workflows"

#=== WORKFLOW STUB TEMPLATE ===

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
{prerequisites}

**Next Steps:**
{next_steps}

**Alternatives:**
{alternatives}

---

## Tags
{tags}
"""

# === HELPER FUNCTIONS ===

def filename_to_title(filename):
    """Convert filename to title."""
    name = filename.replace('.md', '').replace('_', ' ').replace('-', ' ')
    return ' '.join(word.capitalize() for word in name.split())


def extract_tags_from_title(title, category):
    """Extract tags based on title and category."""
    tags = []
    title_lower = title.lower()
    
    # Add category tag
    tags.append(category.replace('-', ' '))
    
    # Technology tags
    tech_map = {
        'python': 'python',
        'docker': 'docker',
        'kubernetes': 'kubernetes',
        'react': 'react',
        'fastapi': 'fastapi',
        'git': 'git',
        'terraform': 'terraform',
        'ml': 'machine-learning',
        'ai': 'artificial-intelligence',
    }
    
    for key, tag in tech_map.items():
        if key in title_lower:
            tags.append(tag)
    
    # Activity tags
    activity_map = {
        'test': 'testing',
        'deploy': 'deployment',
        'monitor': 'monitoring',
        'refactor': 'refactoring',
        'security': 'security',
        'performance': 'performance',
        'setup': 'setup',
        'ci': 'ci-cd',
        'pipeline': 'automation',
    }
    
    for key, tag in activity_map.items():
        if key in title_lower:
            tags.append(tag)
    
    # Deduplicate and limit
    return list(dict.fromkeys(tags))[:7]


def infer_priority(title):
    """Infer priority from title."""
    title_lower = title.lower()
    
    if any(x in title_lower for x in ['security', 'incident', 'emergency', 'hotfix']):
        return 'CRITICAL'
    elif any(x in title_lower for x in ['cicd', 'pipeline', 'deployment', 'setup']):
        return 'HIGH'
    elif any(x in title_lower for x in ['monitoring', 'testing', 'quality']):
        return 'HIGH'
    else:
        return 'MEDIUM'


def infer_complexity(title):
    """Infer complexity from title."""
    title_lower = title.lower()
    
    if any(x in title_lower for x in ['kubernetes', 'terraform', 'distributed', 'architecture']):
        return 'Complex'
    elif any(x in title_lower for x in ['ml', 'ai', 'pipeline', 'infrastructure']):
        return 'Moderate'
    else:
        return 'Simple'


def infer_time(complexity):
    """Infer estimated time from complexity."""
    time_map = {
        'Simple': '15-30 minutes',
        'Moderate': '30-60 minutes',
        'Complex': '1-2 hours',
        'Expert': '2+ hours',
    }
    return time_map.get(complexity, '30 minutes')


def generate_purpose(title):
    """Generate purpose based on title."""
    title_lower = title.lower()
    
    # Generate What
    what = f"Systematic workflow for {title_lower}"
    
    # Generate Why
    if 'test' in title_lower:
        why = "Testing ensures code quality and catches bugs early"
    elif 'deploy' in title_lower:
        why = "Automated deployment reduces errors and speeds up releases"
    elif 'monitor' in title_lower:
        why = "Monitoring provides visibility into system health and performance"
    elif 'security' in title_lower:
        why = "Security practices protect systems and data from threats"
    else:
        why = "This workflow improves development efficiency and code quality"
    
    return what, why


def generate_when_to_use(title):
    """Generate when to use section."""
    items = [
        f"- Working on {title.lower()} tasks",
        "- Setting up new projects",
        "- Improving existing processes",
    ]
    return '\n'.join(items)


# === MAIN GENERATION ===

def generate_all_stubs():
    """Generate all workflow stubs."""
    print("="*80)
    print("WORKFLOW STUB GENERATOR")
    print("="*80)
    
    counters = {}
    total_generated = 0
    
    for source_cat, files in SOURCE_WORKFLOWS.items():
        target_cat = CATEGORY_MAP.get(source_cat, 'development')
        target_dir = os.path.join(TARGET_DIR, target_cat)
        
        # Initialize counter
        if target_cat not in counters:
            counters[target_cat] = 1
        
        print(f"\n{source_cat} -> {target_cat} ({len(files)} workflows)")
        
        for filename in files:
            # Generate metadata
            title = filename_to_title(filename)
            
            # Get category prefix
            prefix = target_cat.split('-')[0][:3]
            workflow_id = f"{prefix}-{counters[target_cat]:03d}"
            counters[target_cat] += 1
            
            priority = infer_priority(title)
            complexity = infer_complexity(title)
            time = infer_time(complexity)
            tags = extract_tags_from_title(title, target_cat)
            
            purpose_what, purpose_why = generate_purpose(title)
            when_to_use = generate_when_to_use(title)
            
            # Format tags
            tags_str = ' '.join(f'`{tag}`' for tag in tags)
            
            # Generate stub content
            stub_content = STUB_TEMPLATE.format(
                title=title,
                id=workflow_id,
                category=target_cat.replace('-', ' ').title(),
                priority=priority,
                complexity=complexity,
                time=time,
                date=datetime.now().strftime('%Y-%m-%d'),
                purpose_what=purpose_what,
                purpose_why=purpose_why,
                when_to_use=when_to_use,
                prerequisites="- [To be determined based on detailed analysis]",
                next_steps="- [To be determined based on detailed analysis]",
                alternatives="- [To be determined based on detailed analysis]",
                tags=tags_str,
            )
            
            # Write file
            output_path = os.path.join(target_dir, filename)
            
            print(f"  {workflow_id} - {title}")
            
            # Create stub file
            os.makedirs(target_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(stub_content)
            
            total_generated += 1
    
    print("\n" + "="*80)
    print(f"COMPLETE: Generated {total_generated} workflow stubs")
    print("="*80)
    
    # Print summary by category
    print("\nWorkflows by Category:")
    for cat, count in sorted(counters.items()):
        print(f"  {cat}: {count-1} workflows")


if __name__ == "__main__":
    generate_all_stubs()
    print("\n✅ Workflow stubs generated successfully!")
    print("Next step: Review and fill in detailed content for each workflow")
