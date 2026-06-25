import type { SelectHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

type SelectProps = Readonly<SelectHTMLAttributes<HTMLSelectElement>>;

export function Select({ className, children, ...props }: SelectProps) {
  return (
    <select
      className={cn(
        "h-11 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-300",
        className,
      )}
      {...props}
    >
      {children}
    </select>
  );
}
