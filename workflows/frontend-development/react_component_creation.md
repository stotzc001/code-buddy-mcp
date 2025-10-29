# React Component Creation

**ID:** fro-008  
**Category:** Frontend Development  
**Priority:** MEDIUM  
**Complexity:** Simple  
**Estimated Time:** 15-30 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematic workflow for creating reusable, well-structured React components following modern best practices

**Why:** 
- Ensures consistent component architecture across the codebase
- Promotes reusability and maintainability
- Follows React best practices and design patterns
- Reduces bugs through proper typing and testing
- Improves developer productivity with clear patterns

**When to use:**
- Creating new UI components from scratch
- Refactoring class components to functional components
- Building component libraries
- Converting designs to React components
- Implementing new features

---

## Prerequisites

**Required:**
- [ ] Node.js and npm/yarn installed
- [ ] React project initialized (Create React App, Vite, Next.js, etc.)
- [ ] Understanding of React hooks (useState, useEffect, etc.)
- [ ] TypeScript knowledge (if using TypeScript)
- [ ] Basic component design patterns

**Check before starting:**
```bash
# Verify Node.js and npm versions
node --version  # Should be >= 18.x
npm --version   # Should be >= 9.x

# Verify React is installed
npm list react react-dom

# Check if TypeScript is configured (if applicable)
cat tsconfig.json

# Verify testing setup
npm list @testing-library/react jest
```

---

## Implementation Steps

### Step 1: Plan Component Structure and API

**What:** Define the component's purpose, props interface, and behavior before writing code

**How:**

1. **Identify component type:**

```typescript
// Presentational Component (UI only, no business logic)
// Example: Button, Card, Badge

// Container Component (data fetching, business logic)
// Example: UserProfile, ProductList

// Compound Component (parent-child relationship)
// Example: Tabs/Tab, Select/Option

// Higher-Order Component (wraps other components)
// Example: withAuth, withLogging
```

2. **Define props interface:**

```typescript
// component-name.types.ts
export interface ButtonProps {
  // Required props
  children: React.ReactNode;
  onClick: () => void;
  
  // Optional props with defaults
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  
  // HTML attributes
  className?: string;
  type?: 'button' | 'submit' | 'reset';
  ariaLabel?: string;
}

// For more complex components
export interface UserCardProps {
  user: {
    id: string;
    name: string;
    email: string;
    avatar?: string;
  };
  onEdit?: (userId: string) => void;
  onDelete?: (userId: string) => void;
  isEditable?: boolean;
}
```

3. **Sketch component hierarchy:**

```
UserCard (Container)
├── Avatar (Presentational)
├── UserInfo (Presentational)
│   ├── Name
│   └── Email
└── ActionButtons (Presentational)
    ├── EditButton
    └── DeleteButton
```

**Verification:**
- [ ] Component responsibility is clear and single-purpose
- [ ] Props interface is well-typed
- [ ] Component follows React naming conventions (PascalCase)
- [ ] Component hierarchy is logical

**If This Fails:**
→ Component is trying to do too much - consider breaking into smaller components
→ Props interface is unclear - revisit the component's purpose

---

### Step 2: Create Component File Structure

**What:** Set up proper file organization for the component

**How:**

```bash
# Option 1: Simple component (single file)
src/components/Button/
├── Button.tsx
├── Button.test.tsx
└── index.ts

# Option 2: Complex component (multiple files)
src/components/UserCard/
├── UserCard.tsx
├── UserCard.types.ts
├── UserCard.styles.ts  # or UserCard.module.css
├── UserCard.test.tsx
├── UserCard.stories.tsx  # Storybook (optional)
├── hooks/
│   └── useUserCard.ts
├── components/  # Sub-components
│   ├── UserAvatar.tsx
│   └── UserInfo.tsx
└── index.ts

# Create the directory structure
mkdir -p src/components/Button
touch src/components/Button/{Button.tsx,Button.test.tsx,index.ts}
```

**File naming conventions:**
```typescript
// Component file
Button.tsx  // PascalCase

// Test file
Button.test.tsx  // or Button.spec.tsx

// Style file
Button.module.css  // CSS Modules
Button.styles.ts   // Styled Components / Emotion

// Types file
Button.types.ts

// Story file
Button.stories.tsx  // Storybook

// Hook file
useButton.ts  // camelCase with 'use' prefix
```

**Verification:**
- [ ] Directory structure follows project conventions
- [ ] All necessary files created
- [ ] index.ts barrel export present

**If This Fails:**
→ Check project's component organization conventions
→ Ensure consistency with existing components

---

### Step 3: Implement Component Logic

**What:** Write the component implementation with TypeScript and modern React patterns

**How:**

1. **Basic functional component pattern:**

```typescript
// Button.tsx
import React from 'react';
import { ButtonProps } from './Button.types';
import './Button.css';

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className = '',
  type = 'button',
  ariaLabel,
}) => {
  // 1. Computed values
  const buttonClasses = [
    'button',
    `button--${variant}`,
    `button--${size}`,
    loading && 'button--loading',
    disabled && 'button--disabled',
    className,
  ].filter(Boolean).join(' ');

  // 2. Event handlers
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (loading || disabled) {
      e.preventDefault();
      return;
    }
    onClick();
  };

  // 3. Render
  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={handleClick}
      disabled={disabled || loading}
      aria-label={ariaLabel}
      aria-busy={loading}
    >
      {loading && <span className="button__spinner" />}
      {children}
    </button>
  );
};

// Set display name for debugging
Button.displayName = 'Button';
```

2. **Component with state and effects:**

```typescript
// UserCard.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { UserCardProps } from './UserCard.types';
import { UserAvatar } from './components/UserAvatar';
import { UserInfo } from './components/UserInfo';

export const UserCard: React.FC<UserCardProps> = ({
  user,
  onEdit,
  onDelete,
  isEditable = false,
}) => {
  // 1. State
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // 2. Effects
  useEffect(() => {
    // Fetch additional data if needed
    console.log('User card mounted for user:', user.id);
    
    return () => {
      // Cleanup
      console.log('User card unmounted');
    };
  }, [user.id]);

  // 3. Callbacks (memoized to prevent unnecessary re-renders)
  const handleEdit = useCallback(() => {
    if (onEdit) {
      setIsLoading(true);
      onEdit(user.id);
      setIsLoading(false);
    }
  }, [onEdit, user.id]);

  const handleDelete = useCallback(() => {
    if (onDelete && window.confirm('Are you sure?')) {
      onDelete(user.id);
    }
  }, [onDelete, user.id]);

  const toggleExpanded = useCallback(() => {
    setIsExpanded(prev => !prev);
  }, []);

  // 4. Render
  return (
    <div className="user-card">
      <UserAvatar 
        src={user.avatar} 
        alt={user.name}
        size="md"
      />
      
      <UserInfo 
        name={user.name}
        email={user.email}
        isExpanded={isExpanded}
      />

      {isEditable && (
        <div className="user-card__actions">
          <button 
            onClick={handleEdit}
            disabled={isLoading}
          >
            Edit
          </button>
          <button 
            onClick={handleDelete}
            className="danger"
          >
            Delete
          </button>
        </div>
      )}

      <button 
        onClick={toggleExpanded}
        className="user-card__toggle"
      >
        {isExpanded ? 'Collapse' : 'Expand'}
      </button>
    </div>
  );
};
```

3. **Custom hook pattern:**

```typescript
// hooks/useUserCard.ts
import { useState, useCallback } from 'react';

interface UseUserCardReturn {
  isExpanded: boolean;
  isLoading: boolean;
  toggleExpanded: () => void;
  handleEdit: () => void;
  handleDelete: () => void;
}

export const useUserCard = (
  userId: string,
  onEdit?: (id: string) => void,
  onDelete?: (id: string) => void
): UseUserCardReturn => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const toggleExpanded = useCallback(() => {
    setIsExpanded(prev => !prev);
  }, []);

  const handleEdit = useCallback(() => {
    if (onEdit) {
      setIsLoading(true);
      onEdit(userId);
      setIsLoading(false);
    }
  }, [onEdit, userId]);

  const handleDelete = useCallback(() => {
    if (onDelete && window.confirm('Are you sure?')) {
      onDelete(userId);
    }
  }, [onDelete, userId]);

  return {
    isExpanded,
    isLoading,
    toggleExpanded,
    handleEdit,
    handleDelete,
  };
};

// Usage in component
const UserCard: React.FC<UserCardProps> = ({ user, onEdit, onDelete }) => {
  const {
    isExpanded,
    isLoading,
    toggleExpanded,
    handleEdit,
    handleDelete,
  } = useUserCard(user.id, onEdit, onDelete);

  // ... render logic
};
```

4. **Compound component pattern:**

```typescript
// Tabs.tsx
import React, { createContext, useContext, useState } from 'react';

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (id: string) => void;
}

const TabsContext = createContext<TabsContextValue | undefined>(undefined);

const useTabs = () => {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tab components must be used within Tabs');
  }
  return context;
};

// Parent component
interface TabsProps {
  defaultTab: string;
  children: React.ReactNode;
}

export const Tabs: React.FC<TabsProps> = ({ defaultTab, children }) => {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
};

// Child components
interface TabListProps {
  children: React.ReactNode;
}

export const TabList: React.FC<TabListProps> = ({ children }) => {
  return <div className="tabs__list">{children}</div>;
};

interface TabProps {
  id: string;
  children: React.ReactNode;
}

export const Tab: React.FC<TabProps> = ({ id, children }) => {
  const { activeTab, setActiveTab } = useTabs();
  const isActive = activeTab === id;

  return (
    <button
      className={`tab ${isActive ? 'tab--active' : ''}`}
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  );
};

export const TabPanel: React.FC<TabProps> = ({ id, children }) => {
  const { activeTab } = useTabs();
  if (activeTab !== id) return null;

  return <div className="tabs__panel">{children}</div>;
};

// Usage
<Tabs defaultTab="profile">
  <TabList>
    <Tab id="profile">Profile</Tab>
    <Tab id="settings">Settings</Tab>
  </TabList>
  
  <TabPanel id="profile">Profile content</TabPanel>
  <TabPanel id="settings">Settings content</TabPanel>
</Tabs>
```

**Verification:**
- [ ] Component follows single responsibility principle
- [ ] Props are properly typed
- [ ] Event handlers are memoized with useCallback
- [ ] Component has proper accessibility attributes
- [ ] No console warnings or errors

**If This Fails:**
→ Check TypeScript errors carefully
→ Ensure all dependencies are in useEffect/useCallback arrays
→ Verify prop types match usage

---

### Step 4: Style the Component

**What:** Add CSS styling using your project's styling approach

**How:**

1. **CSS Modules approach:**

```css
/* Button.module.css */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.25rem;
  
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }
}

/* Variants */
.button--primary {
  background-color: var(--color-primary);
  color: white;
  
  &:hover:not(:disabled) {
    background-color: var(--color-primary-dark);
  }
}

.button--secondary {
  background-color: var(--color-gray-200);
  color: var(--color-gray-900);
  
  &:hover:not(:disabled) {
    background-color: var(--color-gray-300);
  }
}

.button--danger {
  background-color: var(--color-red-600);
  color: white;
  
  &:hover:not(:disabled) {
    background-color: var(--color-red-700);
  }
}

/* Sizes */
.button--sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
}

.button--md {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.button--lg {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}

/* States */
.button--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button--loading {
  position: relative;
  pointer-events: none;
  
  & > *:not(.button__spinner) {
    opacity: 0;
  }
}

.button__spinner {
  position: absolute;
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
```

```typescript
// Usage with CSS Modules
import styles from './Button.module.css';

export const Button: React.FC<ButtonProps> = ({ variant, size, ...props }) => {
  return (
    <button
      className={`${styles.button} ${styles[`button--${variant}`]} ${styles[`button--${size}`]}`}
      {...props}
    />
  );
};
```

2. **Styled Components approach:**

```typescript
// Button.styles.ts
import styled, { css } from 'styled-components';

interface StyledButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const StyledButton = styled.button<StyledButtonProps>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  
  border: none;
  border-radius: 0.375rem;
  
  font-family: inherit;
  font-weight: 500;
  
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:focus-visible {
    outline: 2px solid ${({ theme }) => theme.colors.primary};
    outline-offset: 2px;
  }
  
  /* Variants */
  ${({ variant, theme }) => {
    switch (variant) {
      case 'primary':
        return css`
          background-color: ${theme.colors.primary};
          color: white;
          
          &:hover:not(:disabled) {
            background-color: ${theme.colors.primaryDark};
          }
        `;
      case 'secondary':
        return css`
          background-color: ${theme.colors.gray200};
          color: ${theme.colors.gray900};
          
          &:hover:not(:disabled) {
            background-color: ${theme.colors.gray300};
          }
        `;
      case 'danger':
        return css`
          background-color: ${theme.colors.red600};
          color: white;
          
          &:hover:not(:disabled) {
            background-color: ${theme.colors.red700};
          }
        `;
    }
  }}
  
  /* Sizes */
  ${({ size }) => {
    switch (size) {
      case 'sm':
        return css`
          padding: 0.25rem 0.75rem;
          font-size: 0.75rem;
        `;
      case 'md':
        return css`
          padding: 0.5rem 1rem;
          font-size: 0.875rem;
        `;
      case 'lg':
        return css`
          padding: 0.75rem 1.5rem;
          font-size: 1rem;
        `;
    }
  }}
  
  /* States */
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  ${({ isLoading }) =>
    isLoading &&
    css`
      position: relative;
      pointer-events: none;
      
      & > *:not(${Spinner}) {
        opacity: 0;
      }
    `}
`;

export const Spinner = styled.span`
  position: absolute;
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`;
```

3. **Tailwind CSS approach:**

```typescript
// Button.tsx
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { twMerge } from 'tailwind-merge';

const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
        danger: 'bg-red-600 text-white hover:bg-red-700',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={twMerge(buttonVariants({ variant, size }), className)}
        disabled={loading}
        {...props}
      >
        {loading && (
          <svg
            className="animate-spin h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

**Verification:**
- [ ] Styles applied correctly
- [ ] Responsive design works on mobile/tablet/desktop
- [ ] Dark mode support (if applicable)
- [ ] Hover/focus/active states work
- [ ] No CSS conflicts with other components

**If This Fails:**
→ Check CSS specificity issues
→ Verify CSS variables are defined
→ Test in different browsers

---

### Step 5: Write Component Tests

**What:** Create comprehensive tests for the component

**How:**

```typescript
// Button.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  // Basic rendering
  it('renders with children', () => {
    render(<Button onClick={() => {}}>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  // Props
  it('applies variant classes', () => {
    const { rerender } = render(
      <Button onClick={() => {}} variant="primary">Primary</Button>
    );
    expect(screen.getByRole('button')).toHaveClass('button--primary');

    rerender(<Button onClick={() => {}} variant="secondary">Secondary</Button>);
    expect(screen.getByRole('button')).toHaveClass('button--secondary');
  });

  it('applies size classes', () => {
    render(<Button onClick={() => {}} size="lg">Large</Button>);
    expect(screen.getByRole('button')).toHaveClass('button--lg');
  });

  // Interaction
  it('calls onClick when clicked', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick}>Click me</Button>);
    await user.click(screen.getByRole('button'));
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick} disabled>Click me</Button>);
    await user.click(screen.getByRole('button'));
    
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('does not call onClick when loading', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick} loading>Click me</Button>);
    await user.click(screen.getByRole('button'));
    
    expect(handleClick).not.toHaveBeenCalled();
  });

  // Accessibility
  it('has proper aria attributes when loading', () => {
    render(<Button onClick={() => {}} loading>Loading</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'true');
  });

  it('uses custom aria-label', () => {
    render(
      <Button onClick={() => {}} ariaLabel="Custom label">Icon</Button>
    );
    expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Custom label');
  });

  // Snapshots
  it('matches snapshot', () => {
    const { container } = render(
      <Button onClick={() => {}} variant="primary" size="md">
        Button
      </Button>
    );
    expect(container).toMatchSnapshot();
  });
});
```

**Test coverage checklist:**
- [ ] Component renders correctly
- [ ] All props work as expected
- [ ] User interactions trigger correct behavior
- [ ] Edge cases handled (null, undefined, empty)
- [ ] Accessibility attributes present
- [ ] Error boundaries catch errors (if applicable)

**Verification:**
```bash
# Run tests
npm test Button.test.tsx

# Check coverage
npm test -- --coverage Button.test.tsx

# Should see 90%+ coverage
```

**If This Fails:**
→ Ensure @testing-library/react is installed
→ Check that jest is configured properly
→ Add missing test cases for uncovered branches

---

### Step 6: Add Storybook Stories (Optional)

**What:** Create interactive documentation for the component

**How:**

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'danger'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
    disabled: {
      control: 'boolean',
    },
    loading: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

// Default story
export const Primary: Story = {
  args: {
    children: 'Primary Button',
    variant: 'primary',
    onClick: () => console.log('Clicked!'),
  },
};

export const Secondary: Story = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary',
    onClick: () => console.log('Clicked!'),
  },
};

export const Danger: Story = {
  args: {
    children: 'Delete',
    variant: 'danger',
    onClick: () => console.log('Deleted!'),
  },
};

// Size variants
export const Small: Story = {
  args: {
    children: 'Small Button',
    size: 'sm',
    onClick: () => {},
  },
};

export const Large: Story = {
  args: {
    children: 'Large Button',
    size: 'lg',
    onClick: () => {},
  },
};

// States
export const Disabled: Story = {
  args: {
    children: 'Disabled Button',
    disabled: true,
    onClick: () => {},
  },
};

export const Loading: Story = {
  args: {
    children: 'Loading...',
    loading: true,
    onClick: () => {},
  },
};

// Interactive example
export const WithIcon: Story = {
  args: {
    children: (
      <>
        <svg width="16" height="16" fill="currentColor">
          <path d="M8 0a8 8 0 100 16A8 8 0 008 0z" />
        </svg>
        <span>Button with Icon</span>
      </>
    ),
    onClick: () => {},
  },
};

// All variants showcase
export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
      <Button onClick={() => {}} variant="primary">Primary</Button>
      <Button onClick={() => {}} variant="secondary">Secondary</Button>
      <Button onClick={() => {}} variant="danger">Danger</Button>
      <Button onClick={() => {}} disabled>Disabled</Button>
      <Button onClick={() => {}} loading>Loading</Button>
    </div>
  ),
};
```

**Verification:**
```bash
# Start Storybook
npm run storybook

# Verify component appears in Storybook UI
# Test all interactive controls
# Check responsiveness
```

**If This Fails:**
→ Install Storybook: `npx storybook@latest init`
→ Ensure .storybook configuration is correct

---

### Step 7: Create Barrel Export

**What:** Export the component cleanly from index.ts

**How:**

```typescript
// index.ts
export { Button } from './Button';
export type { ButtonProps } from './Button.types';

// Or if types are in the same file
export { Button, type ButtonProps } from './Button';

// For compound components
export { 
  Tabs, 
  TabList, 
  Tab, 
  TabPanel,
  type TabsProps,
  type TabProps 
} from './Tabs';
```

**Usage in other files:**
```typescript
// Clean import from barrel
import { Button } from '@/components/Button';
// or
import { Button } from 'components/Button';

// Not this:
import { Button } from 'components/Button/Button'; // ❌
```

**Verification:**
- [ ] Import works from parent directory
- [ ] Types are exported
- [ ] No circular dependencies

**If This Fails:**
→ Check tsconfig.json paths configuration
→ Verify barrel export syntax

---

### Step 8: Document Component Usage

**What:** Add JSDoc comments and usage examples

**How:**

```typescript
/**
 * Button component for user interactions
 * 
 * @example
 * ```tsx
 * <Button variant="primary" onClick={() => alert('Clicked!')}>
 *   Click me
 * </Button>
 * ```
 * 
 * @example
 * ```tsx
 * <Button variant="danger" loading>
 *   Deleting...
 * </Button>
 * ```
 */
export const Button: React.FC<ButtonProps> = ({ ... }) => {
  // ...
};

/**
 * Props for the Button component
 * 
 * @property {React.ReactNode} children - Button content
 * @property {() => void} onClick - Click handler
 * @property {'primary' | 'secondary' | 'danger'} variant - Visual style
 * @property {'sm' | 'md' | 'lg'} size - Button size
 * @property {boolean} disabled - Disable interactions
 * @property {boolean} loading - Show loading spinner
 */
export interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
}
```

**Create README if needed:**
```markdown
# Button Component

A reusable button component with multiple variants and sizes.

## Usage

```tsx
import { Button } from '@/components/Button';

function MyComponent() {
  return (
    <Button variant="primary" onClick={() => console.log('Clicked')}>
      Click me
    </Button>
  );
}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| children | ReactNode | required | Button content |
| onClick | () => void | required | Click handler |
| variant | 'primary' \| 'secondary' \| 'danger' | 'primary' | Visual style |
| size | 'sm' \| 'md' \| 'lg' | 'md' | Button size |
| disabled | boolean | false | Disable button |
| loading | boolean | false | Show loading state |

## Examples

### Basic Usage
```tsx
<Button onClick={handleClick}>Submit</Button>
```

### With Variants
```tsx
<Button variant="danger" onClick={handleDelete}>Delete</Button>
```

### Loading State
```tsx
<Button loading>Saving...</Button>
```
```

**Verification:**
- [ ] JSDoc comments present
- [ ] Examples are accurate
- [ ] README created for complex components
- [ ] Props documented

---

## Verification Checklist

After completing component creation:

- [ ] Component renders without errors
- [ ] All props work as documented
- [ ] TypeScript compiles without errors
- [ ] Tests pass with good coverage (>80%)
- [ ] Styles applied correctly across browsers
- [ ] Accessibility requirements met (WCAG AA)
- [ ] Component is responsive
- [ ] Loading/error states handled
- [ ] Performance is acceptable (< 16ms render)
- [ ] No console warnings or errors
- [ ] Component is reusable and well-documented

---

## Common Issues & Solutions

### Issue: Component Re-renders Too Often

**Symptoms:**
- Performance issues
- useEffect running on every render
- Child components re-rendering unnecessarily

**Solution:**
```typescript
// ❌ Bad: New object/function on every render
<Button onClick={() => handleClick(id)} />

// ✅ Good: Memoized callback
const handleClickMemoized = useCallback(() => {
  handleClick(id);
}, [id]);

<Button onClick={handleClickMemoized} />

// ✅ Good: Use React.memo for expensive components
export const ExpensiveComponent = React.memo<ExpensiveComponentProps>(
  ({ data }) => {
    // ...
  },
  (prevProps, nextProps) => {
    // Custom comparison
    return prevProps.data.id === nextProps.data.id;
  }
);
```

**Prevention:**
- Use useCallback for event handlers
- Use useMemo for expensive computations
- Use React.memo for components that render often with same props

---

### Issue: TypeScript Errors with Event Handlers

**Symptoms:**
- Type errors on onClick, onChange, etc.
- "Type 'void' is not assignable to type 'MouseEventHandler'"

**Solution:**
```typescript
// ✅ Correct event handler types
const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
  event.preventDefault();
  // ...
};

const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
  console.log(event.target.value);
};

const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
  event.preventDefault();
  // ...
};

// Or use the handler types directly
interface MyComponentProps {
  onClick: React.MouseEventHandler<HTMLButtonElement>;
  onChange: React.ChangeEventHandler<HTMLInputElement>;
}
```

---

### Issue: Styles Not Applied with CSS Modules

**Symptoms:**
- Classes appear in HTML but no styles applied
- "Cannot find module './Component.module.css'"

**Solution:**
```typescript
// 1. Ensure import is correct
import styles from './Button.module.css'; // ✅
// not
import './Button.module.css'; // ❌

// 2. Check file naming - must end with .module.css
Button.module.css // ✅
Button.css // ❌ (unless configured differently)

// 3. Add TypeScript declaration if needed
// create: src/types/css-modules.d.ts
declare module '*.module.css' {
  const classes: { [key: string]: string };
  export default classes;
}

// 4. Verify webpack/vite config includes CSS modules support
```

---

### Issue: Component Doesn't Update with Props Change

**Symptoms:**
- Component shows stale data
- Props change but UI doesn't update

**Solution:**
```typescript
// ❌ Bad: Not using prop value
const [value, setValue] = useState(initialValue);
// If prop changes, state doesn't update

// ✅ Good: Sync with prop changes
const [value, setValue] = useState(initialValue);

useEffect(() => {
  setValue(initialValue);
}, [initialValue]);

// ✅ Better: Use prop directly if no internal state needed
const value = initialValue;

// ✅ Best: Controlled component pattern
// Let parent control the state
<Input 
  value={parentValue} 
  onChange={(e) => setParentValue(e.target.value)} 
/>
```

---

## Best Practices

### DO:
✅ **Use TypeScript** for type safety
✅ **Follow naming conventions** (PascalCase for components, camelCase for functions)
✅ **Keep components small and focused** (single responsibility)
✅ **Use meaningful prop names** (onClick, isLoading, not action, loading)
✅ **Memoize callbacks** with useCallback to prevent re-renders
✅ **Add accessibility attributes** (aria-label, role, etc.)
✅ **Write tests** for all interactive behavior
✅ **Document complex components** with JSDoc and examples
✅ **Use consistent styling approach** across the project
✅ **Export types** along with components

### DON'T:
❌ **Don't use inline functions as props** (causes re-renders)
❌ **Don't mutate props** (props are read-only)
❌ **Don't store props in state** without synchronization
❌ **Don't mix concerns** (API calls shouldn't be in presentational components)
❌ **Don't use index as key** in lists (use stable unique IDs)
❌ **Don't forget cleanup** in useEffect
❌ **Don't use any type** (defeats purpose of TypeScript)
❌ **Don't nest ternary operators** in JSX (use variables or functions)
❌ **Don't forget error boundaries** for components that might fail
❌ **Don't skip accessibility** (keyboard navigation, screen readers)

---

## Related Workflows

**Prerequisites:**
- [Project Setup](../development/new_repo_scaffolding.md) - Initial React project setup
- [State Management Setup](./state_management_setup.md) - Global state configuration

**Next Steps:**
- [Component Testing Strategy](./component_testing_strategy.md) - Testing components
- [API Integration Patterns](./api_integration_patterns.md) - Connect to backend
- [Form Handling Validation](./form_handling_validation.md) - Forms with React Hook Form

**Related:**
- [Accessibility Workflow](./accessibility_workflow.md) - WCAG compliance
- [Performance Optimization](./performance_optimization.md) - Optimize React apps

---

## Tags
`react` `components` `typescript` `frontend` `ui` `best-practices` `testing` `accessibility`
