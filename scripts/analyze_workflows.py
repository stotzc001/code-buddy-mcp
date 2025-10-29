"""
Workflow Analysis and Mapping Script

This script:
1. Scans all source workflow directories
2. Extracts existing metadata from workflows
3. Creates a mapping to new category structure
4. Generates stub files with core metadata
5. Maps relationships between workflows
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

# Source directories to scan
SOURCE_DIRS = [
    r"C:\Repos\GPT Instructions\Active\workflows",
    r"C:\Repos\skill-automation\all_skills\code_buddy_skills"
]

# Target directory
TARGET_DIR = r"C:\Repos\code_buddy_mcp\workflows"

# Category mapping from old to new structure
CATEGORY_MAPPING = {
    # Old source dirs -> New category
    "development": "development",
    "devops": "devops",
    "data-engineering": "data-engineering",
    "data_engineering": "data-engineering",
    "ml": "machine-learning",
    "ml_ai": "machine-learning",
    "frontend": "frontend-development",
    "git": "version-control",
    "quality": "quality-assurance",
    "testing": "testing",
    "security": "security",
    "setup": "development",  # Setup workflows go to development
    "session": "project-management",  # Session management
    "people": "development",  # People/team workflows
    "maintenance": "development",  # Maintenance workflows
    "emergency": "devops",  # Emergency workflows are ops
    "advanced": "architecture",  # Advanced patterns
}

# Workflow data structure
workflows = []


def extract_metadata_from_file(filepath: str) -> Dict:
    """Extract metadata from a workflow markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return {}
    
    metadata = {
        'filepath': filepath,
        'filename': os.path.basename(filepath),
        'title': '',
        'id': '',
        'category': '',
        'tags': [],
        'purpose': '',
        'priority': 'MEDIUM',
        'complexity': 'Moderate',
        'estimated_time': '30 minutes',
    }
    
    # Extract title (first # heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        metadata['title'] = title_match.group(1).strip()
    
    # Extract ID
    id_match = re.search(r'\*\*ID:\*\*\s*(.+)', content, re.IGNORECASE)
    if id_match:
        metadata['id'] = id_match.group(1).strip()
    
    # Extract Category
    cat_match = re.search(r'\*\*Category:\*\*\s*(.+)', content, re.IGNORECASE)
    if cat_match:
        metadata['category'] = cat_match.group(1).strip()
    
    # Extract Priority
    pri_match = re.search(r'\*\*Priority:\*\*\s*(.+)', content, re.IGNORECASE)
    if pri_match:
        metadata['priority'] = pri_match.group(1).strip()
    
    # Extract Complexity
    comp_match = re.search(r'\*\*Complexity:\*\*\s*(.+)', content, re.IGNORECASE)
    if comp_match:
        metadata['complexity'] = comp_match.group(1).strip()
    
    # Extract Estimated Time
    time_match = re.search(r'\*\*Estimated Time:\*\*\s*(.+)', content, re.IGNORECASE)
    if time_match:
        metadata['estimated_time'] = time_match.group(1).strip()
    
    # Extract Purpose (What/Why/When section)
    purpose_match = re.search(r'\*\*What:\*\*\s*(.+?)(?:\n\n|\*\*)', content, re.DOTALL)
    if purpose_match:
        metadata['purpose'] = purpose_match.group(1).strip()
    
    # Extract tags (at end of file or in tags section)
    tags_match = re.search(r'`([^`]+)`\s*`([^`]+)`', content)
    if tags_match:
        # Extract all tags in backticks
        all_tags = re.findall(r'`([^`]+)`', content[-500:])  # Last 500 chars
        metadata['tags'] = [tag.strip() for tag in all_tags if tag.strip()]
    
    return metadata


def extract_metadata_from_skill_zip(filename: str) -> Dict:
    """Extract metadata from skill zip filename."""
    # Remove .zip extension
    name = filename.replace('.zip', '')
    
    # Convert filename to title
    title = name.replace('-', ' ').title()
    
    # Generate ID based on category inference
    category = infer_category_from_name(name)
    
    metadata = {
        'filepath': filename,
        'filename': filename,
        'title': title,
        'id': '',  # Will be assigned later
        'category': category,
        'tags': extract_tags_from_name(name),
        'purpose': '',  # Will need to be filled
        'priority': 'MEDIUM',
        'complexity': 'Moderate',
        'estimated_time': '30 minutes',
    }
    
    return metadata


def infer_category_from_name(name: str) -> str:
    """Infer category from workflow name."""
    name_lower = name.lower()
    
    if any(x in name_lower for x in ['frontend', 'react', 'component', 'accessibility', 'responsive', 'e2e']):
        return 'frontend-development'
    elif any(x in name_lower for x in ['ml', 'model', 'feature-engineering', 'deep-learning', 'automl', 'mlops']):
        return 'machine-learning'
    elif any(x in name_lower for x in ['docker', 'kubernetes', 'cicd', 'pipeline', 'deployment', 'monitoring', 'infrastructure']):
        return 'devops'
    elif any(x in name_lower for x in ['data-lake', 'etl', 'pipeline', 'data-quality', 'dbt', 'airflow', 'kafka', 'spark']):
        return 'data-engineering'
    elif any(x in name_lower for x in ['git', 'merge', 'commit', 'branch']):
        return 'version-control'
    elif any(x in name_lower for x in ['test', 'coverage', 'mocking']):
        return 'testing'
    elif any(x in name_lower for x in ['quality', 'mypy', 'ruff', 'lint', 'code-review', 'graduation']):
        return 'quality-assurance'
    elif any(x in name_lower for x in ['secret', 'security', 'key-rotation', 'incident']):
        return 'security'
    elif any(x in name_lower for x in ['settings', 'config', 'pydantic', 'application']):
        return 'configuration-management'
    elif any(x in name_lower for x in ['architecture', 'design', 'pattern', 'caching', 'scalability', 'microservices', 'distributed']):
        return 'architecture'
    elif any(x in name_lower for x in ['spike', 'research', 'discovery']):
        return 'discovery'
    elif any(x in name_lower for x in ['progress', 'session', 'knowledge-transfer']):
        return 'project-management'
    else:
        return 'development'


def extract_tags_from_name(name: str) -> List[str]:
    """Extract relevant tags from workflow name."""
    tags = []
    name_lower = name.lower()
    
    # Technology tags
    tech_keywords = {
        'python', 'fastapi', 'react', 'docker', 'kubernetes', 'terraform',
        'postgres', 'redis', 'kafka', 'spark', 'airflow', 'dbt',
        'pytest', 'mypy', 'ruff', 'git', 'github', 'gitlab'
    }
    
    for tech in tech_keywords:
        if tech in name_lower:
            tags.append(tech)
    
    # Activity tags
    activity_keywords = {
        'setup', 'deployment', 'testing', 'monitoring', 'refactoring',
        'optimization', 'migration', 'integration', 'configuration'
    }
    
    for activity in activity_keywords:
        if activity in name_lower:
            tags.append(activity)
    
    return tags[:5]  # Limit to 5 tags


def scan_workflows():
    """Scan all source directories for workflows."""
    print("Scanning workflows...\n")
    
    # Scan Active workflows directory
    active_workflows_dir = SOURCE_DIRS[0]
    
    for subdir in os.listdir(active_workflows_dir):
        subdir_path = os.path.join(active_workflows_dir, subdir)
        
        if not os.path.isdir(subdir_path):
            continue
        
        if subdir in ['templates', 'advanced']:
            continue
        
        print(f"Scanning {subdir}...")
        
        for file in os.listdir(subdir_path):
            if file.endswith('.md') and not file.startswith('_'):
                filepath = os.path.join(subdir_path, file)
                metadata = extract_metadata_from_file(filepath)
                
                # Map to new category
                metadata['source_category'] = subdir
                metadata['target_category'] = CATEGORY_MAPPING.get(subdir, 'development')
                
                workflows.append(metadata)
    
    # Scan skill zips
    skills_dir = SOURCE_DIRS[1]
    if os.path.exists(skills_dir):
        print(f"\nScanning {skills_dir}...")
        
        for file in os.listdir(skills_dir):
            if file.endswith('.zip'):
                metadata = extract_metadata_from_skill_zip(file)
                metadata['source_category'] = 'skills'
                metadata['target_category'] = metadata['category']
                workflows.append(metadata)
    
    print(f"\nTotal workflows found: {len(workflows)}")


def assign_ids():
    """Assign sequential IDs to workflows by category."""
    # Group by target category
    by_category = {}
    for w in workflows:
        cat = w['target_category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(w)
    
    # Assign IDs
    category_counters = {}
    
    for cat, wfs in by_category.items():
        # Get category prefix
        prefix = cat.split('-')[0][:3] if '-' in cat else cat[:3]
        
        counter = 1
        for w in wfs:
            # Skip if already has ID
            if not w.get('id'):
                w['id'] = f"{prefix}-{counter:03d}"
                counter += 1
    
    print("\nIDs assigned by category:")
    for cat, wfs in by_category.items():
        print(f"  {cat}: {len(wfs)} workflows")


def generate_summary_report():
    """Generate a summary report of all workflows."""
    print("\n" + "="*80)
    print("WORKFLOW ANALYSIS SUMMARY")
    print("="*80)
    
    # Group by target category
    by_category = {}
    for w in workflows:
        cat = w['target_category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(w)
    
    # Print summary
    for cat in sorted(by_category.keys()):
        wfs = by_category[cat]
        print(f"\n{cat.upper().replace('-', ' ')} ({len(wfs)} workflows)")
        print("-" * 80)
        
        for w in sorted(wfs, key=lambda x: x.get('id', '')):
            id_str = w.get('id', 'TBD').ljust(10)
            title = w.get('title', w.get('filename', 'Unknown'))[:60]
            print(f"  {id_str} {title}")
    
    print("\n" + "="*80)
    print(f"TOTAL: {len(workflows)} workflows across {len(by_category)} categories")
    print("="*80)


def save_mapping_json():
    """Save workflow mapping to JSON file."""
    output_file = os.path.join(TARGET_DIR, 'workflow_mapping.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(workflows, f, indent=2)
    
    print(f"\nMapping saved to: {output_file}")


if __name__ == "__main__":
    print("="*80)
    print("WORKFLOW ANALYSIS AND MAPPING TOOL")
    print("="*80)
    
    scan_workflows()
    assign_ids()
    generate_summary_report()
    save_mapping_json()
    
    print("\nAnalysis complete!")
