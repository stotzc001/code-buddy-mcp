# Accessibility Workflow

**ID:** fro-001  
**Category:** Frontend Development  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Implement WCAG 2.1 Level AA accessibility standards in React applications using semantic HTML, ARIA, and testing tools

**Why:** Accessible applications reach more users, meet legal requirements, improve SEO, and provide better UX for everyone

**When to use:**
- Building new components or features
- Auditing existing applications
- Fixing accessibility issues
- Preparing for WCAG compliance review
- Implementing keyboard navigation
- Adding screen reader support

---

## Prerequisites

**Required:**
- [ ] Understanding of semantic HTML
- [ ] React component structure knowledge
- [ ] Basic keyboard navigation concepts
- [ ] Screen reader testing capability

**Check before starting:**
```bash
# Install testing tools
npm install -D @axe-core/react
npm install -D jest-axe
npm install -D @testing-library/react
npm install -D @testing-library/jest-dom

# Verify browser extensions installed
# - axe DevTools
# - WAVE
# - Lighthouse

# Check if screen reader available
# macOS: VoiceOver (Cmd+F5)
# Windows: NVDA (free) or JAWS
# Linux: Orca
```

---

## Implementation Steps

### Step 1: Set Up Accessibility Testing Tools

**What:** Install and configure automated accessibility testing

**How:**

**Install Axe Core:**
```typescript
// src/index.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

if (process.env.NODE_ENV !== 'production') {
  import('@axe-core/react').then(axe => {
    axe.default(React, ReactDOM, 1000);
  });
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**Jest Axe for Unit Tests:**
```typescript
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Button', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

**ESLint Plugin:**
```bash
npm install -D eslint-plugin-jsx-a11y
```

```javascript
// .eslintrc.js
module.exports = {
  extends: ['plugin:jsx-a11y/recommended'],
  plugins: ['jsx-a11y'],
  rules: {
    'jsx-a11y/alt-text': 'error',
    'jsx-a11y/anchor-has-content': 'error',
    'jsx-a11y/anchor-is-valid': 'error',
    'jsx-a11y/aria-props': 'error',
    'jsx-a11y/aria-role': 'error',
    'jsx-a11y/label-has-associated-control': 'error',
    'jsx-a11y/no-autofocus': 'warn',
  },
};
```

**Playwright Accessibility Tests:**
```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage should not have accessibility violations', async ({ page }) => {
  await page.goto('/');
  
  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();
  
  expect(accessibilityScanResults.violations).toEqual([]);
});
```

**Verification:**
- [ ] Axe DevTools running in development
- [ ] Jest tests configured
- [ ] ESLint warnings showing
- [ ] Playwright accessibility tests passing

**If This Fails:**
→ Check React version compatibility with axe-core/react
→ Ensure jest-axe is properly configured in test setup
→ Verify ESLint is running correctly
→ Update Playwright if axe-core/playwright fails

---

### Step 2: Implement Semantic HTML Structure

**What:** Use proper HTML elements for their intended purpose

**How:**

**Page Structure:**
```typescript
export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      {/* Skip to main content link */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      <header>
        <nav aria-label="Main navigation">
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/contact">Contact</a></li>
          </ul>
        </nav>
      </header>

      <main id="main-content" tabIndex={-1}>
        {children}
      </main>

      <aside aria-label="Sidebar">
        {/* Complementary content */}
      </aside>

      <footer>
        <p>&copy; 2024 Company Name</p>
      </footer>
    </>
  );
}
```

**Skip Link CSS:**
```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: white;
  padding: 8px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

**Headings Hierarchy:**
```typescript
export function ArticlePage() {
  return (
    <article>
      {/* Main page title - only one h1 per page */}
      <h1>Article Title</h1>
      
      {/* Section headings */}
      <section>
        <h2>Introduction</h2>
        <p>Content...</p>
        
        {/* Subsections */}
        <h3>Background</h3>
        <p>More content...</p>
      </section>
      
      <section>
        <h2>Main Content</h2>
        <h3>Subsection 1</h3>
        <h4>Detail Level</h4>
      </section>
    </article>
  );
}
```

**Lists:**
```typescript
// ❌ BAD: Divs that look like lists
<div className="item-list">
  <div className="item">Item 1</div>
  <div className="item">Item 2</div>
  <div className="item">Item 3</div>
</div>

// ✅ GOOD: Semantic list
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
  <li>Item 3</li>
</ul>

// For navigation
<nav aria-label="Main menu">
  <ul>
    <li><a href="/">Home</a></li>
    <li><a href="/products">Products</a></li>
  </ul>
</nav>

// For ordered steps
<ol>
  <li>Step 1: Do this</li>
  <li>Step 2: Then this</li>
  <li>Step 3: Finally this</li>
</ol>
```

**Buttons vs Links:**
```typescript
// ❌ BAD: Link used as button
<a href="#" onClick={handleSubmit}>Submit</a>

// ✅ GOOD: Button for actions
<button type="button" onClick={handleSubmit}>
  Submit
</button>

// ❌ BAD: Button used for navigation
<button onClick={() => navigate('/about')}>About</button>

// ✅ GOOD: Link for navigation
<Link to="/about">About</Link>
```

**Verification:**
- [ ] Page has proper landmark structure
- [ ] Heading hierarchy is logical
- [ ] Lists use proper markup
- [ ] Buttons and links used correctly

**If This Fails:**
→ Run axe DevTools to identify issues
→ Check heading outline in browser DevTools
→ Verify with screen reader navigation
→ Review WCAG Success Criterion 1.3.1

---

### Step 3: Implement Keyboard Navigation

**What:** Ensure all interactive elements are keyboard accessible

**How:**

**Focus Management:**
```typescript
import { useRef, useEffect } from 'react';

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Store previously focused element
      previousFocusRef.current = document.activeElement as HTMLElement;
      
      // Focus modal
      modalRef.current?.focus();
      
      // Trap focus inside modal
      const handleTab = (e: KeyboardEvent) => {
        if (e.key !== 'Tab') return;

        const focusableElements = modalRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (!focusableElements || focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement.focus();
            e.preventDefault();
          }
        }
      };

      document.addEventListener('keydown', handleTab);
      return () => document.removeEventListener('keydown', handleTab);
    } else {
      // Restore focus when modal closes
      previousFocusRef.current?.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      tabIndex={-1}
      className="modal"
    >
      <h2 id="modal-title">{title}</h2>
      {children}
      <button onClick={onClose}>Close</button>
    </div>
  );
}
```

**Keyboard Event Handlers:**
```typescript
export function Dropdown({ items }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'Enter':
      case ' ': // Space
        e.preventDefault();
        setIsOpen(!isOpen);
        break;
      case 'Escape':
        setIsOpen(false);
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setFocusedIndex(prev => 
            prev < items.length - 1 ? prev + 1 : prev
          );
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        setFocusedIndex(prev => (prev > 0 ? prev - 1 : 0));
        break;
      case 'Home':
        e.preventDefault();
        setFocusedIndex(0);
        break;
      case 'End':
        e.preventDefault();
        setFocusedIndex(items.length - 1);
        break;
    }
  };

  return (
    <div className="dropdown">
      <button
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        Select item
      </button>
      
      {isOpen && (
        <ul role="listbox" aria-label="Options">
          {items.map((item, index) => (
            <li
              key={item.id}
              role="option"
              aria-selected={index === focusedIndex}
              tabIndex={index === focusedIndex ? 0 : -1}
            >
              {item.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

**Focus Visible Styles:**
```css
/* Remove default outline */
*:focus {
  outline: none;
}

/* Add visible focus indicator */
*:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}

/* Custom focus styles for buttons */
button:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(0, 102, 204, 0.2);
}

/* Skip link focus */
.skip-link:focus {
  outline: 2px solid #fff;
  outline-offset: 2px;
}
```

**Verification:**
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators clearly visible
- [ ] Tab order is logical
- [ ] Focus trap works in modals
- [ ] Keyboard shortcuts don't conflict

**If This Fails:**
→ Test with Tab, Shift+Tab, Enter, Space, Arrow keys
→ Use browser DevTools to track :focus-visible
→ Check tabindex values (avoid positive values)
→ Test with screen reader + keyboard

---

### Step 4: Add ARIA Labels and Roles

**What:** Provide additional context for assistive technologies

**How:**

**Form Labels:**
```typescript
export function LoginForm() {
  return (
    <form onSubmit={handleSubmit}>
      {/* ✅ GOOD: Explicit label */}
      <label htmlFor="email">
        Email Address
      </label>
      <input
        id="email"
        type="email"
        name="email"
        required
        aria-required="true"
        aria-describedby="email-hint"
      />
      <span id="email-hint" className="hint">
        We'll never share your email
      </span>

      {/* ✅ GOOD: aria-label for icon-only button */}
      <button type="submit" aria-label="Log in">
        <LoginIcon />
      </button>
    </form>
  );
}
```

**Dynamic Content Announcements:**
```typescript
export function SearchResults({ results, isLoading }: Props) {
  return (
    <div>
      {/* Announce loading state */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
      >
        {isLoading && 'Loading results...'}
        {!isLoading && `${results.length} results found`}
      </div>

      {/* Results list */}
      <ul role="list" aria-label="Search results">
        {results.map(result => (
          <li key={result.id}>{result.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

**Custom Components with ARIA:**
```typescript
export function Tabs({ tabs }: TabsProps) {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <div>
      {/* Tab list */}
      <div role="tablist" aria-label="Account settings">
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            role="tab"
            id={`tab-${index}`}
            aria-controls={`panel-${index}`}
            aria-selected={activeTab === index}
            tabIndex={activeTab === index ? 0 : -1}
            onClick={() => setActiveTab(index)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab panels */}
      {tabs.map((tab, index) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${index}`}
          aria-labelledby={`tab-${index}`}
          hidden={activeTab !== index}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}
```

**Live Regions for Notifications:**
```typescript
export function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  return (
    <div
      role="region"
      aria-label="Notifications"
      aria-live="assertive" // Interrupts screen reader
      aria-atomic="true"
    >
      {notifications.map(notification => (
        <div key={notification.id} role="alert">
          {notification.message}
        </div>
      ))}
    </div>
  );
}

// For non-urgent updates, use aria-live="polite"
export function StatusMessage({ message }: { message: string }) {
  return (
    <div role="status" aria-live="polite">
      {message}
    </div>
  );
}
```

**Dialog/Modal ARIA:**
```typescript
export function AlertDialog({ title, message, onConfirm, onCancel }: Props) {
  return (
    <div
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
      aria-describedby="dialog-description"
    >
      <h2 id="dialog-title">{title}</h2>
      <p id="dialog-description">{message}</p>
      
      <button onClick={onConfirm}>Confirm</button>
      <button onClick={onCancel}>Cancel</button>
    </div>
  );
}
```

**Verification:**
- [ ] All form inputs have labels
- [ ] Dynamic content announced
- [ ] Custom widgets have proper roles
- [ ] Live regions working correctly

**If This Fails:**
→ Test with screen reader (VoiceOver, NVDA)
→ Check ARIA roles in axe DevTools
→ Verify aria-labelledby IDs match
→ Review WCAG Success Criterion 4.1.2

---

### Step 5: Ensure Color Contrast and Visual Accessibility

**What:** Make content perceivable for users with low vision or color blindness

**How:**

**Color Contrast Checking:**
```typescript
// Use contrast checker tools or this helper
function checkContrast(foreground: string, background: string): {
  ratio: number;
  passes: { aa: boolean; aaa: boolean };
} {
  // Implementation would calculate contrast ratio
  // WCAG AA requires 4.5:1 for normal text, 3:1 for large text
  // WCAG AAA requires 7:1 for normal text, 4.5:1 for large text
}

// Example usage in design system
const colors = {
  // ✅ GOOD: 7.31:1 contrast
  text: '#1a1a1a',
  background: '#ffffff',
  
  // ❌ BAD: 2.1:1 contrast - fails WCAG
  // textLight: '#999999',
  // background: '#ffffff',
  
  // ✅ GOOD: 4.51:1 contrast for links
  link: '#0066cc',
  linkVisited: '#551a8b',
};
```

**CSS for High Contrast Mode:**
```css
/* Support Windows High Contrast Mode */
@media (prefers-contrast: high) {
  button {
    border: 2px solid currentColor;
  }
  
  .card {
    border: 1px solid currentColor;
  }
}

/* Ensure focus indicators work in high contrast */
*:focus-visible {
  outline: 2px solid;
  outline-offset: 2px;
}
```

**Don't Rely on Color Alone:**
```typescript
// ❌ BAD: Color only
<span style={{ color: 'red' }}>Required</span>

// ✅ GOOD: Color + text + icon
<span style={{ color: 'red' }} aria-label="Required field">
  <RequiredIcon /> Required *
</span>

// For status indicators
export function StatusBadge({ status }: { status: 'success' | 'error' | 'warning' }) {
  const config = {
    success: { icon: CheckIcon, label: 'Success', color: 'green' },
    error: { icon: XIcon, label: 'Error', color: 'red' },
    warning: { icon: AlertIcon, label: 'Warning', color: 'yellow' },
  }[status];

  return (
    <span
      className={`badge badge-${config.color}`}
      role="status"
      aria-label={config.label}
    >
      <config.icon aria-hidden="true" />
      {config.label}
    </span>
  );
}
```

**Text Sizing and Zoom:**
```css
/* Use relative units for text */
body {
  font-size: 16px; /* Base size */
}

h1 {
  font-size: 2rem; /* Scales with user preferences */
}

p {
  font-size: 1rem;
  line-height: 1.5; /* WCAG recommends 1.5 minimum */
}

/* Allow text to reflow at 200% zoom */
.content {
  max-width: 100%;
  word-wrap: break-word;
}

/* Don't fix heights on text containers */
.text-box {
  /* ❌ height: 100px; */
  min-height: 100px; /* ✅ Allows expansion */
}
```

**Verification:**
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Information not conveyed by color alone
- [ ] Text resizable to 200%
- [ ] High contrast mode works
- [ ] Content readable in grayscale

**If This Fails:**
→ Use browser DevTools color contrast checker
→ Test with WebAIM Contrast Checker
→ Enable high contrast mode in OS settings
→ Use browser zoom to test at 200%
→ Take screenshot and convert to grayscale

---

### Step 6: Make Media Accessible

**What:** Provide alternatives for images, videos, and audio content

**How:**

**Image Alt Text:**
```typescript
// ❌ BAD: Missing alt
<img src="product.jpg" />

// ❌ BAD: Redundant alt
<img src="image.jpg" alt="Image of..." />

// ✅ GOOD: Descriptive alt
<img src="product.jpg" alt="Blue wireless headphones" />

// ✅ GOOD: Decorative image
<img src="background.jpg" alt="" role="presentation" />

// For complex images
<figure>
  <img src="chart.png" alt="Sales data chart" />
  <figcaption id="chart-description">
    Sales increased from $100K in Q1 to $250K in Q4
  </figcaption>
</figure>

// For data visualization
export function AccessibleChart({ data }: Props) {
  return (
    <>
      <div role="img" aria-labelledby="chart-title chart-desc">
        <svg>{/* Chart visualization */}</svg>
      </div>
      <h3 id="chart-title">Annual Revenue</h3>
      <p id="chart-desc">
        Revenue grew steadily from $100K in January to $250K in December
      </p>
      
      {/* Also provide data table */}
      <table>
        <caption>Revenue by Month</caption>
        <thead>
          <tr>
            <th>Month</th>
            <th>Revenue</th>
          </tr>
        </thead>
        <tbody>
          {data.map(row => (
            <tr key={row.month}>
              <td>{row.month}</td>
              <td>${row.revenue}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
```

**Video Accessibility:**
```typescript
export function AccessibleVideo({ src, poster, captions }: Props) {
  return (
    <video
      controls
      poster={poster}
      aria-label="Product demonstration video"
    >
      <source src={src} type="video/mp4" />
      
      {/* Captions for deaf/hard-of-hearing users */}
      <track
        kind="captions"
        src={captions.en}
        srclang="en"
        label="English"
        default
      />
      <track
        kind="captions"
        src={captions.es}
        srclang="es"
        label="Español"
      />
      
      {/* Audio description for blind users */}
      <track
        kind="descriptions"
        src="/video-audio-description.vtt"
        srclang="en"
        label="Audio descriptions"
      />
      
      {/* Fallback for browsers without video support */}
      <p>
        Your browser doesn't support HTML5 video.{' '}
        <a href={src}>Download the video</a>
      </p>
    </video>
  );
}
```

**WebVTT Caption File Example:**
```
WEBVTT

00:00:00.000 --> 00:00:03.000
[Music playing]

00:00:03.000 --> 00:00:06.000
Welcome to our product demonstration.

00:00:06.500 --> 00:00:09.000
[Speaker clicks button]

00:00:09.000 --> 00:00:12.000
Let me show you the key features.
```

**Audio Transcripts:**
```typescript
export function PodcastEpisode({ audioSrc, transcript }: Props) {
  return (
    <div>
      <audio controls src={audioSrc}>
        <p>
          Your browser doesn't support HTML5 audio.{' '}
          <a href={audioSrc}>Download the audio file</a>
        </p>
      </audio>
      
      <details>
        <summary>Read transcript</summary>
        <div dangerouslySetInnerHTML={{ __html: transcript }} />
      </details>
    </div>
  );
}
```

**Verification:**
- [ ] All images have appropriate alt text
- [ ] Videos have captions
- [ ] Audio has transcripts
- [ ] Complex images have long descriptions
- [ ] Decorative images marked as presentational

**If This Fails:**
→ Review alt text quality with screen reader
→ Test video captions in different players
→ Ensure WebVTT files are properly formatted
→ Check WCAG Success Criterion 1.1.1 and 1.2

---

### Step 7: Create Accessible Forms

**What:** Build forms that work for all users

**How:**

**Complete Accessible Form:**
```typescript
export function ContactForm() {
  const [errors, setErrors] = useState<Record<string, string>>({});

  return (
    <form onSubmit={handleSubmit} noValidate>
      <fieldset>
        <legend>Personal Information</legend>
        
        {/* Text input */}
        <div className="form-group">
          <label htmlFor="name">
            Full Name <span aria-label="required">*</span>
          </label>
          <input
            id="name"
            type="text"
            name="name"
            required
            aria-required="true"
            aria-invalid={!!errors.name}
            aria-describedby={errors.name ? 'name-error' : 'name-hint'}
          />
          <span id="name-hint" className="hint">
            Enter your first and last name
          </span>
          {errors.name && (
            <span id="name-error" className="error" role="alert">
              {errors.name}
            </span>
          )}
        </div>

        {/* Email input */}
        <div className="form-group">
          <label htmlFor="email">Email Address *</label>
          <input
            id="email"
            type="email"
            name="email"
            required
            aria-required="true"
            aria-invalid={!!errors.email}
            aria-describedby={errors.email ? 'email-error' : undefined}
            autoComplete="email"
          />
          {errors.email && (
            <span id="email-error" className="error" role="alert">
              {errors.email}
            </span>
          )}
        </div>

        {/* Radio buttons */}
        <fieldset>
          <legend>Contact Preference</legend>
          <div>
            <input
              type="radio"
              id="contact-email"
              name="contact"
              value="email"
            />
            <label htmlFor="contact-email">Email</label>
          </div>
          <div>
            <input
              type="radio"
              id="contact-phone"
              name="contact"
              value="phone"
            />
            <label htmlFor="contact-phone">Phone</label>
          </div>
        </fieldset>

        {/* Checkboxes */}
        <div className="form-group">
          <input
            type="checkbox"
            id="newsletter"
            name="newsletter"
          />
          <label htmlFor="newsletter">
            Subscribe to newsletter
          </label>
        </div>

        {/* Select */}
        <div className="form-group">
          <label htmlFor="country">Country</label>
          <select id="country" name="country">
            <option value="">Select a country</option>
            <option value="us">United States</option>
            <option value="uk">United Kingdom</option>
          </select>
        </div>
      </fieldset>

      {/* Submit button */}
      <button type="submit">
        Send Message
      </button>
    </form>
  );
}
```

**Form Validation:**
```typescript
export function useFormValidation() {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const errorSummaryRef = useRef<HTMLDivElement>(null);

  const validate = (formData: FormData): boolean => {
    const newErrors: Record<string, string> = {};

    // Validation logic
    if (!formData.get('name')) {
      newErrors.name = 'Name is required';
    }

    if (!formData.get('email')) {
      newErrors.email = 'Email is required';
    }

    setErrors(newErrors);

    // Focus error summary if errors exist
    if (Object.keys(newErrors).length > 0) {
      errorSummaryRef.current?.focus();
      return false;
    }

    return true;
  };

  const ErrorSummary = () => {
    if (Object.keys(errors).length === 0) return null;

    return (
      <div
        ref={errorSummaryRef}
        role="alert"
        aria-labelledby="error-summary-title"
        tabIndex={-1}
        className="error-summary"
      >
        <h2 id="error-summary-title">There are {Object.keys(errors).length} errors</h2>
        <ul>
          {Object.entries(errors).map(([field, message]) => (
            <li key={field}>
              <a href={`#${field}`}>{message}</a>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return { errors, validate, ErrorSummary };
}
```

**Verification:**
- [ ] All inputs have labels
- [ ] Error messages associated with inputs
- [ ] Required fields marked
- [ ] Validation errors announced
- [ ] Form submittable with keyboard

**If This Fails:**
→ Test with screen reader to verify error announcements
→ Ensure aria-describedby IDs exist
→ Check autocomplete attributes for personal data
→ Verify fieldsets group related inputs

---

### Step 8: Test with Assistive Technologies

**What:** Verify accessibility with actual screen readers and tools

**How:**

**Screen Reader Testing Checklist:**
```markdown
## macOS VoiceOver Testing
1. Enable: Cmd + F5
2. Navigate: VO + Arrow keys (VO = Ctrl + Option)
3. Rotor: VO + U
4. Test:
   - [ ] Page landmarks announced
   - [ ] Headings navigable
   - [ ] Form labels read correctly
   - [ ] Button purposes clear
   - [ ] Images have alt text
   - [ ] Dynamic updates announced

## Windows NVDA Testing
1. Enable: Ctrl + Alt + N
2. Navigate: Arrow keys
3. Elements List: NVDA + F7
4. Test same checklist as above

## Mobile VoiceOver (iOS)
1. Settings > Accessibility > VoiceOver
2. Three-finger triple-tap for screen curtain
3. Test on actual device, not simulator
```

**Automated Testing Script:**
```typescript
// pa11y for automated testing
import pa11y from 'pa11y';

async function testAccessibility(url: string) {
  const results = await pa11y(url, {
    standard: 'WCAG2AA',
    runners: ['axe', 'htmlcs'],
    includeNotices: true,
    includeWarnings: true,
  });

  console.log(`Issues found: ${results.issues.length}`);
  
  results.issues.forEach(issue => {
    console.log(`
      Type: ${issue.type}
      Code: ${issue.code}
      Message: ${issue.message}
      Context: ${issue.context}
      Selector: ${issue.selector}
    `);
  });

  return results;
}

// Run in CI
testAccessibility('http://localhost:3000').then(results => {
  if (results.issues.length > 0) {
    process.exit(1);
  }
});
```

**Real User Testing:**
```markdown
## User Testing Protocol
1. Recruit users who:
   - Use screen readers daily
   - Have low vision
   - Have motor impairments
   - Are color blind

2. Test scenarios:
   - [ ] Navigate homepage
   - [ ] Complete signup form
   - [ ] Use search functionality
   - [ ] Complete checkout flow
   - [ ] Access help documentation

3. Collect feedback on:
   - Confusing announcements
   - Missing labels
   - Difficult navigation
   - Unclear error messages
```

**Verification:**
- [ ] Tested with VoiceOver/NVDA
- [ ] Mobile screen reader tested
- [ ] Automated tests passing
- [ ] User testing completed
- [ ] Issues documented and fixed

**If This Fails:**
→ Practice using screen reader first (tutorial mode)
→ Start with simple pages before complex interactions
→ Record sessions for later analysis
→ Consult with accessibility experts
→ Review WCAG documentation for specific issues

---

## Verification Checklist

After completing this workflow:

- [ ] Automated tests passing (axe, jest-axe, Playwright)
- [ ] ESLint jsx-a11y rules passing
- [ ] Manual screen reader testing completed
- [ ] Keyboard navigation works throughout
- [ ] Color contrast meets WCAG AA
- [ ] All images have alt text
- [ ] Forms fully accessible
- [ ] Focus indicators visible
- [ ] ARIA labels appropriate
- [ ] No layout shift on zoom
- [ ] Captions on videos
- [ ] Transcripts for audio
- [ ] Lighthouse accessibility score > 95

---

## Common Issues & Solutions

### Issue: Screen Reader Not Announcing Dynamic Content

**Symptoms:**
- Updates happen silently
- Users miss important information
- Loading states not communicated

**Solution:**
```typescript
// Use aria-live regions
export function SearchResults({ results, isLoading }: Props) {
  return (
    <>
      <div role="status" aria-live="polite" aria-atomic="true">
        {isLoading ? 'Loading...' : `${results.length} results found`}
      </div>
      
      <ul aria-label="Search results">
        {results.map(result => (
          <li key={result.id}>{result.title}</li>
        ))}
      </ul>
    </>
  );
}

// For urgent announcements
export function ErrorMessage({ message }: { message: string }) {
  return (
    <div role="alert" aria-live="assertive">
      {message}
    </div>
  );
}
```

**Prevention:**
- Use `aria-live="polite"` for non-urgent updates
- Use `aria-live="assertive"` for critical alerts
- Set `aria-atomic="true"` to announce full content

---

### Issue: Keyboard Focus Not Visible

**Symptoms:**
- Can't see where focus is
- Lost while tabbing
- Difficult to navigate

**Solution:**
```css
/* Remove default outline ONLY if replacing it */
*:focus {
  outline: none;
}

/* Always provide visible focus indicator */
*:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
  border-radius: 4px;
}

/* High contrast support */
@media (prefers-contrast: high) {
  *:focus-visible {
    outline: 3px solid;
    outline-offset: 3px;
  }
}

/* Specific component focus styles */
button:focus-visible {
  box-shadow: 0 0 0 4px rgba(0, 102, 204, 0.2);
}
```

**Prevention:**
- Never remove focus styles without replacement
- Test with keyboard navigation
- Use :focus-visible instead of :focus
- Ensure 3:1 contrast ratio for focus indicators

---

## Best Practices

### DO:
✅ Use semantic HTML elements
✅ Provide text alternatives for non-text content
✅ Ensure keyboard navigation works everywhere
✅ Make focus indicators highly visible
✅ Test with actual screen readers
✅ Use ARIA only when semantic HTML isn't enough
✅ Maintain logical heading hierarchy
✅ Provide skip links
✅ Ensure color contrast meets WCAG AA
✅ Support browser zoom to 200%
✅ Announce dynamic content changes
✅ Include accessibility in code reviews

### DON'T:
❌ Use divs/spans for interactive elements
❌ Rely on color alone to convey information
❌ Remove focus indicators without replacement
❌ Use placeholder as label
❌ Auto-focus inputs on page load
❌ Use positive tabindex values
❌ Create keyboard traps
❌ Ignore automated test failures
❌ Skip manual testing
❌ Forget mobile accessibility
❌ Disable zoom
❌ Use CAPTCHAs without alternatives

---

## Related Workflows

**Prerequisites:**
- [react_component_creation.md](./react_component_creation.md) - Component structure
- [component_testing_strategy.md](./component_testing_strategy.md) - Testing basics

**Next Steps:**
- [e2e_testing_workflow.md](./e2e_testing_workflow.md) - E2E accessibility testing

**Related:**
- [form_handling_validation.md](./form_handling_validation.md) - Accessible forms
- [responsive_design_implementation.md](./responsive_design_implementation.md) - Responsive accessibility

---

## Tags
`frontend development` `accessibility` `a11y` `wcag` `aria` `screen-reader` `keyboard-navigation` `semantic-html`
