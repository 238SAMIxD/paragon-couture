import React from 'react';
import { Toggle } from "@/components/atoms/Toggle";

interface ToggleRowProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  id?: string;
}

export const ToggleRow: React.FC<ToggleRowProps> = ({ label, checked, onChange, id }) => {
  const toggleId = id || label.replace(/\s+/g, '-').toLowerCase();
  return (
    <div className="flex items-center justify-between group">
      <label htmlFor={toggleId} className="cursor-pointer font-label-caps text-label-caps text-primary group-hover:text-secondary transition-colors tracking-widest">
        {label}
      </label>
      <Toggle id={toggleId} checked={checked} onChange={onChange} />
    </div>
  );
};
