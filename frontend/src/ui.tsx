import { ReactNode } from "react";
import type { JobStatus } from "./api";

export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-xl border border-ink-600 bg-ink-800/80 p-5 shadow-lg shadow-black/30 backdrop-blur-sm ${className}`}
    >
      {children}
    </div>
  );
}

export function Button({
  children,
  onClick,
  variant = "primary",
  disabled,
  type = "button",
}: {
  children: ReactNode;
  onClick?: () => void;
  variant?: "primary" | "ghost" | "danger";
  disabled?: boolean;
  type?: "button" | "submit";
}) {
  const styles: Record<string, string> = {
    primary:
      "bg-brand-600 text-white hover:bg-brand-500 shadow-glow",
    ghost:
      "bg-ink-700 text-slate-200 hover:bg-ink-600 border border-ink-500",
    danger: "bg-brand-900/40 text-brand-300 hover:bg-brand-900/70",
  };
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`rounded-lg px-4 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-40 ${styles[variant]}`}
    >
      {children}
    </button>
  );
}

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-8 flex items-start justify-between">
      <div>
        <h1 className="text-2xl font-extrabold tracking-tight text-white">
          {title}
        </h1>
        {subtitle && <p className="mt-1 text-sm text-slate-400">{subtitle}</p>}
        <div className="mt-3 h-0.5 w-12 rounded-full bg-brand-600" />
      </div>
      {actions}
    </div>
  );
}

const STATUS_COLORS: Record<JobStatus, string> = {
  pending: "bg-ink-600 text-slate-400",
  running: "bg-brand-900/50 text-brand-300 ring-1 ring-brand-700",
  completed: "bg-emerald-900/40 text-emerald-300 ring-1 ring-emerald-700/50",
  failed: "bg-brand-900/60 text-brand-200 ring-1 ring-brand-600",
  cancelled: "bg-ink-600 text-slate-500",
};

export function StatusPill({ status }: { status: JobStatus }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${STATUS_COLORS[status]}`}
    >
      {status}
    </span>
  );
}

export function Field({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-400">
        {label}
      </span>
      {children}
    </label>
  );
}

export const inputClass =
  "w-full rounded-lg border border-ink-500 bg-ink-900 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500";

export const cardHover =
  "cursor-pointer transition hover:border-brand-600 hover:shadow-glow";

export function ErrorBox({ message }: { message: string }) {
  return (
    <div className="mb-4 rounded-lg border border-brand-700/60 bg-brand-900/30 px-4 py-3 text-sm text-brand-200">
      {message}
    </div>
  );
}
