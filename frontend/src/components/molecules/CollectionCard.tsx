import React from 'react';
import { Badge } from '../atoms/Badge';

interface CollectionCardProps {
  title: string;
  imageSrc: string;
  imageAlt: string;
  badges: string[];
  hiddenLg?: boolean;
}

export const CollectionCard: React.FC<CollectionCardProps> = ({ title, imageSrc, imageAlt, badges, hiddenLg }) => (
  <article className={`flex-col group cursor-pointer ${hiddenLg ? 'hidden lg:flex' : 'flex'}`}>
    <div className="aspect-[3/4] border border-primary overflow-hidden relative mb-6">
      <div className="absolute inset-0 bg-surface flex items-center justify-center p-8 z-10 transition-opacity duration-500 group-hover:opacity-0 border-b border-primary">
        <h3 className="font-headline-md text-headline-md text-primary text-center">{title}</h3>
      </div>
      <img
        alt={imageAlt}
        className="w-full h-full object-cover absolute inset-0 grayscale z-0"
        src={imageSrc}
      />
    </div>
    <div className="flex flex-wrap gap-2">
      {badges.map(badge => <Badge key={badge}>{badge}</Badge>)}
    </div>
  </article>
);
