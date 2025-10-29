"""Test the updated parser on a workflow with inline metadata."""
from pathlib import Path
from parse_workflows_v2 import WorkflowParserV2

# Test on a file with inline metadata
parser = WorkflowParserV2()
workflow_path = Path("C:/Repos/code_buddy_mcp/workflows/architecture/api_design_best_practices.md")

print(f"Testing parser on: {workflow_path.name}")
print("=" * 80)

workflow = parser.parse_file(workflow_path)

print(f"✓ Name: {workflow.name}")
print(f"✓ Title: {workflow.title}")
print(f"✓ Category: {workflow.category}")
print(f"✓ Complexity: {workflow.complexity}")
print(f"✓ Estimated Time: {workflow.estimated_time_minutes} minutes")
print(f"✓ Tasks: {len(workflow.tasks)}")
print(f"✓ Skills: {len(workflow.skills)}")

if workflow.category:
    print("\n🎉 SUCCESS! Category extracted from inline metadata!")
else:
    print("\n❌ FAILED! Category is still empty")

print("\n" + "=" * 80)
