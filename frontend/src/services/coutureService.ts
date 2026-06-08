import type { CoutureRequest, CoutureResponse } from "@/types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type ApiCoutureResponse = {
  collection_title: string;
  species_fit: string;
  keywords: string[];
  image_url: string;
};

export async function generateParagonCouture(
  request: CoutureRequest,
): Promise<CoutureResponse> {
  const response = await fetch(`${API_BASE_URL}/api/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      trend_description: request.trendDescription,
      monkey_tower_class: request.monkeyTowerClass,
      camo_detection: request.camoDetection,
      lead_popping: request.leadPopping,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `Backend request failed (${response.status}): ${errorText}`,
    );
  }

  const data: ApiCoutureResponse = await response.json();
  
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid response format from server');
  }

  return {
    collectionTitle: data.collection_title || 'Unknown Collection',
    speciesFit: data.species_fit || 'Unknown Fit',
    keywords: Array.isArray(data.keywords) ? data.keywords : [],
    imageUrl: data.image_url || '',
  };
}
