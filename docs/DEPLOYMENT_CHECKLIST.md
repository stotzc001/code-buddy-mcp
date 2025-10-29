# Code Buddy MCP - Deployment Checklist

## ✅ Phase 1: Repository Cleanup (5 minutes)

### 1.1: Run Cleanup Script
```powershell
cd C:\Repos\code_buddy_mcp
python cleanup_repo.py
```

**Expected Result:** 
- ~40 temporary files moved to `archive/` folder
- Clean repository structure

### 1.2: Create Virtual Environment
```powershell
# Create .venv
python -m venv .venv

# Activate
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Expected Result:**
- `.venv/` folder created
- All dependencies installed

### 1.3: Test Locally
```powershell
# Quick test
python -c "from src.server import mcp; print('✓ Server imports successfully')"

# Full server test (Ctrl+C to stop)
python -m src.server
```

**Expected Result:**
- No import errors
- Server starts successfully

---

## ✅ Phase 2: Git and GitHub (10 minutes)

### 2.1: Check Git Status
```powershell
git status
```

### 2.2: Add Files
```powershell
# Add all files
git add .

# Check what's being committed
git status
```

**Verify .venv is NOT in the list** (should be in .gitignore)

### 2.3: Commit
```powershell
git commit -m "Production-ready Code Buddy MCP

- 117 workflows with full embeddings
- 730 tasks, 343 skills
- Railway deployment configuration
- Clean repository structure
- Complete documentation"
```

### 2.4: Create GitHub Repository

**Option A: GitHub CLI**
```powershell
gh repo create code-buddy-mcp --public --source=. --remote=origin
git push -u origin main
```

**Option B: Web Interface**
1. Go to https://github.com/new
2. Repository name: `code-buddy-mcp`
3. Choose Public or Private
4. DO NOT initialize with README (we have one)
5. Click "Create repository"
6. Run:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/code-buddy-mcp.git
git branch -M main
git push -u origin main
```

**Expected Result:**
- Repository created on GitHub
- Code pushed successfully
- Verify at: https://github.com/YOUR_USERNAME/code-buddy-mcp

---

## ✅ Phase 3: Railway Deployment (15 minutes)

### 3.1: Login to Railway
1. Go to https://railway.app
2. Sign in with GitHub

### 3.2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your GitHub
4. Choose `code-buddy-mcp` repository
5. Click "Deploy Now"

### 3.3: Configure Environment Variables

In Railway dashboard:
1. Click your service
2. Go to "Variables" tab
3. Click "Raw Editor"
4. Paste:

```env
DATABASE_URL=postgresql://postgres:NCZNJ9yWWcpGTLKm-vvpNeuA3J-vvbuH@shortline.proxy.rlwy.net:38056/railway
COHERE_API_KEY=JSbTlybyl89CpMGaAlcLKVtARcBBYZZqLBASC1jQ
EMBEDDING_PROVIDER=cohere
EMBEDDING_MODEL=embed-english-v3.0
EMBEDDING_DIMENSIONS=1024
MCP_SERVER_NAME=code-buddy
LOG_LEVEL=INFO
```

5. Click "Update Variables"

### 3.4: Wait for Deployment

**Monitor deployment:**
- Watch "Deployments" tab
- Status should change: Building → Deploying → Running
- Takes 2-3 minutes

### 3.5: Get Service URL

1. Click "Settings" tab
2. Scroll to "Networking"
3. Click "Generate Domain"
4. Copy the URL (e.g., `code-buddy-mcp-production.up.railway.app`)

**Expected Result:**
- Service shows "Running" status (green)
- Domain URL available
- No errors in logs

---

## ✅ Phase 4: Configure Claude Desktop (5 minutes)

### 4.1: Locate Config File

**Windows:**
```powershell
notepad $env:APPDATA\Claude\claude_desktop_config.json
```

**Mac:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 4.2: Add Configuration

**For Railway Deployment:**
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

**Note:** This uses local server but connects to Railway database. For full Railway deployment, see DEPLOYMENT_GUIDE.md

### 4.3: Restart Claude Desktop

**Windows:**
- Close Claude Desktop completely (check system tray)
- Reopen Claude Desktop

**Mac:**
- Quit (Cmd+Q)
- Reopen

**Expected Result:**
- Claude Desktop restarts successfully
- No error messages

---

## ✅ Phase 5: Test Integration (5 minutes)

In Claude Desktop, test these commands:

### Test 1: List Categories
```
Can you list all workflow categories?
```
**Expected:** List of 11 categories with workflow counts

### Test 2: Search Workflows
```
Search for workflows about API design
```
**Expected:** Relevant workflows returned with descriptions

### Test 3: Get Workflow
```
Show me workflow ID 1
```
**Expected:** Complete workflow content displayed

### Test 4: Filtered Search
```
Find beginner-level workflows about Docker
```
**Expected:** Filtered results by complexity and technology

### Test 5: Category Browse
```
What workflows are available for Data Engineering?
```
**Expected:** Data Engineering workflows listed

---

## ✅ Success Criteria

Your deployment is complete when:

- ✅ Repository is clean (temporary files archived)
- ✅ Code pushed to GitHub successfully
- ✅ Railway shows "Running" status
- ✅ No errors in Railway logs
- ✅ Claude Desktop shows Code Buddy tools
- ✅ Search queries return workflows
- ✅ All 5 test commands work

---

## 🎊 You're Done!

Your Code Buddy MCP is now:
- ✅ Production-ready
- ✅ Deployed to Railway
- ✅ Integrated with Claude Desktop
- ✅ Accessible to your team

**Next Steps:**
1. Share GitHub repo with team
2. Share Railway URL with team
3. Document any custom workflows
4. Monitor usage analytics
5. Add more workflows as needed

---

## 🐛 Troubleshooting

### Cleanup Issues
**Problem:** cleanup_repo.py fails
**Solution:** Run manually or skip - not critical for deployment

### Git Issues
**Problem:** "fatal: not a git repository"
**Solution:** Run `git init` first

### Railway Issues
**Problem:** Build fails
**Solution:** Check logs, verify requirements.txt is correct

### Claude Desktop Issues
**Problem:** MCP tools not appearing
**Solution:** 
1. Verify JSON syntax in config
2. Restart Claude Desktop
3. Check logs in Help > View Logs

---

## 📞 Need Help?

- Check DEPLOYMENT_GUIDE.md for detailed instructions
- Check TROUBLESHOOTING.md for common issues
- Check Railway logs for errors
- Review GitHub Issues

**Total Time:** ~40 minutes from start to finish
