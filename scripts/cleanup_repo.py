#!/usr/bin/env python3
"""
Cleanup Script - Organize Code Buddy MCP Repository
Moves temporary/development files to an archive folder
"""

import os
import shutil
from pathlib import Path

# Files and patterns to archive (temporary development files)
ARCHIVE_PATTERNS = [
    # Temporary analysis scripts
    "analyze_*.py",
    "check_*.py",
    "clear_*.py",
    "comprehensive_*.py",
    "count_*.py",
    "enhance_*.py",
    "final_*.py",
    "grade_*.py",
    "preflight_*.py",
    "test_*.py",
    
    # Temporary markdown files
    "COMMANDS.md",
    "COMPLETE_SOLUTION.md",
    "COMPLETION_REPORT*.md",
    "CURRENT_STATUS*.md",
    "DETAILED_WORKFLOW_GRADES.md",
    "DO_THIS*.md",
    "FILE_GUIDE.md",
    "FINAL_REIMPORT.md",
    "FIXES_APPLIED.md",
    "FIX_SKILLS_NOW.md",
    "IMPORT_GUIDE.md",
    "IMPORT_WORKFLOWS_GUIDE.md",
    "INSTALLATION_VERIFIED.md",
    "MISSING_WORKFLOWS.md",
    "MVP_SETUP.md",
    "NEXT_STEPS*.md",
    "PROGRESS.md",
    "PROJECT_STATUS.md",
    "QA_GRADING_TRACKER.md",
    "QUICK_REFERENCE.md",
    "QUICK_START_CHECKLIST.md",
    "REIMPORT*.md",
    "REQUIREMENTS_FIXED.md",
    "SESSION_*.md",
    "SETUP_PART_*.md",
    "START_HERE.md",
    "TESTING_*.md",
    "VERSION_CONTROL_CATEGORY_GRADES.md",
    "WORKFLOW_QUALITY_ASSESSMENT.md",
    "WORKFLOW_TRACKER.md",
    
    # PowerShell scripts
    "push_workflow_fixes.ps1",
]

# Files to KEEP (production files)
KEEP_FILES = [
    "README.md",
    "READY_TO_USE.md",
    "PROJECT_OVERVIEW.md",
    "SETUP_GUIDE.md",
    "SETUP_MASTER_GUIDE.md",
    "SETUP_QUICK_REFERENCE.md",
    "TROUBLESHOOTING.md",
    ".gitignore",
    ".env.example",
    "requirements.txt",
]

def cleanup_repo():
    """Move temporary files to archive folder."""
    repo_root = Path("C:/Repos/code_buddy_mcp")
    archive_dir = repo_root / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("CLEANING UP CODE BUDDY MCP REPOSITORY")
    print("=" * 80)
    
    moved_count = 0
    
    # Process each pattern
    for pattern in ARCHIVE_PATTERNS:
        matches = list(repo_root.glob(pattern))
        for file in matches:
            if file.name not in KEEP_FILES and file.is_file():
                try:
                    dest = archive_dir / file.name
                    shutil.move(str(file), str(dest))
                    print(f"✓ Moved: {file.name}")
                    moved_count += 1
                except Exception as e:
                    print(f"✗ Error moving {file.name}: {e}")
    
    print(f"\n{'=' * 80}")
    print(f"Moved {moved_count} files to archive/")
    print("=" * 80)
    
    # Create archive README
    archive_readme = archive_dir / "README.md"
    with open(archive_readme, "w") as f:
        f.write("""# Archive

This folder contains temporary development files that were used during the 
Code Buddy MCP development process. These files are kept for reference but
are not needed for production deployment.

## Contents
- Analysis scripts used during workflow parsing development
- Temporary status reports and session logs
- Quality assessment and grading documents
- Import/setup guides (superseded by main docs)

These files can be safely deleted if not needed for historical reference.
""")
    
    print("\nRepository cleaned! Ready for production deployment.")

if __name__ == "__main__":
    cleanup_repo()
