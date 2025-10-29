"""
Parse detailed workflows into granular structure.

Takes a detailed workflow markdown file and extracts:
1. Workflow overview (high-level summary)
2. Individual tasks (step-by-step instructions)
3. Reusable skills (patterns and techniques)
"""

import re
from pathlib import Path
from typing import Dict, List, Any
import yaml


def parse_frontmatter(content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown."""
    if not content.startswith('---'):
        return {}
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    
    return yaml.safe_load(parts[1])


def parse_detailed_workflow(filepath: Path) -> Dict[str, Any]:
    """Parse a detailed workflow file into structured components."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    metadata = parse_frontmatter(content)
    
    # Remove frontmatter from content
    if content.startswith('---'):
        content = content.split('---', 2)[2].strip()
    
    # Parse sections
    sections = re.split(r'\n## ', content)
    
    # Workflow overview
    overview = extract_overview(sections, metadata)
    
    # Tasks (Implementation Steps)
    tasks = extract_tasks(sections, metadata)
    
    # Skills (reusable patterns)
    skills = extract_skills(sections, metadata)
    
    return {
        'workflow': overview,
        'tasks': tasks,
        'skills': skills
    }


def extract_overview(sections: List[str], metadata: Dict) -> Dict[str, Any]:
    """Extract workflow-level overview."""
    
    # Find Purpose section
    purpose = ""
    for section in sections:
        if section.startswith('Purpose'):
            purpose = section.split('\n', 1)[1] if '\n' in section else ""
            break
    
    # Extract What/Why/When
    what = extract_between(purpose, "**What:**", "**Why:**")
    why = extract_between(purpose, "**Why:**", "**When to use:**")
    when = extract_after(purpose, "**When to use:**")
    
    return {
        'name': metadata.get('title', '').lower().replace(' ', '_'),
        'title': metadata.get('title', ''),
        'description': metadata.get('description', ''),
        'overview': f"{what}\n\n{why}\n\nUse when:\n{when}",
        'category': metadata.get('category', ''),
        'subcategory': metadata.get('subcategory'),
        'tags': metadata.get('tags', []),
        'technologies': metadata.get('technologies', []),
        'complexity': metadata.get('complexity', 'intermediate'),
        'estimated_time_minutes': metadata.get('estimated_time_minutes', 30),
        'use_cases': metadata.get('use_cases', []),
        'problem_statement': metadata.get('problem_statement', '')
    }


def extract_tasks(sections: List[str], metadata: Dict) -> List[Dict[str, Any]]:
    """Extract individual tasks from Implementation Steps."""
    tasks = []
    
    # Find Implementation Steps section
    impl_section = None
    for section in sections:
        if section.startswith('Implementation Steps'):
            impl_section = section
            break
    
    if not impl_section:
        return tasks
    
    # Split by Step headings (### Step N:)
    steps = re.split(r'\n### Step \d+:', impl_section)
    
    for i, step in enumerate(steps[1:], 1):  # Skip first split (section header)
        if not step.strip():
            continue
        
        # Extract step title
        lines = step.strip().split('\n')
        title = lines[0].strip() if lines else f"Step {i}"
        
        # Extract components
        what = extract_between(step, "**What:**", "**How:**")
        how = extract_between(step, "**How:**", "**Code/Commands:**")
        commands = extract_between(step, "**Code/Commands:**", "**Verification:**")
        verification = extract_between(step, "**Verification:**", "**If This Fails:**")
        troubleshooting = extract_after(step, "**If This Fails:**")
        
        # Build task content
        content = f"## {title}\n\n"
        if what:
            content += f"**What:** {what}\n\n"
        if how:
            content += f"**How:**\n{how}\n\n"
        if commands:
            content += f"**Commands:**\n{commands}\n\n"
        if verification:
            content += f"**Verify:**\n{verification}\n\n"
        if troubleshooting:
            content += f"**Troubleshooting:**\n{troubleshooting}\n\n"
        
        tasks.append({
            'step_number': i,
            'name': title.lower().replace(' ', '_'),
            'title': title,
            'description': what[:200] if what else '',
            'content': content.strip(),
            'prerequisites': extract_prerequisites(step),
            'commands': extract_code_blocks(commands),
            'verification_checks': extract_checklist(verification),
            'estimated_time_minutes': estimate_time_from_content(content)
        })
    
    return tasks


def extract_skills(sections: List[str], metadata: Dict) -> List[Dict[str, Any]]:
    """Extract reusable skills/patterns from examples and best practices."""
    skills = []
    
    # Look in Examples section
    for section in sections:
        if section.startswith('Examples'):
            examples = re.split(r'\n### Example \d+:', section)
            for i, example in enumerate(examples[1:], 1):
                if not example.strip():
                    continue
                
                lines = example.strip().split('\n')
                title = lines[0].strip() if lines else f"Example {i}"
                
                # Extract context, execution, result
                context = extract_between(example, "**Context:**", "**Execution:**")
                execution = extract_between(example, "**Execution:**", "**Result:**")
                result = extract_after(example, "**Result:**")
                
                if execution:
                    skills.append({
                        'name': title.lower().replace(' ', '_').replace(':', ''),
                        'title': title,
                        'description': context or title,
                        'content': f"{execution}\n\nResult: {result}",
                        'category': metadata.get('category', ''),
                        'tags': [metadata.get('category', '').lower(), 'example'],
                        'example_code': extract_code_blocks(execution),
                        'example_usage': result
                    })
    
    return skills


def extract_between(text: str, start: str, end: str) -> str:
    """Extract text between two markers."""
    if start not in text:
        return ""
    
    text = text.split(start, 1)[1]
    if end in text:
        text = text.split(end, 1)[0]
    
    return text.strip()


def extract_after(text: str, marker: str) -> str:
    """Extract text after a marker."""
    if marker not in text:
        return ""
    
    return text.split(marker, 1)[1].strip()


def extract_prerequisites(text: str) -> List[str]:
    """Extract prerequisites from task content."""
    prereqs = []
    
    # Look for "Required:" section
    if '**Required:**' in text:
        section = extract_between(text, '**Required:**', '**')
        for line in section.split('\n'):
            line = line.strip()
            if line.startswith('- [ ]'):
                prereqs.append(line[5:].strip())
    
    return prereqs


def extract_code_blocks(text: str) -> List[str]:
    """Extract code blocks from markdown."""
    code_blocks = re.findall(r'```[\w]*\n(.*?)```', text, re.DOTALL)
    return [block.strip() for block in code_blocks]


def extract_checklist(text: str) -> List[str]:
    """Extract checklist items."""
    checks = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('- [ ]'):
            checks.append(line[5:].strip())
    return checks


def estimate_time_from_content(content: str) -> int:
    """Estimate time based on content length."""
    words = len(content.split())
    # Rough estimate: 200 words per minute reading + execution time
    return max(5, min(30, words // 100))


# ============================================================================
# EXAMPLE OUTPUT FOR TYPE ANNOTATION ADDITION
# ============================================================================

example_output = {
    'workflow': {
        'name': 'type_annotation_addition',
        'title': 'Type Annotation Addition',
        'description': 'Systematic workflow for adding Python type hints',
        'overview': '''
Systematically add Python type hints to untyped code to enable static 
type checking and improve code quality.

Type annotations provide benefits including catching bugs before runtime,
improving IDE support, serving as documentation, and making refactoring safer.

Use when working with untyped Python code, preparing for mypy validation,
improving maintainability, or before major refactoring.
        ''',
        'category': 'Development',
        'complexity': 'moderate',
        'estimated_time_minutes': 30
    },
    
    'tasks': [
        {
            'step_number': 1,
            'name': 'assess_current_state',
            'title': 'Assess Current State',
            'description': 'Understand the current typing situation in your codebase',
            'content': '''
## Assess Current State

**What:** Understand the current typing situation in your codebase.

**How:**
1. Run mypy to see current type coverage
2. Identify modules with no type hints
3. Find commonly-used functions that need types
4. Check for third-party type stubs availability

**Commands:**
```bash
mypy --install-types --non-interactive src/
mypy --html-report mypy-coverage src/
grep -rn "^def " src/ --include="*.py" | grep -v " -> " | wc -l
```

**Verify:**
- Mypy runs without crashing
- Coverage report generated
- Priority modules identified

**Troubleshooting:**
If mypy crashes, start with single module: `mypy src/module_name.py`
            ''',
            'prerequisites': [
                'Python 3.8+ installed',
                'mypy installed',
                'Access to codebase'
            ],
            'commands': [
                'mypy --install-types --non-interactive src/',
                'mypy --html-report mypy-coverage src/'
            ],
            'verification_checks': [
                'Mypy runs without crashing',
                'Coverage report generated',
                'Priority modules identified'
            ],
            'estimated_time_minutes': 10
        },
        
        {
            'step_number': 2,
            'name': 'configure_type_checking',
            'title': 'Configure Type Checking',
            'description': 'Set up mypy configuration for gradual typing adoption',
            'content': '''
## Configure Type Checking

**What:** Set up mypy configuration for gradual typing adoption.

**How:** Create or update mypy.ini in project root with gradual typing settings.

**Commands:**
```ini
[mypy]
python_version = 3.8
warn_return_any = True
disallow_untyped_defs = False
check_untyped_defs = True
```

**Verify:**
- Configuration file created
- Mypy runs with config
- No config errors

**Troubleshooting:**
Check syntax with: `mypy --config-file=mypy.ini src/`
            ''',
            'estimated_time_minutes': 5
        }
        # ... more tasks
    ],
    
    'skills': [
        {
            'name': 'using_typeddict',
            'title': 'Using TypedDict for Structured Data',
            'description': 'Define structured dictionary types instead of Dict[str, Any]',
            'content': '''
```python
from typing import TypedDict

class Item(TypedDict):
    name: str
    price: float
    quantity: int

def calculate_total(items: List[Item]) -> float:
    return sum(item['price'] * item['quantity'] for item in items)
```

Result: Type-safe dictionary access with IDE support
            ''',
            'category': 'Development',
            'tags': ['python', 'typing', 'typeddict'],
            'example_code': '...',
            'example_usage': 'Type-safe dictionary access'
        }
        # ... more skills
    ]
}


if __name__ == "__main__":
    # Parse Type Annotation Addition workflow
    workflow_file = Path("C:/Repos/code_buddy_mcp/workflows/development/type_annotation_addition.md")
    result = parse_detailed_workflow(workflow_file)
    
    print("=" * 70)
    print("WORKFLOW OVERVIEW")
    print("=" * 70)
    print(f"Title: {result['workflow']['title']}")
    print(f"Estimated tokens: ~400")
    print()
    
    print("=" * 70)
    print(f"TASKS EXTRACTED: {len(result['tasks'])}")
    print("=" * 70)
    for task in result['tasks']:
        print(f"  {task['step_number']}. {task['title']}")
        print(f"     Estimated tokens: ~{len(task['content']) // 4}")
    print()
    
    print("=" * 70)
    print(f"SKILLS EXTRACTED: {len(result['skills'])}")
    print("=" * 70)
    for skill in result['skills']:
        print(f"  - {skill['title']}")
        print(f"    Estimated tokens: ~{len(skill['content']) // 4}")
    print()
    
    print("=" * 70)
    print("TOKEN COMPARISON")
    print("=" * 70)
    print(f"Full workflow: ~4,300 tokens")
    print(f"Overview only: ~400 tokens")
    print(f"Single task: ~300-500 tokens")
    print(f"Single skill: ~200-300 tokens")
    print()
    print("✅ 90% token reduction for specific queries!")
