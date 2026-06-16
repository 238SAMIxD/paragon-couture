import React from "react";

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  id?: string;
}

export const Toggle: React.FC<ToggleProps> = ({ checked, onChange, id }) => (
  <label className="relative w-10 h-3 flex items-center cursor-pointer">
    <input
      id={id}
      type="checkbox"
      role="switch"
      aria-checked={checked}
      className="sr-only peer"
      checked={checked}
      onChange={(e) => onChange(e.target.checked)}
    />
    <div className="w-10 h-1 border border-primary bg-transparent peer-checked:bg-primary transition-all peer-focus-visible:ring-2 peer-focus-visible:ring-offset-2 peer-focus-visible:ring-primary"></div>
    <div className="absolute left-0 w-3 h-3 bg-primary border border-primary peer-checked:translate-x-7 peer-checked:bg-tertiary-fixed-dim transition-all"></div>
  </label>
);
