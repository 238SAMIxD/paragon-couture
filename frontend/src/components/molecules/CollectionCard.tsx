import React from "react";
import { Badge } from "@/components/atoms/Badge";

interface CollectionCardProps {
  title: string;
  imageSrc: string;
  imageAlt: string;
  badges: string[];
  hiddenLg?: boolean;
}

export const CollectionCard: React.FC<CollectionCardProps> = ({
  title,
  imageSrc,
  imageAlt,
  badges,
  hiddenLg,
}) => (
  <article className={`flex-col ${hiddenLg ? "hidden lg:flex" : "flex"}`}>
    <div className="aspect-[3/4] border border-primary overflow-hidden relative mb-6 bg-surface-container">
      <img alt={imageAlt} className="w-full h-full object-cover grayscale" src={imageSrc} />
    </div>
    <h3 className="font-headline-md text-headline-md text-primary mb-4">{title}</h3>
    <div className="flex flex-wrap gap-2">
      {badges.map((badge) => (
        <Badge key={badge}>{badge}</Badge>
      ))}
    </div>
  </article>
);
