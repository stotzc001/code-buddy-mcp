# CSS Architecture

**ID:** fro-081  
**Category:** Frontend Development  
**Priority:** MEDIUM  
**Complexity:** Intermediate  
**Estimated Time:** 2-4 hours (setup), ongoing maintenance  
**Prerequisites:** Understanding of CSS and component-based design  

---

## Overview

CSS architecture defines how you organize, structure, and scale your stylesheets. This workflow helps you implement a maintainable CSS strategy that prevents conflicts, promotes reusability, and scales with your application.

**When to Use:**
- Starting a new frontend project
- Refactoring existing CSS codebase
- Scaling a small project to medium/large
- Addressing CSS maintenance challenges
- Implementing design system

**Problems CSS Architecture Solves:**
- Style conflicts and specificity wars
- Difficulty finding and modifying styles
- Duplicate styles across codebase
- Performance issues from bloated CSS
- Inconsistent design patterns

---

## Quick Start

```bash
# Choose methodology: BEM, SMACSS, or CSS-in-JS
# Recommended: BEM + utility classes (most practical)

# Example structure:
src/
  styles/
    base/          # Reset, typography, globals
    components/    # Component-specific styles
    utilities/     # Utility classes
    variables.css  # Design tokens
    main.css       # Entry point
```

---

## CSS Methodologies Comparison

```markdown
| Methodology | Complexity | Learning Curve | Tooling | Best For |
|-------------|------------|----------------|---------|----------|
| BEM | Low | Easy | None required | Most projects |
| SMACSS | Medium | Moderate | None required | Large teams |
| ITCSS | Medium | Moderate | None required | Complex projects |
| CSS-in-JS | High | Steep | Build tools | React/JS-heavy |
| Atomic/Utility | Low | Easy | Tailwind/etc | Rapid development |
| CSS Modules | Low | Easy | Bundler | Component isolation |
```

---

## Recommended Approach: BEM + Utility Classes

### Setup Directory Structure

```
src/
├── styles/
│   ├── base/
│   │   ├── _reset.css          # Normalize or reset styles
│   │   ├── _typography.css     # Global font styles
│   │   └── _global.css         # Body, html, etc.
│   │
│   ├── components/
│   │   ├── _button.css         # Button component
│   │   ├── _card.css           # Card component
│   │   ├── _form.css           # Form elements
│   │   └── _modal.css          # Modal component
│   │
│   ├── layout/
│   │   ├── _header.css         # Site header
│   │   ├── _footer.css         # Site footer
│   │   ├── _sidebar.css        # Sidebar layout
│   │   └── _grid.css           # Grid system
│   │
│   ├── utilities/
│   │   ├── _spacing.css        # Margin/padding utilities
│   │   ├── _text.css           # Text utilities
│   │   └── _colors.css         # Color utilities
│   │
│   ├── _variables.css          # CSS custom properties
│   └── main.css                # Import everything
│
└── components/
    ├── Button/
    │   ├── Button.jsx
    │   └── Button.module.css   # CSS Modules alternative
    └── Card/
        ├── Card.jsx
        └── Card.module.css
```

---

## Step-by-Step Implementation

### Phase 1: Define Design Tokens (30 minutes)

```css
/* styles/_variables.css */

:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-dark: #2563eb;
  --color-primary-light: #60a5fa;
  
  --color-secondary: #8b5cf6;
  --color-secondary-dark: #7c3aed;
  --color-secondary-light: #a78bfa;
  
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;
  
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
  
  /* Typography */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'Monaco', 'Courier New', monospace;
  
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */
  
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Spacing */
  --spacing-1: 0.25rem;   /* 4px */
  --spacing-2: 0.5rem;    /* 8px */
  --spacing-3: 0.75rem;   /* 12px */
  --spacing-4: 1rem;      /* 16px */
  --spacing-5: 1.25rem;   /* 20px */
  --spacing-6: 1.5rem;    /* 24px */
  --spacing-8: 2rem;      /* 32px */
  --spacing-10: 2.5rem;   /* 40px */
  --spacing-12: 3rem;     /* 48px */
  --spacing-16: 4rem;     /* 64px */
  
  /* Border radius */
  --radius-sm: 0.125rem;  /* 2px */
  --radius-base: 0.25rem; /* 4px */
  --radius-md: 0.375rem;  /* 6px */
  --radius-lg: 0.5rem;    /* 8px */
  --radius-xl: 0.75rem;   /* 12px */
  --radius-2xl: 1rem;     /* 16px */
  --radius-full: 9999px;  /* Fully rounded */
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 300ms ease;
  --transition-slow: 500ms ease;
  
  /* Breakpoints (for reference in JS) */
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
}
```

---

### Phase 2: Create Base Styles (30 minutes)

```css
/* styles/base/_reset.css */

/* Modern CSS reset */
*, *::before, *::after {
  box-sizing: border-box;
}

* {
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-sans);
  font-size: var(--font-size-base);
  line-height: 1.5;
  color: var(--color-gray-900);
  background-color: #ffffff;
}

img, picture, video, canvas, svg {
  display: block;
  max-width: 100%;
}

input, button, textarea, select {
  font: inherit;
}

p, h1, h2, h3, h4, h5, h6 {
  overflow-wrap: break-word;
}

/* styles/base/_typography.css */

h1, h2, h3, h4, h5, h6 {
  font-weight: var(--font-weight-bold);
  line-height: 1.2;
  margin-bottom: var(--spacing-4);
}

h1 { font-size: var(--font-size-4xl); }
h2 { font-size: var(--font-size-3xl); }
h3 { font-size: var(--font-size-2xl); }
h4 { font-size: var(--font-size-xl); }
h5 { font-size: var(--font-size-lg); }
h6 { font-size: var(--font-size-base); }

p {
  margin-bottom: var(--spacing-4);
}

a {
  color: var(--color-primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

a:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

code {
  font-family: var(--font-mono);
  font-size: 0.9em;
  background-color: var(--color-gray-100);
  padding: 0.125rem 0.25rem;
  border-radius: var(--radius-sm);
}

pre {
  font-family: var(--font-mono);
  background-color: var(--color-gray-100);
  padding: var(--spacing-4);
  border-radius: var(--radius-md);
  overflow-x: auto;
}
```

---

### Phase 3: Component Styles with BEM (1-2 hours)

```css
/* styles/components/_button.css */

/* Block */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  line-height: 1;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
}

.button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.button:active {
  transform: translateY(0);
}

.button:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

/* Modifiers - Variants */
.button--primary {
  background-color: var(--color-primary);
  color: white;
}

.button--primary:hover {
  background-color: var(--color-primary-dark);
}

.button--secondary {
  background-color: var(--color-secondary);
  color: white;
}

.button--outline {
  background-color: transparent;
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.button--outline:hover {
  background-color: var(--color-primary);
  color: white;
}

.button--ghost {
  background-color: transparent;
  color: var(--color-primary);
}

.button--ghost:hover {
  background-color: var(--color-gray-100);
}

/* Modifiers - Sizes */
.button--small {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-sm);
}

.button--large {
  padding: var(--spacing-3) var(--spacing-6);
  font-size: var(--font-size-lg);
}

/* Modifiers - Full width */
.button--full {
  width: 100%;
}

/* Elements - Button with icon */
.button__icon {
  margin-right: var(--spacing-2);
}

.button__icon--right {
  margin-right: 0;
  margin-left: var(--spacing-2);
}

/* Usage Examples:
<button class="button button--primary">Primary</button>
<button class="button button--outline button--large">Large Outline</button>
<button class="button button--ghost button--full">
  <span class="button__icon">🔍</span>
  Search
</button>
*/
```

```css
/* styles/components/_card.css */

.card {
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-base);
  overflow: hidden;
  transition: box-shadow var(--transition-base);
}

.card:hover {
  box-shadow: var(--shadow-lg);
}

.card--bordered {
  border: 1px solid var(--color-gray-200);
  box-shadow: none;
}

.card--interactive {
  cursor: pointer;
}

/* Elements */
.card__header {
  padding: var(--spacing-6);
  border-bottom: 1px solid var(--color-gray-200);
}

.card__body {
  padding: var(--spacing-6);
}

.card__footer {
  padding: var(--spacing-6);
  border-top: 1px solid var(--color-gray-200);
  background-color: var(--color-gray-50);
}

.card__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-2);
}

.card__description {
  color: var(--color-gray-600);
  margin-bottom: 0;
}
```

---

### Phase 4: Utility Classes (30 minutes)

```css
/* styles/utilities/_spacing.css */

/* Margin utilities */
.m-0 { margin: 0; }
.m-1 { margin: var(--spacing-1); }
.m-2 { margin: var(--spacing-2); }
.m-4 { margin: var(--spacing-4); }
.m-8 { margin: var(--spacing-8); }

.mt-0 { margin-top: 0; }
.mt-2 { margin-top: var(--spacing-2); }
.mt-4 { margin-top: var(--spacing-4); }

.mb-0 { margin-bottom: 0; }
.mb-2 { margin-bottom: var(--spacing-2); }
.mb-4 { margin-bottom: var(--spacing-4); }

/* Padding utilities */
.p-0 { padding: 0; }
.p-2 { padding: var(--spacing-2); }
.p-4 { padding: var(--spacing-4); }
.p-8 { padding: var(--spacing-8); }

/* styles/utilities/_text.css */

.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

.text-sm { font-size: var(--font-size-sm); }
.text-base { font-size: var(--font-size-base); }
.text-lg { font-size: var(--font-size-lg); }

.font-normal { font-weight: var(--font-weight-normal); }
.font-medium { font-weight: var(--font-weight-medium); }
.font-bold { font-weight: var(--font-weight-bold); }

/* styles/utilities/_colors.css */

.text-primary { color: var(--color-primary); }
.text-secondary { color: var(--color-secondary); }
.text-gray { color: var(--color-gray-600); }

.bg-white { background-color: white; }
.bg-gray-100 { background-color: var(--color-gray-100); }
.bg-primary { background-color: var(--color-primary); }
```

---

### Phase 5: Main CSS Entry Point

```css
/* styles/main.css */

/* Import order matters! */

/* 1. Variables first */
@import './_variables.css';

/* 2. Base/reset styles */
@import './base/_reset.css';
@import './base/_typography.css';
@import './base/_global.css';

/* 3. Layout components */
@import './layout/_header.css';
@import './layout/_footer.css';
@import './layout/_grid.css';

/* 4. Reusable components */
@import './components/_button.css';
@import './components/_card.css';
@import './components/_form.css';
@import './components/_modal.css';

/* 5. Utility classes last (highest specificity when needed) */
@import './utilities/_spacing.css';
@import './utilities/_text.css';
@import './utilities/_colors.css';
```

---

## Alternative: CSS Modules

```jsx
// Button.module.css
.button {
  padding: var(--spacing-2) var(--spacing-4);
  background-color: var(--color-primary);
  color: white;
  border-radius: var(--radius-md);
}

.button:hover {
  background-color: var(--color-primary-dark);
}

.primary {
  background-color: var(--color-primary);
}

.secondary {
  background-color: var(--color-secondary);
}

// Button.jsx
import styles from './Button.module.css';

export function Button({ variant = 'primary', children }) {
  return (
    <button className={`${styles.button} ${styles[variant]}`}>
      {children}
    </button>
  );
}
```

---

## Best Practices

### DO:
✅ **Use CSS custom properties** - Easy theming and maintenance  
✅ **Keep specificity low** - Avoid deep nesting  
✅ **Follow naming convention consistently** - Pick BEM or similar  
✅ **Create reusable components** - DRY principle  
✅ **Document your system** - Maintain style guide  
✅ **Use utilities sparingly** - For one-off adjustments  

### DON'T:
❌ **Use !important** - Almost never necessary  
❌ **Nest too deeply** - Max 3-4 levels  
❌ **Use ID selectors** - Too specific  
❌ **Inline critical styles** - Keep in stylesheet  
❌ **Over-use utilities** - They should complement, not replace components  

---

## Related Workflows

**Prerequisites:**
- [[fro-009]] React Component Creation - Component structure
- [[fro-010]] Responsive Design Implementation - Responsive patterns

**Next Steps:**
- [[fro-008]] Performance Optimization - CSS optimization
- [[fro-001]] Accessibility Workflow - Accessible styling

---

## Tags

`frontend` `css` `architecture` `bem` `styling` `design-system` `scalability` `maintenance`
