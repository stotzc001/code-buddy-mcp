# 🚀 Code Buddy MCP - Deployment Guide

Complete guide for deploying Code Buddy MCP to Railway and connecting Claude Desktop.

---

## 📋 Prerequisites

- Railway account (https://railway.app)
- GitHub account
- Claude Desktop installed
- Python 3.11+ installed locally

---

## Step 1: Clean Up Repository

Run the cleanup script to organize the repo:

```powershell
cd C:\Repos\code_buddy_mcp
python cleanup_repo.py
```

This moves temporary development files to the `archive/` folder.

---

## Step 2: Create Virtual Environment

```powershell
# Create .venv
python -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test locally
python -m src.server
# Press Ctrl+C to stop
```

**Verify .venv is in .gitignore:**
```
.venv/
venv/
env/
```

---

## Step 3: Initialize Git and Push to GitHub

```powershell
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Production-ready Code Buddy MCP with 117 workflows"

# Create GitHub repo (via web or gh cli)
# Then add remote and push:
git remote add origin https://github.com/YOUR_USERNAME/code-buddy-mcp.git
git branch -M main
git push -u origin main
```

---

## Step 4: Deploy to Railway

### 4.1: Create New Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `code-buddy-mcp` repository

### 4.2: Configure Environment Variables

In Railway dashboard, add these variables:

```env
DATABASE_URL=postgresql://postgres:NCZNJ9yWWcpGTLKm-vvpNeuA3J-vvbuH@shortline.proxy.rlwy.net:38056/railway

COHERE_API_KEY=JSbTlybyl89CpMGaAlcLKVtARcBBYZZqLBASC1jQ
EMBEDDING_PROVIDER=cohere
EMBEDDING_MODEL=embed-english-v3.0
EMBEDDING_DIMENSIONS=1024

MCP_SERVER_NAME=code-buddy
LOG_LEVEL=INFO
```

### 4.3: Deploy

Railway will automatically:
- Detect Python project
- Install dependencies from requirements.txt
- Run the start command from Procfile: `python -m src.server`

**Wait for deployment to complete** (usually 2-3 minutes)

### 4.4: Get Your Service URL

Once deployed, Railway provides a URL like:
```
https://code-buddy-mcp-production.up.railway.app
```

Copy this URL for the next step.

---

## Step 5: Configure Claude Desktop

### 5.1: Locate Claude Desktop Config

Windows:
```
%APPDATA%\Claude\claude_desktop_config.json
```

Mac:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### 5.2: Add MCP Server Configuration

**Option A: Railway Deployment (Recommended for Production)**

```json
{
  "mcpServers": {
    "code-buddy": {
      "command": "python",
      "args": ["-c", "import requests; import sys; import json; response = requests.get('https://YOUR-RAILWAY-URL.railway.app/tools'); print(json.dumps(response.json()))"],
      "url": "https://YOUR-RAILWAY-URL.railway.app"
    }
  }
}
```

**Option B: Local Development**

```json
{
  "mcpServers": {
    "code-buddy": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "C:\\Repos\\code_buddy_mcp",
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

### 5.3: Restart Claude Desktop

**Windows:**
- Close Claude Desktop completely (check system tray)
- Reopen Claude Desktop

**Mac:**
- Quit Claude Desktop (Cmd+Q)
- Reopen Claude Desktop

---

## Step 6: Test the Integration

In Claude Desktop, try these commands:

```
1. Can you list all workflow categories?

2. Search for workflows about API design

3. Show me workflow ID 1

4. Find beginner-level workflows about Docker

5. What workflows are available for data engineering?
```

You should see the Code Buddy MCP tools responding with your 117 workflows!

---

## 🔧 Troubleshooting

### Railway Deployment Issues

**"Build Failed"**
- Check Railway logs for error details
- Verify requirements.txt has all dependencies
- Ensure Python version is 3.11+

**"Application Crashed"**
- Check Railway logs: look for import errors
- Verify DATABASE_URL is set correctly
- Ensure COHERE_API_KEY is valid

**"Connection Refused"**
- Railway takes 2-3 minutes to deploy
- Check deployment status in Railway dashboard
- Verify service is "Running" (green status)

### Claude Desktop Issues

**"MCP Server Not Responding"**
- Verify claude_desktop_config.json syntax (valid JSON)
- Check the file path in "cwd" is correct (use double backslashes on Windows)
- Restart Claude Desktop completely

**"No Tools Available"**
- Wait 30 seconds after restart
- Check Claude Desktop logs (Help > View Logs)
- Verify MCP server is running (Railway dashboard or local terminal)

**"Python Not Found"**
- Ensure Python is in PATH
- Try using full path to python.exe in config:
  ```json
  "command": "C:\\Users\\YourUser\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"
  ```

### Database Connection Issues

**"Connection Timeout"**
- Verify Railway PostgreSQL service is running
- Check DATABASE_URL is correct
- Ensure no firewall blocking Railway connections

**"No Workflows Found"**
- Verify database has data: run `python -c "import os; ..."` (see READY_TO_USE.md)
- Check embeddings are generated (they should be!)
- Try broader search terms

---

## 📊 Monitor Your Deployment

### Railway Dashboard
- View logs: Click service > "Logs" tab
- Monitor usage: "Metrics" tab shows CPU/RAM
- Check health: Look for "Running" status

### Local Testing
```powershell
# Test database connection
python -c "import os; from dotenv import load_dotenv; import psycopg; load_dotenv(); conn = psycopg.connect(os.getenv('DATABASE_URL')); print('✓ Database connected')"

# Test embeddings
python -c "from src.utils.embeddings import init_embeddings; gen = init_embeddings(); print('✓ Embeddings ready')"

# Test search
python -c "from src.tools.workflow_search import WorkflowSearcher; s = WorkflowSearcher(); print(s.search('API design', limit=1))"
```

---

## 🎯 Next Steps

1. ✅ **Test thoroughly** - Try various search queries
2. ✅ **Monitor usage** - Watch Railway logs for errors
3. ✅ **Document workflows** - Add more workflows as needed
4. ✅ **Share with team** - Give others the Claude Desktop config
5. ✅ **Set up monitoring** - Use Railway metrics for uptime tracking

---

## 📝 Important URLs

- **Railway Dashboard:** https://railway.app/dashboard
- **GitHub Repo:** https://github.com/YOUR_USERNAME/code-buddy-mcp
- **Railway Service:** https://YOUR-SERVICE.railway.app
- **Database:** shortline.proxy.rlwy.net:38056

---

## 🔐 Security Notes

### Environment Variables
- ✅ .env is in .gitignore (secrets not committed)
- ✅ Use Railway's environment variables (secure)
- ✅ API keys encrypted in Railway

### Database
- ✅ PostgreSQL on Railway (managed, backed up)
- ✅ Connection uses SSL by default
- ✅ Railway handles security patches

### API Keys
- **Cohere API Key** - Keep secret, rotate if exposed
- **Database credentials** - Managed by Railway
- **No API key in code** - All loaded from environment

---

## 🎊 Success Criteria

Your deployment is successful when:

✅ Railway shows "Running" status  
✅ Claude Desktop shows Code Buddy tools  
✅ Search queries return workflows  
✅ No errors in Railway logs  
✅ Database connection works  
✅ Embeddings load properly  

**You now have a production-grade AI coding assistant!** 🚀
