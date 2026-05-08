"use client";

import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  variant?: "primary" | "secondary";
};

export function Button({ children, className, variant = "primary", ...rest }: ButtonProps) {
  return (
    <button
      {...rest}
      className={cn(
        "rounded-xl px-4 py-2.5 text-sm font-semibold transition disabled:opacity-60",
        variant === "primary" ? "bg-ink text-white hover:opacity-90" : "border border-slate-300 bg-white text-slate-700 hover:bg-slate-100",
        className,
      )}
    >
      {children}
    </button>
  );
}
