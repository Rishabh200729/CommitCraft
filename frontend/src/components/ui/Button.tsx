import React from "react";

type ButtonVariant = "primary" | "secondary" | "tertiary" | "install";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

export function Button({ variant = "primary", className = "", children, ...props }: ButtonProps) {
  let baseClasses = "flex items-center justify-center transition-colors text-button-md outline-none";
  let variantClasses = "";

  if (props.disabled) {
    variantClasses = "bg-surface-elevated text-ash rounded-md px-4 py-2 h-[36px] cursor-not-allowed";
  } else {
    switch (variant) {
      case "primary":
        variantClasses = "bg-primary hover:bg-primary-pressed text-on-primary rounded-md px-4 py-2 h-[36px]";
        break;
      case "secondary":
        variantClasses = "bg-transparent text-ink rounded-md px-4 py-2 h-[36px]";
        break;
      case "tertiary":
        variantClasses = "bg-surface-elevated text-ink rounded-md px-4 py-2 h-[36px]";
        break;
      case "install":
        variantClasses = "bg-transparent border border-hairline-strong text-ink rounded-md px-[14px] py-[6px]";
        break;
    }
  }

  return (
    <button className={`${baseClasses} ${variantClasses} ${className}`} {...props}>
      {children}
    </button>
  );
}
