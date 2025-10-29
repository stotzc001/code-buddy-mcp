# Code Buddy Setup - Quick Reference Card

One-page reference for the complete setup process.

---

## 📋 Prerequisites
```powershell
# Verify everything is ready
python --version              # Python 3.9+
Test-Path C:\Repos\code_buddy_mcp\.env  # True
cd C:\Repos\code_buddy_mcp
pip install -r requirements.txt
```

---

## ⚡ Quick Setup (30 minutes)

### Step 1: Deploy Schema (2 min)
```powershell
cd C:\Repos\code_buddy_mcp
python scripts/deploy_schema_v2.py
```

### Step 2: Import Workflows (20 min)
```powershell
python scripts/import_workflows_v2.py
# Wait for: ✓ Successfully imported: 121
```

### Step 3: Verify Import (1 min)
```powershell
python -c "import os; from dotenv import load_dotenv; import psycopg; load_dotenv(); conn = psycopg.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM workflows'); print(f'Workflows: {cur.fetchone()[0]}'); cur.execute('SELECT COUNT(*) FROM workflows WHERE embedding IS NOT NULL'); print(f'Embeddings: {cur.fetchone()[0]}'); conn.close()"
# Expected: Workflows: 121, Embeddings: 121
```

### Step 4: Configure Claude (5 min)
```powershell
# Edit config
notepad $env:APPDATA\Claude\claude_desktop_config.json
```

Add this (adjust path if needed):
```json
{
  "mcpServers": {
    "code-buddy": {
      "command": "python",
      "args": ["C:/Repos/code_buddy_mcp/src/server.py"],
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

### Step 5: Restart Claude (2 min)
1. Right-click Claude tray icon → Quit
2. Wait 5 seconds
3. Reopen Claude Desktop
4. Look for 🔌 icon → "code-buddy" 🟢

### Step 6: Test (1 min)
In Claude Desktop:
```
Search for workflows about FastAPI
```

---

## 🔍 Quick Diagnostics

### Test Database
```powershell
python test_db.py
```

### Count Everything
```powershell
python count_workflows.py
python -c "import os; from dotenv import load_dotenv; import psycopg; load_dotenv(); conn = psycopg.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM workflows'); wf=cur.fetchone()[0]; cur.execute('SELECT COUNT(*) FROM tasks'); t=cur.fetchone()[0]; cur.execute('SELECT COUNT(*) FROM skills'); s=cur.fetchone()[0]; print(f'Workflows: {wf}\nTasks: {t}\nSkills: {s}\nTotal: {wf+t+s}'); conn.close()"
```

### Verify Config
```powershell
python -c "import json; json.load(open(r'$env:APPDATA\Claude\claude_desktop_config.json')); print('✓ Valid JSON')"
```

### Test Server
```powershell
python src\server.py
# Ctrl+C to stop
```

### View Logs
```powershell
Get-Content "$env:APPDATA\Claude\logs\mcp*.log" -Tail 30
```

---

## 🆘 Quick Fixes

### Import Fails
```powershell
# Re-run (skips completed workflows)
python scripts/import_workflows_v2.py
```

### Missing Dependencies
```powershell
pip install -r requirements.txt
```

### MCP Not Connecting
```powershell
# Check config syntax
python -c "import json; json.load(open(r'$env:APPDATA\Claude\claude_desktop_config.json'))"

# Test server
cd C:\Repos\code_buddy_mcp
python src\server.py
```

### No Search Results
```powershell
# Verify imports
python -c "import os; from dotenv import load_dotenv; import psycopg; load_dotenv(); conn = psycopg.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM workflows WHERE embedding IS NOT NULL'); print(f'Embeddings: {cur.fetchone()[0]}/121'); conn.close()"
```

---

## ✅ Success Checklist

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured
- [ ] Database schema deployed
- [ ] 121 workflows imported
- [ ] 906 embeddings generated
- [ ] `claude_desktop_config.json` updated
- [ ] Claude Desktop restarted
- [ ] 🔌 icon shows "code-buddy" 🟢
- [ ] Search returns results

---

## 📚 Full Documentation

- **Master Guide:** [SETUP_MASTER_GUIDE.md](SETUP_MASTER_GUIDE.md)
- **Part 1 (Database):** [SETUP_PART_1_DATABASE_IMPORT.md](SETUP_PART_1_DATABASE_IMPORT.md)
- **Part 2 (Embeddings):** [SETUP_PART_2_EMBEDDINGS.md](SETUP_PART_2_EMBEDDINGS.md)
- **Part 3 (MCP Server):** [SETUP_PART_3_MCP_SERVER.md](SETUP_PART_3_MCP_SERVER.md)

---

## 🎯 Expected Results

| Metric | Value |
|--------|-------|
| Workflows | 121 |
| Tasks | ~605 |
| Skills | ~180 |
| Embeddings | 906 |
| Import Time | 15-20 min |
| Database Size | ~50 MB |

---

## 🚀 Test Queries

Try these in Claude Desktop:

1. `Search for workflows about FastAPI`
2. `Get the Docker container workflow`
3. `Show me all DevOps workflows`
4. `How do I set up CI/CD for Python?`
5. `I need to deploy a web app to production`

---

**Setup Time: 30 minutes** | **Difficulty: Easy** | **Worth It: Absolutely!** 🎉
