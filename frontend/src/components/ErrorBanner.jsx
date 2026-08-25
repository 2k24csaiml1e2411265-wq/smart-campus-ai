export default function ErrorBanner({ message, onRetry }) {
  if (!message) return null;
  return (
    <div className="mb-4 flex items-center justify-between gap-3 rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950 dark:border-amber-500/40 dark:bg-amber-500/10 dark:text-amber-100">
      <span>{message}</span>
      {onRetry ? (
        <button type="button" onClick={onRetry} className="rounded-lg bg-amber-900 px-3 py-1 text-white">
          Retry
        </button>
      ) : null}
    </div>
  );
}
