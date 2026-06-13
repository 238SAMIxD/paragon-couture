export type MonkeyTowerClass = "primary" | "military" | "magic" | "support" | "hero";

export interface ParagonConfigurationState {
  trendDescription: string;
  monkeyTowerClass: MonkeyTowerClass;
  camoDetection: boolean;
  leadPopping: boolean;
}

export interface CoutureRequest {
  trendDescription: string;
  monkeyTowerClass: MonkeyTowerClass;
  camoDetection: boolean;
  leadPopping: boolean;
}

export interface CoutureResponse {
  collectionTitle: string;
  speciesFit: string;
  keywords: string[];
  imageUrl: string;
  fallbackUsed: boolean;
}
