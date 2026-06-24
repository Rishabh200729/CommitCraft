import React from "react";

type InputVariant = "default" | "searchBar";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: InputVariant;
}

export function Input({ variant = "default", className = "", ...props }: InputProps) {
  let baseClasses = "bg-surface-elevated text-ink text-body-md outline-none transition-colors placeholder:text-mute border";
  let variantClasses = "";

  switch (variant) {
    case "default":
      variantClasses = "border-hairline focus:border-hairline-strong rounded-md px-[12px] py-[8px] h-[36px]";
      break;
    case "searchBar":
      variantClasses = "border-transparent focus:border-hairline-strong rounded-md px-[16px] py-[10px] h-[44px]";
      break;
  }

  return (
    <input className={`${baseClasses} ${variantClasses} ${className}`} {...props} />
  );
}
