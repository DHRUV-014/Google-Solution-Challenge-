import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AppStore, User, ScanResult, Language } from '@/types';

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      // ─── Auth ────────────────────────────────────────
      user: null,
      token: null,
      setUser: (user: User, token: string) => set({ user, token }),
      logout: () => set({ user: null, token: null, lastScanResult: null }),

      // ─── Scan ────────────────────────────────────────
      lastScanResult: null,
      setLastScanResult: (result: ScanResult) => set({ lastScanResult: result }),

      // ─── UI ──────────────────────────────────────────
      language: 'en' as Language,
      setLanguage: (lang: Language) => set({ language: lang }),
      sidebarCollapsed: false,
      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    }),
    {
      name: 'janarogya-store',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        language: state.language,
      }),
    }
  )
);
