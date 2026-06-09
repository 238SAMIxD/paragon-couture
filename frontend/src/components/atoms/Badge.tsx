import React from 'react';

export const Badge: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <span
    data-testid="badge"
    className="border border-primary bg-white text-primary font-label-caps text-[10px] px-3 py-1 tracking-widest"
  >
    {children}
  </span>
);
