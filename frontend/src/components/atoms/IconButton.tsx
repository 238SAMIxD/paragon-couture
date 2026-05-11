import React from 'react';

export const IconButton: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement>> = ({ children, ...props }) => (
  <button
    {...props}
    className="text-primary dark:text-on-primary hover:opacity-70 transition-opacity duration-300"
  >
    {children}
  </button>
);
