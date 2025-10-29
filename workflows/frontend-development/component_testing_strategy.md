# Component Testing Strategy

**ID:** fro-004  
**Category:** Frontend Development  
**Priority:** HIGH  
**Complexity:** Medium  
**Estimated Time:** 30-60 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Comprehensive strategy for testing React components using modern testing tools and best practices

**Why:** 
- Catch bugs before they reach production
- Enable confident refactoring and feature additions
- Document component behavior through tests
- Improve code quality and maintainability
- Reduce manual testing effort
- Support continuous integration/deployment

**When to use:**
- Writing new React components
- Adding features to existing components
- Refactoring component code
- Fixing bugs (write test first)
- Setting up testing infrastructure
- Code review and quality assurance

---

## Prerequisites

**Required:**
- [ ] React project with TypeScript
- [ ] Understanding of component behavior
- [ ] Knowledge of testing fundamentals
- [ ] Familiarity with Jest and React Testing Library

**Check before starting:**
```bash
# Verify testing libraries
npm list @testing-library/react @testing-library/jest-dom jest

# Check test script exists
grep "test" package.json

# Run existing tests
npm test
```

---

## Implementation Steps

### Step 1: Setup Testing Environment

**What:** Configure Jest and React Testing Library for optimal testing

**How:**

```bash
# Install dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom
npm install --save-dev @testing-library/user-event
npm install --save-dev jest-environment-jsdom

# For React 18+
npm install --save-dev @testing-library/react@^14
```

**Configure Jest:**

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      tsconfig: {
        jsx: 'react',
      },
    }],
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.tsx',
  ],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

**Setup file:**

```typescript
// src/setupTests.ts
import '@testing-library/jest-dom';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
} as any;
```

**Verification:**
```bash
# Run tests
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

---

### Step 2: Write Basic Component Tests

**What:** Test component rendering, props, and basic interactions

**How:**

```typescript
// components/Button.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  // Test 1: Rendering
  it('renders with children', () => {
    render(<Button onClick={() => {}}>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  // Test 2: Props
  it('applies variant classes', () => {
    const { rerender } = render(
      <Button onClick={() => {}} variant="primary">Primary</Button>
    );
    expect(screen.getByRole('button')).toHaveClass('button--primary');

    rerender(<Button onClick={() => {}} variant="secondary">Secondary</Button>);
    expect(screen.getByRole('button')).toHaveClass('button--secondary');
  });

  // Test 3: User Interaction
  it('calls onClick when clicked', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick}>Click me</Button>);
    await user.click(screen.getByRole('button'));
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  // Test 4: Disabled State
  it('does not call onClick when disabled', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick} disabled>Click me</Button>);
    await user.click(screen.getByRole('button'));
    
    expect(handleClick).not.toHaveBeenCalled();
  });

  // Test 5: Accessibility
  it('has proper aria attributes when loading', () => {
    render(<Button onClick={() => {}} loading>Loading</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'true');
  });

  // Test 6: Custom aria-label
  it('uses custom aria-label', () => {
    render(
      <Button onClick={() => {}} ariaLabel="Close dialog">
        <span aria-hidden>×</span>
      </Button>
    );
    expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Close dialog');
  });
});
```

**Best practices for queries:**

```typescript
// ✅ Prefer accessible queries
screen.getByRole('button', { name: 'Submit' })
screen.getByLabelText('Email')
screen.getByPlaceholderText('Enter email')

// ⚠️ Use these sparingly
screen.getByTestId('custom-element')

// ❌ Avoid these (implementation details)
screen.getByClassName('button')
container.querySelector('.button')
```

---

### Step 3: Test Component State and Effects

**What:** Test stateful components and side effects

**How:**

```typescript
// components/Counter.test.tsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Counter } from './Counter';

describe('Counter', () => {
  it('starts at initial count', () => {
    render(<Counter initialCount={5} />);
    expect(screen.getByText('Count: 5')).toBeInTheDocument();
  });

  it('increments count when button clicked', async () => {
    const user = userEvent.setup();
    render(<Counter initialCount={0} />);
    
    await user.click(screen.getByRole('button', { name: 'Increment' }));
    expect(screen.getByText('Count: 1')).toBeInTheDocument();
    
    await user.click(screen.getByRole('button', { name: 'Increment' }));
    expect(screen.getByText('Count: 2')).toBeInTheDocument();
  });

  it('decrements count when button clicked', async () => {
    const user = userEvent.setup();
    render(<Counter initialCount={5} />);
    
    await user.click(screen.getByRole('button', { name: 'Decrement' }));
    expect(screen.getByText('Count: 4')).toBeInTheDocument();
  });

  it('calls onChange callback when count changes', async () => {
    const handleChange = jest.fn();
    const user = userEvent.setup();
    
    render(<Counter initialCount={0} onChange={handleChange} />);
    await user.click(screen.getByRole('button', { name: 'Increment' }));
    
    expect(handleChange).toHaveBeenCalledWith(1);
  });
});

// Testing useEffect
describe('DataFetcher', () => {
  it('fetches and displays data on mount', async () => {
    // Mock fetch
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ name: 'Test User' }),
      })
    ) as jest.Mock;

    render(<DataFetcher userId="123" />);

    // Loading state
    expect(screen.getByText('Loading...')).toBeInTheDocument();

    // Wait for data
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
    });

    expect(fetch).toHaveBeenCalledWith('/api/users/123');
  });

  it('displays error when fetch fails', async () => {
    global.fetch = jest.fn(() =>
      Promise.reject(new Error('API Error'))
    ) as jest.Mock;

    render(<DataFetcher userId="123" />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

---

### Step 4: Test Forms and User Input

**What:** Test form validation, submission, and complex user interactions

**How:**

```typescript
// components/LoginForm.test.tsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('submits form with valid data', async () => {
    const handleSubmit = jest.fn();
    const user = userEvent.setup();
    
    render(<LoginForm onSubmit={handleSubmit} />);

    // Fill form
    await user.type(screen.getByLabelText('Email'), 'user@example.com');
    await user.type(screen.getByLabelText('Password'), 'password123');
    
    // Submit
    await user.click(screen.getByRole('button', { name: 'Log In' }));

    // Verify submission
    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 'password123',
      });
    });
  });

  it('shows validation errors for empty fields', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={jest.fn()} />);

    // Submit empty form
    await user.click(screen.getByRole('button', { name: 'Log In' }));

    // Check errors
    expect(await screen.findByText('Email is required')).toBeInTheDocument();
    expect(await screen.findByText('Password is required')).toBeInTheDocument();
  });

  it('shows validation error for invalid email', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={jest.fn()} />);

    await user.type(screen.getByLabelText('Email'), 'invalid-email');
    await user.tab(); // Trigger blur validation

    expect(await screen.findByText('Invalid email address')).toBeInTheDocument();
  });

  it('disables submit button during submission', async () => {
    const handleSubmit = jest.fn(() => new Promise(resolve => setTimeout(resolve, 100)));
    const user = userEvent.setup();
    
    render(<LoginForm onSubmit={handleSubmit} />);

    await user.type(screen.getByLabelText('Email'), 'user@example.com');
    await user.type(screen.getByLabelText('Password'), 'password123');
    
    const submitButton = screen.getByRole('button', { name: 'Log In' });
    await user.click(submitButton);

    expect(submitButton).toBeDisabled();
    expect(screen.getByText('Logging in...')).toBeInTheDocument();
  });
});
```

---

### Step 5: Test Async Operations and API Calls

**What:** Test components that fetch data or interact with APIs

**How:**

```typescript
// components/UserList.test.tsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserList } from './UserList';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Helper to wrap with providers
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('UserList', () => {
  beforeEach(() => {
    // Mock fetch
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('displays loading state initially', () => {
    (global.fetch as jest.Mock).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<UserList />, { wrapper: createWrapper() });
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('displays users after successful fetch', async () => {
    const mockUsers = [
      { id: '1', name: 'Alice', email: 'alice@example.com' },
      { id: '2', name: 'Bob', email: 'bob@example.com' },
    ];

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: mockUsers }),
    });

    render(<UserList />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
    });
  });

  it('displays error message on fetch failure', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(
      new Error('Network error')
    );

    render(<UserList />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('deletes user when delete button clicked', async () => {
    const mockUsers = [
      { id: '1', name: 'Alice', email: 'alice@example.com' },
    ];

    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockUsers }),
      })
      .mockResolvedValueOnce({ ok: true }); // Delete request

    const user = userEvent.setup();
    render(<UserList />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
    });

    // Confirm delete
    window.confirm = jest.fn(() => true);
    await user.click(screen.getByRole('button', { name: 'Delete' }));

    await waitFor(() => {
      expect(screen.queryByText('Alice')).not.toBeInTheDocument();
    });
  });
});
```

---

### Step 6: Test Context and Custom Hooks

**What:** Test components that use Context or custom hooks

**How:**

```typescript
// hooks/useAuth.test.tsx
import { renderHook, act, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../contexts/AuthContext';

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
);

describe('useAuth', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    localStorage.clear();
  });

  it('initializes with no user', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('logs in user successfully', async () => {
    const mockUser = {
      id: '1',
      name: 'Test User',
      email: 'test@example.com',
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        user: mockUser,
        access_token: 'mock-token',
      }),
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(localStorage.getItem('auth_token')).toBe('mock-token');
  });

  it('logs out user', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    // Set initial authenticated state
    await act(async () => {
      // ... login first
    });

    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(localStorage.getItem('auth_token')).toBeNull();
  });
});

// Testing components with context
describe('UserProfile with Auth Context', () => {
  it('displays user info when authenticated', () => {
    const mockUser = { name: 'Test User', email: 'test@example.com' };
    
    render(
      <AuthProvider initialUser={mockUser}>
        <UserProfile />
      </AuthProvider>
    );

    expect(screen.getByText('Test User')).toBeInTheDocument();
  });

  it('redirects to login when not authenticated', () => {
    const mockNavigate = jest.fn();
    jest.mock('react-router-dom', () => ({
      useNavigate: () => mockNavigate,
    }));

    render(
      <AuthProvider>
        <UserProfile />
      </AuthProvider>
    );

    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });
});
```

---

### Step 7: Measure and Improve Coverage

**What:** Track test coverage and fill gaps

**How:**

```bash
# Generate coverage report
npm test -- --coverage --watchAll=false

# Coverage report in terminal:
# -------------------------|---------|----------|---------|---------|
# File                     | % Stmts | % Branch | % Funcs | % Lines |
# -------------------------|---------|----------|---------|---------|
# All files                |   85.71 |    83.33 |   88.88 |   85.71 |
#  Button.tsx              |     100 |      100 |     100 |     100 |
#  LoginForm.tsx           |   66.66 |       50 |      75 |   66.66 |
# -------------------------|---------|----------|---------|---------|

# Open HTML coverage report
open coverage/lcov-report/index.html
```

**Identify untested code:**

```typescript
// Coverage shows LoginForm.tsx needs more tests
// Look for:
// - Red lines (not executed)
// - Yellow lines (partial branch coverage)

// Add missing tests
it('shows forgot password link', () => {
  render(<LoginForm onSubmit={jest.fn()} />);
  expect(screen.getByText('Forgot password?')).toBeInTheDocument();
});

it('toggles password visibility', async () => {
  const user = userEvent.setup();
  render(<LoginForm onSubmit={jest.fn()} />);
  
  const passwordInput = screen.getByLabelText('Password');
  expect(passwordInput).toHaveAttribute('type', 'password');
  
  await user.click(screen.getByLabelText('Show password'));
  expect(passwordInput).toHaveAttribute('type', 'text');
});
```

**Verification:**
- [ ] Coverage report generated
- [ ] Coverage meets thresholds (80%+)
- [ ] Critical paths tested
- [ ] Edge cases covered

---

## Verification Checklist

After implementing component testing:

- [ ] All components have test files
- [ ] Tests pass consistently
- [ ] Coverage meets targets (80%+)
- [ ] Tests run fast (< 10 seconds for 100 tests)
- [ ] No flaky tests
- [ ] Tests are readable and maintainable
- [ ] Mocks are properly cleaned up
- [ ] Accessibility tested
- [ ] Error states covered
- [ ] Loading states tested

---

## Common Issues & Solutions

### Issue: "Unable to find element"

**Solution:**
```typescript
// ❌ Wrong: Element not rendered yet
expect(screen.getByText('Success')).toBeInTheDocument();

// ✅ Correct: Wait for element
await waitFor(() => {
  expect(screen.getByText('Success')).toBeInTheDocument();
});

// Or use findBy (combines getBy + waitFor)
expect(await screen.findByText('Success')).toBeInTheDocument();
```

---

### Issue: "act() warning"

**Solution:**
```typescript
// Wrap state updates in act()
await act(async () => {
  await result.current.fetchData();
});

// Or use Testing Library's async utils (handles act() automatically)
await userEvent.click(button);
await waitFor(() => expect(...));
```

---

### Issue: Tests Timeout

**Solution:**
```typescript
// Increase timeout for slow tests
it('loads data', async () => {
  // ...
}, 10000); // 10 second timeout

// Or fix the underlying issue:
// - Mock slow API calls
// - Use fake timers for delays
jest.useFakeTimers();
```

---

## Best Practices

### DO:
✅ **Test user behavior**, not implementation
✅ **Use accessible queries** (getByRole, getByLabelText)
✅ **Mock external dependencies** (API calls, localStorage)
✅ **Test error states** and edge cases
✅ **Keep tests isolated** (no shared state)
✅ **Write descriptive test names** that explain behavior
✅ **Use userEvent** over fireEvent for realistic interactions
✅ **Clean up after tests** (jest.restoreAllMocks())
✅ **Test accessibility** (ARIA attributes, keyboard nav)
✅ **Aim for 80%+ coverage** on critical code

### DON'T:
❌ **Don't test implementation details** (internal state, class names)
❌ **Don't use waitFor unnecessarily** (slows tests)
❌ **Don't forget to clean up mocks** between tests
❌ **Don't test third-party libraries** (trust they work)
❌ **Don't make tests dependent** on execution order
❌ **Don't ignore flaky tests** - fix them
❌ **Don't skip testing error cases**
❌ **Don't use snapshots** excessively (brittle)
❌ **Don't test trivial code** (simple getters, etc.)
❌ **Don't write slow tests** - mock expensive operations

---

## Related Workflows

**Prerequisites:**
- [React Component Creation](./react_component_creation.md) - Create components to test
- [State Management Setup](./state_management_setup.md) - Test state management

**Next Steps:**
- [E2E Testing Workflow](./e2e_testing_workflow.md) - End-to-end testing
- [Test Writing](../development/test_writing.md) - General testing practices

**Related:**
- [CI/CD Pipeline Setup](../devops/cicd_pipeline_setup.md) - Automated testing
- [Code Review Checklist](../quality-assurance/code_review_checklist.md) - Review tests

---

## Tags
`testing` `jest` `react-testing-library` `unit-tests` `component-tests` `tdd` `coverage` `mocking` `accessibility-testing`
