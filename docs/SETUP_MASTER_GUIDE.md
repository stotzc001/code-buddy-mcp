# Code Buddy Setup: Complete 3-Part Guide

This is your comprehensive guide to getting Code Buddy MCP Server up and running with all 121 workflows.

---

## 🎯 Overview

You're going to:
1. **Import workflows** to PostgreSQL database (15-20 min)
2. **Generate embeddings** for semantic search (already done in step 1!)
3. **Configure and restart** Claude Desktop (5-10 min)

**Total Time:** ~20-30 minutes  
**Result:** Fully functional MCP server with 121 searchable workflows

---

## 📋 Prerequisites

Before you begin, make sure you have:

- ✅ **Claude Desktop** installed
- ✅ **Python 3.9+** installed
- ✅ **PostgreSQL database** deployed (Railway)
- ✅ **Cohere API key** (or OpenAI API key)
- ✅ **Git repository** cloned to `C:\Repos\code_buddy_mcp`
- ✅ **`.env` file** configured with database credentials

### Quick Prerequisites Check

```powershell
# Check Python
python --version
# Should output: Python 3.9.x or higher

# Check repo location
Test-Path C:\Repos\code_buddy_mcp
# Should output: True

# Check .env file
Test-Path C:\Repos\code_buddy_mcp\.env
# Should output: True

# Check dependencies
cd C:\Repos\code_buddy_mcp
pip install -r requirements.txt
```

If any of these fail, fix them before proceeding.

---

## 📚 The 3-Part Setup Process

### Part 1: Import Workflows to Database

**Time:** 15-20 minutes  
**What:** Import all 121 workflow files and generate embeddings

[**📖 Read Part 1: Database Import**](SETUP_PART_1_DATABASE_IMPORT.md)

**Quick Summary:**
1. Deploy database schema (create tables)
2. Run import script (`import_workflows_v2.py`)
3. Wait for all 121 workflows to import
4. Verify 906 embeddings were generated

**Key Command:**
```powershell
python scripts/import_workflows_v2.py
```

---

### Part 2: Embeddings for Semantic Search

**Time:** Already done! ✅  
**What:** Embeddings were automatically generated in Part 1

[**📖 Read Part 2: Embeddings**](SETUP_PART_2_EMBEDDINGS.md)

**Quick Summary:**
- Embeddings were generated during import (Part 1)
- No additional steps needed
- Verify 100% coverage

**Key Command:**
```powershell
# Verify embeddings
python -c "import os; from dotenv import load_dotenv; import psycopg; load_dotenv(); conn = psycopg.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM workflows WHERE embedding IS NOT NULL'); print(f'Embeddings: {cur.fetchone()[0]}/121'); conn.close()"
```

---

### Part 3: Restart MCP Server

**Time:** 5-10 minutes  
**What:** Configure Claude Desktop and connect to your MCP server

[**📖 Read Part 3: MCP Server**](SETUP_PART_3_MCP_SERVER.md)

**Quick Summary:**
1. Edit `claude_desktop_config.json`
2. Add MCP server configuration
3. Restart Claude Desktop
4. Verify connection (look for 🔌 icon)
5. Test with sample queries

**Key Steps:**
```powershell
# 1. Open config file
notepad $env:APPDATA\Claude\claude_desktop_config.json

# 2. Add configuration (see Part 3 guide)

# 3. Restart Claude Desktop (quit from tray icon)

# 4. Test in Claude:
# "Search for workflows about FastAPI"
```

---

## 🚀 Quick Start (For the Impatient)

If you just want the commands without reading the full guides:

```powershell
# Navigate to repo
cd C:\Repos\code_buddy_mcp

# Install dependencies
pip install -r requirements.txt

# Deploy database schema
python scripts/deploy_schema_v2.py

# Import workflows (takes 15-20 minutes)
python scripts/import_workflows_v2.py

# Verify import
python -c "import os; from dotenv import load_dotenv; import psycopg; load_dotenv(); conn = psycopg.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM workflows'); print(f'Workflows: {cur.fetchone()[0]}'); conn.close()"

# Configure Claude Desktop
notepad $env:APPDATA\Claude\claude_desktop_config.json
# (Add configuration from Part 3 guide)

# Restart Claude Desktop
# (Right-click tray icon → Quit → Reopen)
```

---

## ✅ Success Checklist

After completing all three parts, verify:

- [ ] **Database has 121 workflows**
  ```powershell
  python -c "import os; from dotenv import load_dotenv; import psycopg; load_dotenv(); conn = psycopg.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM workflows'); print(f'Workflows: {cur.fetchone()[0]}'); conn.close()"
  ```
  Expected: `Workflows: 121`

- [ ] **All embeddings generated**
  ```powershell
  python -c "import os; from dotenv import load_dotenv; import psycopg; load_dotenv(); conn = psycopg.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM workflows WHERE embedding IS NOT NULL'); print(f'Embeddings: {cur.fetchone()[0]}/121'); conn.close()"
  ```
  Expected: `Embeddings: 121/121`

- [ ] **MCP server shows in Claude Desktop**
  - Look for 🔌 icon in bottom-right corner
  - Click it and verify "code-buddy" is listed
  - Status should show 🟢 Connected

- [ ] **Search works**
  - Test query: "Search for workflows about FastAPI"
  - Should return relevant results

- [ ] **Can retrieve workflows**
  - Test query: "Get the FastAPI endpoint workflow"
  - Should return full workflow details

---

## 🔍 Troubleshooting

### Database Connection Issues

**Problem:** Can't connect to database

**Quick Fix:**
```powershell
cd C:\Repos\code_buddy_mcp
python test_db.py
```

If this fails, check your `.env` file for correct `DATABASE_URL`.

---

### Import Fails or Hangs

**Problem:** Import script crashes or stops responding

**Quick Fix:**
1. Press Ctrl+C to stop
2. Re-run the script - it will skip already-imported workflows:
```powershell
python scripts/import_workflows_v2.py
```

---

### MCP Server Not Connecting

**Problem:** 🔌 icon doesn't appear or shows red

**Quick Fix:**
1. Check configuration file syntax:
```powershell
python -c "import json; json.load(open(r'$env:APPDATA\Claude\claude_desktop_config.json')); print('✓ Valid JSON')"
```

2. Test server manually:
```powershell
cd C:\Repos\code_buddy_mcp
python src\server.py
```

3. Check logs:
```powershell
Get-Content "$env:APPDATA\Claude\logs\mcp*.log" -Tail 50
```

---

### Search Returns No Results

**Problem:** MCP connected but searches fail

**Quick Fix:**
1. Verify workflows imported:
```powershell
python -c "import os; from dotenv import load_dotenv; import psycopg; load_dotenv(); conn = psycopg.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM workflows'); print(f'Workflows: {cur.fetchone()[0]}'); conn.close()"
```

2. Verify embeddings exist:
```powershell
python -c "import os; from dotenv import load_dotenv; import psycopg; load_dotenv(); conn = psycopg.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM workflows WHERE embedding IS NOT NULL'); print(f'Embeddings: {cur.fetchone()[0]}'); conn.close()"
```

---

## 🎓 Learning the System

### How It Works

1. **You ask Claude a question** (e.g., "How do I deploy a Docker container?")
2. **Claude calls the MCP server** using the `search_workflows` tool
3. **MCP server generates an embedding** of your question
4. **Database searches** using vector similarity (cosine distance)
5. **Most relevant workflows** are returned to Claude
6. **Claude synthesizes** the workflow content into a helpful response

### Architecture

```
You → Claude Desktop → MCP Server → PostgreSQL Database
                          ↓
                    Cohere API (embeddings)
                          ↓
                    Vector Search
                          ↓
                    Relevant Workflows
```

### What's in the Database

- **121 workflows** - High-level guidance
- **605 tasks** - Step-by-step instructions
- **180 skills** - Reusable techniques
- **906 embeddings** - For semantic search
- **Relationships** - Prerequisites and related workflows

---

## 📖 Additional Resources

### Core Documentation
- [README.md](README.md) - Project overview
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed troubleshooting
- [API.md](docs/API.md) - MCP server API documentation

### Workflow Documentation
- [WORKFLOW_INVENTORY.md](docs/WORKFLOW_INVENTORY.md) - List of all workflows
- [WORKFLOW_FILE_STRUCTURE.md](docs/WORKFLOW_FILE_STRUCTURE.md) - Markdown format

### Setup Guides (Detailed)
- [Part 1: Database Import](SETUP_PART_1_DATABASE_IMPORT.md)
- [Part 2: Embeddings](SETUP_PART_2_EMBEDDINGS.md)
- [Part 3: MCP Server](SETUP_PART_3_MCP_SERVER.md)

---

## 🎉 You're All Set!

Once you've completed all three parts and verified everything works, you can:

### Start Using Code Buddy

Ask Claude natural questions like:
- "How do I create a FastAPI endpoint?"
- "Show me CI/CD workflows for Python"
- "What's the process for deploying to Kubernetes?"
- "Help me set up automated testing"

### Customize for Your Needs

- **Add new workflows** - Create markdown files in `workflows/`
- **Modify existing workflows** - Edit the markdown files
- **Re-import after changes** - Run `python scripts/import_workflows_v2.py`
- **Track usage** - Check `workflow_usage` table for analytics

### Share with Your Team

- **Deploy for team** - Set up shared database
- **Add team workflows** - Contribute team-specific workflows
- **Track what works** - Use analytics to see what's helpful

---

## 🆘 Need Help?

### Something Not Working?

1. **Check the detailed guides** - Each part has extensive troubleshooting
2. **Read error messages** - They usually tell you exactly what's wrong
3. **Check logs** - `%APPDATA%\Claude\logs`
4. **Test components** - Database, embeddings, server individually

### Common Issues & Solutions

| Problem | Guide Section |
|---------|---------------|
| Database won't connect | Part 1, Step 1 |
| Import fails | Part 1, Step 4 |
| Missing embeddings | Part 2, verification |
| MCP not connecting | Part 3, Step 5 |
| Search doesn't work | Part 3, troubleshooting |

---

## 📊 System Status Check

Run this comprehensive check to verify everything:

```powershell
cd C:\Repos\code_buddy_mcp

Write-Host "`n=== Code Buddy System Check ===" -ForegroundColor Cyan

# Check Python
Write-Host "`nPython:" -ForegroundColor Yellow
python --version

# Check dependencies
Write-Host "`nDependencies:" -ForegroundColor Yellow
python -c "import psycopg; import cohere; print('✓ All dependencies installed')"

# Check database
Write-Host "`nDatabase:" -ForegroundColor Yellow
python test_db.py

# Check workflow count
Write-Host "`nWorkflows:" -ForegroundColor Yellow
python -c "import os; from dotenv import load_dotenv; import psycopg; load_dotenv(); conn = psycopg.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM workflows'); print(f'  Total: {cur.fetchone()[0]}'); cur.execute('SELECT COUNT(*) FROM workflows WHERE embedding IS NOT NULL'); print(f'  With embeddings: {cur.fetchone()[0]}'); conn.close()"

# Check config file
Write-Host "`nClaude Desktop Config:" -ForegroundColor Yellow
if (Test-Path "$env:APPDATA\Claude\claude_desktop_config.json") {
    python -c "import json; json.load(open(r'$env:APPDATA\Claude\claude_desktop_config.json')); print('  ✓ Valid JSON')"
    Write-Host "  ✓ File exists"
} else {
    Write-Host "  ✗ File not found" -ForegroundColor Red
}

Write-Host "`n=== Check Complete ===" -ForegroundColor Cyan
```

---

## 🎯 Next Steps

**Option 1: Basic Usage**
- Start using Code Buddy immediately
- Ask Claude questions about coding workflows
- Get step-by-step guidance

**Option 2: Advanced Setup**
- Add your own custom workflows
- Integrate with CI/CD
- Set up team deployment

**Option 3: Contributing**
- Improve existing workflows
- Add new categories
- Share with the community

---

**Happy Coding with Code Buddy!** 🚀

---

*Last Updated: October 28, 2025*  
*Version: 2.0 (Granular Architecture)*
