import React from "react";
import { Logo } from "@/components/atoms/Logo";
import { NavLink } from "@/components/atoms/NavLink";

export const Footer: React.FC = () => (
  <footer className="bg-surface dark:bg-primary flex flex-col md:flex-row justify-between items-center px-margin-desktop py-12 w-full mt-section-gap border-t border-primary dark:border-outline flat no-shadows">
    <div className="mb-6 md:mb-0">
      <Logo />
    </div>
    <div className="flex flex-wrap justify-center gap-8 mb-6 md:mb-0">
      <NavLink href="#">LEGAL</NavLink>
      <NavLink href="#">PRIVACY</NavLink>
      <NavLink href="#">SHIPPING</NavLink>
      <NavLink href="#">CONTACT</NavLink>
    </div>
    <div>
      <span className="text-secondary dark:text-secondary-fixed-dim font-label-caps text-label-caps text-primary dark:text-on-primary">
        © 2024 PARAGON COUTURE. ALL RIGHTS RESERVED.
      </span>
    </div>
  </footer>
);
