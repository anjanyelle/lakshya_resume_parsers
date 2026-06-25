import * as React from "react";
import { cn } from "../../lib/utils";

type DivProps = Readonly<React.HTMLAttributes<HTMLDivElement>>;

export function Card({ className, ...props }: DivProps) {
  return (
    <div
      className={cn(
        "rounded-md border border-slate-200 bg-white",
        className,
      )}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }: DivProps) {
  return <div className={cn("space-y-1.5 p-6", className)} {...props} />;
}

type CardTitleProps = Readonly<React.HTMLAttributes<HTMLHeadingElement>>;

export function CardTitle({ className, children, ...props }: CardTitleProps) {
  return (
    <h3 className={cn("text-xl font-semibold text-slate-900", className)} {...props}>
      {children}
    </h3>
  );
}

export function CardContent({ className, ...props }: DivProps) {
  return <div className={cn("p-6 pt-0", className)} {...props} />;
}
