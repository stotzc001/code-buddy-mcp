# Performance Optimization

**ID:** fro-007  
**Category:** Frontend Development  
**Priority:** HIGH  
**Complexity:** Advanced  
**Estimated Time:** 90-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematically optimize React application performance through code splitting, lazy loading, memoization, and bundle optimization

**Why:** Performance directly impacts user experience, SEO rankings, and conversion rates. A 1-second delay can reduce conversions by 7%

**When to use:**
- Application feels slow or unresponsive
- Bundle sizes are growing too large
- Lighthouse scores declining
- Users on slow networks experiencing issues
- Preparing for production deployment
- Investigating performance regressions

---

## Prerequisites

**Required:**
- [ ] React 18+ with concurrent features
- [ ] Vite or Webpack build setup
- [ ] Chrome DevTools profiling knowledge
- [ ] Basic understanding of React rendering

**Check before starting:**
```bash
# Check React version
npm list react

# Verify build tools
npm list vite webpack

# Check bundle analyzer is available
npm list --depth=0 | grep -E "webpack-bundle-analyzer|rollup-plugin-visualizer"

# Run baseline Lighthouse audit
npx lighthouse http://localhost:3000 --only-categories=performance --view
```

---

## Implementation Steps

### Step 1: Analyze Current Performance

**What:** Establish baseline metrics and identify bottlenecks

**How:**

**Run Lighthouse Audit:**
```bash
# Generate performance report
npx lighthouse http://localhost:3000 \
  --only-categories=performance \
  --output=html \
  --output-path=./lighthouse-report.html \
  --view

# Look for metrics:
# - First Contentful Paint (FCP) < 1.8s
# - Largest Contentful Paint (LCP) < 2.5s
# - Time to Interactive (TTI) < 3.8s
# - Total Blocking Time (TBT) < 200ms
# - Cumulative Layout Shift (CLS) < 0.1
```

**Analyze Bundle Size (Vite):**
```bash
# Install visualizer
npm install -D rollup-plugin-visualizer

# Add to vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';

export default {
  plugins: [
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
};

# Build and view
npm run build
```

**Webpack Bundle Analyzer:**
```bash
npm install -D webpack-bundle-analyzer

# Add to webpack.config.js
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin(),
  ],
};
```

**React DevTools Profiler:**
```typescript
// Wrap your app with Profiler
import { Profiler } from 'react';

function onRenderCallback(
  id: string,
  phase: 'mount' | 'update',
  actualDuration: number,
  baseDuration: number,
  startTime: number,
  commitTime: number,
) {
  console.log(`${id} ${phase} took ${actualDuration}ms`);
}

export function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      {/* Your app */}
    </Profiler>
  );
}
```

**Chrome Performance Tab:**
```typescript
// Add performance marks
performance.mark('component-render-start');
// ... component renders
performance.mark('component-render-end');
performance.measure(
  'component-render',
  'component-render-start',
  'component-render-end'
);

// View in Chrome DevTools > Performance > User Timing
```

**Verification:**
- [ ] Baseline metrics recorded
- [ ] Bundle size analyzed
- [ ] Bottlenecks identified
- [ ] Performance goals defined

**If This Fails:**
→ Ensure dev server is running on consistent hardware
→ Use incognito mode to avoid extension interference
→ Run multiple audits and average results
→ Check network throttling settings in DevTools

---

### Step 2: Implement Code Splitting and Lazy Loading

**What:** Split code into smaller chunks that load on demand

**How:**

**Route-Based Code Splitting:**
```typescript
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// ❌ BAD: All routes loaded upfront
// import Home from './pages/Home';
// import Dashboard from './pages/Dashboard';
// import Settings from './pages/Settings';

// ✅ GOOD: Lazy load route components
const Home = lazy(() => import('./pages/Home'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

export function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

**Component-Level Code Splitting:**
```typescript
import { lazy, Suspense } from 'react';

// Heavy components that aren't immediately needed
const Chart = lazy(() => import('./components/Chart'));
const DataTable = lazy(() => import('./components/DataTable'));
const RichTextEditor = lazy(() => import('./components/RichTextEditor'));

export function Dashboard() {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <h1>Dashboard</h1>
      
      {/* Load chart only when needed */}
      <button onClick={() => setShowChart(true)}>
        Show Chart
      </button>
      
      {showChart && (
        <Suspense fallback={<ChartSkeleton />}>
          <Chart data={data} />
        </Suspense>
      )}
    </div>
  );
}
```

**Named Exports Code Splitting:**
```typescript
// components/icons/index.ts

// ❌ BAD: Imports everything
// export { IconHome, IconUser, IconSettings } from './icons';

// ✅ GOOD: Named lazy imports
export const IconHome = lazy(() => 
  import('./icons').then(module => ({ default: module.IconHome }))
);

export const IconUser = lazy(() => 
  import('./icons').then(module => ({ default: module.IconUser }))
);

// Usage with Suspense
<Suspense fallback={<IconSkeleton />}>
  <IconHome />
</Suspense>
```

**Prefetch Critical Routes:**
```typescript
import { useEffect } from 'react';

export function Home() {
  useEffect(() => {
    // Prefetch dashboard when idle
    const prefetch = () => {
      import('./pages/Dashboard');
    };

    if ('requestIdleCallback' in window) {
      requestIdleCallback(prefetch);
    } else {
      setTimeout(prefetch, 1000);
    }
  }, []);

  return <div>Home Page</div>;
}
```

**Webpack Magic Comments:**
```typescript
// Name chunks for better debugging
const Dashboard = lazy(() => 
  import(/* webpackChunkName: "dashboard" */ './pages/Dashboard')
);

// Prefetch on hover
const Settings = lazy(() => 
  import(/* webpackPrefetch: true */ './pages/Settings')
);

// Preload (higher priority than prefetch)
const Critical = lazy(() => 
  import(/* webpackPreload: true */ './pages/Critical')
);
```

**Verification:**
- [ ] Initial bundle size reduced
- [ ] Routes load independently
- [ ] Heavy components lazy loaded
- [ ] Network waterfall shows chunks loading on demand

**If This Fails:**
→ Check that Suspense boundaries are properly placed
→ Verify build output shows separate chunks
→ Ensure components are actually heavy enough to warrant splitting
→ Test with network throttling to see actual impact

---

### Step 3: Optimize Component Rendering

**What:** Prevent unnecessary re-renders using React optimization techniques

**How:**

**Use React.memo for Pure Components:**
```typescript
// ❌ BAD: Re-renders on every parent update
export function ExpensiveComponent({ data }: { data: string }) {
  return <div>{performExpensiveCalculation(data)}</div>;
}

// ✅ GOOD: Only re-renders when data changes
export const ExpensiveComponent = React.memo(
  function ExpensiveComponent({ data }: { data: string }) {
    return <div>{performExpensiveCalculation(data)}</div>;
  }
);

// With custom comparison
export const ExpensiveComponent = React.memo(
  function ExpensiveComponent({ data }: { data: string }) {
    return <div>{performExpensiveCalculation(data)}</div>;
  },
  (prevProps, nextProps) => {
    // Return true if props are equal (skip re-render)
    return prevProps.data === nextProps.data;
  }
);
```

**useMemo for Expensive Calculations:**
```typescript
import { useMemo } from 'react';

export function DataVisualization({ data }: { data: number[] }) {
  // ❌ BAD: Recalculates on every render
  // const processedData = expensiveDataProcessing(data);

  // ✅ GOOD: Only recalculates when data changes
  const processedData = useMemo(
    () => expensiveDataProcessing(data),
    [data]
  );

  return <Chart data={processedData} />;
}

// Example: Filter large lists
export function UserList({ users, searchTerm }: Props) {
  const filteredUsers = useMemo(
    () => users.filter(user => 
      user.name.toLowerCase().includes(searchTerm.toLowerCase())
    ),
    [users, searchTerm]
  );

  return (
    <ul>
      {filteredUsers.map(user => (
        <UserItem key={user.id} user={user} />
      ))}
    </ul>
  );
}
```

**useCallback for Stable Function References:**
```typescript
import { useCallback } from 'react';

export function TodoList({ todos }: { todos: Todo[] }) {
  // ❌ BAD: Creates new function on every render
  // const handleToggle = (id: string) => {
  //   updateTodo(id);
  // };

  // ✅ GOOD: Stable function reference
  const handleToggle = useCallback((id: string) => {
    updateTodo(id);
  }, [updateTodo]);

  return (
    <ul>
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={handleToggle}
        />
      ))}
    </ul>
  );
}
```

**Virtualize Long Lists:**
```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

export function VirtualizedList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  return (
    <div
      ref={parentRef}
      style={{ height: '600px', overflow: 'auto' }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map(virtualItem => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <Item data={items[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

**Optimize Context to Prevent Cascading Re-renders:**
```typescript
// ❌ BAD: Single context causes everything to re-render
const AppContext = createContext({ user, theme, settings, notifications });

// ✅ GOOD: Split contexts by update frequency
const UserContext = createContext(user);
const ThemeContext = createContext(theme);
const SettingsContext = createContext(settings);
const NotificationsContext = createContext(notifications);

// Or use Context Selectors
import { createContext, useContextSelector } from 'use-context-selector';

const AppContext = createContext({ user, theme, settings });

function UserProfile() {
  // Only re-renders when user changes
  const user = useContextSelector(AppContext, ctx => ctx.user);
  return <div>{user.name}</div>;
}
```

**Verification:**
- [ ] React DevTools Profiler shows fewer re-renders
- [ ] Expensive calculations memoized
- [ ] Long lists virtualized
- [ ] Context splits implemented where needed

**If This Fails:**
→ Use React DevTools "Highlight updates" to visualize re-renders
→ Add console.logs to verify memoization working
→ Check dependency arrays in useMemo/useCallback
→ Ensure memo comparison functions are correct

---

### Step 4: Optimize Images and Assets

**What:** Reduce image sizes and implement modern formats

**How:**

**Modern Image Formats:**
```typescript
export function OptimizedImage({ src, alt }: { src: string; alt: string }) {
  return (
    <picture>
      {/* WebP for browsers that support it */}
      <source 
        type="image/webp" 
        srcSet={`${src}.webp`} 
      />
      {/* AVIF for cutting-edge browsers */}
      <source 
        type="image/avif" 
        srcSet={`${src}.avif`} 
      />
      {/* Fallback to JPEG */}
      <img 
        src={`${src}.jpg`} 
        alt={alt} 
        loading="lazy"
        decoding="async"
      />
    </picture>
  );
}
```

**Responsive Images:**
```typescript
export function ResponsiveImage({ src, alt }: Props) {
  return (
    <img
      src={`${src}?w=1024`}
      srcSet={`
        ${src}?w=320 320w,
        ${src}?w=640 640w,
        ${src}?w=1024 1024w,
        ${src}?w=1920 1920w
      `}
      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
      alt={alt}
      loading="lazy"
    />
  );
}
```

**Image CDN with Automatic Optimization:**
```typescript
// Using Cloudinary or similar
export function CloudinaryImage({ publicId, alt }: Props) {
  const baseUrl = 'https://res.cloudinary.com/your-cloud/image/upload';
  
  return (
    <img
      src={`${baseUrl}/f_auto,q_auto,w_800/${publicId}`}
      srcSet={`
        ${baseUrl}/f_auto,q_auto,w_320/${publicId} 320w,
        ${baseUrl}/f_auto,q_auto,w_640/${publicId} 640w,
        ${baseUrl}/f_auto,q_auto,w_1024/${publicId} 1024w
      `}
      sizes="100vw"
      alt={alt}
      loading="lazy"
    />
  );
}
```

**Blurhash Placeholders:**
```typescript
import { Blurhash } from 'react-blurhash';

export function ImageWithPlaceholder({ src, blurhash, alt }: Props) {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className="relative">
      {!loaded && (
        <Blurhash
          hash={blurhash}
          width="100%"
          height="100%"
          resolutionX={32}
          resolutionY={32}
          punch={1}
        />
      )}
      <img
        src={src}
        alt={alt}
        onLoad={() => setLoaded(true)}
        className={loaded ? 'opacity-100' : 'opacity-0'}
        style={{ transition: 'opacity 0.3s' }}
      />
    </div>
  );
}
```

**SVG Optimization:**
```bash
# Install SVGO
npm install -D svgo

# Optimize SVGs
npx svgo -f src/assets/icons -o public/icons

# Or use in Vite
import { defineConfig } from 'vite';
import svgr from 'vite-plugin-svgr';

export default defineConfig({
  plugins: [
    svgr({
      svgrOptions: {
        plugins: ['@svgr/plugin-svgo', '@svgr/plugin-jsx'],
        svgoConfig: {
          plugins: [
            {
              name: 'removeViewBox',
              active: false,
            },
          ],
        },
      },
    }),
  ],
});
```

**Font Optimization:**
```css
/* Preload critical fonts */
/* Add to index.html */
<link
  rel="preload"
  href="/fonts/inter-var.woff2"
  as="font"
  type="font/woff2"
  crossorigin
>

/* Use font-display for better loading */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter-var.woff2') format('woff2');
  font-weight: 100 900;
  font-display: swap; /* Show fallback immediately */
}

/* Subset fonts to only include needed characters */
/* Use tools like glyphhanger or subset via Google Fonts */
```

**Verification:**
- [ ] Images in modern formats (WebP/AVIF)
- [ ] Responsive srcset working
- [ ] Lazy loading implemented
- [ ] Fonts optimized and preloaded

**If This Fails:**
→ Use image CDN for automatic optimization
→ Check browser support for WebP/AVIF
→ Verify font loading with Chrome DevTools Network tab
→ Test with slow 3G throttling

---

### Step 5: Optimize JavaScript Bundle

**What:** Reduce bundle size and improve code efficiency

**How:**

**Tree Shaking:**
```typescript
// ❌ BAD: Imports entire library
import _ from 'lodash';
const result = _.debounce(fn, 300);

// ✅ GOOD: Import only what you need
import debounce from 'lodash/debounce';
const result = debounce(fn, 300);

// Even better: Use ES modules that tree-shake well
import { debounce } from 'lodash-es';
```

**Replace Heavy Libraries:**
```typescript
// ❌ moment.js (69KB minified)
import moment from 'moment';
const date = moment().format('YYYY-MM-DD');

// ✅ date-fns (2KB per function)
import { format } from 'date-fns';
const date = format(new Date(), 'yyyy-MM-dd');

// ❌ axios (13KB minified)
import axios from 'axios';

// ✅ native fetch (0KB)
const response = await fetch('/api/data');
const data = await response.json();
```

**Dynamic Imports for Conditional Code:**
```typescript
// Only load PDF library when needed
async function exportToPDF() {
  const { jsPDF } = await import('jspdf');
  const doc = new jsPDF();
  // ... generate PDF
}

// Load charts only when tab is active
function ChartTab() {
  const [Chart, setChart] = useState(null);

  useEffect(() => {
    import('react-chartjs-2').then(module => {
      setChart(() => module.Chart);
    });
  }, []);

  return Chart ? <Chart data={data} /> : <Loading />;
}
```

**Analyze and Remove Unused Code:**
```bash
# Find unused exports
npm install -D ts-prune
npx ts-prune

# Find duplicate dependencies
npm install -D depcheck
npx depcheck

# Analyze bundle
npm run build
npx vite-bundle-visualizer
```

**Minification and Compression:**
```javascript
// vite.config.ts
export default defineConfig({
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.logs in production
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
        },
      },
    },
  },
});

// Enable Brotli compression
import compression from 'vite-plugin-compression';

export default defineConfig({
  plugins: [
    compression({ algorithm: 'brotliCompress' }),
  ],
});
```

**Verification:**
- [ ] Bundle size reduced by >20%
- [ ] No duplicate dependencies
- [ ] Heavy libraries replaced
- [ ] Tree shaking working

**If This Fails:**
→ Use webpack-bundle-analyzer to find culprits
→ Check for circular dependencies
→ Ensure ESM imports for tree shaking
→ Review package.json for unnecessary dependencies

---

### Step 6: Implement Performance Monitoring

**What:** Track performance metrics in production

**How:**

**Web Vitals Monitoring:**
```typescript
import { onCLS, onFID, onLCP, onFCP, onTTFB } from 'web-vitals';

function sendToAnalytics(metric: Metric) {
  // Send to your analytics service
  fetch('/api/analytics', {
    method: 'POST',
    body: JSON.stringify(metric),
  });
}

onCLS(sendToAnalytics);
onFID(sendToAnalytics);
onLCP(sendToAnalytics);
onFCP(sendToAnalytics);
onTTFB(sendToAnalytics);
```

**React Performance Monitoring:**
```typescript
import { Profiler, ProfilerOnRenderCallback } from 'react';

const onRenderCallback: ProfilerOnRenderCallback = (
  id,
  phase,
  actualDuration,
  baseDuration,
  startTime,
  commitTime,
) => {
  if (actualDuration > 16) { // Slower than 60fps
    console.warn(`Slow render detected in ${id}: ${actualDuration}ms`);
    
    // Send to monitoring service
    fetch('/api/performance', {
      method: 'POST',
      body: JSON.stringify({
        component: id,
        phase,
        duration: actualDuration,
        timestamp: Date.now(),
      }),
    });
  }
};

export function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      {/* Your app */}
    </Profiler>
  );
}
```

**Custom Performance Marks:**
```typescript
export function trackComponentPerformance<T extends ComponentType<any>>(
  Component: T,
  componentName: string
): T {
  return React.forwardRef((props, ref) => {
    useEffect(() => {
      performance.mark(`${componentName}-mount`);
      
      return () => {
        performance.mark(`${componentName}-unmount`);
        performance.measure(
          `${componentName}-lifetime`,
          `${componentName}-mount`,
          `${componentName}-unmount`
        );
      };
    }, []);

    return <Component {...props} ref={ref} />;
  }) as T;
}

// Usage
const TrackedDashboard = trackComponentPerformance(Dashboard, 'Dashboard');
```

**Performance Budget in CI:**
```json
// lighthouse-budget.json
[
  {
    "path": "/*",
    "resourceSizes": [
      {
        "resourceType": "script",
        "budget": 300
      },
      {
        "resourceType": "stylesheet",
        "budget": 50
      },
      {
        "resourceType": "image",
        "budget": 500
      },
      {
        "resourceType": "total",
        "budget": 1000
      }
    ],
    "resourceCounts": [
      {
        "resourceType": "third-party",
        "budget": 10
      }
    ]
  }
]
```

```yaml
# .github/workflows/performance.yml
name: Performance Budget

on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build app
        run: npm ci && npm run build
      - name: Run Lighthouse
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            http://localhost:3000
          budgetPath: ./lighthouse-budget.json
          uploadArtifacts: true
```

**Verification:**
- [ ] Web Vitals tracked
- [ ] Performance data sent to analytics
- [ ] Slow renders logged
- [ ] Performance budget enforced in CI

**If This Fails:**
→ Ensure analytics endpoint is working
→ Check CSP headers allow analytics requests
→ Verify performance marks are placed correctly
→ Test monitoring in production-like environment

---

### Step 7: Optimize Third-Party Scripts

**What:** Reduce impact of external scripts on performance

**How:**

**Defer Non-Critical Scripts:**
```html
<!-- ❌ BAD: Blocks rendering -->
<script src="https://analytics.example.com/script.js"></script>

<!-- ✅ GOOD: Loads asynchronously -->
<script async src="https://analytics.example.com/script.js"></script>

<!-- ✅ BETTER: Loads after page is parsed -->
<script defer src="https://analytics.example.com/script.js"></script>
```

**Lazy Load Third-Party Components:**
```typescript
// Load analytics only after user interaction
export function App() {
  useEffect(() => {
    const loadAnalytics = () => {
      const script = document.createElement('script');
      script.src = 'https://analytics.example.com/script.js';
      script.async = true;
      document.body.appendChild(script);
    };

    // Load after idle
    if ('requestIdleCallback' in window) {
      requestIdleCallback(loadAnalytics);
    } else {
      setTimeout(loadAnalytics, 2000);
    }
  }, []);

  return <div>App</div>;
}
```

**Self-Host Third-Party Scripts:**
```bash
# Download and serve locally
curl https://analytics.example.com/script.js > public/analytics.js

# Update script tag
<script defer src="/analytics.js"></script>

# Or use Partytown to run in Web Worker
npm install @builder.io/partytown
```

**Partytown for Web Workers:**
```typescript
import { Partytown } from '@builder.io/partytown/react';

export function App() {
  return (
    <>
      <Partytown
        debug={false}
        forward={['dataLayer.push']}
      />
      
      {/* Third-party scripts run in worker */}
      <script
        type="text/partytown"
        src="https://analytics.example.com/script.js"
      />
      
      {/* Your app */}
    </>
  );
}
```

**Verification:**
- [ ] Third-party scripts deferred
- [ ] Non-essential scripts lazy loaded
- [ ] Critical scripts self-hosted
- [ ] Main thread blocking reduced

**If This Fails:**
→ Check if scripts support async/defer
→ Test that scripts still work when deferred
→ Verify Partytown compatibility with your scripts
→ Monitor for broken functionality after changes

---

### Step 8: Implement Caching Strategies

**What:** Use service workers and HTTP caching to improve repeat visits

**How:**

**Service Worker with Workbox:**
```bash
npm install -D workbox-webpack-plugin
# or for Vite
npm install -D vite-plugin-pwa
```

```typescript
// vite.config.ts
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
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
            },
          },
          {
            urlPattern: /^https:\/\/cdn\.example\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'cdn-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 30, // 30 days
              },
            },
          },
        ],
      },
    }),
  ],
});
```

**HTTP Cache Headers:**
```typescript
// next.config.js or server config
module.exports = {
  async headers() {
    return [
      {
        source: '/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-cache, must-revalidate',
          },
        ],
      },
    ];
  },
};
```

**React Query for Data Caching:**
```typescript
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      cacheTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* Your app */}
    </QueryClientProvider>
  );
}

function UserProfile() {
  const { data, isLoading } = useQuery({
    queryKey: ['user'],
    queryFn: fetchUser,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  if (isLoading) return <Skeleton />;
  return <div>{data.name}</div>;
}
```

**Verification:**
- [ ] Service worker installed
- [ ] Static assets cached
- [ ] API responses cached appropriately
- [ ] Cache invalidation working

**If This Fails:**
→ Check service worker registration in DevTools
→ Verify cache headers in Network tab
→ Test with disabled cache to ensure cache isn't hiding bugs
→ Clear service worker cache during debugging

---

## Verification Checklist

After completing this workflow:

- [ ] Lighthouse Performance score > 90
- [ ] Bundle size reduced by 30%+
- [ ] FCP < 1.8s, LCP < 2.5s
- [ ] TBT < 200ms
- [ ] No layout shifts (CLS < 0.1)
- [ ] Images optimized and lazy loaded
- [ ] Code splitting implemented
- [ ] Unnecessary re-renders eliminated
- [ ] Third-party scripts optimized
- [ ] Caching strategies in place
- [ ] Performance monitoring active
- [ ] Real user metrics tracked

---

## Common Issues & Solutions

### Issue: Bundle Size Still Too Large

**Symptoms:**
- Initial load takes >3 seconds
- Large JavaScript files in Network tab
- Bundle analyzer shows huge chunks

**Solution:**
```bash
# Find large dependencies
npm install -D webpack-bundle-analyzer

# Replace heavy libraries
# Before: moment.js (69KB)
npm uninstall moment
npm install date-fns

# Before: lodash (70KB)
npm uninstall lodash
npm install lodash-es

# Use dynamic imports
const HeavyComponent = lazy(() => import('./HeavyComponent'));

# Split vendor chunks
// vite.config.ts
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        },
      },
    },
  },
};
```

**Prevention:**
- Set bundle size budgets
- Review dependencies before adding
- Use bundlephobia.com to check package sizes

---

### Issue: Components Re-rendering Too Often

**Symptoms:**
- Laggy interactions
- React DevTools shows frequent updates
- CPU usage high during typing

**Solution:**
```typescript
// 1. Memoize expensive components
export const ExpensiveList = React.memo(function ExpensiveList({ items }) {
  return <ul>{items.map(item => <li key={item.id}>{item.name}</li>)}</ul>;
});

// 2. Use useCallback for event handlers
const handleClick = useCallback(() => {
  doSomething();
}, [dependency]);

// 3. Split context to prevent cascading updates
// Instead of one big context, split by update frequency
const AuthContext = createContext(auth);
const ThemeContext = createContext(theme);

// 4. Use state colocation - move state closer to where it's used
// Instead of global state for modal, use local state
const [isOpen, setIsOpen] = useState(false);
```

**Prevention:**
- Use React DevTools Profiler regularly
- Add render logging in development
- Keep state as local as possible
- Avoid passing new object/array references as props

---

## Best Practices

### DO:
✅ Measure before optimizing (avoid premature optimization)
✅ Use React.memo judiciously (not everywhere)
✅ Implement code splitting at route level
✅ Lazy load heavy components
✅ Use modern image formats (WebP, AVIF)
✅ Implement virtualization for long lists
✅ Monitor Core Web Vitals in production
✅ Set performance budgets in CI
✅ Optimize critical rendering path
✅ Use production builds for testing
✅ Implement proper caching strategies

### DON'T:
❌ Optimize without measuring first
❌ Wrap every component in React.memo
❌ Ignore bundle size warnings
❌ Load all routes upfront
❌ Use inline functions as props to memoized components
❌ Forget to lazy load images
❌ Skip compression (gzip/brotli)
❌ Ignore third-party script impact
❌ Use development builds in production
❌ Over-optimize at the expense of readability
❌ Forget about mobile performance

---

## Related Workflows

**Prerequisites:**
- [react_component_creation.md](./react_component_creation.md) - Component structure
- [build_deployment.md](./build_deployment.md) - Production builds

**Next Steps:**
- [e2e_testing_workflow.md](./e2e_testing_workflow.md) - Performance testing
- [accessibility_workflow.md](./accessibility_workflow.md) - Accessible performance

**Related:**
- [responsive_design_implementation.md](./responsive_design_implementation.md) - Mobile performance
- [api_integration_patterns.md](./api_integration_patterns.md) - API optimization

---

## Tags
`frontend development` `performance` `optimization` `web vitals` `react` `bundle-size` `lazy-loading` `code-splitting`
