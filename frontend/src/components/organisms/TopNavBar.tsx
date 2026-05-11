import React from 'react';
import { Search, ShoppingBag } from 'lucide-react';
import { Logo } from '../atoms/Logo';
import { NavLink } from '../atoms/NavLink';
import { IconButton } from '../atoms/IconButton';

export const TopNavBar: React.FC = () => (
  <nav className="bg-surface dark:bg-primary flex justify-between items-center px-margin-desktop py-8 w-full z-50 border-b border-primary dark:border-outline flat no-shadows docked full-width top-0 sticky">
    <div className="flex items-center gap-12">
      <a href="#"><Logo /></a>
      <div className="hidden md:flex items-center gap-8">
        <NavLink href="#">COLLECTIONS</NavLink>
        <NavLink href="#">EDITORIAL</NavLink>
        <NavLink href="#">ARCHIVES</NavLink>
        <NavLink href="#" active>BESPOKE</NavLink>
      </div>
    </div>
    <div className="flex items-center gap-6">
      <IconButton><Search size={24} strokeWidth={1.5} /></IconButton>
      <IconButton><ShoppingBag size={24} strokeWidth={1.5} /></IconButton>
    </div>
  </nav>
);
