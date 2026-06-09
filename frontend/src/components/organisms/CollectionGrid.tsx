import React, { useEffect, useState } from "react";

import { CollectionCard } from "@/components/molecules/CollectionCard";
import { fetchCollections, type CollectionItem } from "@/services/coutureService";

// ---------------------------------------------------------------------------
// Skeleton card — shown while loading
// ---------------------------------------------------------------------------

const SkeletonCard: React.FC = () => (
  <div className="flex flex-col animate-pulse">
    <div className="aspect-[3/4] bg-surface-container border border-primary mb-6" />
    <div className="flex gap-2">
      <div className="h-5 w-20 bg-surface-container" />
      <div className="h-5 w-16 bg-surface-container" />
    </div>
  </div>
);

// ---------------------------------------------------------------------------
// CollectionGrid
// ---------------------------------------------------------------------------

export const CollectionGrid: React.FC = () => {
  const [items, setItems] = useState<CollectionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    fetchCollections()
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch((err) => {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Failed to load collections.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="lg:col-span-12 mt-section-gap pt-16 border-t border-primary">
      <h2 className="font-headline-lg text-headline-lg text-primary text-center mb-16 tracking-tighter">
        THE SEASONAL COLLECTION
      </h2>

      {/* Loading skeletons */}
      {loading && (
        <div
          aria-label="Loading collections"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter"
          role="status"
        >
          {[0, 1, 2].map((i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      )}

      {/* Error state */}
      {!loading && error && (
        <p role="alert" className="text-center text-error font-body-md">{error}</p>
      )}

      {/* Empty state */}
      {!loading && !error && items.length === 0 && (
        <p className="text-center text-on-surface-variant font-body-md">
          No collections yet — generate your first bespoke paragon above.
        </p>
      )}

      {/* Live grid */}
      {!loading && !error && items.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">
          {items.map((item, index) => (
            <CollectionCard
              key={item.id}
              title={item.collectionTitle}
              imageSrc={item.imageUrl}
              imageAlt={item.collectionTitle}
              badges={[item.speciesFit, ...item.keywords]}
              hiddenLg={index >= 3}
            />
          ))}
        </div>
      )}
    </div>
  );
};
