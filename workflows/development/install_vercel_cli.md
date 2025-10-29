# Install Vercel CLI

**ID:** dev-020  
**Category:** Development  
**Priority:** LOW  
**Complexity:** Simple  
**Estimated Time:** 5-10 minutes  
**Frequency:** Once per machine  
**Last Updated:** 2025-10-27  
**Status:** ✅ Complete

---

## Purpose

**What:** Install and configure Vercel CLI for deploying web applications to Vercel's hosting platform directly from the command line.

**Why:** Vercel CLI enables rapid deployment, preview environments, environment variable management, and local development workflows. Essential for teams using Vercel for frontend hosting.

**When to use:**
- Setting up a new development machine
- Starting a project that deploys to Vercel
- Need to manage Vercel deployments from CLI
- Automating deployments in CI/CD
- Managing environment variables programmatically

---

## Prerequisites

**Required Knowledge:**
- [ ] Basic command line usage
- [ ] Understanding of npm/node

**Required Tools:**
- [ ] Node.js 14.x or higher
- [ ] npm or yarn package manager

**Check before starting:**
```bash
node --version  # Should show v14.0.0 or higher
npm --version   # Should show 6.0.0 or higher
```

---

## Implementation Steps

### Step 1: Install Vercel CLI Globally

**What:** Install the `vercel` command globally on your system

**How:**

```bash
# Using npm (recommended)
npm install -g vercel

# Or using yarn
yarn global add vercel

# Or using pnpm
pnpm add -g vercel
```

**Expected Output:**
```
added 1 package in 3s
```

**Verification:**
```bash
vercel --version
# Should output: Vercel CLI X.X.X
```

**If This Fails:**
→ Check Node.js version is 14+ and npm has write permissions

---

### Step 2: Login to Vercel Account

**What:** Authenticate CLI with your Vercel account

**How:**

```bash
# Interactive login (opens browser)
vercel login

# Or login with email
vercel login --email your.email@example.com

# Or use authentication token (CI/CD)
vercel login --token YOUR_TOKEN_HERE
```

**Expected Flow:**
1. Command opens browser
2. Login to Vercel account
3. Authorize CLI access
4. Success message in terminal

**Verification:**
```bash
# Check authentication status
vercel whoami
# Should show: > your-username
```

**If This Fails:**
→ Ensure browser allows popups, or use email login method

---

### Step 3: Link Project to Vercel (Optional)

**What:** Connect your local project to a Vercel project

**How:**

```bash
# Navigate to your project directory
cd /path/to/your/project

# Link to existing Vercel project
vercel link

# Or create new project and link
vercel

# Follow prompts:
# - Set up and deploy?
# - Which scope?
# - Link to existing project?
# - Project name?
```

**Expected Result:**
- `.vercel` directory created
- `project.json` contains project configuration

**Verification:**
```bash
# Check link status
ls -la .vercel/
# Should show project.json

# View configuration
cat .vercel/project.json
```

---

### Step 4: Configure Environment Variables (Optional)

**What:** Set environment variables for deployments

**How:**

```bash
# Add environment variable
vercel env add NEXT_PUBLIC_API_URL

# Choose which environments:
# - Production
# - Preview
# - Development

# List all environment variables
vercel env ls

# Pull environment variables to local
vercel env pull .env.local

# Remove environment variable
vercel env rm VARIABLE_NAME
```

**Verification:**
```bash
vercel env ls
# Should show all configured variables
```

---

### Step 5: Test Local Development

**What:** Run development server with Vercel CLI

**How:**

```bash
# Start development server
vercel dev

# Specify port
vercel dev --listen 8080

# With environment variables
vercel dev --env-file=.env.local
```

**Expected Output:**
```
Vercel CLI X.X.X
> Ready! Available at http://localhost:3000
```

**Verification:**
- [ ] Server starts without errors
- [ ] Can access application at localhost
- [ ] Environment variables loaded correctly

---

### Step 6: Deploy from CLI

**What:** Deploy application to Vercel

**How:**

```bash
# Deploy to preview (test deployment)
vercel

# Deploy to production
vercel --prod

# Deploy with specific environment
vercel --env production

# Deploy with build command override
vercel --build-env NODE_ENV=production
```

**Expected Output:**
```
🔍  Inspect: https://vercel.com/username/project/...
✅  Preview: https://project-abc123.vercel.app
```

**Verification:**
- [ ] Deployment succeeds
- [ ] Preview URL accessible
- [ ] Application works as expected

---

## Verification Checklist

After installation:

- [ ] `vercel --version` shows version number
- [ ] `vercel whoami` shows your username
- [ ] Can run `vercel login` successfully
- [ ] Can run `vercel dev` in project directory
- [ ] Can deploy with `vercel` command
- [ ] Environment variables accessible (if configured)

---

## Common Issues & Solutions

### Issue 1: Permission Denied During Installation

**Symptoms:**
```
Error: EACCES: permission denied
```

**Solution:**
```bash
# Option 1: Use sudo (not recommended)
sudo npm install -g vercel

# Option 2: Fix npm permissions (recommended)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
npm install -g vercel
```

---

### Issue 2: Command Not Found After Installation

**Symptoms:**
```bash
$ vercel
vercel: command not found
```

**Solution:**
```bash
# Check npm global bin location
npm config get prefix

# Add to PATH (Linux/Mac)
export PATH="$(npm config get prefix)/bin:$PATH"
echo 'export PATH="$(npm config get prefix)/bin:$PATH"' >> ~/.bashrc

# Windows: Add npm global folder to System PATH
# Usually: C:\Users\USERNAME\AppData\Roaming\npm
```

---

### Issue 3: Login Hangs or Fails

**Symptoms:**
- Browser doesn't open
- Login process times out

**Solution:**
```bash
# Use email-based login
vercel login --email your.email@example.com

# Or use authentication token
# Get token from: https://vercel.com/account/tokens
vercel login --token YOUR_TOKEN_HERE

# For CI/CD, use environment variable
export VERCEL_TOKEN=your_token_here
vercel deploy
```

---

## Best Practices

### DO:
✅ Install globally for easy access across projects  
✅ Use `vercel dev` for local development  
✅ Set up environment variables through CLI  
✅ Use preview deployments before production  
✅ Store tokens securely for CI/CD  
✅ Keep CLI updated: `npm update -g vercel`

### DON'T:
❌ Commit `.vercel` directory to git  
❌ Share authentication tokens  
❌ Deploy directly to prod without testing  
❌ Ignore CLI version warnings  
❌ Hardcode environment variables in code

---

## Examples

### Example 1: Complete Setup

```bash
# Install CLI
$ npm install -g vercel
+ vercel@33.0.1

# Verify installation
$ vercel --version
Vercel CLI 33.0.1

# Login
$ vercel login
Vercel CLI 33.0.1
> Log in to Vercel
> Success! Email verified

# Check auth
$ vercel whoami
> john-doe

# Link project
$ cd my-nextjs-app
$ vercel link
? Set up "~/my-nextjs-app"? [Y/n] y
? Which scope should contain your project? john-doe
? Link to existing project? [y/N] n
? What's your project's name? my-nextjs-app
? In which directory is your code located? ./
✅ Linked to john-doe/my-nextjs-app

# Deploy
$ vercel
✅ Preview: https://my-nextjs-app-abc123.vercel.app
```

---

### Example 2: Setting Up Environment Variables

```bash
# Add API URL
$ vercel env add NEXT_PUBLIC_API_URL
? What's the value of NEXT_PUBLIC_API_URL? https://api.example.com
? Add NEXT_PUBLIC_API_URL to which Environments? Production, Preview, Development
✅ Added Environment Variable NEXT_PUBLIC_API_URL

# Pull to local
$ vercel env pull .env.local
✅ Created .env.local file

# Verify
$ cat .env.local
NEXT_PUBLIC_API_URL="https://api.example.com"
```

---

### Example 3: CI/CD Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Vercel CLI
        run: npm install -g vercel
      
      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        run: |
          vercel pull --yes --environment=production
          vercel build --prod
          vercel deploy --prebuilt --prod
```

---

## Related Workflows

**Before This Workflow:**
- [[dev-022]](environment_initialization.md) - Set up development environment
- [[fro-003]](../frontend-development/build_deployment.md) - Build configuration

**After This Workflow:**
- [[dvo-004]](../devops/cicd_pipeline_setup.md) - Full CI/CD setup
- [[fro-003]](../frontend-development/build_deployment.md) - Deploy frontend

**Alternative Workflows:**
- [[dvo-010]](../devops/kubernetes_deployment.md) - Alternative deployment platform

---

## Tags

`vercel` `deployment` `cli-tools` `hosting` `frontend` `ci-cd` `setup` `development`
