import React from "react";

import { Button } from "@/components/atoms/Button";
import { Select } from "@/components/atoms/Select";
import { TextArea } from "@/components/atoms/TextArea";
import { FormField } from "@/components/molecules/FormField";
import { SectionHeader } from "@/components/molecules/SectionHeader";
import { ToggleRow } from "@/components/molecules/ToggleRow";

import type { ParagonConfigurationState, MonkeyTowerClass } from "@/types";
interface ConfigurationFormProps {
  config: ParagonConfigurationState;
  setConfig: React.Dispatch<React.SetStateAction<ParagonConfigurationState>>;
  onSubmit: () => void;
  isLoading: boolean;
}

const TOWER_OPTIONS = [
  { value: "primary", label: "PRIMARY" },
  { value: "military", label: "MILITARY" },
  { value: "magic", label: "MAGIC" },
  { value: "support", label: "SUPPORT" },
  { value: "hero", label: "HERO" },
];

export const ConfigurationForm: React.FC<ConfigurationFormProps> = ({
  config,
  setConfig,
  onSubmit,
  isLoading,
}) => (
  <div className="lg:col-span-7 lg:pl-16 flex flex-col justify-center mt-8 lg:mt-0">
    <SectionHeader
      title="BESPOKE TAILORING"
      description="Commission an exclusive creation. Every paragon is meticulously crafted to exacting standards, utilizing only the finest structural elements."
    />
    <form
      className="space-y-12 max-w-2xl"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <FormField label="DESCRIBE THE PARAGON TREND" htmlFor="trend_desc">
        <TextArea
          id="trend_desc"
          rows={4}
          placeholder="Articulate your vision..."
          value={config.trendDescription}
          onChange={(e) => setConfig({ ...config, trendDescription: e.target.value })}
        />
      </FormField>

      <FormField label="MONKEY TOWER CLASS" htmlFor="tower_class">
        <Select
          id="tower_class"
          options={TOWER_OPTIONS}
          value={config.monkeyTowerClass}
          onChange={(e) =>
            setConfig({
              ...config,
              monkeyTowerClass: e.target.value as MonkeyTowerClass,
            })
          }
        />
      </FormField>

      <div className="space-y-6 pt-4">
        <ToggleRow
          label="CAMO DETECTION THREADING"
          checked={config.camoDetection}
          onChange={(c) => setConfig({ ...config, camoDetection: c })}
        />
        <ToggleRow
          label="LEAD-POPPING DURABILITY"
          checked={config.leadPopping}
          onChange={(c) => setConfig({ ...config, leadPopping: c })}
        />
      </div>

      <div className="pt-8">
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "TAILORING PARAGON FIT..." : "REQUEST BESPOKE GENERATION"}
        </Button>
      </div>
    </form>
  </div>
);
