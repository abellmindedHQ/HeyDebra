/**
 * Format cents to a dollar string
 */
export function formatCents(cents: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(cents / 100);
}

/**
 * Format seconds to a human-readable duration
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  if (minutes < 60) {
    return remainingSeconds > 0
      ? `${minutes}m ${remainingSeconds}s`
      : `${minutes}m`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes > 0
    ? `${hours}h ${remainingMinutes}m`
    : `${hours}h`;
}

/**
 * Format a phone number to (XXX) XXX-XXXX format
 */
export function formatPhone(phone: string): string {
  const cleaned = phone.replace(/\D/g, '');
  const match = cleaned.match(/^1?(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return `(${match[1]}) ${match[2]}-${match[3]}`;
  }
  return phone;
}

/**
 * Format a date to a friendly relative string
 */
export function formatRelativeDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
}

/**
 * Generate a random ID
 */
export function generateId(prefix = ''): string {
  const rand = Math.random().toString(36).substring(2, 10);
  const ts = Date.now().toString(36);
  return prefix ? `${prefix}_${ts}_${rand}` : `${ts}_${rand}`;
}

/**
 * Get status color/label for issue statuses
 */
export function getIssueStatusConfig(status: string) {
  const configs: Record<string, { label: string; color: string; bg: string }> = {
    new: { label: 'New', color: 'text-slate-300', bg: 'bg-slate-700' },
    researching: { label: 'Researching', color: 'text-blue-300', bg: 'bg-blue-900/50' },
    calling: { label: 'Calling', color: 'text-amber-300', bg: 'bg-amber-900/50' },
    waiting_on_them: { label: 'Waiting', color: 'text-yellow-300', bg: 'bg-yellow-900/50' },
    waiting_on_me: { label: 'Action Needed', color: 'text-orange-300', bg: 'bg-orange-900/50' },
    resolved: { label: 'Resolved', color: 'text-green-300', bg: 'bg-green-900/50' },
    closed: { label: 'Closed', color: 'text-slate-400', bg: 'bg-slate-800' },
  };
  return configs[status] ?? { label: status, color: 'text-slate-300', bg: 'bg-slate-700' };
}

/**
 * Get status config for call statuses
 */
export function getCallStatusConfig(status: string) {
  const configs: Record<string, { label: string; color: string; bg: string }> = {
    queued: { label: 'Queued', color: 'text-slate-300', bg: 'bg-slate-700' },
    connecting: { label: 'Connecting', color: 'text-blue-300', bg: 'bg-blue-900/50' },
    hold_mode: { label: 'On Hold', color: 'text-amber-300', bg: 'bg-amber-900/50' },
    ivr_navigating: { label: 'Navigating IVR', color: 'text-purple-300', bg: 'bg-purple-900/50' },
    conversation_mode: { label: 'Speaking', color: 'text-green-300', bg: 'bg-green-900/50' },
    completed: { label: 'Completed', color: 'text-green-300', bg: 'bg-green-900/50' },
    failed: { label: 'Failed', color: 'text-red-300', bg: 'bg-red-900/50' },
    canceled: { label: 'Canceled', color: 'text-slate-400', bg: 'bg-slate-800' },
  };
  return configs[status] ?? { label: status, color: 'text-slate-300', bg: 'bg-slate-700' };
}
