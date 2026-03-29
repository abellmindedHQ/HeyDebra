import { cn } from '@/lib/utils/cn';
import { getIssueStatusConfig, getCallStatusConfig } from '@/lib/utils/format';

interface StatusBadgeProps {
  status: string;
  type?: 'issue' | 'call';
  className?: string;
}

export function StatusBadge({ status, type = 'issue', className }: StatusBadgeProps) {
  const config = type === 'call'
    ? getCallStatusConfig(status)
    : getIssueStatusConfig(status);

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        config.bg,
        config.color,
        className,
      )}
    >
      {status === 'calling' || status === 'conversation_mode' || status === 'hold_mode' ? (
        <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-current animate-pulse" />
      ) : null}
      {config.label}
    </span>
  );
}
