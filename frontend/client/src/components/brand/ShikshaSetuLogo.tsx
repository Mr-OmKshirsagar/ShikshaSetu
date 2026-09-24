import React from "react";
import { Link } from "wouter";

export type ShikshaSetuLogoVariant = "full" | "compact" | "icon" | "mobile";
export type ShikshaSetuLogoSize = "sm" | "md" | "lg" | "xl";

export interface ShikshaSetuLogoProps {
  /**
   * Logo variant:
   * - "full": Full official logo asset with emblem, wordmark, and subtitle contained.
   * - "compact": Official emblem icon side-by-side with brand typography (ideal for narrow horizontal navbars).
   * - "icon": Official emblem icon alone.
   * - "mobile": Responsively sized for mobile headers.
   */
  variant?: ShikshaSetuLogoVariant;
  /**
   * Size preset:
   * - "sm": Compact/subtle
   * - "md": Standard (sidebar / headers)
   * - "lg": Prominent (login card, hero)
   * - "xl": Large showcase
   */
  size?: ShikshaSetuLogoSize;
  /**
   * Optional custom subtitle (used in "compact" mode, defaults to "Capability Intelligence")
   */
  subtitle?: string;
  /**
   * If provided, wraps the logo in an accessible navigation link.
   */
  href?: string;
  /**
   * Optional class name for the wrapper element.
   */
  className?: string;
  /**
   * Optional class name for the <img> element.
   */
  imgClassName?: string;
  /**
   * Accessible alt text. Defaults strictly to "ShikshaSetu".
   */
  alt?: string;
  /**
   * Eager loading for above-the-fold brand elements.
   */
  priority?: boolean;
}

const FULL_SIZE_CLASSES: Record<ShikshaSetuLogoSize, string> = {
  sm: "h-10 w-auto",
  md: "h-14 w-auto",
  lg: "h-20 w-auto",
  xl: "h-28 w-auto",
};

const ICON_SIZE_CLASSES: Record<ShikshaSetuLogoSize, string> = {
  sm: "h-7 w-auto",
  md: "h-9 w-auto",
  lg: "h-12 w-auto",
  xl: "h-16 w-auto",
};

export const ShikshaSetuLogo: React.FC<ShikshaSetuLogoProps> = ({
  variant = "full",
  size = "md",
  subtitle,
  href,
  className = "",
  imgClassName = "",
  alt = "ShikshaSetu",
  priority = false,
}) => {
  const loadingAttr = priority ? "eager" : "lazy";

  let content: React.ReactNode;

  if (variant === "icon") {
    const sizeCls = ICON_SIZE_CLASSES[size] || ICON_SIZE_CLASSES.md;
    content = (
      <img
        src="/assets/shikshasetu-logo-official.png"
        alt={alt}
        loading={loadingAttr}
        className={`max-w-full select-none object-contain ${sizeCls} ${imgClassName}`}
      />
    );
  } else if (variant === "compact" || variant === "mobile") {
    const iconCls = variant === "mobile" ? "h-8 w-auto" : (ICON_SIZE_CLASSES[size] || "h-8 w-auto");
    content = (
      <div className={`inline-flex items-center gap-2.5 select-none ${className}`}>
        <img
          src="/assets/shikshasetu-logo-official.png"
          alt={alt}
          loading={loadingAttr}
          className={`flex-shrink-0 object-contain ${iconCls} ${imgClassName}`}
        />
        <div className="flex items-center gap-2">
          <span className="text-base sm:text-[17px] font-bold tracking-tight text-[#123057] leading-none">
            ShikshaSetu
          </span>
          {subtitle && (
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#087f76] leading-none">
              {subtitle}
            </span>
          )}
        </div>
      </div>
    );
  } else {
    // "full" variant
    // Renders the exact official asset containing [Emblem], SHIKSHASETU, and CAPABILITY INTELLIGENCE.
    // Preserves aspect ratio, never stretches, never crops, object-fit: contain.
    const sizeCls = FULL_SIZE_CLASSES[size] || FULL_SIZE_CLASSES.md;
    content = (
      <div className={`inline-flex items-center justify-center ${className}`}>
        <img
          src="/assets/shikshasetu-logo-official.png"
          alt={alt}
          loading={loadingAttr}
          className={`max-w-full select-none object-contain ${sizeCls} ${imgClassName}`}
        />
      </div>
    );
  }

  if (href) {
    // If href starts with http or #, use <a>, otherwise use wouter <Link>
    if (href.startsWith("http") || href.startsWith("#")) {
      return (
        <a
          href={href}
          aria-label={alt}
          className="inline-flex items-center focus:outline-hidden focus:ring-2 focus:ring-[#087f76]/40 rounded-lg transition-opacity hover:opacity-90"
        >
          {content}
        </a>
      );
    }
    return (
      <Link
        href={href}
        aria-label={alt}
        className="inline-flex items-center focus:outline-hidden focus:ring-2 focus:ring-[#087f76]/40 rounded-lg transition-opacity hover:opacity-90"
      >
        {content}
      </Link>
    );
  }

  return <>{content}</>;
};

export default ShikshaSetuLogo;
