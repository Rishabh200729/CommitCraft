import React from "react";

type BadgeVariant = "pro" | "infoSoft" | "pillTab" | "pillTabActive" | "keycap";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

export function Badge({ variant = "pro", className = "", children, ...props }: BadgeProps) {
  let variantClasses = "";

  switch (variant) {
    case "pro":
      variantClasses = "bg-surface-elevated text-mute text-caption-sm rounded-xs px-[6px] py-[2px]";
      break;
    case "infoSoft":
      variantClasses = "bg-accent-blue-soft text-accent-blue text-caption-sm rounded-xs px-[8px] py-[2px]";
      break;
    case "pillTab":
      variantClasses = "bg-transparent text-body text-body-sm rounded-full px-[10px] py-[4px]";
      break;
    case "pillTabActive":
      variantClasses = "bg-surface-elevated text-ink text-body-sm rounded-full px-[10px] py-[4px]";
      break;
    case "keycap":
      variantClasses = "bg-surface-card text-body text-caption-md rounded-xs px-[6px] py-[1px] h-[20px] inline-flex items-center justify-center";
      break;
  }

  return (
    <span className={`${variantClasses} ${className}`} {...props}>
      {children}
    </span>
  );
}
