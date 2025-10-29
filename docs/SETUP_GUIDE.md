# 🚀 Code Buddy MCP - Final Setup Steps

## Current Status ✅
- ✅ All code complete and ready
- ✅ Railway PostgreSQL database deployed
- ✅ Configuration set to use Cohere embeddings
- ✅ Requirements updated with Cohere SDK

## What You Need to Do Next (15 minutes)

### Step 1: Install Dependencies (2 min)

Open a terminal in `C:\Repos\code_buddy_mcp` and run:

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- FastMCP (MCP server framework)
- PostgreSQL drivers (psycopg2, SQLAlchemy, pgvector)
- Cohere SDK (for embeddings)
- Utilities (click, rich, python-dotenv)

### Step 2: Verify Database Connection (1 min)

Test the connection to your Railway database:

```bash
python test_db.py
```

Expected output:
```
🔍 Testing database connection...
✅ Connection successful!
📋 Existing tables:
  (No tables found - database needs initialization)
🔍 pgvector extension: ✅ Installed
✅ All checks passed!
```

### Step 3: Initialize Database Schema (2 min)

Create all tables, indexes, and functions:

```bash
python scripts/setup_database.py
```

This will:
- ✅ Enable pgvector extension
- ✅ Create workflows table (with vector support)
- ✅ Create categories table
- ✅ Create workflow_relationships table
- ✅ Create workflow_usage table (analytics)
- ✅ Create indexes for performance
- ✅ Seed initial categories
- ✅ Create materialized views

Expected output:
```
🚀 Code Buddy - Database Setup
==================================================
📡 Connecting to database...
🔍 Testing connection...
✅ Connection successful
🔍 Checking pgvector extension...
✅ pgvector extension found
📄 Executing schema from src/database/schema.sql...
✅ Schema executed successfully
🔍 Verifying tables...
📋 Found tables:
  ✅ workflows
  ✅ workflow_relationships
  ✅ workflow_usage
  ✅ categories
==================================================
🎉 Database setup complete!
```

**Optional**: If you see "tables already exist" errors, run with `--reset` to start fresh:
```bash
python scripts/setup_database.py --reset
```

### Step 4: Prepare Your Workflows (5 min)

You have 118 workflows to import. Organize them in the `workflows/` directory:

```
workflows/
├── development/           # Backend, frontend, API workflows
├── data-engineering/      # ETL, pipelines, data quality
├── devops/               # CI/CD, deployment, infrastructure
├── architecture/         # System design, patterns
├── project-management/   # Agile, planning, coordination
└── discovery/            # Research, POCs, spikes
```

Each workflow should be a `.md` file with YAML frontmatter:

```markdown
---
title: Your Workflow Title
description: Brief description of what this workflow does
category: Development
subcategory: Backend
tags: [api, rest, python]
technologies: [Python, FastAPI, PostgreSQL]
complexity: intermediate
estimated_time_minutes: 45
use_cases:
  - Creating REST APIs
  - Building microservices
problem_statement: How to create production-ready API endpoints
---

# Workflow Content Here

Your actual workflow content in markdown...
```

### Step 5: Import Workflows (2 min)

Import all your workflows with automatic embedding generation:

```bash
python scripts/import_workflows.py --directory ./workflows
```

This will:
- 📁 Scan all `.md` files in subdirectories
- 📝 Parse YAML frontmatter
- 🧠 Generate embeddings using Cohere
- 💾 Store in PostgreSQL with vector support
- 🔄 Skip duplicates (based on content hash)
- ✅ Show progress for each file

Expected output:
```
🚀 Workflow Import Tool
========================================
📁 Scanning ./workflows for .md files...
✅ Found 118 workflow files

🔄 Processing workflows...
[1/118] ✅ fastapi-endpoint-workflow.md
[2/118] ✅ database-migration-workflow.md
[3/118] ✅ cicd-pipeline-setup.md
...
[118/118] ✅ api-versioning-strategy.md

📊 Import Summary:
✅ Successfully imported: 118
⏭️  Skipped (unchanged): 0
❌ Failed: 0

🎉 All workflows imported!
Next: python src/server.py
```

**Time estimate**: ~30 seconds for 118 workflows (Cohere is fast!)

### Step 6: Start MCP Server (1 min)

Launch the MCP server:

```bash
python src/server.py
```

Expected output:
```
🚀 Starting Code Buddy MCP Server
========================================
📡 Connecting to database...
✅ Database connection successful
🔍 Found 118 active workflows
🧠 Initialized Cohere embeddings (embed-english-v3.0)
✅ Server ready!

Available tools:
  - search_workflows
  - get_workflow
  - list_categories
  - get_prerequisites
  - track_usage

Listening for MCP connections...
```

**Keep this terminal window open!** The server needs to stay running.

### Step 7: Configure Claude Desktop (2 min)

#### Windows
Edit: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "code-buddy": {
      "command": "python",
      "args": ["C:\\Repos\\code_buddy_mcp\\src\\server.py"],
      "env": {
        "DATABASE_URL": "postgresql://postgres:NCZNJ9yWWcpGTLKm-vvpNeuA3J-vvbuH@shortline.proxy.rlwy.net:38056/railway",
        "COHERE_API_KEY": "JSbTlybyl89CpMGaAlcLKVtARcBBYZZqLBASC1jQ",
        "EMBEDDING_PROVIDER": "cohere",
        "EMBEDDING_MODEL": "embed-english-v3.0",
        "EMBEDDING_DIMENSIONS": "1024"
      }
    }
  }
}
```

**Important**: 
- Replace backslashes with double backslashes in path: `\\`
- Use your actual DATABASE_URL and COHERE_API_KEY from `.env`

#### Mac
Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "code-buddy": {
      "command": "python",
      "args": ["/path/to/code_buddy_mcp/src/server.py"],
      "env": {
        "DATABASE_URL": "your-database-url",
        "COHERE_API_KEY": "your-cohere-key",
        "EMBEDDING_PROVIDER": "cohere",
        "EMBEDDING_MODEL": "embed-english-v3.0",
        "EMBEDDING_DIMENSIONS": "1024"
      }
    }
  }
}
```

### Step 8: Restart Claude Desktop (1 min)

1. Quit Claude Desktop completely
2. Relaunch Claude Desktop
3. Look for "🔧" icon in the text input area (shows MCP tools available)

### Step 9: Test It! (2 min)

Try these queries in Claude:

**Test 1: Simple Search**
```
Search for workflows about creating REST API endpoints
```

Expected: Claude will use the `search_workflows` tool and return relevant FastAPI workflows

**Test 2: Filtered Search**
```
Find Python workflows for data pipelines that take less than 30 minutes
```

Expected: Filtered results matching your criteria

**Test 3: Browse Categories**
```
What workflow categories are available?
```

Expected: List of categories (Development, Data Engineering, etc.)

**Test 4: Prerequisites**
```
Show me the prerequisite chain for microservices architecture workflow
```

Expected: Dependency tree of workflows to complete first

## 🎉 Success Indicators

You'll know it's working when:
- ✅ MCP server starts without errors
- ✅ Claude shows "code-buddy" in available tools
- ✅ Searches return relevant workflows
- ✅ Token usage is ~6-10KB instead of 236KB
- ✅ Results include similarity scores
- ✅ Can see prerequisite relationships

## 📊 Performance Expectations

| Metric | Expected Value |
|--------|---------------|
| Import Speed | ~0.5s per workflow |
| Search Response | <100ms |
| Token Usage | 6-10KB per query |
| Accuracy | 95%+ relevance |

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### "Database connection failed"
- Verify DATABASE_URL in `.env` matches Railway
- Check Railway database is running
- Test with: `python test_db.py`

### "pgvector not installed"
Railway includes pgvector by default. If needed:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### "No workflows found" after import
- Check files are in `.md` format
- Verify YAML frontmatter format
- Run import with verbose flag: `--verbose`

### MCP server not showing in Claude
- Verify claude_desktop_config.json syntax (JSON must be valid)
- Check file path uses double backslashes on Windows
- Restart Claude Desktop completely
- Check server is running: `python src/server.py` should show "Listening..."

## 📈 Next: Add Your 118 Workflows!

Once basic setup works with the 2 example workflows:

1. **Organize Your Files**
   - Move all 118 workflow files to appropriate subdirectories
   - Ensure each has proper frontmatter

2. **Bulk Import**
   ```bash
   python scripts/import_workflows.py --directory ./workflows
   ```

3. **Verify Count**
   ```bash
   python -c "
   from src.database.connection import DatabaseConnection
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   db = DatabaseConnection(os.getenv('DATABASE_URL'))
   with db.get_session() as session:
       from sqlalchemy import text
       result = session.execute(text('SELECT COUNT(*) FROM workflows'))
       print(f'Total workflows: {result.scalar()}')
   "
   ```

4. **Test Advanced Queries**
   - "Find all Python workflows"
   - "What are the most popular workflows?"
   - "Show me beginner-level data engineering workflows"

## 🎯 What You Get

✅ **Intelligent Search**: Semantic understanding of queries  
✅ **Token Efficiency**: 39x reduction (236KB → 6-10KB)  
✅ **Scalability**: Handles 1000+ workflows  
✅ **Analytics**: Track usage and helpfulness  
✅ **Relationships**: Prerequisite chains  
✅ **Cloud-Based**: Accessible from any computer  

## 📚 Documentation

- **Quick Start**: `docs/QUICKSTART.md`
- **API Reference**: `docs/API.md`
- **Deployment**: `docs/DEPLOYMENT.md`
- **Status**: `PROJECT_STATUS.md`

---

**Total Setup Time**: 15-20 minutes

**Ready to start?** Begin with Step 1! 🚀
