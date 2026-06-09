import React from "react";

export const NavLink: React.FC<
  React.AnchorHTMLAttributes<HTMLAnchorElement> & { active?: boolean }
> = ({ children, active, ...props }) => (
  <a
    {...props}
    className={`text-secondary dark:text-secondary-fixed-dim font-label-caps text-label-caps transition-all duration-300 ${
      active
        ? "text-primary dark:text-on-primary border-b border-primary dark:border-on-primary pb-1 opacity-70 hover:opacity-100"
        : "hover:text-primary dark:hover:text-on-primary"
    }`}
  >
    {children}
  </a>
);
