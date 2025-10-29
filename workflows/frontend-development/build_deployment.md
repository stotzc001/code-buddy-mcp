# Build Deployment

**ID:** fro-003  
**Category:** Frontend Development  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Configure production builds and deploy React applications to popular hosting platforms

**Why:** Proper build configuration ensures optimal performance, security, and reliability for production applications

**When to use:**
- Setting up first deployment
- Configuring CI/CD pipelines
- Optimizing build performance
- Migrating between platforms
- Implementing preview deployments
- Troubleshooting deployment issues

---

## Prerequisites

**Required:**
- [ ] React application with Vite or Create React App
- [ ] Git repository
- [ ] Platform account (Vercel/Netlify/AWS/etc.)
- [ ] Basic understanding of environment variables
- [ ] Node.js 18+ installed

**Check before starting:**
```bash
# Verify project builds locally
npm run build

# Check build output
ls -lh dist/ # Vite
ls -lh build/ # CRA

# Verify environment variables format
cat .env.example

# Test production build locally
npm run preview # Vite
npx serve -s build # CRA
```

---

## Implementation Steps

### Step 1: Configure Build Settings

**What:** Optimize build configuration for production

**How:**

**Vite Configuration (vite.config.ts):**
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';
import compression from 'vite-plugin-compression';

export default defineConfig({
  plugins: [
    react(),
    
    // Compress with Brotli
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
    
    // Compress with gzip
    compression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
    
    // Bundle analysis
    visualizer({
      open: false,
      gzipSize: true,
      brotliSize: true,
      filename: 'dist/stats.html',
    }),
  ],

  build: {
    // Output directory
    outDir: 'dist',
    
    // Enable source maps for production debugging
    sourcemap: true,
    
    // Minification
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.logs
        drop_debugger: true,
      },
    },
    
    // Chunk size warnings
    chunkSizeWarningLimit: 1000,
    
    // Rollup options
    rollupOptions: {
      output: {
        // Manual chunk splitting
        manualChunks: {
          // Vendor chunk for React
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          
          // UI libraries
          'ui-vendor': [
            '@radix-ui/react-dialog',
            '@radix-ui/react-dropdown-menu',
          ],
          
          // Utilities
          'utils': ['date-fns', 'lodash-es'],
        },
        
        // Asset naming
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    
    // Asset inlining threshold (base64)
    assetsInlineLimit: 4096, // 4KB
  },

  // Preview server settings
  preview: {
    port: 3000,
    strictPort: true,
  },
});
```

**Webpack Configuration (webpack.config.js):**
```javascript
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  mode: 'production',
  entry: './src/index.tsx',
  
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'static/js/[name].[contenthash:8].js',
    chunkFilename: 'static/js/[name].[contenthash:8].chunk.js',
    assetModuleFilename: 'static/media/[name].[hash][ext]',
    clean: true,
    publicPath: '/',
  },

  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
          },
        },
      }),
      new CssMinimizerPlugin(),
    ],
    
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          priority: -10,
          reuseExistingChunk: true,
        },
        default: {
          minChunks: 2,
          priority: -20,
          reuseExistingChunk: true,
        },
      },
    },
    
    runtimeChunk: 'single',
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
      minify: {
        removeComments: true,
        collapseWhitespace: true,
        removeRedundantAttributes: true,
        useShortDoctype: true,
        removeEmptyAttributes: true,
        removeStyleLinkTypeAttributes: true,
        keepClosingSlash: true,
        minifyJS: true,
        minifyCSS: true,
        minifyURLs: true,
      },
    }),
    
    new MiniCssExtractPlugin({
      filename: 'static/css/[name].[contenthash:8].css',
      chunkFilename: 'static/css/[name].[contenthash:8].chunk.css',
    }),
    
    new CompressionPlugin({
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
      minRatio: 0.8,
    }),
    
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
      reportFilename: 'bundle-report.html',
    }),
  ],
};
```

**Package.json Scripts:**
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "build:analyze": "vite build --mode analyze",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint src --ext ts,tsx",
    "type-check": "tsc --noEmit",
    "clean": "rm -rf dist"
  }
}
```

**Verification:**
- [ ] Build completes successfully
- [ ] Bundle sizes acceptable (<250KB initial)
- [ ] Source maps generated
- [ ] Assets properly hashed
- [ ] Compression working

**If This Fails:**
→ Check for TypeScript errors: `npm run type-check`
→ Verify all dependencies installed
→ Review build logs for specific errors
→ Ensure output directories exist and are writable

---

### Step 2: Set Up Environment Variables

**What:** Manage configuration across environments

**How:**

**Environment Variable Files:**
```bash
# .env.example (commit this)
VITE_API_URL=
VITE_API_KEY=
VITE_ANALYTICS_ID=
VITE_ENVIRONMENT=

# .env.development (local development)
VITE_API_URL=http://localhost:3001/api
VITE_API_KEY=dev-key-12345
VITE_ANALYTICS_ID=
VITE_ENVIRONMENT=development

# .env.production (production - DO NOT COMMIT)
VITE_API_URL=https://api.production.com
VITE_API_KEY=<secret>
VITE_ANALYTICS_ID=UA-XXXXX-Y
VITE_ENVIRONMENT=production
```

**.gitignore:**
```gitignore
# Environment files
.env
.env.local
.env.production
.env.development.local
.env.test.local
.env.production.local

# Build outputs
dist/
build/

# Dependencies
node_modules/

# Logs
*.log
```

**Using Environment Variables:**
```typescript
// src/config/env.ts
interface Config {
  apiUrl: string;
  apiKey: string;
  analyticsId: string;
  environment: 'development' | 'production' | 'staging';
  isDevelopment: boolean;
  isProduction: boolean;
}

export const config: Config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:3001/api',
  apiKey: import.meta.env.VITE_API_KEY || '',
  analyticsId: import.meta.env.VITE_ANALYTICS_ID || '',
  environment: (import.meta.env.VITE_ENVIRONMENT as Config['environment']) || 'development',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
};

// Validation
if (!config.apiUrl) {
  throw new Error('VITE_API_URL is required');
}

if (config.isProduction && !config.apiKey) {
  throw new Error('VITE_API_KEY is required in production');
}
```

**Usage in Components:**
```typescript
import { config } from '@/config/env';

export function ApiClient() {
  const baseUrl = config.apiUrl;
  
  const fetchData = async () => {
    const response = await fetch(`${baseUrl}/data`, {
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
      },
    });
    return response.json();
  };

  return <div>API URL: {baseUrl}</div>;
}
```

**Verification:**
- [ ] Environment files not committed
- [ ] Variables properly prefixed (VITE_, REACT_APP_)
- [ ] Production values different from dev
- [ ] Validation errors on missing vars
- [ ] No secrets in client code

**If This Fails:**
→ Check variable naming (must start with VITE_ or REACT_APP_)
→ Restart dev server after adding new variables
→ Verify .env files are in project root
→ Check that variables are defined before using

---

### Step 3: Deploy to Vercel

**What:** Deploy to Vercel with automatic CI/CD

**How:**

**Install Vercel CLI:**
```bash
npm install -g vercel
vercel login
```

**Initialize Project:**
```bash
# Link to Vercel project
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? my-app
# - Directory? ./
# - Override settings? No
```

**vercel.json Configuration:**
```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  
  "env": {
    "VITE_API_URL": "https://api.production.com",
    "VITE_ENVIRONMENT": "production"
  },
  
  "regions": ["iad1"],
  
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://api.backend.com/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    },
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ],
  
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

**GitHub Actions for Vercel:**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install Vercel CLI
        run: npm install -g vercel
      
      - name: Pull Vercel Environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
      
      - name: Build Project
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
      
      - name: Deploy to Vercel
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

**Deploy:**
```bash
# Preview deployment (branch)
vercel

# Production deployment
vercel --prod

# With custom domain
vercel --prod --domain=myapp.com
```

**Verification:**
- [ ] Deployment successful
- [ ] Environment variables set
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] Preview deployments working

**If This Fails:**
→ Check build logs in Vercel dashboard
→ Verify environment variables in project settings
→ Ensure build command outputs to correct directory
→ Check DNS settings for custom domains

---

### Step 4: Deploy to Netlify

**What:** Alternative deployment platform with similar features

**How:**

**Install Netlify CLI:**
```bash
npm install -g netlify-cli
netlify login
```

**Initialize Project:**
```bash
netlify init

# Follow prompts:
# - Create new site
# - Team: Your team
# - Site name: my-app
# - Build command: npm run build
# - Directory: dist
```

**netlify.toml Configuration:**
```toml
[build]
  command = "npm run build"
  publish = "dist"
  
[build.environment]
  NODE_VERSION = "18"
  NPM_VERSION = "9"

[[redirects]]
  from = "/api/*"
  to = "https://api.backend.com/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

# A/B Testing
[[redirects]]
  from = "/"
  to = "/home-a"
  status = 200
  force = false
  conditions = {Cookie = ["ab_test=variant_a"]}

[[redirects]]
  from = "/"
  to = "/home-b"
  status = 200
  force = false
  conditions = {Cookie = ["ab_test=variant_b"]}
```

**GitHub Actions for Netlify:**
```yaml
# .github/workflows/netlify.yml
name: Deploy to Netlify

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}
          VITE_API_KEY: ${{ secrets.VITE_API_KEY }}
      
      - name: Deploy to Netlify
        uses: netlify/actions/cli@master
        with:
          args: deploy --prod --dir=dist
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

**Deploy:**
```bash
# Preview deployment
netlify deploy

# Production deployment
netlify deploy --prod

# Open site
netlify open:site
```

**Verification:**
- [ ] Site deployed successfully
- [ ] Redirects working
- [ ] Environment variables configured
- [ ] Custom domain set up
- [ ] Deploy previews working

**If This Fails:**
→ Check deploy logs: `netlify watch`
→ Verify build directory exists
→ Test build locally first
→ Check Netlify dashboard for errors

---

### Step 5: Deploy to AWS S3 + CloudFront

**What:** Deploy to AWS for full control and scalability

**How:**

**Install AWS CLI:**
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure
aws configure
```

**Create S3 Bucket:**
```bash
# Create bucket
aws s3 mb s3://my-app-production

# Enable static website hosting
aws s3 website s3://my-app-production \
  --index-document index.html \
  --error-document index.html

# Set bucket policy
aws s3api put-bucket-policy \
  --bucket my-app-production \
  --policy file://bucket-policy.json
```

**bucket-policy.json:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-app-production/*"
    }
  ]
}
```

**CloudFront Distribution:**
```bash
# Create distribution
aws cloudfront create-distribution \
  --origin-domain-name my-app-production.s3.amazonaws.com \
  --default-root-object index.html

# Or use AWS Console for GUI configuration
```

**Deploy Script (deploy.sh):**
```bash
#!/bin/bash
set -e

# Build
echo "Building application..."
npm run build

# Sync to S3
echo "Uploading to S3..."
aws s3 sync dist/ s3://my-app-production \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "index.html"

# Upload index.html without cache
aws s3 cp dist/index.html s3://my-app-production/index.html \
  --cache-control "no-cache, must-revalidate" \
  --content-type "text/html"

# Invalidate CloudFront cache
echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
  --distribution-id E1234EXAMPLE \
  --paths "/*"

echo "Deployment complete!"
```

**GitHub Actions for AWS:**
```yaml
# .github/workflows/aws.yml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy to S3
        run: |
          aws s3 sync dist/ s3://my-app-production \
            --delete \
            --cache-control "public, max-age=31536000, immutable" \
            --exclude "index.html"
          
          aws s3 cp dist/index.html s3://my-app-production/index.html \
            --cache-control "no-cache, must-revalidate"
      
      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"
```

**Verification:**
- [ ] S3 bucket created and public
- [ ] CloudFront distribution configured
- [ ] SSL certificate installed
- [ ] Custom domain working
- [ ] Cache invalidation working

**If This Fails:**
→ Check IAM permissions for S3 and CloudFront
→ Verify bucket policy allows public access
→ Ensure CloudFront origin is correct
→ Check DNS propagation for custom domains

---

### Step 6: Set Up Continuous Deployment

**What:** Automate deployments on every push

**How:**

**Complete CI/CD Pipeline (.github/workflows/ci-cd.yml):**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '18'

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linter
        run: npm run lint
      
      - name: Type check
        run: npm run type-check
      
      - name: Run tests
        run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/

  deploy-preview:
    name: Deploy Preview
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v3
      
      - name: Download build
        uses: actions/download-artifact@v3
        with:
          name: dist
          path: dist/
      
      - name: Deploy to Vercel Preview
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  deploy-production:
    name: Deploy Production
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: production
      url: https://myapp.com
    steps:
      - uses: actions/checkout@v3
      
      - name: Download build
        uses: actions/download-artifact@v3
        with:
          name: dist
          path: dist/
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
      
      - name: Notify Slack
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "✅ Deployment to production successful!"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

**Branch Protection Rules:**
```markdown
## Required Status Checks
- ✅ Test
- ✅ Build
- ✅ Lighthouse Performance > 90

## Required Reviews
- 1 approval required
- Dismiss stale reviews on new commits

## Branch Restrictions
- main: Protected
- develop: Protected
```

**Verification:**
- [ ] CI runs on every push
- [ ] Tests must pass before merge
- [ ] Preview deployments automatic
- [ ] Production deploys on merge to main
- [ ] Notifications working

**If This Fails:**
→ Check GitHub Actions logs for specific errors
→ Verify all secrets are set in repository settings
→ Ensure branch protection rules configured
→ Test workflow locally with act

---

### Step 7: Monitor and Debug Deployments

**What:** Set up monitoring and error tracking

**How:**

**Sentry Integration:**
```bash
npm install @sentry/react
```

```typescript
// src/main.tsx
import * as Sentry from '@sentry/react';

if (import.meta.env.PROD) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.VITE_ENVIRONMENT,
    integrations: [
      new Sentry.BrowserTracing(),
      new Sentry.Replay(),
    ],
    tracesSampleRate: 0.1,
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
  });
}

// Wrap app with Sentry
const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(
  <Sentry.ErrorBoundary fallback={ErrorFallback}>
    <App />
  </Sentry.ErrorBoundary>
);
```

**Source Map Upload:**
```yaml
# In CI/CD pipeline
- name: Upload source maps to Sentry
  run: |
    npx @sentry/cli releases new ${{ github.sha }}
    npx @sentry/cli releases files ${{ github.sha }} upload-sourcemaps ./dist
    npx @sentry/cli releases finalize ${{ github.sha }}
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: your-org
    SENTRY_PROJECT: your-project
```

**Analytics Integration:**
```typescript
// src/analytics.ts
export function initAnalytics() {
  if (import.meta.env.PROD) {
    // Google Analytics
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${config.analyticsId}`;
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    function gtag(...args: any[]) {
      window.dataLayer.push(args);
    }
    gtag('js', new Date());
    gtag('config', config.analyticsId);
  }
}

export function trackPageView(path: string) {
  if (window.gtag) {
    window.gtag('config', config.analyticsId, {
      page_path: path,
    });
  }
}
```

**Health Check Endpoint:**
```typescript
// public/_health
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Uptime Monitoring:**
```yaml
# .github/workflows/health-check.yml
name: Health Check

on:
  schedule:
    - cron: '*/15 * * * *' # Every 15 minutes

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check production health
        run: |
          response=$(curl -s -o /dev/null -w "%{http_code}" https://myapp.com/_health)
          if [ $response != 200 ]; then
            curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
              -H 'Content-Type: application/json' \
              -d '{"text":"🚨 Production health check failed!"}'
            exit 1
          fi
```

**Verification:**
- [ ] Error tracking active
- [ ] Source maps uploaded
- [ ] Analytics tracking
- [ ] Health checks running
- [ ] Alerts configured

**If This Fails:**
→ Check Sentry DSN is correct
→ Verify source maps generated during build
→ Test health endpoint returns 200
→ Ensure webhook URLs are valid

---

### Step 8: Optimize Cache and CDN

**What:** Configure caching for optimal performance

**How:**

**Cache Headers Configuration:**
```typescript
// vercel.json
{
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=0, must-revalidate"
        }
      ]
    }
  ]
}
```

**Service Worker for Offline Support:**
```typescript
// src/serviceWorkerRegistration.ts
export function register() {
  if ('serviceWorker' in navigator && import.meta.env.PROD) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js')
        .then(registration => {
          console.log('SW registered:', registration);
        })
        .catch(error => {
          console.log('SW registration failed:', error);
        });
    });
  }
}
```

**Workbox Configuration:**
```javascript
// vite.config.ts - Add PWA plugin
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
      manifest: {
        name: 'My App',
        short_name: 'App',
        description: 'My awesome app',
        theme_color: '#ffffff',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
      workbox: {
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.example\.com\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24, // 24 hours
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
        ],
      },
    }),
  ],
});
```

**Verification:**
- [ ] Static assets cached correctly
- [ ] HTML not cached (or short TTL)
- [ ] Service worker registered
- [ ] Offline mode working
- [ ] Cache invalidation on deploy

**If This Fails:**
→ Check cache headers in Network tab
→ Clear browser cache and test
→ Verify service worker in DevTools
→ Test offline mode with DevTools

---

## Verification Checklist

After completing this workflow:

- [ ] Production build optimized
- [ ] Environment variables configured
- [ ] Deployment automated via CI/CD
- [ ] Custom domain configured with SSL
- [ ] Error tracking active
- [ ] Analytics implemented
- [ ] Health checks running
- [ ] Cache strategy optimized
- [ ] Source maps uploaded
- [ ] Preview deployments working
- [ ] Rollback procedure documented
- [ ] Monitoring and alerts set up

---

## Common Issues & Solutions

### Issue: Build Fails in Production

**Symptoms:**
- Works locally, fails in CI
- Type errors in build
- Missing dependencies

**Solution:**
```bash
# Test production build locally
NODE_ENV=production npm run build

# Check for type errors
npm run type-check

# Verify all dependencies in package.json
npm ci

# Check for platform-specific issues
rm -rf node_modules package-lock.json
npm install
```

**Prevention:**
- Use `npm ci` instead of `npm install` in CI
- Run production builds locally before pushing
- Keep dependencies up to date
- Use same Node version locally and in CI

---

### Issue: Environment Variables Not Working

**Symptoms:**
- Variables undefined in production
- API calls failing
- Features not working

**Solution:**
```typescript
// 1. Check variable naming (must have prefix)
// ❌ API_URL
// ✅ VITE_API_URL (Vite)
// ✅ REACT_APP_API_URL (CRA)

// 2. Verify in platform dashboard
// Vercel: Project Settings > Environment Variables
// Netlify: Site Settings > Environment Variables

// 3. Restart build after adding variables

// 4. Use validation
if (!import.meta.env.VITE_API_URL) {
  throw new Error('VITE_API_URL not configured');
}
```

**Prevention:**
- Document all required env vars in .env.example
- Add validation on app startup
- Use TypeScript for env config

---

## Best Practices

### DO:
✅ Use semantic versioning for releases
✅ Enable compression (gzip/brotli)
✅ Set up proper caching headers
✅ Monitor production errors with Sentry
✅ Implement health checks
✅ Use preview deployments for testing
✅ Keep dependencies updated
✅ Generate and upload source maps
✅ Set up automated tests in CI
✅ Use environment-specific configs
✅ Document deployment process
✅ Have rollback plan ready

### DON'T:
❌ Commit secrets or API keys
❌ Skip testing before deploying
❌ Deploy directly to production
❌ Ignore build warnings
❌ Use development builds in production
❌ Skip source maps
❌ Forget to invalidate CDN cache
❌ Deploy without backing up
❌ Ignore monitoring alerts
❌ Use insecure dependencies
❌ Deploy on Fridays 😉

---

## Related Workflows

**Prerequisites:**
- [react_component_creation.md](./react_component_creation.md) - App structure
- [performance_optimization.md](./performance_optimization.md) - Build optimization

**Next Steps:**
- [../devops/application_monitoring_setup.md](../devops/application_monitoring_setup.md) - Production monitoring
- [../devops/cicd_pipeline_setup.md](../devops/cicd_pipeline_setup.md) - Advanced CI/CD

**Related:**
- [e2e_testing_workflow.md](./e2e_testing_workflow.md) - Testing before deploy
- [../security/secret_management_solo.md](../security/secret_management_solo.md) - Managing secrets

---

## Tags
`frontend development` `deployment` `ci-cd` `vercel` `netlify` `aws` `build` `production` `devops`
