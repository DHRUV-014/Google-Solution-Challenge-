'use client';

import { cn } from '@/lib/utils';
import type { Language } from '@/types';

const languages: { code: Language; label: string; script: string }[] = [
  { code: 'en', label: 'EN', script: 'English' },
  { code: 'hi', label: 'HI', script: 'हिंदी' },
  { code: 'ta', label: 'TA', script: 'தமிழ்' },
  { code: 'te', label: 'TE', script: 'తెలుగు' },
];

interface LanguageSelectorProps {
  value: Language;
  onChange: (l: Language) => void;
}

export default function LanguageSelector({ value, onChange }: LanguageSelectorProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-300 mb-2">Result Language</label>
      <div className="flex gap-2 flex-wrap">
        {languages.map((l) => (
          <button
            key={l.code}
            type="button"
            onClick={() => onChange(l.code)}
            className={cn(
              'flex flex-col items-center px-4 py-2 rounded-xl border text-sm font-medium transition-all duration-200',
              value === l.code
                ? 'border-accent bg-accent/10 text-accent'
                : 'border-border bg-background-card text-muted hover:border-border-light hover:text-white'
            )}
          >
            <span className="font-bold">{l.label}</span>
            <span className="text-xs opacity-70">{l.script}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
