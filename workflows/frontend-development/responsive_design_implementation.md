# Responsive Design Implementation

**ID:** fro-009  
**Category:** Frontend Development  
**Priority:** HIGH  
**Complexity:** Intermediate  
**Estimated Time:** 60-90 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Implement responsive design patterns using mobile-first approach, CSS Grid, Flexbox, and media queries

**Why:** Responsive design ensures your application works seamlessly across all devices, improving user experience and accessibility

**When to use:**
- Building new features or components
- Refactoring legacy responsive code
- Implementing design system breakpoints
- Optimizing for specific device types
- Troubleshooting layout issues on mobile/tablet

---

## Prerequisites

**Required:**
- [ ] Basic understanding of CSS Flexbox and Grid
- [ ] React component structure knowledge
- [ ] Browser DevTools familiarity
- [ ] Understanding of CSS units (rem, em, vh, vw, %)

**Check before starting:**
```bash
# Verify project has Tailwind or CSS-in-JS setup
npm list tailwindcss
# or
npm list styled-components

# Check if PostCSS is configured
cat postcss.config.js

# Verify responsive design system exists
ls src/styles/breakpoints.ts
```

---

## Implementation Steps

### Step 1: Define Breakpoint System

**What:** Establish a consistent breakpoint system across your application

**How:**

**Tailwind Configuration (tailwind.config.js):**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    screens: {
      // Mobile first (min-width)
      'sm': '640px',   // Small tablets
      'md': '768px',   // Tablets
      'lg': '1024px',  // Laptops
      'xl': '1280px',  // Desktops
      '2xl': '1536px', // Large desktops
      
      // Custom breakpoints
      'xs': '475px',   // Large phones
      '3xl': '1920px', // Extra large screens
      
      // Max-width breakpoints (for mobile-first edge cases)
      'max-sm': { max: '639px' },
      'max-md': { max: '767px' },
    },
  },
  plugins: [],
};
```

**CSS Custom Properties (src/styles/breakpoints.css):**
```css
:root {
  /* Breakpoints */
  --breakpoint-xs: 475px;
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
  
  /* Container max-widths */
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
  
  /* Spacing scale */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;
  
  /* Typography scale */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
}
```

**TypeScript Constants (src/styles/breakpoints.ts):**
```typescript
export const breakpoints = {
  xs: 475,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

export type Breakpoint = keyof typeof breakpoints;

// Media query helpers
export const media = {
  xs: `@media (min-width: ${breakpoints.xs}px)`,
  sm: `@media (min-width: ${breakpoints.sm}px)`,
  md: `@media (min-width: ${breakpoints.md}px)`,
  lg: `@media (min-width: ${breakpoints.lg}px)`,
  xl: `@media (min-width: ${breakpoints.xl}px)`,
  '2xl': `@media (min-width: ${breakpoints['2xl']}px)`,
} as const;

// React hook for current breakpoint
export function useBreakpoint(): Breakpoint {
  const [breakpoint, setBreakpoint] = React.useState<Breakpoint>('sm');

  React.useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width >= breakpoints['2xl']) setBreakpoint('2xl');
      else if (width >= breakpoints.xl) setBreakpoint('xl');
      else if (width >= breakpoints.lg) setBreakpoint('lg');
      else if (width >= breakpoints.md) setBreakpoint('md');
      else if (width >= breakpoints.sm) setBreakpoint('sm');
      else setBreakpoint('xs');
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return breakpoint;
}

// React hook for media queries
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = React.useState(false);

  React.useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    setMatches(mediaQuery.matches);

    const handler = (event: MediaQueryListEvent) => setMatches(event.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);

  return matches;
}
```

**Verification:**
- [ ] Breakpoints defined consistently
- [ ] Custom properties accessible
- [ ] TypeScript types working
- [ ] Hooks functional

**If This Fails:**
→ Ensure Tailwind config is imported in CSS
→ Check TypeScript compilation
→ Verify React version supports hooks

---

### Step 2: Create Responsive Layout Components

**What:** Build flexible layout primitives that handle responsive behavior

**How:**

**Container Component (src/components/layout/Container.tsx):**
```typescript
import React from 'react';

interface ContainerProps {
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  padding?: boolean;
  className?: string;
}

export function Container({ 
  children, 
  maxWidth = 'xl', 
  padding = true,
  className = '' 
}: ContainerProps) {
  const maxWidthClasses = {
    sm: 'max-w-screen-sm',
    md: 'max-w-screen-md',
    lg: 'max-w-screen-lg',
    xl: 'max-w-screen-xl',
    full: 'max-w-full',
  };

  return (
    <div 
      className={`
        mx-auto 
        ${maxWidthClasses[maxWidth]}
        ${padding ? 'px-4 sm:px-6 lg:px-8' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
}
```

**Grid Component (src/components/layout/Grid.tsx):**
```typescript
import React from 'react';

interface GridProps {
  children: React.ReactNode;
  cols?: {
    default?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: number;
  className?: string;
}

export function Grid({ 
  children, 
  cols = { default: 1, sm: 2, lg: 3 },
  gap = 4,
  className = '' 
}: GridProps) {
  const gridCols = [
    cols.default && `grid-cols-${cols.default}`,
    cols.sm && `sm:grid-cols-${cols.sm}`,
    cols.md && `md:grid-cols-${cols.md}`,
    cols.lg && `lg:grid-cols-${cols.lg}`,
    cols.xl && `xl:grid-cols-${cols.xl}`,
  ].filter(Boolean).join(' ');

  return (
    <div 
      className={`
        grid 
        ${gridCols}
        gap-${gap}
        ${className}
      `}
    >
      {children}
    </div>
  );
}
```

**Stack Component (src/components/layout/Stack.tsx):**
```typescript
import React from 'react';

interface StackProps {
  children: React.ReactNode;
  direction?: 'row' | 'column';
  responsive?: {
    base: 'row' | 'column';
    sm?: 'row' | 'column';
    md?: 'row' | 'column';
    lg?: 'row' | 'column';
  };
  gap?: number;
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around';
  className?: string;
}

export function Stack({
  children,
  direction = 'column',
  responsive,
  gap = 4,
  align = 'stretch',
  justify = 'start',
  className = '',
}: StackProps) {
  const directionClasses = responsive
    ? [
        `flex-${responsive.base}`,
        responsive.sm && `sm:flex-${responsive.sm}`,
        responsive.md && `md:flex-${responsive.md}`,
        responsive.lg && `lg:flex-${responsive.lg}`,
      ].filter(Boolean).join(' ')
    : `flex-${direction}`;

  const alignClasses = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
    stretch: 'items-stretch',
  };

  const justifyClasses = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between',
    around: 'justify-around',
  };

  return (
    <div 
      className={`
        flex
        ${directionClasses}
        gap-${gap}
        ${alignClasses[align]}
        ${justifyClasses[justify]}
        ${className}
      `}
    >
      {children}
    </div>
  );
}
```

**Usage Example:**
```typescript
function ProductGrid() {
  return (
    <Container maxWidth="xl">
      <Grid 
        cols={{ default: 1, sm: 2, md: 3, lg: 4 }}
        gap={6}
      >
        {products.map(product => (
          <ProductCard key={product.id} {...product} />
        ))}
      </Grid>
    </Container>
  );
}

function HeroSection() {
  return (
    <Container>
      <Stack
        responsive={{ base: 'column', lg: 'row' }}
        gap={8}
        align="center"
      >
        <div className="flex-1">
          <h1 className="text-3xl md:text-4xl lg:text-5xl">
            Welcome to Our App
          </h1>
          <p className="text-base md:text-lg mt-4">
            Build amazing things
          </p>
        </div>
        <img 
          src="/hero.jpg" 
          alt="Hero" 
          className="flex-1 w-full lg:w-auto"
        />
      </Stack>
    </Container>
  );
}
```

**Verification:**
- [ ] Layout components render correctly
- [ ] Responsive props work across breakpoints
- [ ] Spacing consistent
- [ ] TypeScript types valid

**If This Fails:**
→ Check Tailwind JIT is processing dynamic classes
→ Use safelist in tailwind.config.js for dynamic classes
→ Verify component props match Tailwind utilities

---

### Step 3: Implement Responsive Typography

**What:** Create fluid typography that scales smoothly across devices

**How:**

**Fluid Typography System (src/styles/typography.css):**
```css
/* Base fluid typography using clamp() */
:root {
  /* Fluid font sizes */
  --font-size-xs: clamp(0.75rem, 0.7rem + 0.2vw, 0.875rem);
  --font-size-sm: clamp(0.875rem, 0.8rem + 0.3vw, 1rem);
  --font-size-base: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
  --font-size-lg: clamp(1.125rem, 1rem + 0.5vw, 1.25rem);
  --font-size-xl: clamp(1.25rem, 1.1rem + 0.6vw, 1.5rem);
  --font-size-2xl: clamp(1.5rem, 1.3rem + 1vw, 2rem);
  --font-size-3xl: clamp(1.875rem, 1.5rem + 1.5vw, 2.5rem);
  --font-size-4xl: clamp(2.25rem, 1.75rem + 2vw, 3rem);
  --font-size-5xl: clamp(3rem, 2.25rem + 3vw, 4rem);
  
  /* Line heights */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}

/* Responsive headings */
h1 {
  font-size: var(--font-size-4xl);
  line-height: var(--line-height-tight);
  font-weight: 800;
}

h2 {
  font-size: var(--font-size-3xl);
  line-height: var(--line-height-tight);
  font-weight: 700;
}

h3 {
  font-size: var(--font-size-2xl);
  line-height: var(--line-height-normal);
  font-weight: 600;
}

body {
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
}

/* Responsive text utilities */
.text-responsive {
  font-size: var(--font-size-base);
}

.text-responsive-lg {
  font-size: var(--font-size-lg);
}
```

**Typography Component (src/components/Typography.tsx):**
```typescript
import React from 'react';

interface TypographyProps {
  variant?: 'h1' | 'h2' | 'h3' | 'h4' | 'body' | 'caption';
  responsive?: boolean;
  children: React.ReactNode;
  className?: string;
}

export function Typography({
  variant = 'body',
  responsive = true,
  children,
  className = '',
}: TypographyProps) {
  const baseClasses = responsive ? 'responsive-text' : '';
  
  const variantClasses = {
    h1: 'text-4xl md:text-5xl lg:text-6xl font-bold',
    h2: 'text-3xl md:text-4xl lg:text-5xl font-bold',
    h3: 'text-2xl md:text-3xl lg:text-4xl font-semibold',
    h4: 'text-xl md:text-2xl lg:text-3xl font-semibold',
    body: 'text-base md:text-lg',
    caption: 'text-sm md:text-base text-gray-600',
  };

  const Component = variant.startsWith('h') ? variant : 'p';

  return React.createElement(
    Component,
    {
      className: `${baseClasses} ${variantClasses[variant]} ${className}`,
    },
    children
  );
}
```

**Verification:**
- [ ] Text scales smoothly
- [ ] No layout shift at breakpoints
- [ ] Readability maintained across devices
- [ ] Performance acceptable (no excessive reflows)

**If This Fails:**
→ Test clamp() browser support (IE11 doesn't support it)
→ Use PostCSS plugin for clamp() polyfill if needed
→ Verify CSS custom properties are defined

---

### Step 4: Handle Responsive Images and Media

**What:** Optimize images for different screen sizes and pixel densities

**How:**

**Responsive Image Component (src/components/ResponsiveImage.tsx):**
```typescript
import React from 'react';

interface ResponsiveImageProps {
  src: string;
  alt: string;
  sizes?: string;
  aspectRatio?: '16/9' | '4/3' | '1/1' | 'auto';
  loading?: 'lazy' | 'eager';
  className?: string;
}

export function ResponsiveImage({
  src,
  alt,
  sizes = '100vw',
  aspectRatio = 'auto',
  loading = 'lazy',
  className = '',
}: ResponsiveImageProps) {
  const aspectRatioClasses = {
    '16/9': 'aspect-video',
    '4/3': 'aspect-4/3',
    '1/1': 'aspect-square',
    'auto': '',
  };

  return (
    <img
      src={src}
      srcSet={`
        ${src}?w=640 640w,
        ${src}?w=768 768w,
        ${src}?w=1024 1024w,
        ${src}?w=1280 1280w,
        ${src}?w=1536 1536w
      `}
      sizes={sizes}
      alt={alt}
      loading={loading}
      className={`
        w-full h-auto object-cover
        ${aspectRatioClasses[aspectRatio]}
        ${className}
      `}
    />
  );
}
```

**Picture Element for Art Direction:**
```typescript
export function ArtDirectedImage() {
  return (
    <picture>
      {/* Mobile: Portrait crop */}
      <source
        media="(max-width: 767px)"
        srcSet="/images/hero-mobile.jpg"
      />
      {/* Tablet: Square crop */}
      <source
        media="(max-width: 1023px)"
        srcSet="/images/hero-tablet.jpg"
      />
      {/* Desktop: Landscape */}
      <img
        src="/images/hero-desktop.jpg"
        alt="Hero banner"
        className="w-full h-auto"
      />
    </picture>
  );
}
```

**Video Component:**
```typescript
export function ResponsiveVideo({ src, poster }: { src: string; poster: string }) {
  return (
    <video
      className="w-full h-auto"
      poster={poster}
      controls
      playsInline // Important for iOS
    >
      <source src={`${src}.webm`} type="video/webm" />
      <source src={`${src}.mp4`} type="video/mp4" />
      Your browser doesn't support HTML5 video.
    </video>
  );
}
```

**Background Images with Media Queries:**
```css
.hero-section {
  background-image: url('/images/hero-mobile.jpg');
  background-size: cover;
  background-position: center;
}

@media (min-width: 768px) {
  .hero-section {
    background-image: url('/images/hero-tablet.jpg');
  }
}

@media (min-width: 1024px) {
  .hero-section {
    background-image: url('/images/hero-desktop.jpg');
  }
}
```

**Verification:**
- [ ] Images load appropriate sizes
- [ ] No layout shift during load
- [ ] Lazy loading working
- [ ] Art direction correct

**If This Fails:**
→ Use image CDN (Cloudinary, imgix) for automatic resizing
→ Implement blurhash or LQIP for placeholders
→ Check srcset and sizes syntax

---

### Step 5: Create Responsive Navigation

**What:** Build a navigation that adapts between mobile and desktop views

**How:**

**Mobile-First Navigation (src/components/Navigation.tsx):**
```typescript
import React, { useState } from 'react';
import { Menu, X } from 'lucide-react';
import { useMediaQuery } from '@/hooks/useMediaQuery';

export function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const isDesktop = useMediaQuery('(min-width: 1024px)');

  // Close menu when switching to desktop
  React.useEffect(() => {
    if (isDesktop) {
      setMobileMenuOpen(false);
    }
  }, [isDesktop]);

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <img src="/logo.svg" alt="Logo" className="h-8 w-auto" />
          </div>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex lg:items-center lg:space-x-8">
            <a href="/products" className="text-gray-700 hover:text-gray-900">
              Products
            </a>
            <a href="/about" className="text-gray-700 hover:text-gray-900">
              About
            </a>
            <a href="/contact" className="text-gray-700 hover:text-gray-900">
              Contact
            </a>
            <button className="btn-primary">
              Get Started
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="lg:hidden p-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="lg:hidden py-4 space-y-4">
            <a
              href="/products"
              className="block py-2 text-gray-700 hover:text-gray-900"
            >
              Products
            </a>
            <a
              href="/about"
              className="block py-2 text-gray-700 hover:text-gray-900"
            >
              About
            </a>
            <a
              href="/contact"
              className="block py-2 text-gray-700 hover:text-gray-900"
            >
              Contact
            </a>
            <button className="btn-primary w-full">
              Get Started
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
```

**Slide-out Mobile Menu with Animation:**
```typescript
import { AnimatePresence, motion } from 'framer-motion';

export function SlidingMobileMenu() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(true)}>
        <Menu size={24} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            />

            {/* Menu */}
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 20 }}
              className="fixed top-0 right-0 bottom-0 w-64 bg-white shadow-xl z-50 lg:hidden"
            >
              <div className="p-4">
                <button
                  onClick={() => setIsOpen(false)}
                  className="mb-8"
                >
                  <X size={24} />
                </button>

                <nav className="space-y-4">
                  <a href="/products" className="block py-2">
                    Products
                  </a>
                  <a href="/about" className="block py-2">
                    About
                  </a>
                  <a href="/contact" className="block py-2">
                    Contact
                  </a>
                </nav>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
```

**Verification:**
- [ ] Menu toggles correctly on mobile
- [ ] Desktop navigation always visible
- [ ] Menu closes on route change
- [ ] Accessible with keyboard
- [ ] No layout shift

**If This Fails:**
→ Add `overflow-hidden` to body when menu open
→ Use proper ARIA attributes for accessibility
→ Test on actual mobile devices, not just browser DevTools

---

### Step 6: Implement Responsive Forms

**What:** Create form layouts that adapt to different screen sizes

**How:**

**Responsive Form Component:**
```typescript
export function ResponsiveForm() {
  return (
    <form className="space-y-6">
      {/* Full-width on mobile, half on desktop */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            First Name
          </label>
          <input
            type="text"
            className="w-full px-4 py-2 border rounded-lg"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">
            Last Name
          </label>
          <input
            type="text"
            className="w-full px-4 py-2 border rounded-lg"
          />
        </div>
      </div>

      {/* Always full-width */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Email
        </label>
        <input
          type="email"
          className="w-full px-4 py-2 border rounded-lg"
        />
      </div>

      {/* Responsive button group */}
      <div className="flex flex-col sm:flex-row gap-4">
        <button type="submit" className="flex-1 btn-primary">
          Submit
        </button>
        <button type="button" className="flex-1 btn-secondary">
          Cancel
        </button>
      </div>
    </form>
  );
}
```

**Mobile-Optimized Input Sizes:**
```css
/* Prevent zoom on iOS when input focused */
input,
textarea,
select {
  font-size: 16px; /* iOS zooms if less than 16px */
}

/* Touch-friendly sizing */
@media (max-width: 767px) {
  button,
  input,
  select,
  textarea {
    min-height: 44px; /* Apple's recommended minimum touch target */
  }
}
```

**Verification:**
- [ ] Form fields properly sized
- [ ] Touch targets large enough (44x44px minimum)
- [ ] No horizontal scroll on mobile
- [ ] Keyboard navigation works

**If This Fails:**
→ Check viewport meta tag is set correctly
→ Test on actual devices for input zoom behavior
→ Ensure min-height meets accessibility guidelines

---

### Step 7: Test and Debug Responsive Behavior

**What:** Verify your responsive implementation across devices and browsers

**How:**

**Browser DevTools Testing:**
```bash
# Chrome DevTools
# 1. Open DevTools (F12)
# 2. Toggle device toolbar (Ctrl+Shift+M)
# 3. Test common devices:
#    - iPhone SE (375x667)
#    - iPhone 12 Pro (390x844)
#    - iPad (768x1024)
#    - iPad Pro (1024x1366)
#    - Desktop (1920x1080)
```

**Automated Responsive Testing (Playwright):**
```typescript
import { test, expect } from '@playwright/test';

const viewports = [
  { name: 'Mobile', width: 375, height: 667 },
  { name: 'Tablet', width: 768, height: 1024 },
  { name: 'Desktop', width: 1920, height: 1080 },
];

for (const viewport of viewports) {
  test(`Navigation works on ${viewport.name}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto('/');

    if (viewport.width < 768) {
      // Mobile: Check hamburger menu
      await expect(page.getByLabel('Toggle menu')).toBeVisible();
      await page.getByLabel('Toggle menu').click();
      await expect(page.getByRole('navigation')).toBeVisible();
    } else {
      // Desktop: Check horizontal nav
      await expect(page.getByRole('navigation')).toBeVisible();
      await expect(page.getByLabel('Toggle menu')).not.toBeVisible();
    }
  });
}
```

**Visual Regression Testing:**
```typescript
import { test } from '@playwright/test';

test('homepage screenshots across breakpoints', async ({ page }) => {
  await page.goto('/');

  // Mobile
  await page.setViewportSize({ width: 375, height: 667 });
  await page.screenshot({ path: 'screenshots/home-mobile.png', fullPage: true });

  // Tablet
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.screenshot({ path: 'screenshots/home-tablet.png', fullPage: true });

  // Desktop
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.screenshot({ path: 'screenshots/home-desktop.png', fullPage: true });
});
```

**Real Device Testing Tools:**
```bash
# BrowserStack / LambdaTest for real device testing
# ngrok for mobile testing on local network
npx ngrok http 3000

# Then access the ngrok URL on your mobile device
```

**Common Issues Checklist:**
```typescript
// Responsive Debug Helper Component
export function ResponsiveDebug() {
  const breakpoint = useBreakpoint();
  const [viewport, setViewport] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateViewport = () => {
      setViewport({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };
    
    updateViewport();
    window.addEventListener('resize', updateViewport);
    return () => window.removeEventListener('resize', updateViewport);
  }, []);

  if (process.env.NODE_ENV !== 'development') return null;

  return (
    <div className="fixed bottom-4 right-4 bg-black text-white p-3 rounded-lg text-xs font-mono z-50">
      <div>Breakpoint: {breakpoint}</div>
      <div>Viewport: {viewport.width}x{viewport.height}</div>
    </div>
  );
}
```

**Verification:**
- [ ] No horizontal scroll on any device
- [ ] Touch targets appropriately sized
- [ ] Text readable without zooming
- [ ] Images scale correctly
- [ ] Navigation usable on mobile

**If This Fails:**
→ Check for fixed widths (replace with max-width)
→ Verify overflow-x: hidden not hiding content
→ Test on real devices, not just emulators
→ Use Chrome DevTools Performance tab to check for layout thrashing

---

### Step 8: Optimize Performance for Mobile

**What:** Ensure responsive design doesn't hurt performance on slower devices

**How:**

**Lazy Load Below-the-Fold Images:**
```typescript
export function LazyImage({ src, alt }: { src: string; alt: string }) {
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      className="w-full h-auto"
    />
  );
}
```

**Responsive Lazy Loading with Intersection Observer:**
```typescript
export function ResponsiveLazyImage({ src, alt }: { src: string; alt: string }) {
  const [isLoaded, setIsLoaded] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsLoaded(true);
          observer.disconnect();
        }
      },
      { rootMargin: '50px' }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <img
      ref={imgRef}
      src={isLoaded ? src : '/placeholder.jpg'}
      alt={alt}
      className="w-full h-auto"
    />
  );
}
```

**Conditional Component Loading:**
```typescript
// Only load heavy components on desktop
const HeavyChart = lazy(() => import('./HeavyChart'));

export function Dashboard() {
  const isDesktop = useMediaQuery('(min-width: 1024px)');

  return (
    <div>
      <h1>Dashboard</h1>
      {isDesktop ? (
        <Suspense fallback={<ChartSkeleton />}>
          <HeavyChart />
        </Suspense>
      ) : (
        <SimpleMobileChart />
      )}
    </div>
  );
}
```

**Reduce Bundle Size for Mobile:**
```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'mobile-only': ['./src/components/MobileMenu'],
          'desktop-only': ['./src/components/DesktopChart'],
        },
      },
    },
  },
};
```

**Verification:**
- [ ] Images lazy load correctly
- [ ] Heavy components load conditionally
- [ ] No unnecessary JS on mobile
- [ ] Fast LCP and FID scores

**If This Fails:**
→ Use Lighthouse to audit performance
→ Check Network tab for unnecessary downloads
→ Consider using service workers for caching
→ Implement critical CSS inlining

---

## Verification Checklist

After completing this workflow:

- [ ] Breakpoint system defined and consistent
- [ ] All components responsive across mobile, tablet, desktop
- [ ] No horizontal scroll on any device
- [ ] Touch targets meet 44x44px minimum
- [ ] Text readable without zooming
- [ ] Images properly sized for device
- [ ] Navigation works on mobile and desktop
- [ ] Forms usable on small screens
- [ ] Performance acceptable on mobile devices
- [ ] Visual regression tests passing
- [ ] Real device testing completed

---

## Common Issues & Solutions

### Issue: Layout Breaks at Specific Breakpoints

**Symptoms:**
- Content overflows container
- Horizontal scroll appears
- Text overlaps other elements

**Solution:**
```css
/* Find the problematic element */
* {
  outline: 1px solid red;
}

/* Common fixes */
.container {
  /* Instead of width: 100vw */
  width: 100%;
  max-width: 100%;
  overflow-x: hidden; /* Use sparingly */
}

/* Prevent text overflow */
.text-content {
  overflow-wrap: break-word;
  word-wrap: break-word;
  hyphens: auto;
}

/* Responsive images */
img {
  max-width: 100%;
  height: auto;
}
```

**Prevention:**
- Test at every breakpoint during development
- Use `max-width` instead of fixed `width`
- Apply `box-sizing: border-box` globally

---

### Issue: Touch Targets Too Small on Mobile

**Symptoms:**
- Hard to tap buttons
- Wrong buttons get clicked
- Poor mobile usability

**Solution:**
```css
/* Ensure minimum 44x44px touch targets */
@media (max-width: 767px) {
  button,
  a,
  input[type="checkbox"],
  input[type="radio"] {
    min-width: 44px;
    min-height: 44px;
    padding: 12px 16px;
  }
  
  /* Add spacing between touch targets */
  .button-group > * + * {
    margin-left: 8px;
  }
}
```

**Prevention:**
- Follow WCAG 2.1 Level AAA guidelines (44x44px minimum)
- Add padding around clickable elements
- Test on actual mobile devices

---

### Issue: Images Loading Wrong Sizes

**Symptoms:**
- Large images on mobile
- Blurry images on desktop
- Slow page load

**Solution:**
```typescript
// Use srcset and sizes properly
<img
  src="image-1024.jpg"
  srcSet="
    image-640.jpg 640w,
    image-1024.jpg 1024w,
    image-1920.jpg 1920w
  "
  sizes="
    (max-width: 640px) 100vw,
    (max-width: 1024px) 50vw,
    33vw
  "
  alt="Product"
/>

// Or use image CDN
<img
  src={`https://cdn.example.com/image.jpg?w=${width}&q=80`}
  alt="Product"
/>
```

**Prevention:**
- Use image CDN for automatic optimization
- Implement responsive images from the start
- Set explicit width/height to prevent layout shift

---

## Best Practices

### DO:
✅ Design mobile-first, then scale up
✅ Use relative units (rem, em, %, vw, vh)
✅ Test on real devices, not just emulators
✅ Use semantic HTML with proper ARIA labels
✅ Implement touch-friendly UI (44x44px minimum)
✅ Optimize images for different screen sizes
✅ Use CSS Grid and Flexbox for layouts
✅ Test at all defined breakpoints
✅ Use system fonts for better performance
✅ Implement smooth transitions between breakpoints
✅ Ensure text is readable without zooming

### DON'T:
❌ Use fixed pixel widths for containers
❌ Rely solely on desktop testing
❌ Ignore touch target sizes
❌ Use viewport-locking meta tags
❌ Load desktop-only assets on mobile
❌ Forget about landscape orientation
❌ Use hover-only interactions
❌ Ignore different device pixel ratios
❌ Assume all mobile devices have the same capabilities
❌ Use `!important` to fix responsive issues
❌ Forget about print styles

---

## Related Workflows

**Prerequisites:**
- [react_component_creation.md](./react_component_creation.md) - Component basics

**Next Steps:**
- [performance_optimization.md](./performance_optimization.md) - Optimize mobile performance
- [accessibility_workflow.md](./accessibility_workflow.md) - Ensure accessible responsive design

**Related:**
- [e2e_testing_workflow.md](./e2e_testing_workflow.md) - Test responsive behavior
- [build_deployment.md](./build_deployment.md) - Deploy responsive apps

---

## Tags
`frontend development` `responsive design` `mobile-first` `css` `tailwind` `flexbox` `grid` `breakpoints`
