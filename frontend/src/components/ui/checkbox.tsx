import type { InputHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

type CheckboxProps = Readonly<InputHTMLAttributes<HTMLInputElement>>;

export function Checkbox({ className, ...props }: CheckboxProps) {
  return (
    <input
      type="checkbox"
      className={cn(
        "h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-300",
        className,
      )}
      {...props}
    />
  );
}
