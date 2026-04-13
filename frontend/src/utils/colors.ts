import type { BlockStyle } from "@/types/preprocessing";

// --- Start of Color Conversion Helpers ---

/**
 * Converts a hex color string to an rgba string.
 * @param hex - The hex color (e.g., "#RRGGBB").
 * @param alpha - The alpha transparency (0 to 1).
 * @returns The rgba string.
 */
function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Creates a full BlockStyle object from a single hex color.
 * @param hexColor - The base hex color.
 * @returns A BlockStyle object with solid and shadow colors.
 */
export function createBlockStyle(hexColor: string): BlockStyle {
  return {
    solid: hexColor,
    shadow: hexToRgba(hexColor, 0.25), // Standard shadow for all blocks
  };
}


// --- Color Generation Logic ---

export const ARC_COLORS: string[] = [
  '#A1C9F4', '#FFB482', '#8DE5A1', '#FF9F9B', '#D0BBFF',
  '#FBE790', '#93E0E3', '#FFC8D9', '#C4D79B', '#B5B9FF',
];

function rgbToHsl(r: number, g: number, b: number): [number, number, number] {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  let h = 0, s = 0, l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      case b: h = (r - g) / d + 4; break;
    }
    h /= 6;
  }
  return [h * 360, s, l];
}

function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  let r: number, g: number, b: number;
  if (s === 0) {
    r = g = b = l; // achromatic
  } else {
    const hue2rgb = (p: number, q: number, t: number) => {
      if (t < 0) t += 1; if (t > 1) t -= 1;
      if (t < 1/6) return p + (q - p) * 6 * t;
      if (t < 1/2) return q;
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
      return p;
    };
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    h /= 360;
    r = hue2rgb(p, q, h + 1/3); g = hue2rgb(p, q, h); b = hue2rgb(p, q, h - 1/3);
  }
  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

export function generateShades(hexColor: string, count: number): string[] {
  if (count === 0) return [];

  const [r, g, b] = hexColor.replace('#', '').match(/.{2}/g)?.map(c => parseInt(c, 16)) || [0, 0, 0];
  const [h, s, l] = rgbToHsl(r, g, b);
  
  const palette: string[] = [];
  const LIGHTNESS_STEP = 0.07; 
  const MAX_SHADES = 5;
  const safeCount = Math.min(count, MAX_SHADES);

  for (let i = 0; i < safeCount; i++) {
    const newL = Math.max(0, l - LIGHTNESS_STEP * (i + 1));
    const [newR, newG, newB] = hslToRgb(h, s, newL);
    const newHex = `#${[newR, newG, newB].map(c => c.toString(16).padStart(2, '0')).join('')}`;
    palette.push(newHex);
  }

  const finalPalette: string[] = [];
  for (let i = 0; i < count; i++) {
    finalPalette.push(palette[i % palette.length]);
  }

  return finalPalette;
}
