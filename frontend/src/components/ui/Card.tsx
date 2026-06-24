import React from "react";

type CardVariant = "feature" | "featureElevated" | "store" | "pricing" | "commandPalette";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
}

export function Card({ variant = "feature", className = "", children, ...props }: CardProps) {
  let baseClasses = "border border-hairline";
  let variantClasses = "";

  switch (variant) {
    case "feature":
      variantClasses = "bg-surface rounded-lg p-xl text-ink text-body-md";
      break;
    case "featureElevated":
      variantClasses = "bg-surface-elevated rounded-lg p-xl text-ink text-body-md";
      break;
    case "store":
      variantClasses = "bg-surface rounded-md p-lg text-ink text-body-md";
      break;
    case "pricing":
      variantClasses = "bg-surface rounded-lg p-xl text-ink text-body-md";
      break;
    case "commandPalette":
      variantClasses = "bg-surface rounded-lg p-0 text-ink text-body-md";
      break;
  }

  return (
    <div className={`${baseClasses} ${variantClasses} ${className}`} {...props}>
      {children}
    </div>
  );
}
