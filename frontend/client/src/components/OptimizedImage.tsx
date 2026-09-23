import React, { useState, useEffect, useRef } from "react";

interface OptimizedImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  className?: string;
  priority?: boolean;
  quality?: number;
  placeholder?: "blur" | "empty";
  placeholderSrc?: string;
}

/**
 * Optimized Image component with lazy loading, intersection observer,
 * and blur placeholder support for better perceived performance
 */
export function OptimizedImage({
  src,
  alt,
  className = "",
  priority = false,
  quality = 90,
  placeholder = "empty",
  placeholderSrc,
  ...props
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(priority);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    if (priority) return; // Skip intersection observer for priority images

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.disconnect();
          }
        });
      },
      {
        rootMargin: "50px", // Start loading 50px before image enters viewport
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [priority]);

  const handleLoad = () => {
    setIsLoaded(true);
  };

  const imgSrc = isInView ? src : placeholderSrc || "";
  const loading = priority ? "eager" : "lazy";

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {placeholder === "blur" && !isLoaded && (
        <div className="absolute inset-0 bg-slate-200 animate-pulse" />
      )}
      <img
        ref={imgRef}
        src={imgSrc}
        alt={alt}
        loading={loading}
        decoding={priority ? "sync" : "async"}
        onLoad={handleLoad}
        className={`w-full h-full object-cover transition-opacity duration-300 ${
          isLoaded ? "opacity-100" : "opacity-0"
        }`}
        {...props}
      />
    </div>
  );
}
