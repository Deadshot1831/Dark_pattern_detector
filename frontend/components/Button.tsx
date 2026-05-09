"use client";

import { forwardRef } from "react";
import type { ButtonHTMLAttributes, ReactNode } from "react";

export type ButtonVariant = "primary" | "secondary" | "ghost";
export type ButtonSize = "sm" | "md" | "lg";

const VARIANT_CLASSES: Record<ButtonVariant, string> = {
  primary:
    "bg-accent text-accent-foreground hover:brightness-110 hover:shadow-glow-button",
  secondary:
    "border border-border bg-transparent text-foreground hover:bg-white/5 hover:border-border-hover",
  ghost:
    "bg-transparent text-foreground hover:bg-white/5",
};

const SIZE_CLASSES: Record<ButtonSize, string> = {
  sm: "h-9 px-4 text-xs",
  md: "h-11 px-6 text-sm",
  lg: "h-12 px-7 text-base",
};

const BASE =
  "inline-flex items-center justify-center gap-2 rounded-lg font-medium tracking-tight " +
  "transition-all duration-200 ease-out " +
  "active:scale-[0.98] " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent " +
  "focus-visible:ring-offset-2 focus-visible:ring-offset-background " +
  "disabled:pointer-events-none disabled:opacity-50";

/** Shared class string. Use this when you need the look on a non-button
 *  element (anchor, label-as-button). */
export function buttonClasses(
  variant: ButtonVariant = "primary",
  size: ButtonSize = "md",
  extra = "",
): string {
  return [BASE, VARIANT_CLASSES[variant], SIZE_CLASSES[size], extra]
    .filter(Boolean)
    .join(" ");
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = "primary", size = "md", className = "", children, ...rest },
  ref,
) {
  return (
    <button ref={ref} className={buttonClasses(variant, size, className)} {...rest}>
      {children}
    </button>
  );
});
