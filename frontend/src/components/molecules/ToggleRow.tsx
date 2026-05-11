import React from 'react';
import { Toggle } from "@/components/atoms/Toggle";

interface ToggleRowProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export const ToggleRow: React.FC<ToggleRowProps> = ({ label, checked, onChange }) => (
  <label className="flex items-center justify-between cursor-pointer group">
    <span className="font-label-caps text-label-caps text-primary group-hover:text-secondary transition-colors tracking-widest">
      {label}
    </span>
    <Toggle checked={checked} onChange={onChange} />
  </label>
);
