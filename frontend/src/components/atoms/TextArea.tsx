import React from 'react';

export const TextArea: React.FC<React.TextareaHTMLAttributes<HTMLTextAreaElement>> = (props) => (
  <textarea
    {...props}
    className="w-full bg-transparent border-0 border-b border-primary focus:border-tertiary-fixed-dim focus:ring-0 p-0 font-body-md text-body-md text-primary resize-none placeholder-secondary-fixed-dim outline-none"
  />
);
