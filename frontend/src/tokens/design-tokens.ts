/**
 * SemanticFS Design Tokens
 * 
 * Strict canonical tokens extracted from the Figma design specification.
 * No arbitrary hex codes or "close enough" values are permitted in components.
 */

export const COLORS = {
  base: '#16161D',
  surface: '#1E1F29',
  border: '#2A2B38',
  textPrimary: '#F2F1ED',
  textSecondary: '#8B8D98',
  accent: '#9D7CFF',
  success: '#7FBF6B',
  warning: '#E6C265',
  danger: '#E5637A',
  highlight: '#FF6FA8',
  mono: '#6FD3E8',
} as const;

export const EXT_COLORS: Record<string, string> = {
  md: '#6FD3E8',
  txt: '#8B8D98',
  pdf: '#E5637A',
  py: '#E6C265',
  ts: '#6FD3E8',
  tsx: '#9D7CFF',
  js: '#E6C265',
  json: '#7FBF6B',
  csv: '#7FBF6B',
  png: '#FF6FA8',
  jpg: '#FF6FA8',
  mp4: '#FF6FA8',
  zip: '#8B8D98',
  dir: '#8B8D98',
} as const;

export const SPACING = {
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  6: 24,
  8: 32,
  12: 48,
} as const;

export const FONT_SIZES = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 20,
  xl: 28,
} as const;

export const FONTS = {
  sans: "'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  mono: "'JetBrains Mono', monospace",
} as const;

export const RADII = {
  sm: 4,
  md: 6,
  lg: 10,
} as const;

export type ColorKey = keyof typeof COLORS;
export type SpacingKey = keyof typeof SPACING;
export type FontSizeKey = keyof typeof FONT_SIZES;
export type RadiusKey = keyof typeof RADII;
