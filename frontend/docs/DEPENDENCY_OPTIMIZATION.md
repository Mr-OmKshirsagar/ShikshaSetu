# Dependency Optimization Guide for ShikshaSetu

## Overview
This guide covers best practices for managing and optimizing dependencies to reduce bundle size and improve load times.

## Bundle Analysis

### Run Bundle Analysis
```bash
# Install rollup-plugin-visualizer
npm install -D rollup-plugin-visualizer

# Build with analysis (already configured in vite.config.ts)
npm run build

# View the generated stats.html in dist/
```

## Current Dependencies Audit

### Heavy Dependencies (> 100KB)
1. **recharts** (~400KB) - Charts library
   - Used in: Admin analytics pages
   - Optimization: Lazy load chart pages ✅ (already implemented)
   
2. **@radix-ui/** (~300KB total) - UI primitives
   - Used in: All UI components
   - Optimization: Tree-shaking enabled, using specific packages ✅

3. **framer-motion** (~150KB) - Animation library
   - Used in: UI animations
   - Optimization: Consider lazy loading or replacing with CSS animations

4. **react-markdown** (~80KB) - Markdown renderer
   - Used in: Content rendering
   - Optimization: Lazy load when needed

5. **lucide-react** (~100KB) - Icon library
   - Used in: Icons throughout app
   - Optimization: Consider using individual icon imports

## Optimization Strategies

### 1. Use Named Imports (Tree-Shaking)

❌ **Bad:**
```tsx
import * as Lucide from 'lucide-react';
<Lucide.Home />
```

✅ **Good:**
```tsx
import { Home, Settings, User } from 'lucide-react';
<Home />
```

### 2. Lazy Load Heavy Components

❌ **Bad:**
```tsx
import { LineChart } from 'recharts';

function Dashboard() {
  return <LineChart data={data} />;
}
```

✅ **Good:**
```tsx
const ChartComponent = lazy(() => import('./ChartComponent'));

function Dashboard() {
  return (
    <Suspense fallback={<ChartSkeleton />}>
      <ChartComponent data={data} />
    </Suspense>
  );
}
```

### 3. Use Lightweight Alternatives

Consider replacing heavy libraries with lighter alternatives:

| Heavy Library | Lightweight Alternative | Savings |
|--------------|------------------------|---------|
| moment.js (232KB) | date-fns (13KB) | ~95% |
| lodash (72KB) | lodash-es + tree-shaking | ~80% |
| axios (13KB) | native fetch | 100% |
| chart.js (186KB) | lightweight-charts (50KB) | ~73% |

### 4. Dynamic Imports for Features

```tsx
// Only load when user clicks "Export"
async function handleExport() {
  const { exportToCSV } = await import('@/utils/export');
  exportToCSV(data);
}
```

### 5. Optimize Radix UI Imports

Already optimized ✅ - using specific packages:
```tsx
import * as DialogPrimitive from "@radix-ui/react-dialog";
// NOT: import { Dialog } from "@radix-ui/react";
```

## Bundle Size Targets

### Current Build Analysis
- Total bundle size: ~800KB (gzipped: ~250KB)
- Vendor chunks: ~600KB (gzipped: ~180KB)
- App code: ~200KB (gzipped: ~70KB)

### Target Metrics
- Initial JS load: < 200KB (gzipped)
- Total JS (with lazy): < 500KB (gzipped)
- CSS: < 50KB (gzipped)

## Checklist for Adding New Dependencies

Before adding a new dependency, ask:

- [ ] Is this necessary? Can I build it myself?
- [ ] Bundle size? Check on [bundlephobia.com](https://bundlephobia.com)
- [ ] Tree-shakeable? Does it support ES modules?
- [ ] Last updated? Is it actively maintained?
- [ ] Dependencies count? Fewer is better
- [ ] TypeScript support? Better DX and smaller builds
- [ ] Can it be lazy loaded? Load only when needed

### Size Guidelines
- ✅ Tiny: < 5KB
- ⚠️ Small: 5-20KB
- ⚠️ Medium: 20-50KB
- ❌ Large: > 50KB (requires justification)

## Common Optimization Patterns

### Pattern 1: Code Splitting by Route
```tsx
// Already implemented in App.tsx ✅
const TrainerDashboard = lazy(() => import("./pages/trainer/TrainerDashboard"));
```

### Pattern 2: Conditional Loading
```tsx
// Load heavy library only in production
const Analytics = import.meta.env.PROD
  ? lazy(() => import('./Analytics'))
  : () => <div>Analytics disabled in dev</div>;
```

### Pattern 3: Debounced Imports
```tsx
// Load search library only after user starts typing
const [SearchLib, setSearchLib] = useState(null);

const handleFocus = async () => {
  if (!SearchLib) {
    const lib = await import('fuse.js');
    setSearchLib(() => lib.default);
  }
};
```

## Monitoring Bundle Size

### In CI/CD
Add bundle size checks to prevent regressions:

```bash
# In package.json scripts
"check-size": "vite build && size-limit"
```

### GitHub Actions
```yaml
- name: Check bundle size
  run: npm run check-size
```

## Quick Wins Implemented ✅

1. ✅ Vite code splitting with 9 vendor chunks
2. ✅ Tree-shaking enabled in production
3. ✅ Dynamic imports for all pages
4. ✅ Terser minification with console removal
5. ✅ CSS code splitting
6. ✅ Route prefetching for faster navigation
7. ✅ Service worker for caching

## Future Optimizations

1. Consider replacing framer-motion with CSS animations
2. Implement virtual scrolling for large lists
3. Use react-window for long data tables
4. Evaluate replacing recharts with lighter alternative
5. Implement progressive image loading
6. Add HTTP/2 server push for critical resources

## Resources
- [Bundlephobia](https://bundlephobia.com) - Check package sizes
- [Webpack Bundle Analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)
- [Import Cost VSCode Extension](https://marketplace.visualstudio.com/items?itemName=wix.vscode-import-cost)
