import React from "react";

interface FormFieldProps {
  label: string;
  htmlFor: string;
  children: React.ReactNode;
}

export const FormField: React.FC<FormFieldProps> = ({ label, htmlFor, children }) => (
  <div className="flex flex-col relative">
    <label
      className="font-label-caps text-label-caps text-primary mb-2 tracking-widest"
      htmlFor={htmlFor}
    >
      {label}
    </label>
    {children}
  </div>
);
