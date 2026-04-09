'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import Sidebar from '@/components/dashboard/Sidebar';
import { RoleBadge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { getAdminUsers, getSystemHealth, getAllCentres } from '@/lib/api';
import { getToken } from '@/lib/auth';
import { useAppStore } from '@/store';
import { formatDate } from '@/lib/utils';
import { CheckCircle, XCircle, Activity } from 'lucide-react';
import { useState } from 'react';

function UptimeDisplay({ seconds }: { seconds: number }) {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return <span className="font-mono text-success">{d}d {h}h {m}m</span>;
}

export default function AdminPage() {
  const router = useRouter();
  const collapsed = useAppStore((s) => s.sidebarCollapsed);
  const [tab, setTab] = useState<'health' | 'users' | 'centres'>('health');

  useEffect(() => {
    if (!getToken()) router.push('/login');
  }, [router]);

  const { data: health, isLoading: hl } = useQuery({
    queryKey: ['system-health'],
    queryFn: getSystemHealth,
    refetchInterval: 30_000,
  });

  const { data: users, isLoading: ul } = useQuery({
    queryKey: ['admin-users'],
    queryFn: getAdminUsers,
  });

  const { data: centres, isLoading: cl } = useQuery({
    queryKey: ['centres-all'],
    queryFn: getAllCentres,
  });

  const sideW = collapsed ? 'ml-16' : 'ml-60';

  const StatusDot = ({ ok }: { ok: boolean }) => ok
    ? <CheckCircle className="h-4 w-4 text-success" />
    : <XCircle className="h-4 w-4 text-danger" />;

  return (
    <div className="flex h-screen bg-background-primary overflow-hidden">
      <Sidebar />
      <main className={`flex-1 overflow-y-auto p-6 transition-all duration-300 ${sideW}`}>
        <h1 className="text-2xl font-bold text-white mb-1">Admin Panel</h1>
        <p className="text-muted mb-6">System management and oversight</p>

        <div className="flex gap-1 bg-background-card rounded-xl p-1 border border-border mb-6 w-fit">
          {(['health', 'users', 'centres'] as const).map((t) => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-4 py-2 rounded-lg text-sm font-medium capitalize ${tab === t ? 'bg-accent text-white' : 'text-muted hover:text-white'}`}>
              {t === 'health' ? 'System Health' : t === 'users' ? 'User Management' : 'Centres'}
            </button>
          ))}
        </div>

        {tab === 'health' && (
          hl ? <div className="flex justify-center py-20"><Spinner size="lg" /></div> :
          health ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  { label: 'API Status', ok: health.api_status === 'ok' },
                  { label: 'Oral Model', ok: health.model_status?.oral ?? false },
                  { label: 'Skin Model', ok: health.model_status?.skin ?? false },
                  { label: 'Firebase', ok: health.firebase_status ?? false },
                ].map(({ label, ok }) => (
                  <div key={label} className="bg-background-card rounded-2xl border border-border p-5 flex items-center gap-3">
                    <StatusDot ok={ok} />
                    <div>
                      <p className="text-white font-medium text-sm">{label}</p>
                      <p className={`text-xs ${ok ? 'text-success' : 'text-danger'}`}>{ok ? 'Operational' : 'Offline'}</p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="bg-background-card rounded-2xl border border-border p-6 flex items-center gap-4">
                <Activity className="h-8 w-8 text-accent" />
                <div>
                  <p className="text-muted text-sm">System Uptime</p>
                  <p className="text-lg font-bold text-white mt-0.5">
                    <UptimeDisplay seconds={health.uptime_seconds ?? 0} />
                  </p>
                </div>
                <div className="ml-8">
                  <p className="text-muted text-sm">Version</p>
                  <p className="text-white font-mono mt-0.5">{health.version ?? '1.0.0'}</p>
                </div>
              </div>
            </div>
          ) : <p className="text-muted">Could not load system health. Is backend running?</p>
        )}

        {tab === 'users' && (
          ul ? <div className="flex justify-center py-20"><Spinner size="lg" /></div> :
          <div className="bg-background-card rounded-2xl border border-border overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b border-border">
                <tr>
                  {['Name', 'Email', 'Role', 'Scans', 'Joined'].map((h) => (
                    <th key={h} className="px-4 py-3 text-left text-xs text-muted uppercase">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {(users ?? []).map((u) => (
                  <tr key={u.id} className="hover:bg-background-secondary/50">
                    <td className="px-4 py-3 text-white font-medium">{u.name}</td>
                    <td className="px-4 py-3 text-muted">{u.email}</td>
                    <td className="px-4 py-3"><RoleBadge role={u.role} /></td>
                    <td className="px-4 py-3 text-muted font-mono">{u.scan_count}</td>
                    <td className="px-4 py-3 text-muted">{formatDate(u.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'centres' && (
          cl ? <div className="flex justify-center py-20"><Spinner size="lg" /></div> :
          <div className="bg-background-card rounded-2xl border border-border overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b border-border">
                <tr>
                  {['Name', 'City', 'State', 'Phone', 'Type'].map((h) => (
                    <th key={h} className="px-4 py-3 text-left text-xs text-muted uppercase">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {(centres ?? []).map((c) => (
                  <tr key={c.id} className="hover:bg-background-secondary/50">
                    <td className="px-4 py-3 text-white font-medium">{c.name}</td>
                    <td className="px-4 py-3 text-muted">{c.city}</td>
                    <td className="px-4 py-3 text-muted">{c.state}</td>
                    <td className="px-4 py-3 text-muted font-mono text-xs">{c.phone}</td>
                    <td className="px-4 py-3 text-muted capitalize">{c.type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
