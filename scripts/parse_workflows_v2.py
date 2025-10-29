"""
Workflow Parser V2 - Extract Tasks and Skills
Parses workflow markdown files into granular components for token-efficient storage.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Any
import yaml


class Task:
    """Represents a single task/step in a workflow."""
    
    def __init__(
        self,
        step_number: int,
        name: str,
        title: str,
        description: str,
        content: str,
        prerequisites: List[str],
        commands: List[str],
        verification_checks: List[str],
        estimated_time_minutes: Optional[int] = None
    ):
        self.step_number = step_number
        self.name = name
        self.title = title
        self.description = description
        self.content = content
        self.prerequisites = prerequisites
        self.commands = commands
        self.verification_checks = verification_checks
        self.estimated_time_minutes = estimated_time_minutes


class Skill:
    """Represents a reusable pattern/technique extracted from workflows."""
    
    def __init__(
        self,
        name: str,
        title: str,
        description: str,
        content: str,
        category: str,
        tags: List[str],
        use_cases: List[str],
        example_code: Optional[str] = None,
        example_usage: Optional[str] = None
    ):
        self.name = name
        self.title = title
        self.description = description
        self.content = content
        self.category = category
        self.tags = tags
        self.use_cases = use_cases
        self.example_code = example_code
        self.example_usage = example_usage


class WorkflowV2:
    """Represents a parsed workflow with granular components."""
    
    def __init__(
        self,
        name: str,
        title: str,
        description: str,
        overview: str,
        category: str,
        subcategory: Optional[str],
        tags: List[str],
        technologies: List[str],
        complexity: str,
        estimated_time_minutes: int,
        use_cases: List[str],
        problem_statement: str,
        author: str,
        tasks: List[Task],
        skills: List[Skill],
        raw_content: str
    ):
        self.name = name
        self.title = title
        self.description = description
        self.overview = overview
        self.category = category
        self.subcategory = subcategory
        self.tags = tags
        self.technologies = technologies
        self.complexity = complexity
        self.estimated_time_minutes = estimated_time_minutes
        self.use_cases = use_cases
        self.problem_statement = problem_statement
        self.author = author
        self.tasks = tasks
        self.skills = skills
        self.raw_content = raw_content


class WorkflowParserV2:
    """Parses markdown workflow files into granular components."""
    
    def __init__(self):
        self.skill_patterns = [
            r"### Skill:",
            r"### Pattern:",
            r"### Example \d+:",
            r"### Using .+",
            r"### .+ Pattern",
        ]
    
    def parse_file(self, filepath: Path) -> WorkflowV2:
        """Parse a workflow markdown file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter = self._extract_frontmatter(content)
        body = self._extract_body(content)
        overview = self._generate_overview(frontmatter, body)
        tasks = self._extract_tasks(body)
        name = filepath.stem
        skills = self._extract_skills(body, frontmatter, name)  # Pass workflow name
        
        return WorkflowV2(
            name=name,
            title=frontmatter.get('title', ''),
            description=frontmatter.get('description', ''),
            overview=overview,
            category=frontmatter.get('category', ''),
            subcategory=frontmatter.get('subcategory'),
            tags=frontmatter.get('tags', []),
            technologies=frontmatter.get('technologies', []),
            complexity=frontmatter.get('complexity', 'intermediate'),
            estimated_time_minutes=frontmatter.get('estimated_time_minutes', 30),
            use_cases=frontmatter.get('use_cases', []),
            problem_statement=frontmatter.get('problem_statement', ''),
            author=frontmatter.get('author', 'Code Buddy Team'),
            tasks=tasks,
            skills=skills,
            raw_content=content
        )
    
    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter and/or inline metadata."""
        metadata = {}
        
        # First try YAML frontmatter
        yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            try:
                metadata = yaml.safe_load(yaml_match.group(1))
            except yaml.YAMLError:
                pass
        
        # Also extract inline metadata (format: **Key:** Value)
        inline_metadata = self._extract_inline_metadata(content)
        
        # Merge: inline metadata takes precedence if both exist
        metadata.update(inline_metadata)
        
        return metadata
    
    def _extract_inline_metadata(self, content: str) -> Dict[str, Any]:
        """Extract inline metadata from markdown (format: **Key:** Value)."""
        metadata = {}
        
        # Extract the header section (before ## Purpose or first ##)
        header_match = re.search(r'^#[^#].*?\n(.*?)(?=\n## |\Z)', content, re.DOTALL | re.MULTILINE)
        if not header_match:
            return metadata
        
        header_section = header_match.group(1)
        
        # Extract **Key:** Value patterns
        inline_patterns = {
            'category': r'\*\*Category:\*\*\s*(.+?)(?:\n|$)',
            'subcategory': r'\*\*Subcategory:\*\*\s*(.+?)(?:\n|$)',
            'priority': r'\*\*Priority:\*\*\s*(.+?)(?:\n|$)',
            'complexity': r'\*\*Complexity:\*\*\s*(.+?)(?:\n|$)',
            'estimated_time': r'\*\*Estimated Time:\*\*\s*(.+?)(?:\n|$)',
        }
        
        for key, pattern in inline_patterns.items():
            match = re.search(pattern, header_section, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                
                # Map to expected frontmatter keys and normalize values
                if key == 'category':
                    metadata['category'] = value
                elif key == 'subcategory':
                    metadata['subcategory'] = value
                elif key == 'complexity':
                    # Normalize complexity values
                    complexity_map = {
                        'simple': 'beginner',
                        'low': 'beginner',
                        'easy': 'beginner',
                        'moderate': 'intermediate',
                        'medium': 'intermediate',
                        'high': 'advanced',
                        'hard': 'advanced',
                        'complex': 'advanced',
                        'expert': 'expert'
                    }
                    normalized = complexity_map.get(value.lower(), value.lower())
                    metadata['complexity'] = normalized
                elif key == 'estimated_time':
                    # Extract minutes from strings like "30-60 minutes" or "45 minutes"
                    time_match = re.search(r'(\d+)', value)
                    if time_match:
                        metadata['estimated_time_minutes'] = int(time_match.group(1))
        
        return metadata
    
    def _extract_body(self, content: str) -> str:
        """Extract markdown body after frontmatter."""
        match = re.match(r'^---\n.*?\n---\n(.*)$', content, re.DOTALL)
        if match:
            return match.group(1)
        return content
    
    def _generate_overview(self, frontmatter: Dict, body: str) -> str:
        """Generate concise overview from Purpose section."""
        overview_parts = []
        
        if frontmatter.get('description'):
            overview_parts.append(frontmatter['description'])
        
        purpose_match = re.search(
            r'## Purpose\s*\n(.*?)(?=\n##|\Z)',
            body,
            re.DOTALL
        )
        if purpose_match:
            purpose_text = purpose_match.group(1).strip()
            what_match = re.search(r'\*\*What:\*\*(.*?)(?=\*\*Why:|\*\*When|\Z)', purpose_text, re.DOTALL)
            why_match = re.search(r'\*\*Why:\*\*(.*?)(?=\*\*When:|\Z)', purpose_text, re.DOTALL)
            
            if what_match:
                overview_parts.append("What: " + what_match.group(1).strip())
            if why_match:
                overview_parts.append("Why: " + why_match.group(1).strip())
        
        overview = "\n\n".join(overview_parts)
        
        if len(overview) > 2000:
            overview = overview[:2000] + "..."
        
        return overview
    
    def _extract_tasks(self, body: str) -> List[Task]:
        """Extract tasks from Step sections."""
        tasks = []
        
        # Find all "## Step N:" OR "### Step N:" sections
        # Some workflows use ## (h2) and others use ### (h3)
        step_pattern = r'##\#?\s+Step (\d+):\s*(.+?)\n(.*?)(?=\n##\#?\s+(?:Step \d+:|[A-Z])|\Z)'
        step_matches = re.finditer(step_pattern, body, re.DOTALL)
        
        for match in step_matches:
            step_num = int(match.group(1))
            step_title = match.group(2).strip()
            step_content = match.group(3).strip()
            
            # Extract description (usually first paragraph)
            lines = step_content.split('\n')
            description = lines[0] if lines else ""
            
            # Extract commands/code blocks
            commands = self._extract_code_blocks(step_content)
            
            # Extract verification checks (look for "Test" or "Verify" mentions)
            verification = []
            
            # Extract prerequisites from content
            prereqs = []
            
            # Estimate time
            estimated_time = self._estimate_task_time(step_content)
            
            # Generate task name from title
            task_name = re.sub(r'[^a-z0-9]+', '_', step_title.lower()).strip('_')
            
            task = Task(
                step_number=step_num,
                name=task_name,
                title=step_title,
                description=description,
                content=step_content,
                prerequisites=prereqs,
                commands=commands,
                verification_checks=verification,
                estimated_time_minutes=estimated_time
            )
            
            tasks.append(task)
        
        return tasks
    
    def _extract_skills(self, body: str, frontmatter: Dict, workflow_name: str) -> List[Skill]:
        """Extract reusable skills from Best Practices and Common Patterns sections."""
        skills = []
        
        # Extract from Best Practices section
        bp_match = re.search(
            r'## Best Practices\s*\n(.*?)(?=\n## Common Patterns|\n## Troubleshooting|\n## Next Steps|\n## References|\Z)',
            body,
            re.DOTALL
        )
        
        if bp_match:
            bp_content = bp_match.group(1).strip()
            # Extract ### subsections as skills
            skill_pattern = r'### (\d+\.\s*)?(.+?)\n(.*?)(?=\n###|\Z)'
            for match in re.finditer(skill_pattern, bp_content, re.DOTALL):
                skill_title = match.group(2).strip()
                skill_content = match.group(3).strip()
                
                code_blocks = self._extract_code_blocks(skill_content)
                skill_name = re.sub(r'[^a-z0-9]+', '_', skill_title.lower()).strip('_')
                
                skill = Skill(
                    name=f"{workflow_name}_bp_{skill_name}",  # Include workflow name to avoid collisions
                    title=skill_title,
                    description=skill_title,
                    content=skill_content,
                    category=frontmatter.get('category', 'General'),
                    tags=frontmatter.get('tags', []),
                    use_cases=[],
                    example_code="\n\n".join(code_blocks) if code_blocks else None
                )
                skills.append(skill)
        
        # Extract from Common Patterns section
        cp_match = re.search(
            r'## Common Patterns\s*\n(.*?)(?=\n## Troubleshooting|\n## Next Steps|\n## References|\Z)',
            body,
            re.DOTALL
        )
        
        if cp_match:
            cp_content = cp_match.group(1).strip()
            # Extract ### subsections as skills
            skill_pattern = r'### (.+?)\n(.*?)(?=\n###|\Z)'
            for match in re.finditer(skill_pattern, cp_content, re.DOTALL):
                skill_title = match.group(1).strip()
                skill_content = match.group(2).strip()
                
                code_blocks = self._extract_code_blocks(skill_content)
                skill_name = re.sub(r'[^a-z0-9]+', '_', skill_title.lower()).strip('_')
                
                skill = Skill(
                    name=f"{workflow_name}_pattern_{skill_name}",  # Include workflow name to avoid collisions
                    title=skill_title,
                    description=skill_title,
                    content=skill_content,
                    category=frontmatter.get('category', 'General'),
                    tags=frontmatter.get('tags', []),
                    use_cases=[],
                    example_code="\n\n".join(code_blocks) if code_blocks else None
                )
                skills.append(skill)
        
        return skills
    
    def _extract_code_blocks(self, content: str) -> List[str]:
        """Extract code blocks from markdown content."""
        code_pattern = r'```(?:\w+)?\n(.*?)```'
        matches = re.findall(code_pattern, content, re.DOTALL)
        return [match.strip() for match in matches]
    
    def _extract_verification(self, content: str) -> List[str]:
        """Extract verification checks from task content."""
        checks = []
        
        verify_match = re.search(
            r'\*\*Verification:\*\*\s*\n(.*?)(?=\n\*\*If This Fails:|\Z)',
            content,
            re.DOTALL
        )
        
        if verify_match:
            verify_text = verify_match.group(1)
            check_items = re.findall(r'- \[ \] (.+)', verify_text)
            checks.extend(check_items)
        
        return checks
    
    def _extract_prerequisites(self, content: str) -> List[str]:
        """Extract prerequisites from task content."""
        prereqs = []
        
        prereq_patterns = [
            r'Prerequisites?:\s*\n(.*?)(?=\n\*\*|\Z)',
            r'Required:\s*\n(.*?)(?=\n\*\*|\Z)',
        ]
        
        for pattern in prereq_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                prereq_text = match.group(1)
                items = re.findall(r'[-*] (.+)', prereq_text)
                prereqs.extend(items)
        
        return prereqs
    
    def _estimate_task_time(self, content: str) -> int:
        """Estimate task time from content."""
        time_pattern = r'(\d+)[\s-]*(min|minute)s?'
        match = re.search(time_pattern, content, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        word_count = len(content.split())
        if word_count < 200:
            return 5
        elif word_count < 500:
            return 10
        elif word_count < 1000:
            return 15
        else:
            return 20
