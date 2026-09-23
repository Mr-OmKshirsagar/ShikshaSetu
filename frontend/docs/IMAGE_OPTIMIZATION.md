# Image Optimization Guide for ShikshaSetu

## Overview
This guide provides best practices for optimizing images to improve page load performance.

## Image Formats

### Recommended Formats
1. **WebP**: Best for photos and complex images (80% smaller than JPEG)
2. **SVG**: Best for logos, icons, and simple graphics (vector, scalable)
3. **PNG**: Only for images requiring transparency when WebP not supported
4. **JPEG**: Fallback for older browsers

## Optimization Tools

### Online Tools
- **TinyPNG** (https://tinypng.com) - PNG/JPEG compression
- **Squoosh** (https://squoosh.app) - Advanced image compression
- **SVGO** (https://jakearchibald.github.io/svgomg/) - SVG optimization

### CLI Tools
```bash
# Install ImageMagick for batch conversion
npm install -g imagemagick

# Convert PNG to WebP
convert input.png -quality 85 output.webp

# Resize and optimize
convert input.jpg -resize 1200x -quality 85 output.jpg
```

## Image Sizing Guidelines

### Logo Images
- Small logo: 120x30px (navbar)
- Medium logo: 180x45px (general use)
- Large logo: 240x60px (hero sections)

### Dashboard Images
- Thumbnail: 150x150px
- Card image: 400x300px
- Hero banner: 1200x400px
- Profile photo: 200x200px

### General Rules
- Maximum width: 1920px (for hero images)
- Maximum file size: 200KB per image
- Use responsive images with `srcset` for different screen sizes

## Using OptimizedImage Component

```tsx
import { OptimizedImage } from "@/components/OptimizedImage";

// Basic usage with lazy loading (default)
<OptimizedImage
  src="/assets/image.jpg"
  alt="Description"
  className="w-full h-auto"
/>

// Priority image (above the fold)
<OptimizedImage
  src="/assets/hero.jpg"
  alt="Hero image"
  priority={true}
  className="w-full h-auto"
/>

// With blur placeholder
<OptimizedImage
  src="/assets/photo.jpg"
  alt="Photo"
  placeholder="blur"
  className="aspect-video"
/>
```

## Checklist for New Images

- [ ] Compress image to reduce file size
- [ ] Convert to WebP format when possible
- [ ] Resize to appropriate dimensions
- [ ] Add descriptive alt text
- [ ] Use `loading="lazy"` for below-the-fold images
- [ ] Use `loading="eager"` or `priority={true}` for above-the-fold images
- [ ] Test image loads on slow 3G connection

## Performance Targets

- First Contentful Paint (FCP): < 1.8s
- Largest Contentful Paint (LCP): < 2.5s
- Cumulative Layout Shift (CLS): < 0.1

## Current Image Audit

### Existing Images
- `/assets/shikshasetu-logo.png` - 20KB ✅
- `/assets/shikshasetu-icon.png` - 8KB ✅
- `shikshasetu-square.svg` - Vector ✅
- `shikshasetu-icon.svg` - Vector ✅

### Action Items
1. Convert PNG logos to WebP format for 30-50% size reduction
2. Audit all dashboard images for size optimization
3. Implement responsive image loading with `srcset`
4. Add blur placeholders for content images

## Resources
- [Web.dev Image Optimization](https://web.dev/fast/#optimize-your-images)
- [MDN Responsive Images](https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Responsive_images)
