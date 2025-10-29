# E2E Testing Workflow

**ID:** fro-005  
**Category:** Frontend Development  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 45-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** End-to-end testing workflow using Playwright or Cypress to test complete user flows

**Why:** E2E tests verify that your application works correctly from the user's perspective, catching integration issues that unit tests miss

**When to use:**
- Setting up E2E testing infrastructure
- Writing tests for critical user journeys
- Adding test coverage for new features
- Debugging flaky E2E tests
- Setting up CI/CD integration for E2E tests

---

## Prerequisites

**Required:**
- [ ] React application with routing
- [ ] Node.js 16+ and npm/yarn
- [ ] Basic understanding of async/await
- [ ] Running development or staging environment

**Check before starting:**
```bash
# Verify Node version
node --version  # Should be 16+

# Check if app runs locally
npm run dev

# Verify you can access the app
curl http://localhost:3000
```

---

## Implementation Steps

### Step 1: Choose and Install E2E Testing Framework

**What:** Select between Playwright (recommended) or Cypress and install dependencies

**How:**

**Option A: Playwright (Recommended for modern apps)**
```bash
# Install Playwright
npm install -D @playwright/test

# Install browsers
npx playwright install

# Initialize Playwright config
npx playwright init
```

**Option B: Cypress (Good for React-specific features)**
```bash
# Install Cypress
npm install -D cypress

# Open Cypress for first time setup
npx cypress open
```

**Playwright Configuration (playwright.config.ts):**
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // Mobile viewports
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

**Cypress Configuration (cypress.config.ts):**
```typescript
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    video: false,
    screenshotOnRunFailure: true,
    
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
```

**Verification:**
- [ ] Framework installed successfully
- [ ] Config file created
- [ ] Browsers installed (Playwright) or Cypress opens

**If This Fails:**
→ Check Node.js version compatibility
→ Clear node_modules and reinstall: `rm -rf node_modules package-lock.json && npm install`
→ For Playwright browser issues: `npx playwright install --with-deps`

---

### Step 2: Set Up Test Directory Structure

**What:** Organize your E2E tests with a clear structure

**How:**

**Playwright Structure:**
```bash
# Create directory structure
mkdir -p e2e/{auth,dashboard,checkout}
mkdir -p e2e/fixtures
mkdir -p e2e/helpers
```

```
e2e/
├── auth/
│   ├── login.spec.ts
│   └── signup.spec.ts
├── dashboard/
│   ├── user-profile.spec.ts
│   └── settings.spec.ts
├── checkout/
│   └── purchase-flow.spec.ts
├── fixtures/
│   ├── users.json
│   └── products.json
└── helpers/
    ├── auth.ts
    └── api.ts
```

**Cypress Structure:**
```bash
mkdir -p cypress/{e2e,fixtures,support}
```

```
cypress/
├── e2e/
│   ├── auth/
│   ├── dashboard/
│   └── checkout/
├── fixtures/
│   ├── users.json
│   └── products.json
└── support/
    ├── commands.ts
    └── e2e.ts
```

**Create Test Fixtures (e2e/fixtures/users.json):**
```json
{
  "validUser": {
    "email": "test@example.com",
    "password": "Test123!@#",
    "name": "Test User"
  },
  "adminUser": {
    "email": "admin@example.com",
    "password": "Admin123!@#",
    "name": "Admin User"
  }
}
```

**Verification:**
- [ ] Directory structure created
- [ ] Fixture files created
- [ ] Helper files ready for shared utilities

**If This Fails:**
→ Check file permissions
→ Ensure you're in the project root directory

---

### Step 3: Write Your First E2E Test

**What:** Create a simple test to verify the testing infrastructure works

**How:**

**Playwright Example (e2e/auth/login.spec.ts):**
```typescript
import { test, expect } from '@playwright/test';
import users from '../fixtures/users.json';

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should display login form', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /login/i })).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.getByRole('button', { name: /sign in/i }).click();
    
    await expect(page.getByText(/email is required/i)).toBeVisible();
    await expect(page.getByText(/password is required/i)).toBeVisible();
  });

  test('should successfully login with valid credentials', async ({ page }) => {
    // Fill in login form
    await page.getByLabel(/email/i).fill(users.validUser.email);
    await page.getByLabel(/password/i).fill(users.validUser.password);
    
    // Submit form
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText(/welcome back/i)).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.getByLabel(/email/i).fill('wrong@example.com');
    await page.getByLabel(/password/i).fill('WrongPassword123');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    await expect(page.getByText(/invalid credentials/i)).toBeVisible();
  });
});
```

**Cypress Example (cypress/e2e/auth/login.cy.ts):**
```typescript
import users from '../../fixtures/users.json';

describe('Login Flow', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('should display login form', () => {
    cy.findByRole('heading', { name: /login/i }).should('be.visible');
    cy.findByLabelText(/email/i).should('be.visible');
    cy.findByLabelText(/password/i).should('be.visible');
    cy.findByRole('button', { name: /sign in/i }).should('be.visible');
  });

  it('should show validation errors for empty fields', () => {
    cy.findByRole('button', { name: /sign in/i }).click();
    cy.findByText(/email is required/i).should('be.visible');
    cy.findByText(/password is required/i).should('be.visible');
  });

  it('should successfully login with valid credentials', () => {
    cy.findByLabelText(/email/i).type(users.validUser.email);
    cy.findByLabelText(/password/i).type(users.validUser.password);
    cy.findByRole('button', { name: /sign in/i }).click();
    
    cy.url().should('include', '/dashboard');
    cy.findByText(/welcome back/i).should('be.visible');
  });

  it('should show error for invalid credentials', () => {
    cy.findByLabelText(/email/i).type('wrong@example.com');
    cy.findByLabelText(/password/i).type('WrongPassword123');
    cy.findByRole('button', { name: /sign in/i }).click();
    
    cy.findByText(/invalid credentials/i).should('be.visible');
  });
});
```

**Verification:**
- [ ] Test file created
- [ ] Tests use proper selectors (roles, labels)
- [ ] Assertions are clear and descriptive

**If This Fails:**
→ Verify app is running on correct port
→ Check selector syntax matches your UI
→ Use Playwright/Cypress inspector to debug selectors

---

### Step 4: Create Reusable Test Helpers

**What:** Extract common patterns into helper functions to reduce duplication

**How:**

**Playwright Helpers (e2e/helpers/auth.ts):**
```typescript
import { Page } from '@playwright/test';
import users from '../fixtures/users.json';

export async function login(page: Page, userType: 'valid' | 'admin' = 'valid') {
  const user = userType === 'admin' ? users.adminUser : users.validUser;
  
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(user.email);
  await page.getByLabel(/password/i).fill(user.password);
  await page.getByRole('button', { name: /sign in/i }).click();
  
  // Wait for navigation
  await page.waitForURL('/dashboard');
}

export async function logout(page: Page) {
  await page.getByRole('button', { name: /profile/i }).click();
  await page.getByRole('menuitem', { name: /logout/i }).click();
}

export async function setupAuthenticatedSession(page: Page) {
  // Use API to set up auth faster than UI
  const response = await page.request.post('/api/auth/login', {
    data: {
      email: users.validUser.email,
      password: users.validUser.password,
    },
  });
  
  const { token } = await response.json();
  
  // Set auth cookie/localStorage
  await page.context().addCookies([{
    name: 'auth_token',
    value: token,
    domain: 'localhost',
    path: '/',
  }]);
}
```

**Cypress Custom Commands (cypress/support/commands.ts):**
```typescript
import users from '../fixtures/users.json';

declare global {
  namespace Cypress {
    interface Chainable {
      login(userType?: 'valid' | 'admin'): Chainable<void>;
      logout(): Chainable<void>;
      setupAuthSession(): Chainable<void>;
    }
  }
}

Cypress.Commands.add('login', (userType = 'valid') => {
  const user = userType === 'admin' ? users.adminUser : users.validUser;
  
  cy.visit('/login');
  cy.findByLabelText(/email/i).type(user.email);
  cy.findByLabelText(/password/i).type(user.password);
  cy.findByRole('button', { name: /sign in/i }).click();
  cy.url().should('include', '/dashboard');
});

Cypress.Commands.add('logout', () => {
  cy.findByRole('button', { name: /profile/i }).click();
  cy.findByRole('menuitem', { name: /logout/i }).click();
});

Cypress.Commands.add('setupAuthSession', () => {
  cy.request('POST', '/api/auth/login', {
    email: users.validUser.email,
    password: users.validUser.password,
  }).then((response) => {
    cy.setCookie('auth_token', response.body.token);
  });
});
```

**Usage in Tests:**
```typescript
// Playwright
import { test, expect } from '@playwright/test';
import { login } from '../helpers/auth';

test('user can view their profile', async ({ page }) => {
  await login(page);
  await page.goto('/profile');
  await expect(page.getByRole('heading', { name: /my profile/i })).toBeVisible();
});

// Cypress
it('user can view their profile', () => {
  cy.login();
  cy.visit('/profile');
  cy.findByRole('heading', { name: /my profile/i }).should('be.visible');
});
```

**Verification:**
- [ ] Helper functions created
- [ ] Functions reduce test duplication
- [ ] Custom commands registered (Cypress)

**If This Fails:**
→ Check import paths are correct
→ Ensure types are properly declared (Cypress commands)
→ Verify helper functions are exported

---

### Step 5: Test Complex User Flows

**What:** Write tests for multi-step user journeys like checkout or onboarding

**How:**

**E-commerce Checkout Flow (e2e/checkout/purchase-flow.spec.ts):**
```typescript
import { test, expect } from '@playwright/test';
import { setupAuthenticatedSession } from '../helpers/auth';

test.describe('Checkout Flow', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticatedSession(page);
  });

  test('complete purchase with valid payment', async ({ page }) => {
    // Step 1: Browse and add product to cart
    await page.goto('/products');
    await page.getByRole('link', { name: /premium headphones/i }).click();
    
    await expect(page.getByRole('heading', { name: /premium headphones/i })).toBeVisible();
    await page.getByRole('button', { name: /add to cart/i }).click();
    
    // Verify cart badge updates
    await expect(page.getByTestId('cart-count')).toHaveText('1');
    
    // Step 2: Go to cart and proceed to checkout
    await page.getByRole('link', { name: /cart/i }).click();
    await expect(page.getByText(/premium headphones/i)).toBeVisible();
    await page.getByRole('button', { name: /proceed to checkout/i }).click();
    
    // Step 3: Fill shipping information
    await page.getByLabel(/full name/i).fill('John Doe');
    await page.getByLabel(/address/i).fill('123 Main St');
    await page.getByLabel(/city/i).fill('San Francisco');
    await page.getByLabel(/state/i).selectOption('CA');
    await page.getByLabel(/zip code/i).fill('94102');
    await page.getByRole('button', { name: /continue to payment/i }).click();
    
    // Step 4: Enter payment details
    await page.getByLabel(/card number/i).fill('4242424242424242');
    await page.getByLabel(/expiry/i).fill('12/25');
    await page.getByLabel(/cvc/i).fill('123');
    
    // Step 5: Place order
    await page.getByRole('button', { name: /place order/i }).click();
    
    // Step 6: Verify order confirmation
    await expect(page).toHaveURL(/\/order\/[a-z0-9-]+/);
    await expect(page.getByRole('heading', { name: /order confirmed/i })).toBeVisible();
    await expect(page.getByText(/order number:/i)).toBeVisible();
    
    // Verify order details
    await expect(page.getByText(/premium headphones/i)).toBeVisible();
    await expect(page.getByText(/john doe/i)).toBeVisible();
    await expect(page.getByText(/123 main st/i)).toBeVisible();
  });

  test('cannot checkout with empty cart', async ({ page }) => {
    await page.goto('/cart');
    await expect(page.getByText(/your cart is empty/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /proceed to checkout/i })).toBeDisabled();
  });

  test('validate payment form errors', async ({ page }) => {
    // Add item and go to checkout
    await page.goto('/products');
    await page.getByRole('link', { name: /premium headphones/i }).click();
    await page.getByRole('button', { name: /add to cart/i }).click();
    await page.getByRole('link', { name: /cart/i }).click();
    await page.getByRole('button', { name: /proceed to checkout/i }).click();
    
    // Fill shipping and go to payment
    await page.getByLabel(/full name/i).fill('John Doe');
    await page.getByLabel(/address/i).fill('123 Main St');
    await page.getByLabel(/city/i).fill('San Francisco');
    await page.getByLabel(/state/i).selectOption('CA');
    await page.getByLabel(/zip code/i).fill('94102');
    await page.getByRole('button', { name: /continue to payment/i }).click();
    
    // Try to submit without payment details
    await page.getByRole('button', { name: /place order/i }).click();
    
    await expect(page.getByText(/card number is required/i)).toBeVisible();
    await expect(page.getByText(/expiry date is required/i)).toBeVisible();
    await expect(page.getByText(/cvc is required/i)).toBeVisible();
  });
});
```

**Verification:**
- [ ] Multi-step flow tests all stages
- [ ] Each step has assertions
- [ ] Error cases are tested
- [ ] Tests are deterministic (not flaky)

**If This Fails:**
→ Add explicit waits for async operations
→ Use proper selectors (prefer roles over classes/ids)
→ Check for race conditions with network requests

---

### Step 6: Handle Common Testing Patterns

**What:** Implement strategies for dealing with async operations, API mocking, and file uploads

**How:**

**Waiting for API Responses (Playwright):**
```typescript
test('wait for API response', async ({ page }) => {
  // Wait for specific API call
  const responsePromise = page.waitForResponse(
    response => response.url().includes('/api/users') && response.status() === 200
  );
  
  await page.goto('/dashboard');
  const response = await responsePromise;
  const data = await response.json();
  
  expect(data.users).toHaveLength(10);
});

// Intercept and modify API response
test('mock API response', async ({ page }) => {
  await page.route('/api/products', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        products: [
          { id: 1, name: 'Test Product', price: 99.99 }
        ]
      })
    });
  });
  
  await page.goto('/products');
  await expect(page.getByText('Test Product')).toBeVisible();
});
```

**File Upload:**
```typescript
test('upload profile picture', async ({ page }) => {
  await page.goto('/profile/edit');
  
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('./e2e/fixtures/avatar.png');
  
  await page.getByRole('button', { name: /save/i }).click();
  
  // Verify upload success
  await expect(page.getByRole('img', { name: /profile picture/i }))
    .toHaveAttribute('src', /avatar/);
});
```

**Testing Drag and Drop:**
```typescript
test('reorder items with drag and drop', async ({ page }) => {
  await page.goto('/dashboard');
  
  const firstItem = page.getByTestId('item-1');
  const secondItem = page.getByTestId('item-2');
  
  // Drag first item to second position
  await firstItem.dragTo(secondItem);
  
  // Verify new order
  const items = await page.getByTestId(/^item-/).all();
  await expect(items[0]).toHaveAttribute('data-id', '2');
  await expect(items[1]).toHaveAttribute('data-id', '1');
});
```

**Testing with Different Viewports:**
```typescript
test('responsive navigation menu', async ({ page }) => {
  // Desktop view
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.goto('/');
  await expect(page.getByRole('navigation')).toBeVisible();
  await expect(page.getByRole('button', { name: /menu/i })).not.toBeVisible();
  
  // Mobile view
  await page.setViewportSize({ width: 375, height: 667 });
  await expect(page.getByRole('navigation')).not.toBeVisible();
  await expect(page.getByRole('button', { name: /menu/i })).toBeVisible();
  
  // Open mobile menu
  await page.getByRole('button', { name: /menu/i }).click();
  await expect(page.getByRole('navigation')).toBeVisible();
});
```

**Verification:**
- [ ] Async operations handled properly
- [ ] API responses mocked when needed
- [ ] File uploads tested
- [ ] Responsive behavior verified

**If This Fails:**
→ Increase timeout for slow operations: `{ timeout: 10000 }`
→ Use network idle for SPA navigation: `await page.waitForLoadState('networkidle')`
→ Check browser console for errors

---

### Step 7: Integrate E2E Tests with CI/CD

**What:** Run E2E tests automatically in your CI pipeline

**How:**

**GitHub Actions Workflow (.github/workflows/e2e-tests.yml):**
```yaml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
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
      
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      
      - name: Run E2E tests
        run: npm run test:e2e
        env:
          CI: true
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

**Package.json Scripts:**
```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:chromium": "playwright test --project=chromium"
  }
}
```

**Docker Setup for Consistent Test Environment:**
```dockerfile
# Dockerfile.e2e
FROM mcr.microsoft.com/playwright:v1.40.0-jammy

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

CMD ["npm", "run", "test:e2e"]
```

**docker-compose.yml for E2E testing:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=test
    command: npm run dev
    
  e2e-tests:
    build:
      context: .
      dockerfile: Dockerfile.e2e
    depends_on:
      - app
    environment:
      - BASE_URL=http://app:3000
    volumes:
      - ./playwright-report:/app/playwright-report
```

**Verification:**
- [ ] CI workflow file created
- [ ] Tests run successfully in CI
- [ ] Test reports uploaded as artifacts
- [ ] Failures notify the team

**If This Fails:**
→ Check browser dependencies are installed
→ Verify environment variables are set correctly
→ Ensure app starts before tests run
→ Review test artifacts for failure details

---

### Step 8: Debug and Maintain E2E Tests

**What:** Strategies for debugging flaky tests and keeping your test suite healthy

**How:**

**Debug Playwright Tests:**
```bash
# Run in debug mode with inspector
npx playwright test --debug

# Run with headed browser
npx playwright test --headed

# Run specific test file
npx playwright test e2e/auth/login.spec.ts

# Generate trace for failed tests
npx playwright test --trace on

# View trace
npx playwright show-trace trace.zip
```

**Debug Cypress Tests:**
```bash
# Open Cypress Test Runner
npx cypress open

# Run in headless mode with video
npx cypress run

# Run specific test file
npx cypress run --spec "cypress/e2e/auth/login.cy.ts"
```

**Reduce Flaky Tests:**
```typescript
// ❌ BAD: Brittle fixed timeout
await page.waitForTimeout(5000);

// ✅ GOOD: Wait for specific condition
await page.waitForSelector('[data-testid="results"]');
await page.waitForLoadState('networkidle');

// ✅ GOOD: Auto-waiting with retry
await expect(page.getByText('Success')).toBeVisible({ timeout: 10000 });

// ❌ BAD: Fragile CSS selector
await page.locator('.btn-primary.submit-form').click();

// ✅ GOOD: Semantic selector
await page.getByRole('button', { name: /submit/i }).click();

// ✅ GOOD: Test ID for complex cases
await page.getByTestId('submit-form-button').click();
```

**Test Organization Best Practices:**
```typescript
// Use describe blocks for grouping
test.describe('User Profile', () => {
  test.describe('View Mode', () => {
    test('displays user information', async ({ page }) => {
      // test code
    });
  });
  
  test.describe('Edit Mode', () => {
    test('allows updating profile', async ({ page }) => {
      // test code
    });
  });
});

// Use beforeEach for common setup
test.describe('Dashboard Tests', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticatedSession(page);
    await page.goto('/dashboard');
  });
  
  test('test 1', async ({ page }) => {
    // Already authenticated and on dashboard
  });
});

// Tag tests for selective running
test('critical checkout flow @smoke @critical', async ({ page }) => {
  // test code
});

// Run: npx playwright test --grep @smoke
```

**Monitor Test Health:**
```typescript
// Add test metadata
test('user login', {
  tag: '@auth',
  annotation: {
    type: 'issue',
    description: 'https://github.com/org/repo/issues/123'
  }
}, async ({ page }) => {
  // test code
});

// Track test duration
test.describe('Performance Tests', () => {
  test('page loads quickly', async ({ page }) => {
    const start = Date.now();
    await page.goto('/');
    const duration = Date.now() - start;
    
    expect(duration).toBeLessThan(2000);
  });
});
```

**Verification:**
- [ ] Debug tools configured
- [ ] Flaky tests refactored
- [ ] Tests are well-organized
- [ ] Test health monitored

**If This Fails:**
→ Use trace viewer to see exactly what happened
→ Add explicit waits for dynamic content
→ Check for race conditions with network requests
→ Review test reports for patterns in failures

---

## Verification Checklist

After completing this workflow:

- [ ] E2E testing framework installed and configured
- [ ] Test directory structure organized
- [ ] Basic and complex user flows tested
- [ ] Reusable helpers created
- [ ] CI/CD integration working
- [ ] Debug tools set up
- [ ] Tests passing consistently (>95% pass rate)
- [ ] Test coverage for critical user paths

---

## Common Issues & Solutions

### Issue: Tests are Flaky and Fail Randomly

**Symptoms:**
- Tests pass locally but fail in CI
- Same test fails intermittently
- Timeouts in CI environment

**Solution:**
```typescript
// 1. Add explicit waits
await page.waitForLoadState('networkidle');
await page.waitForSelector('[data-loaded="true"]');

// 2. Increase timeouts for CI
test.setTimeout(process.env.CI ? 60000 : 30000);

// 3. Add retries for flaky tests
test.describe.configure({ retries: 2 });

// 4. Use stable selectors
// ❌ await page.locator('.css-xyz-123').click()
// ✅ await page.getByRole('button', { name: 'Submit' }).click()

// 5. Wait for API calls to complete
await Promise.all([
  page.waitForResponse('/api/users'),
  page.click('#load-users')
]);
```

**Prevention:**
- Use semantic selectors (roles, labels)
- Avoid fixed timeouts
- Mock slow API endpoints
- Run tests in parallel to catch race conditions

---

### Issue: Tests are Too Slow

**Symptoms:**
- Test suite takes >10 minutes
- CI pipeline times out
- Developers avoid running E2E tests

**Solution:**
```typescript
// 1. Use API for setup instead of UI
test.beforeEach(async ({ page, request }) => {
  // ❌ SLOW: Log in via UI every test
  // await page.goto('/login');
  // await page.fill('[name="email"]', 'test@example.com');
  // await page.fill('[name="password"]', 'password');
  // await page.click('button[type="submit"]');
  
  // ✅ FAST: Use API to set up auth
  const response = await request.post('/api/auth/login', {
    data: { email: 'test@example.com', password: 'password' }
  });
  const { token } = await response.json();
  await page.context().addCookies([{
    name: 'auth_token',
    value: token,
    domain: 'localhost',
    path: '/'
  }]);
});

// 2. Run tests in parallel
// playwright.config.ts
export default defineConfig({
  workers: process.env.CI ? 2 : 4,
  fullyParallel: true,
});

// 3. Use test fixtures for shared state
import { test as base } from '@playwright/test';

const test = base.extend({
  authenticatedPage: async ({ page, request }, use) => {
    // Set up auth once
    const response = await request.post('/api/auth/login', {
      data: { email: 'test@example.com', password: 'password' }
    });
    const { token } = await response.json();
    await page.context().addCookies([{
      name: 'auth_token',
      value: token,
      domain: 'localhost',
      path: '/'
    }]);
    await use(page);
  },
});

// 4. Skip unnecessary tests
test.skip('slow animation test', async ({ page }) => {
  // Skip in CI
});
```

**Prevention:**
- Use API for test setup
- Run tests in parallel
- Mock external services
- Focus on critical paths, not every edge case

---

### Issue: Can't Find Elements with Selectors

**Symptoms:**
- `Element not found` errors
- Selectors work locally but not in CI
- Dynamic content not loaded

**Solution:**
```typescript
// Use Playwright's auto-waiting
await page.getByRole('button', { name: /submit/i }).click();

// For dynamic content
await page.waitForSelector('[data-testid="content-loaded"]');

// Use has: selector for nested elements
await page.locator('article').filter({ hasText: 'Breaking News' }).click();

// Debug selectors
await page.pause(); // Opens inspector
console.log(await page.content()); // See HTML

// Generate selectors
npx playwright codegen http://localhost:3000
```

**Prevention:**
- Use semantic HTML (proper roles, labels)
- Add data-testid for complex components
- Use getByRole, getByLabel, getByText
- Test with production-like data

---

### Issue: Tests Work Locally But Fail in CI

**Symptoms:**
- All tests pass on developer machine
- Random failures in CI
- Different behavior in CI

**Solution:**
```typescript
// 1. Use consistent viewport
test.use({ viewport: { width: 1280, height: 720 } });

// 2. Handle timezone differences
test.use({ timezoneId: 'America/New_York' });

// 3. Mock dates
test.beforeEach(({ page }) => {
  page.addInitScript(() => {
    Date.now = () => 1640000000000; // Fixed date
  });
});

// 4. Set base URL explicitly
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
  },
});

// 5. Take screenshots on failure
// playwright.config.ts
export default defineConfig({
  use: {
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
});
```

**Prevention:**
- Use Docker for consistent environments
- Mock external dependencies
- Set explicit viewport and locale
- Review CI logs and artifacts

---

## Best Practices

### DO:
✅ Use semantic selectors (roles, labels) over CSS classes
✅ Test user flows, not implementation details
✅ Keep tests independent and isolated
✅ Use page object models for complex pages
✅ Mock external APIs and slow services
✅ Run critical tests in CI on every PR
✅ Use auto-waiting instead of fixed timeouts
✅ Write descriptive test names and error messages
✅ Take screenshots/videos of failures
✅ Test responsive behavior across viewports
✅ Use fixtures for test data
✅ Parallelize tests for faster feedback

### DON'T:
❌ Use fragile CSS selectors (classes, IDs with random hashes)
❌ Test implementation details (component state, internal methods)
❌ Create tests that depend on other tests
❌ Use sleep() or fixed timeouts
❌ Test everything - focus on critical user paths
❌ Ignore flaky tests (fix them!)
❌ Commit sensitive data in fixtures
❌ Run E2E tests for unit test scenarios
❌ Skip CI integration
❌ Write tests without clear assertions
❌ Use production environment for tests
❌ Forget to clean up test data

---

## Related Workflows

**Prerequisites:**
- [react_component_creation.md](./react_component_creation.md) - Component structure
- [component_testing_strategy.md](./component_testing_strategy.md) - Unit testing setup

**Next Steps:**
- [build_deployment.md](./build_deployment.md) - Deploy with E2E tests
- [performance_optimization.md](./performance_optimization.md) - Performance testing

**Related:**
- [api_integration_patterns.md](./api_integration_patterns.md) - API mocking patterns
- [form_handling_validation.md](./form_handling_validation.md) - Form testing

---

## Tags
`frontend development` `testing` `e2e` `playwright` `cypress` `automation` `qa`
