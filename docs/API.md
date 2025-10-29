# Code Buddy API Documentation

Complete reference for all MCP tools available in Code Buddy.

## Overview

Code Buddy provides 6 MCP tools for intelligent workflow discovery and management:

1. **search_workflows** - Multi-stage intelligent search
2. **get_workflow** - Retrieve complete workflow content
3. **list_categories** - Browse workflow taxonomy
4. **get_prerequisites** - View prerequisite chains
5. **track_usage** - Log usage for analytics
6. **suggest_next** - Get personalized recommendations (coming soon)

---

## 1. search_workflows

Find relevant workflows using three-stage intelligent filtering.

### Signature

```python
def search_workflows(
    query: str,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    technologies: Optional[List[str]] = None,
    complexity: Optional[str] = None,
    max_time_minutes: Optional[int] = None,
    limit: int = 5
) -> str
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Natural language search query |
| `category` | string | No | Filter by category (e.g., "Development", "Data Engineering") |
| `tags` | list[string] | No | Filter by tags (any match) |
| `technologies` | list[string] | No | Filter by technologies (e.g., ["Python", "FastAPI"]) |
| `complexity` | string | No | Filter by complexity: "beginner", "intermediate", "advanced", "expert" |
| `max_time_minutes` | integer | No | Maximum estimated time in minutes |
| `limit` | integer | No | Maximum results (default: 5, max: 20) |

### Returns

Formatted text with workflow summaries including:
- Title and ID
- Category and subcategory
- Complexity level
- Estimated time
- Similarity score
- Usage statistics
- Description
- Tags and technologies
- Use cases

### Examples

#### Basic Search

```
Claude: search_workflows("create a REST API endpoint")
```

**Returns:**
```
Found 3 relevant workflow(s):

## 1. FastAPI Endpoint Creation Workflow
**ID:** 42
**Category:** Development > Backend
**Complexity:** intermediate
**Estimated Time:** 30 minutes
**Similarity Score:** 0.891

Complete guide for creating REST API endpoints with FastAPI...

**Tags:** api, rest, fastapi, backend
**Technologies:** Python, FastAPI, Pydantic
**Use Cases:** Building APIs, Creating endpoints, REST services

*Use get_workflow(42) to see the complete workflow*
---
```

#### Filtered Search

```
Claude: search_workflows(
    query="database migration",
    category="Data Engineering",
    technologies=["PostgreSQL"],
    complexity="intermediate",
    max_time_minutes=60
)
```

#### Technology-Specific Search

```
Claude: search_workflows(
    query="testing strategy",
    technologies=["Python", "pytest"],
    limit=3
)
```

### Search Algorithm

**Stage 1: Metadata Filtering**
- Filters workflows by category, tags, technologies, complexity, time
- Narrows search space for efficient semantic search

**Stage 2: Semantic Search**
- Generates embedding for query
- Finds conceptually similar workflows using pgvector
- Ranks by cosine similarity

**Stage 3: Relationship Ranking**
- Boosts workflows with high usage counts
- Considers helpfulness ratings
- Factors in prerequisite relationships

### Performance

- **Average response time**: 50-100ms
- **Scales to**: 1000+ workflows
- **Token efficiency**: 6-10KB per search

---

## 2. get_workflow

Retrieve the complete content of a specific workflow.

### Signature

```python
def get_workflow(workflow_id: int) -> str
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | integer | Yes | Workflow ID from search results |

### Returns

Complete workflow content with:
- Full title and name
- Problem statement
- Detailed description
- All metadata (category, tags, technologies, complexity, time)
- Prerequisites with links
- Complete workflow content
- Version and author information

### Example

```
Claude: get_workflow(42)
```

**Returns:**
```markdown
# FastAPI Endpoint Creation Workflow

**ID:** 42 | **Name:** fastapi-endpoint-workflow
**Category:** Development > Backend

## Problem Statement
Creating REST API endpoints requires following best practices for validation,
error handling, documentation, and testing.

## Description
Comprehensive guide for creating production-ready FastAPI endpoints...

## Metadata
- **Complexity:** intermediate
- **Estimated Time:** 30 minutes
- **Tags:** api, rest, fastapi, backend
- **Technologies:** Python, FastAPI, Pydantic
- **Version:** 3
- **Author:** Claude Team

## Prerequisites
Complete these workflows first:
- [Python Environment Setup] (ID: 12)
- [FastAPI Basics] (ID: 38)

## Workflow

[Complete workflow content here...]
```

---

## 3. list_categories

Browse all available workflow categories.

### Signature

```python
def list_categories() -> str
```

### Parameters

None

### Returns

Formatted list of categories with:
- Category name with icon
- Description
- Workflow count per category

### Example

```
Claude: list_categories()
```

**Returns:**
```
# Workflow Categories

💻 **Development** (45 workflows)
   Software development workflows including coding, testing, and debugging

📊 **Data Engineering** (28 workflows)
   Data pipelines, ETL processes, and data transformation workflows

🚀 **DevOps** (22 workflows)
   CI/CD, infrastructure, and deployment automation workflows

🏗️ **Architecture** (15 workflows)
   System design patterns and architectural decision-making

📋 **Project Management** (12 workflows)
   Planning, execution, and team coordination workflows

🔍 **Discovery** (8 workflows)
   Research, exploration, and learning workflows

*Use search_workflows(category='Category Name') to browse workflows*
```

---

## 4. get_prerequisites

Get the complete prerequisite chain for a workflow.

### Signature

```python
def get_prerequisites(workflow_id: int) -> str
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | integer | Yes | Workflow ID |

### Returns

Hierarchical list of prerequisites organized by dependency depth.

### Example

```
Claude: get_prerequisites(42)
```

**Returns:**
```
# Prerequisites for Workflow 42

Complete these workflows in order:

**Level 1:**
- [Python Environment Setup] (ID: 12)
  Set up a Python development environment with virtual environments

- [Version Control Basics] (ID: 8)
  Learn Git fundamentals for version control

**Level 2:**
- [FastAPI Basics] (ID: 38)
  Introduction to FastAPI framework and basic concepts

**Level 3:**
- [Pydantic Models] (ID: 40)
  Learn data validation with Pydantic
```

### Use Cases

- **Learning paths**: Determine what to learn first
- **Planning**: Estimate total time for a learning path
- **Context**: Understand workflow dependencies
- **Troubleshooting**: Identify missing prerequisites

---

## 5. track_usage

Track workflow usage for analytics and improved ranking.

### Signature

```python
def track_usage(
    workflow_id: int,
    was_helpful: Optional[bool] = None,
    feedback: Optional[str] = None
) -> str
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | integer | Yes | Workflow ID that was used |
| `was_helpful` | boolean | No | Whether the workflow was helpful |
| `feedback` | string | No | Optional feedback text |

### Returns

Confirmation message

### Examples

#### Basic Usage Tracking

```
Claude: track_usage(42)
```

**Returns:**
```
Usage tracked for workflow 42. Thank you for the feedback!
```

#### With Helpfulness Rating

```
Claude: track_usage(42, was_helpful=True)
```

#### With Detailed Feedback

```
Claude: track_usage(
    42,
    was_helpful=True,
    feedback="Excellent workflow! Very clear steps and examples."
)
```

### Impact on Search

Usage tracking improves future search results:
- **Popular workflows**: Boosted in search rankings
- **Helpful workflows**: Higher priority in results
- **Usage patterns**: Inform relationship suggestions
- **Continuous improvement**: Identify gaps in content

---

## Common Patterns

### Pattern 1: Exploratory Search

```
1. list_categories() - See what's available
2. search_workflows(category="Development") - Browse a category
3. get_workflow(42) - Review specific workflow
4. track_usage(42, was_helpful=True) - Provide feedback
```

### Pattern 2: Specific Need

```
1. search_workflows("create API endpoint", technologies=["Python"]) - Find relevant
2. get_prerequisites(42) - Check requirements
3. get_workflow(42) - Get complete content
4. track_usage(42) - Track usage
```

### Pattern 3: Learning Path

```
1. search_workflows("microservices architecture") - Find starting point
2. get_prerequisites(85) - See what to learn first
3. get_workflow(12) - Start with first prerequisite
4. [Complete workflow]
5. track_usage(12, was_helpful=True) - Mark as completed
6. get_workflow(38) - Move to next prerequisite
```

---

## Error Handling

### Common Errors

**Workflow Not Found**
```
Workflow with ID 999 not found.
```

**No Results**
```
No workflows found matching your criteria. Try broadening your search.
```

**Invalid Parameters**
```
Error: complexity must be one of: beginner, intermediate, advanced, expert
```

### Best Practices

1. **Start broad**: Don't over-filter initially
2. **Use semantic search**: Trust natural language queries
3. **Provide feedback**: Use track_usage to improve results
4. **Check prerequisites**: Review dependencies before starting

---

## Performance Metrics

| Operation | Avg Time | Token Usage |
|-----------|----------|-------------|
| search_workflows | 50-100ms | 2-4KB |
| get_workflow | 10-20ms | 4-8KB |
| list_categories | <10ms | 1KB |
| get_prerequisites | 20-30ms | 1-2KB |
| track_usage | <10ms | 0.5KB |

**Total**: 6-10KB per typical interaction (vs 236KB loading all workflows)

---

## Future Tools (Roadmap)

### suggest_next
Get personalized workflow recommendations based on usage history.

```python
def suggest_next(
    current_workflow_id: Optional[int] = None,
    limit: int = 5
) -> str
```

### create_workflow
Add new workflows programmatically.

```python
def create_workflow(
    name: str,
    title: str,
    description: str,
    content: str,
    category: str,
    **metadata
) -> int
```

### update_workflow
Modify existing workflows.

```python
def update_workflow(
    workflow_id: int,
    **updates
) -> bool
```

---

## Support

For issues or questions:
1. Check logs in `python src/server.py` output
2. Review [Quick Start Guide](QUICKSTART.md)
3. See [Deployment Guide](DEPLOYMENT.md) for Railway issues
4. File bug reports with detailed error messages

---

**Happy workflow hunting!** 🔍
