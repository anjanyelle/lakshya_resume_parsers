import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'official'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  isLoading?: boolean
  icon?: ReactNode
}

const variantClasses: Record<Variant, string> = {
  primary:
    'bg-brand-600 text-white hover:bg-brand-700 focus-visible:ring-brand-500 shadow-md shadow-brand-200/50 active:scale-95',
  secondary:
    'bg-white text-slate-700 border border-slate-200 hover:border-brand-200 hover:text-brand-600 focus-visible:ring-brand-100',
  ghost:
    'bg-transparent text-slate-600 hover:bg-brand-50 hover:text-brand-700 focus-visible:ring-brand-100',
  danger:
    'bg-red-500 text-white hover:bg-red-600 focus-visible:ring-red-400',
  official:
    'bg-brand-600 text-white hover:bg-brand-700 focus-visible:ring-brand-600 rounded-xl font-bold transition-all hover:shadow-lg hover:shadow-brand-600/20 active:scale-95',
}

const sizeClasses: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-5 py-2.5 text-base',
}

export default function Button({
  children,
  className = '',
  variant = 'primary',
  size = 'md',
  isLoading = false,
  icon,
  disabled,
  type = 'button',
  ...rest
}: ButtonProps) {
  const isDisabled = disabled || isLoading

  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-white disabled:cursor-not-allowed disabled:opacity-60 ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      disabled={isDisabled}
      type={type}
      {...rest}
    >
      {isLoading ? (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/50 border-t-white" />
      ) : (
        icon
      )}
      {children}
    </button>
  )
}
