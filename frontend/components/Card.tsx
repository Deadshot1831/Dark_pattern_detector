import type { HTMLAttributes, ReactNode } from "react";

type CardVariant = "glass" | "solid" | "highlighted";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  /** When true, applies the lift-on-hover treatment used by interactive
   *  surfaces (history rows, clickable tiles). Defaults to false so plain
   *  containers stay still. */
  interactive?: boolean;
  children: ReactNode;
}

const VARIANT_CLASSES: Record<CardVariant, string> = {
  glass: "bg-card backdrop-blur-md border border-border",
  solid: "bg-card-solid border border-border",
  highlighted:
    "bg-card backdrop-blur-md border border-accent/20 shadow-border-glow",
};

const INTERACTIVE_CLASSES =
  "hover:border-border-hover hover:bg-card-solid/80 hover:scale-[1.01] hover:shadow-lg";

export function Card({
  variant = "glass",
  interactive = false,
  className = "",
  children,
  ...rest
}: CardProps) {
  return (
    <div
      className={[
        "rounded-xl transition-all duration-300 ease-out",
        VARIANT_CLASSES[variant],
        interactive ? INTERACTIVE_CLASSES : "",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      {...rest}
    >
      {children}
    </div>
  );
}
