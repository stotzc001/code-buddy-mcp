# 🔧 Code Buddy MCP - Troubleshooting Guide

## Quick Diagnostics

Run these commands to check system status:

```bash
# 1. Check Python version (need 3.8+)
python --version

# 2. Test database connection
python test_db.py

# 3. Check installed packages
pip list | grep -E "fastmcp|psycopg2|cohere|sqlalchemy|pgvector"

# 4. Count workflows in database
python -c "from src.database.connection import DatabaseConnection; from dotenv import load_dotenv; import os; load_dotenv(); db = DatabaseConnection(os.getenv('DATABASE_URL')); from sqlalchemy import text; session = db.get_session().__enter__(); result = session.execute(text('SELECT COUNT(*) FROM workflows')); print(f'Workflows: {result.scalar()}')"
```

---

## Issue 1: "Module not found" Errors

### Symptoms
```
ModuleNotFoundError: No module named 'fastmcp'
ModuleNotFoundError: No module named 'cohere'
ModuleNotFoundError: No module named 'psycopg2'
```

### Solutions

**Solution 1: Install dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Solution 2: Check Python version**
```bash
python --version
# Need Python 3.8 or higher
```

**Solution 3: Use virtual environment**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Solution 4: Install specific missing packages**
```bash
pip install fastmcp==0.1.0
pip install cohere==5.11.0
pip install "psycopg[binary]==3.1.18"
pip install sqlalchemy==2.0.23
pip install pgvector==0.2.4
```

**Solution 5: Windows psycopg2-binary build error**
If you see "pg_config executable not found":
```bash
# Uninstall old version
pip uninstall psycopg2 psycopg2-binary

# Install psycopg3 (better Windows support)
pip install "psycopg[binary]"
```

---

## Issue 2: Database Connection Failed

### Symptoms
```
❌ ERROR: DATABASE_URL not found in environment
psycopg2.OperationalError: could not connect to server
Connection refused
```

### Solutions

**Solution 1: Check .env file exists**
```bash
# Windows
type .env

# Mac/Linux
cat .env
```

Should show:
```
DATABASE_URL=postgresql://postgres:...@shortline.proxy.rlwy.net:38056/railway
COHERE_API_KEY=JSbTlybyl89CpMGaAlcLKVtARcBBYZZqLBASC1jQ
...
```

**Solution 2: Verify DATABASE_URL format**
```
Correct format:
postgresql://username:password@host:port/database

Example:
postgresql://postgres:abc123@shortline.proxy.rlwy.net:38056/railway
```

**Solution 3: Test Railway connection**
1. Go to https://railway.app
2. Open your project
3. Click on PostgreSQL service
4. Check "Connect" tab for correct credentials
5. Copy DATABASE_URL from Railway
6. Update .env file

**Solution 4: Check Railway database is running**
1. Go to Railway dashboard
2. Verify PostgreSQL service is "Active"
3. Check recent logs for errors
4. Restart service if needed

**Solution 5: Test connection manually**
```bash
python test_db.py
```

---

## Issue 3: pgvector Extension Not Found

### Symptoms
```
❌ pgvector extension not found
ERROR: extension "vector" does not exist
```

### Solutions

**Solution 1: Railway includes pgvector by default**
Railway PostgreSQL comes with pgvector pre-installed. If missing:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Solution 2: Verify pgvector installation**
```bash
python test_db.py
# Should show: ✅ pgvector extension: Installed
```

**Solution 3: Enable extension manually**
1. Connect to Railway PostgreSQL using their web SQL editor
2. Run: `CREATE EXTENSION IF NOT EXISTS vector;`
3. Test again: `python test_db.py`

---

## Issue 4: No Workflows Found After Import

### Symptoms
```
📊 Import Summary:
✅ Successfully imported: 0
⏭️  Skipped (unchanged): 0
❌ Failed: 0
```

Or in Claude:
```
No workflows found matching your query
```

### Solutions

**Solution 1: Check file format**
Workflows must be `.md` files with YAML frontmatter:
```markdown
---
title: My Workflow
description: Description here
category: Development
tags: [tag1, tag2]
technologies: [Python]
complexity: intermediate
estimated_time_minutes: 30
---

# Content here
```

**Solution 2: Verify file locations**
```bash
# List all markdown files
# Windows
dir /s /b workflows\*.md

# Mac/Linux
find workflows -name "*.md"
```

**Solution 3: Re-run import with verbose mode**
```bash
python scripts/import_workflows.py --directory ./workflows --verbose
```

**Solution 4: Check database directly**
```bash
python -c "from src.database.connection import DatabaseConnection; from dotenv import load_dotenv; import os; load_dotenv(); db = DatabaseConnection(os.getenv('DATABASE_URL')); from sqlalchemy import text; session = db.get_session().__enter__(); result = session.execute(text('SELECT id, title FROM workflows LIMIT 5')); [print(f'{row[0]}: {row[1]}') for row in result]"
```

**Solution 5: Reset and re-import**
```bash
# CAUTION: This deletes all data
python scripts/setup_database.py --reset
python scripts/import_workflows.py --directory ./workflows
```

---

## Issue 5: MCP Server Not Showing in Claude Desktop

### Symptoms
- No 🔧 icon in Claude chat input
- Claude doesn't recognize code-buddy tools
- "code-buddy" not listed in available tools

### Solutions

**Solution 1: Verify config file location**

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
```bash
# Check file exists
type "%APPDATA%\Claude\claude_desktop_config.json"
```

**Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
```bash
# Check file exists
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Solution 2: Validate JSON syntax**
Use a JSON validator: https://jsonlint.com

Common mistakes:
- Missing commas between properties
- Extra comma after last property
- Unescaped backslashes (use `\\` not `\`)

**Correct format**:
```json
{
  "mcpServers": {
    "code-buddy": {
      "command": "python",
      "args": ["C:\\Repos\\code_buddy_mcp\\src\\server.py"],
      "env": {
        "DATABASE_URL": "postgresql://...",
        "COHERE_API_KEY": "...",
        "EMBEDDING_PROVIDER": "cohere",
        "EMBEDDING_MODEL": "embed-english-v3.0",
        "EMBEDDING_DIMENSIONS": "1024"
      }
    }
  }
}
```

**Solution 3: Check path format**

**Windows**: Use double backslashes
```json
"args": ["C:\\Repos\\code_buddy_mcp\\src\\server.py"]
```

**Mac/Linux**: Use forward slashes
```json
"args": ["/Users/username/code_buddy_mcp/src/server.py"]
```

**Solution 4: Verify server starts**
```bash
python src/server.py
```

Should show:
```
✅ Server ready!
Listening for MCP connections...
```

**Solution 5: Complete restart**
1. Quit Claude Desktop completely (check Task Manager/Activity Monitor)
2. Wait 10 seconds
3. Restart Claude Desktop
4. Check for 🔧 icon

**Solution 6: Check Claude logs**

**Windows**: `%APPDATA%\Claude\logs\`
**Mac**: `~/Library/Logs/Claude/`

Look for MCP-related errors

---

## Issue 6: Import is Very Slow

### Symptoms
- Import takes >5 minutes for 118 workflows
- Each workflow takes >2 seconds

### Solutions

**Solution 1: Check internet connection**
Cohere API requires internet. Test:
```bash
curl https://api.cohere.ai/v1/models
```

**Solution 2: Verify API key is valid**
```bash
python -c "import cohere; import os; from dotenv import load_dotenv; load_dotenv(); client = cohere.Client(os.getenv('COHERE_API_KEY')); print('API key valid:', client.check_api_key())"
```

**Solution 3: Use batch processing**
Already enabled by default in `import_workflows.py`

**Solution 4: Check Railway database performance**
1. Go to Railway dashboard
2. Check database metrics (CPU, memory, connections)
3. Upgrade plan if needed

---

## Issue 7: Search Returns Irrelevant Results

### Symptoms
- Searches return workflows not related to query
- Similarity scores are low (<0.5)
- Wrong categories returned

### Solutions

**Solution 1: Check embeddings were generated**
```bash
python -c "from src.database.connection import DatabaseConnection; from dotenv import load_dotenv; import os; load_dotenv(); db = DatabaseConnection(os.getenv('DATABASE_URL')); from sqlalchemy import text; session = db.get_session().__enter__(); result = session.execute(text('SELECT COUNT(*) FROM workflows WHERE embedding IS NOT NULL')); print(f'Workflows with embeddings: {result.scalar()}')"
```

**Solution 2: Regenerate embeddings**
```bash
# Re-import with fresh embeddings
python scripts/import_workflows.py --directory ./workflows --force
```

**Solution 3: Verify embedding dimensions**
Check `.env` file:
```
EMBEDDING_DIMENSIONS=1024  # For Cohere
```

**Solution 4: Check search query in logs**
Run server with debug logging:
```bash
python src/server.py --log-level DEBUG
```

**Solution 5: Test with simple query**
Try: "Python" or "API" (single word queries)

---

## Issue 8: "Cohere API Error"

### Symptoms
```
CohereError: invalid_api_key
CohereError: rate_limit_exceeded
CohereError: too_many_tokens
```

### Solutions

**Solution 1: Verify API key**
1. Go to https://dashboard.cohere.com
2. Check API key is active
3. Copy key exactly (no extra spaces)
4. Update `.env` file

**Solution 2: Check rate limits**
Free tier: 100 requests/minute
- Wait 1 minute
- Retry import

**Solution 3: Reduce batch size**
Edit `src/utils/embeddings.py`:
```python
batch_size = min(batch_size, 10)  # Reduce from 96
```

**Solution 4: Check token limits**
Cohere has token limits per request. If workflow is too long:
- Edit `generate_workflow_embedding()` to truncate more
- Currently: `content[:1000]`
- Reduce to: `content[:500]`

---

## Issue 9: Performance is Slow

### Symptoms
- Searches take >1 second
- Claude waits a long time for results
- Server logs show slow queries

### Solutions

**Solution 1: Check indexes**
```sql
-- Should have these indexes
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE tablename = 'workflows';
```

Expected indexes:
- `idx_workflows_embedding` (IVFFlat for vector search)
- `idx_workflows_category`
- `idx_workflows_tags` (GIN)
- `idx_workflows_technologies` (GIN)

**Solution 2: Refresh materialized view**
```sql
REFRESH MATERIALIZED VIEW popular_workflows;
```

**Solution 3: Analyze database**
```sql
ANALYZE workflows;
VACUUM ANALYZE workflows;
```

**Solution 4: Check Railway database plan**
- Free tier: 512MB RAM
- Consider upgrade for better performance

**Solution 5: Reduce result limit**
Edit `src/tools/workflow_search.py`:
```python
limit: int = 3  # Reduce from 5
```

---

## Issue 10: Claude Desktop Config Not Working

### Symptoms
- Config file looks correct
- Server is running
- But Claude still doesn't show code-buddy

### Solutions

**Solution 1: Check absolute path**
Path must be absolute, not relative:

**Wrong**:
```json
"args": ["./src/server.py"]
"args": ["server.py"]
```

**Correct**:
```json
"args": ["C:\\Repos\\code_buddy_mcp\\src\\server.py"]
```

**Solution 2: Test command manually**
Run the exact command from config:
```bash
python C:\Repos\code_buddy_mcp\src\server.py
```

**Solution 3: Use Python absolute path**
Find Python path:
```bash
# Windows
where python

# Mac/Linux
which python
```

Use full path in config:
```json
"command": "C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"
```

**Solution 4: Check environment variables**
Verify env vars in config match `.env`:
- DATABASE_URL
- COHERE_API_KEY
- EMBEDDING_PROVIDER
- EMBEDDING_MODEL
- EMBEDDING_DIMENSIONS

**Solution 5: Create dedicated config file**
Sometimes helps to create fresh config:
```bash
# Backup old config
copy "%APPDATA%\Claude\claude_desktop_config.json" "%APPDATA%\Claude\claude_desktop_config.json.backup"

# Create new config
# Paste correct JSON
# Save and restart Claude
```

---

## Getting Help

### Diagnostic Report

If issues persist, generate a diagnostic report:

```bash
# Create diagnostics.txt
echo "=== System Info ===" > diagnostics.txt
python --version >> diagnostics.txt
echo "" >> diagnostics.txt

echo "=== Installed Packages ===" >> diagnostics.txt
pip list | grep -E "fastmcp|psycopg2|cohere|sqlalchemy|pgvector" >> diagnostics.txt
echo "" >> diagnostics.txt

echo "=== Database Connection ===" >> diagnostics.txt
python test_db.py >> diagnostics.txt
echo "" >> diagnostics.txt

echo "=== Workflow Count ===" >> diagnostics.txt
python -c "from src.database.connection import DatabaseConnection; from dotenv import load_dotenv; import os; load_dotenv(); db = DatabaseConnection(os.getenv('DATABASE_URL')); from sqlalchemy import text; session = db.get_session().__enter__(); result = session.execute(text('SELECT COUNT(*) FROM workflows')); print(f'Total: {result.scalar()}')" >> diagnostics.txt

echo "Diagnostics saved to diagnostics.txt"
```

### Check Logs

**MCP Server Logs**:
Run server with debug output:
```bash
python src/server.py --log-level DEBUG > server.log 2>&1
```

**Claude Desktop Logs**:
- Windows: `%APPDATA%\Claude\logs\`
- Mac: `~/Library/Logs/Claude/`

### Resources

- **Setup Guide**: `SETUP_GUIDE.md`
- **Commands**: `COMMANDS.md`
- **Progress Tracker**: `PROGRESS.md`
- **Project Status**: `PROJECT_STATUS.md`
- **API Docs**: `docs/API.md`

### Railway Support
- Dashboard: https://railway.app
- Docs: https://docs.railway.app
- Community: https://discord.gg/railway

### Cohere Support
- Dashboard: https://dashboard.cohere.com
- Docs: https://docs.cohere.com
- Community: https://discord.gg/cohere

---

## Prevention Tips

### Best Practices

1. **Use Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
   ```

2. **Keep Dependencies Updated**
   ```bash
   pip install --upgrade pip
   pip install --upgrade -r requirements.txt
   ```

3. **Regular Backups**
   ```bash
   # Export workflows
   pg_dump $DATABASE_URL > backup.sql
   ```

4. **Monitor Railway Usage**
   - Check database size
   - Monitor API calls
   - Set up alerts

5. **Test After Changes**
   ```bash
   python test_db.py
   python src/server.py  # Verify starts
   ```

### Maintenance Schedule

**Weekly**:
- [ ] Check server logs for errors
- [ ] Verify workflow count matches expectations
- [ ] Test search functionality

**Monthly**:
- [ ] Update dependencies
- [ ] Refresh materialized views
- [ ] Review usage analytics

**As Needed**:
- [ ] Re-import workflows when updated
- [ ] Add new categories
- [ ] Update relationship mappings

---

**Still having issues?** Check the full documentation in `docs/` folder.
