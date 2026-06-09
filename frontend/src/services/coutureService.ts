import type { CoutureRequest, CoutureResponse } from "@/types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type ApiCoutureResponse = {
  collection_title: string;
  species_fit: string;
  keywords: string[];
  image_url: string;
  fallback_used?: boolean;
};

type ApiCollectionItem = {
  id: string;
  trend_description: string;
  monkey_tower_class: string;
  collection_title: string;
  species_fit: string;
  keywords: string[];
  image_url: string;
  created_at: string;
};

export interface CollectionItem {
  id: string;
  trendDescription: string;
  monkeyTowerClass: string;
  collectionTitle: string;
  speciesFit: string;
  keywords: string[];
  imageUrl: string;
  createdAt: Date;
}

function mapCollection(item: ApiCollectionItem): CollectionItem {
  return {
    id: item.id,
    trendDescription: item.trend_description,
    monkeyTowerClass: item.monkey_tower_class,
    collectionTitle: item.collection_title,
    speciesFit: item.species_fit,
    keywords: Array.isArray(item.keywords) ? item.keywords : [],
    imageUrl: item.image_url ?? "",
    createdAt: new Date(item.created_at),
  };
}

export async function generateParagonCouture(
  request: CoutureRequest,
): Promise<CoutureResponse> {
  const response = await fetch(`${API_BASE_URL}/api/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      trend_description: request.trendDescription,
      monkey_tower_class: request.monkeyTowerClass,
      camo_detection: request.camoDetection,
      lead_popping: request.leadPopping,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Backend request failed (${response.status}): ${errorText}`);
  }

  const data: ApiCoutureResponse = await response.json();

  if (!data || typeof data !== "object") {
    throw new Error("Invalid response format from server");
  }

  return {
    collectionTitle: data.collection_title || "Unknown Collection",
    speciesFit: data.species_fit || "Unknown Fit",
    keywords: Array.isArray(data.keywords) ? data.keywords : [],
    imageUrl: data.image_url || "",
    fallbackUsed: Boolean(data.fallback_used),
  };
}

export async function fetchCollections(): Promise<CollectionItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/collections`);

  if (!response.ok) {
    throw new Error(`Failed to load collections (${response.status})`);
  }

  const data: ApiCollectionItem[] = await response.json();

  if (!Array.isArray(data)) {
    throw new Error("Unexpected response shape from /api/collections");
  }

  return data.map(mapCollection);
}
