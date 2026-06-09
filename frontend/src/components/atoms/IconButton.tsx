import React from 'react';

import { cn } from "@/utils/cn";

type IconButtonProps = Omit<
  React.ButtonHTMLAttributes<HTMLButtonElement>,
  "aria-label"
> & {
  "aria-label": string;
};

export const IconButton: React.FC<IconButtonProps> = ({
  children,
  className,
  type = "button",
  ...props
}) => (
  <button
    {...props}
    type={type}
    className={cn(
      "text-primary dark:text-on-primary hover:opacity-70 transition-opacity duration-300",
      "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-primary",
      className,
    )}
  >
    {children}
  </button>
);
