# Code Buddy MCP - Quick Start Guide

## ✅ Setup Complete!

Your MCP server is installed and tested. Now let's configure it with Claude Desktop.

## Step 1: Locate Claude Desktop Config

Open this file in a text editor:
```
%APPDATA%\Claude\claude_desktop_config.json
```

Or from PowerShell:
```powershell
notepad "$env:APPDATA\Claude\claude_desktop_config.json"
```

## Step 2: Add Code Buddy Configuration

Add this to your config file:

```json
{
  "mcpServers": {
    "code-buddy": {
      "command": "C:\\Repos\\code_buddy_mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Repos\\code_buddy_mcp\\src\\server.py"
      ],
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

**Note:** If you already have other MCP servers configured, just add the "code-buddy" section inside the existing "mcpServers" object.

## Step 3: Restart Claude Desktop

1. Close Claude Desktop completely
2. Reopen Claude Desktop
3. Look for the 🔌 icon in the bottom right - it should show "code-buddy" is connected

## Step 4: Test It!

Try these queries in Claude:

1. **List categories:**
   ```
   Can you list all workflow categories?
   ```

2. **Search workflows:**
   ```
   Search for workflows about API design
   ```

3. **Get specific workflow:**
   ```
   Show me workflow #1
   ```

4. **Search with filters:**
   ```
   Find Python workflows for beginners about testing
   ```

## Available Tools

Your Code Buddy MCP provides these tools to Claude:

- **search_workflows** - Smart search with semantic matching
- **get_workflow** - Get full workflow details
- **list_categories** - Browse all categories  
- **get_prerequisites** - See workflow dependencies
- **track_usage** - Provide feedback on workflows

## Troubleshooting

### MCP not showing up?
- Check the config file syntax (valid JSON)
- Make sure paths use double backslashes (`\\`)
- Restart Claude Desktop

### Connection errors?
- Verify DATABASE_URL is correct
- Check COHERE_API_KEY is valid
- Look in Claude Desktop logs: `%APPDATA%\Claude\logs`

### Need help?
Run tests again:
```powershell
.\test_mcp.ps1
```

---

🎉 **You're all set!** Your Code Buddy MCP gives Claude access to 117 professional workflows.
