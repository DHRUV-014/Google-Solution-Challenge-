import { CheckCircle, AlertCircle, XCircle, Clock } from 'lucide-react';
import { formatDate } from '@/lib/utils';
import type { RecentScan } from '@/types';

interface RecentActivityProps {
  scans: RecentScan[];
}

export default function RecentActivity({ scans }: RecentActivityProps) {
  if (scans.length === 0) {
    return (
      <div className="text-center py-8 text-muted text-sm">
        No recent activity
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {scans.slice(0, 8).map((scan) => {
        const Icon =
          scan.risk_level === 'LOW_RISK'
            ? CheckCircle
            : scan.risk_level === 'HIGH_RISK'
            ? AlertCircle
            : XCircle;
        const iconColor =
          scan.risk_level === 'LOW_RISK'
            ? 'text-success'
            : scan.risk_level === 'HIGH_RISK'
            ? 'text-danger'
            : 'text-warning';

        return (
          <div
            key={scan.scan_id}
            className="flex items-start gap-3 py-2 border-b border-border last:border-0"
          >
            <Icon className={`h-4 w-4 mt-0.5 shrink-0 ${iconColor}`} />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white capitalize">
                {scan.scan_type} scan — {scan.risk_level.replace('_', ' ')}
              </p>
              <div className="flex items-center gap-1 text-xs text-muted mt-0.5">
                <Clock className="h-3 w-3" />
                {formatDate(scan.created_at)}
              </div>
            </div>
            <span className="text-xs text-muted uppercase">{scan.language}</span>
          </div>
        );
      })}
    </div>
  );
}
