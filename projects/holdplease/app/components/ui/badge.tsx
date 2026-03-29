import * as React from 'react';
import { cn } from '@/lib/utils/cn';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'muted';
}

const variantStyles = {
  default: 'bg-slate-700 text-slate-300',
  success: 'bg-green-900/50 text-green-300 border border-green-700/50',
  warning: 'bg-amber-900/50 text-amber-300 border border-amber-700/50',
  danger: 'bg-red-900/50 text-red-300 border border-red-700/50',
  info: 'bg-blue-900/50 text-blue-300 border border-blue-700/50',
  muted: 'bg-slate-800 text-slate-400',
};

export function Badge({ className, variant = 'default', children, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium',
        variantStyles[variant],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}
