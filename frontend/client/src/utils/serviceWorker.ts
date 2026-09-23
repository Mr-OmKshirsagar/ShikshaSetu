/**
 * Service Worker Registration and Management
 * Handles registration, updates, and lifecycle of the service worker
 */

export interface ServiceWorkerConfig {
  onUpdate?: (registration: ServiceWorkerRegistration) => void;
  onSuccess?: (registration: ServiceWorkerRegistration) => void;
  onError?: (error: Error) => void;
}

/**
 * Register the service worker
 * Should be called after the app has loaded to avoid competing for network resources
 */
export async function registerServiceWorker(config: ServiceWorkerConfig = {}): Promise<void> {
  // Only register in production and if browser supports service workers
  if (import.meta.env.DEV || !("serviceWorker" in navigator)) {
    return;
  }

  try {
    // Wait for page load to not impact initial page performance
    if (document.readyState === "loading") {
      await new Promise((resolve) => {
        window.addEventListener("load", resolve, { once: true });
      });
    }

    // Register the service worker
    const registration = await navigator.serviceWorker.register("/sw.js", {
      scope: "/",
    });

    console.log("[SW] Service worker registered successfully");

    // Check for updates
    registration.addEventListener("updatefound", () => {
      const newWorker = registration.installing;
      if (!newWorker) return;

      newWorker.addEventListener("statechange", () => {
        if (newWorker.state === "installed" && navigator.serviceWorker.controller) {
          // New service worker available
          console.log("[SW] New content available, please refresh");
          config.onUpdate?.(registration);
        } else if (newWorker.state === "activated") {
          // Service worker activated successfully
          console.log("[SW] Service worker activated");
          config.onSuccess?.(registration);
        }
      });
    });

    // Check for updates periodically (every hour)
    setInterval(() => {
      registration.update();
    }, 60 * 60 * 1000);

    // Initial update check
    registration.update();
  } catch (error) {
    console.error("[SW] Service worker registration failed:", error);
    config.onError?.(error as Error);
  }
}

/**
 * Unregister all service workers
 * Useful for debugging or when service worker causes issues
 */
export async function unregisterServiceWorker(): Promise<boolean> {
  if (!("serviceWorker" in navigator)) {
    return false;
  }

  try {
    const registrations = await navigator.serviceWorker.getRegistrations();
    const results = await Promise.all(registrations.map((reg) => reg.unregister()));
    console.log("[SW] Service workers unregistered");
    return results.every((result) => result === true);
  } catch (error) {
    console.error("[SW] Failed to unregister service workers:", error);
    return false;
  }
}

/**
 * Check if service worker is supported and registered
 */
export function isServiceWorkerSupported(): boolean {
  return "serviceWorker" in navigator;
}

/**
 * Get the current service worker registration status
 */
export async function getServiceWorkerStatus(): Promise<{
  supported: boolean;
  registered: boolean;
  controller: ServiceWorker | null;
}> {
  const supported = isServiceWorkerSupported();

  if (!supported) {
    return { supported: false, registered: false, controller: null };
  }

  const registration = await navigator.serviceWorker.getRegistration();
  return {
    supported: true,
    registered: !!registration,
    controller: navigator.serviceWorker.controller,
  };
}

/**
 * Force skip waiting and activate new service worker immediately
 */
export function skipWaiting(): void {
  if (navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage({ type: "SKIP_WAITING" });
  }
}
