import React from 'react';

import { cn } from '@/utils/cn';

export const Button: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement>> = ({
  children,
  disabled,
  className = '',
  ...props
}) => (
  <button
    {...props}
    disabled={disabled}
    className={cn(
      'w-full md:w-auto bg-primary text-on-primary font-label-caps text-label-caps tracking-widest py-4 px-12 border border-primary transition-all duration-300',
      'hover:bg-tertiary-fixed-dim cursor-pointer hover:text-primary hover:border-tertiary-fixed-dim',
      'focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-primary',
      disabled &&
        'opacity-50 cursor-not-allowed hover:bg-primary hover:text-on-primary hover:border-primary',
      className
    )}
  >
    {children}
  </button>
);
