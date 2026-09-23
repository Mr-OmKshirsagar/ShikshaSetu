/**
 * Route prefetching utility for preloading critical routes
 * Improves perceived performance by loading likely next pages in the background
 */

type RouteModule = () => Promise<any>;

const prefetchCache = new Set<string>();

/**
 * Prefetch a lazy-loaded component module
 * @param moduleLoader - The lazy import function
 * @param routeKey - Unique identifier for caching
 */
export function prefetchRoute(moduleLoader: RouteModule, routeKey: string): void {
  // Skip if already prefetched
  if (prefetchCache.has(routeKey)) {
    return;
  }

  // Mark as prefetched before attempting to avoid duplicate requests
  prefetchCache.add(routeKey);

  // Use requestIdleCallback if available, otherwise setTimeout
  if ("requestIdleCallback" in window) {
    window.requestIdleCallback(
      () => {
        moduleLoader().catch((err) => {
          console.warn(`Failed to prefetch route: ${routeKey}`, err);
          prefetchCache.delete(routeKey); // Remove from cache on failure
        });
      },
      { timeout: 2000 }
    );
  } else {
    setTimeout(() => {
      moduleLoader().catch((err) => {
        console.warn(`Failed to prefetch route: ${routeKey}`, err);
        prefetchCache.delete(routeKey);
      });
    }, 100);
  }
}

/**
 * Prefetch multiple routes
 */
export function prefetchRoutes(routes: Array<{ loader: RouteModule; key: string }>): void {
  routes.forEach(({ loader, key }) => {
    prefetchRoute(loader, key);
  });
}

/**
 * Hook to prefetch routes on component mount
 * Usage: usePrefetchRoutes([{ loader: () => import('./Page'), key: 'page' }])
 */
export function usePrefetchRoutes(routes: Array<{ loader: RouteModule; key: string }>): void {
  // Use a ref to ensure we only prefetch once
  const hasPrefetched = React.useRef(false);

  React.useEffect(() => {
    if (!hasPrefetched.current) {
      hasPrefetched.current = true;
      // Delay prefetching to not interfere with initial page load
      setTimeout(() => prefetchRoutes(routes), 1000);
    }
  }, []); // Empty deps - only run once on mount
}

// Add React import for the hook
import React from "react";
