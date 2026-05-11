import React from 'react';

export const Button: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement>> = ({ children, ...props }) => (
  <button
    {...props}
    className="w-full md:w-auto bg-primary text-white font-label-caps text-label-caps tracking-widest py-4 px-12 border border-primary hover:bg-tertiary-fixed-dim hover:text-primary hover:border-tertiary-fixed-dim transition-all duration-300"
  >
    {children}
  </button>
);
