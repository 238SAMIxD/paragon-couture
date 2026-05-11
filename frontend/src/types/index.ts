export type MonkeyTowerClass = "primary" | "military" | "magic" | "support" | "hero";

export interface ParagonConfigurationState {
  trendDescription: string;
  monkeyTowerClass: MonkeyTowerClass;
  camoDetection: boolean;
  leadPopping: boolean;
}
