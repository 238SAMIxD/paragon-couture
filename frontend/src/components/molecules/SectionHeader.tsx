import React from 'react';

interface SectionHeaderProps {
  title: string;
  description: string;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({ title, description }) => (
  <header className="mb-16">
    <h1 className="font-display-lg text-display-lg text-primary mb-6 leading-none tracking-tight">
      {title}
    </h1>
    <p className="font-body-lg text-body-lg text-secondary max-w-xl">{description}</p>
  </header>
);
