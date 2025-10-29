# 🎯 START HERE - One Page Guide

## What is this?
Code Buddy MCP gives Claude access to 117 curated coding workflows with semantic search.

## Current Status
✅ **Database:** 117 workflows, 730 tasks, 343 skills - ALL READY  
✅ **Embeddings:** All generated with Cohere  
✅ **Code:** Production-ready, needs deployment  
⏳ **Deploy:** Follow steps below

---

## 🚀 Deploy in 4 Steps (30 minutes)

### 1️⃣ Setup (5 min)
```powershell
cd C:\Repos\code_buddy_mcp
.\deploy.ps1
```
Cleans repo, creates .venv, installs dependencies

### 2️⃣ GitHub (5 min)
```powershell
git add .
git commit -m "Production-ready Code Buddy MCP"
```
Then create repo at github.com/new and push

### 3️⃣ Railway (10 min)
1. Go to railway.app
2. New Project → Deploy from GitHub  
3. Choose code-buddy-mcp
4. Add environment variables (see EXECUTE_NOW.md)
5. Wait for "Running" status

### 4️⃣ Claude (5 min)
1. Edit: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add config from EXECUTE_NOW.md
3. Restart Claude Desktop
4. Test: "List all workflow categories"

---

## ✅ Success = Claude responds with workflow data!

---

## 📚 Full Documentation

- **EXECUTE_NOW.md** ← Detailed instructions
- **DEPLOYMENT_CHECKLIST.md** ← Step-by-step checklist
- **DEPLOYMENT_SUMMARY.md** ← Complete overview

---

## 🆘 Problems?

**deploy.ps1 fails** → Run commands manually from EXECUTE_NOW.md  
**Railway error** → Check logs in Railway dashboard  
**Claude no tools** → Verify JSON syntax, restart Claude

See **TROUBLESHOOTING.md** for more help

---

**Ready? Run `.\deploy.ps1` now!** 🚀
