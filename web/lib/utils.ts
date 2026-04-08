import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, parseISO, isValid } from 'date-fns';
import type { RiskLevel, Language } from '@/types';

// ─── Tailwind class merger ───────────────────────────────
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

// ─── Date formatting ────────────────────────────────────
export function formatDate(dateStr: string | undefined | null): string {
  if (!dateStr) return '—';
  try {
    const d = parseISO(dateStr);
    if (!isValid(d)) return dateStr;
    return format(d, 'dd MMM yyyy, HH:mm');
  } catch {
    return dateStr;
  }
}

export function formatDateShort(dateStr: string | undefined | null): string {
  if (!dateStr) return '—';
  try {
    const d = parseISO(dateStr);
    if (!isValid(d)) return dateStr;
    return format(d, 'dd MMM yyyy');
  } catch {
    return dateStr;
  }
}

// ─── Risk formatting ─────────────────────────────────────
export function formatRisk(risk: RiskLevel): string {
  const map: Record<RiskLevel, string> = {
    LOW_RISK: 'Low Risk',
    HIGH_RISK: 'High Risk',
    MODERATE_RISK: 'Moderate Risk',
    INVALID: 'Invalid',
  };
  return map[risk] ?? risk;
}

export function getRiskColor(risk: RiskLevel): string {
  const map: Record<RiskLevel, string> = {
    LOW_RISK: 'text-success',
    HIGH_RISK: 'text-danger',
    MODERATE_RISK: 'text-warning',
    INVALID: 'text-warning',
  };
  return map[risk] ?? 'text-muted';
}

export function getRiskBgColor(risk: RiskLevel): string {
  const map: Record<RiskLevel, string> = {
    LOW_RISK: 'bg-success/10 text-success border-success/30',
    HIGH_RISK: 'bg-danger/10 text-danger border-danger/30',
    MODERATE_RISK: 'bg-warning/10 text-warning border-warning/30',
    INVALID: 'bg-warning/10 text-warning border-warning/30',
  };
  return map[risk] ?? 'bg-muted/10 text-muted border-muted/30';
}

// ─── Confidence formatting ───────────────────────────────
export function formatConfidence(confidence: number): string {
  return `${(confidence * 100).toFixed(1)}%`;
}

// ─── Language label ─────────────────────────────────────
export function getLanguageLabel(lang: Language): string {
  const map: Record<Language, string> = {
    en: 'English',
    hi: 'हिंदी',
    ta: 'தமிழ்',
    te: 'తెలుగు',
  };
  return map[lang] ?? lang.toUpperCase();
}

// ─── Uptime formatting ──────────────────────────────────
export function formatUptime(seconds: number): string {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

// ─── Number formatting ──────────────────────────────────
export function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

// ─── Truncate text ──────────────────────────────────────
export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen) + '…';
}

// ─── File to base64 ─────────────────────────────────────
export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      // strip data URL prefix
      const base64 = result.split(',')[1] ?? result;
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}
