import { cn, getRiskBgColor, formatRisk } from '@/lib/utils';
import type { RiskLevel } from '@/types';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  risk?: RiskLevel;
  variant?: 'default' | 'outline';
}

export function Badge({ risk, variant = 'default', className, children, ...props }: BadgeProps) {
  const riskClasses = risk ? getRiskBgColor(risk) : '';

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold border',
        risk ? riskClasses : 'bg-background-card text-muted border-border',
        className
      )}
      {...props}
    >
      {risk ? formatRisk(risk) : children}
    </span>
  );
}

interface RoleBadgeProps {
  role: string;
  className?: string;
}

export function RoleBadge({ role, className }: RoleBadgeProps) {
  const colorMap: Record<string, string> = {
    admin: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    doctor: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    patient: 'bg-green-500/10 text-green-400 border-green-500/30',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold border capitalize',
        colorMap[role] ?? 'bg-muted/10 text-muted border-muted/30',
        className
      )}
    >
      {role}
    </span>
  );
}
