import React from "react";
import { ChevronDown } from "lucide-react";

export const Select: React.FC<
  React.SelectHTMLAttributes<HTMLSelectElement> & { options: { value: string; label: string }[] }
> = ({ options, ...props }) => (
  <div className="relative">
    <select
      {...props}
      className="w-full bg-transparent border-0 border-b border-primary focus:border-tertiary-fixed-dim focus:ring-0 p-0 py-2 font-body-md text-body-md text-primary appearance-none cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-4"
    >
      {options.map((opt) => (
        <option key={opt.value} className="bg-surface text-primary" value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
    <ChevronDown
      className="absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none text-primary"
      size={20}
      strokeWidth={1.5}
    />
  </div>
);
