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

const TrendDescriptionField: React.FC<{
  value: string;
  onChange: (value: string) => void;
}> = ({ value, onChange }) => (
  <FormField label="DESCRIBE THE PARAGON TREND" htmlFor="trend_desc">
    <TextArea
      id="trend_desc"
      rows={4}
      placeholder="Articulate your vision..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  </FormField>
);

const TowerClassField: React.FC<{
  value: MonkeyTowerClass;
  onChange: (value: MonkeyTowerClass) => void;
}> = ({ value, onChange }) => (
  <FormField label="MONKEY TOWER CLASS" htmlFor="tower_class">
    <Select
      id="tower_class"
      options={TOWER_OPTIONS}
      value={value}
      onChange={(e) => onChange(e.target.value as MonkeyTowerClass)}
    />
  </FormField>
);

const OptionsSection: React.FC<{
  camoDetection: boolean;
  leadPopping: boolean;
  onCamoChange: (value: boolean) => void;
  onLeadChange: (value: boolean) => void;
}> = ({ camoDetection, leadPopping, onCamoChange, onLeadChange }) => (
  <div className="space-y-6 pt-4">
    <ToggleRow label="CAMO DETECTION THREADING" checked={camoDetection} onChange={onCamoChange} />
    <ToggleRow label="LEAD-POPPING DURABILITY" checked={leadPopping} onChange={onLeadChange} />
  </div>
);

const SubmitButton: React.FC<{ isLoading: boolean }> = ({ isLoading }) => (
  <div className="pt-8">
    <Button type="submit" disabled={isLoading}>
      {isLoading ? "TAILORING PARAGON FIT..." : "REQUEST BESPOKE GENERATION"}
    </Button>
  </div>
);

export const ConfigurationForm: React.FC<ConfigurationFormProps> = ({
  config,
  setConfig,
  onSubmit,
  isLoading,
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <div className="lg:col-span-7 lg:pl-16 flex flex-col justify-center mt-8 lg:mt-0">
      <SectionHeader
        title="BESPOKE TAILORING"
        description="Commission an exclusive creation. Every paragon is meticulously crafted to exacting standards, utilizing only the finest structural elements."
      />
      <form className="space-y-12 max-w-2xl" onSubmit={handleSubmit}>
        <TrendDescriptionField
          value={config.trendDescription}
          onChange={(value) => setConfig({ ...config, trendDescription: value })}
        />
        <TowerClassField
          value={config.monkeyTowerClass}
          onChange={(value) => setConfig({ ...config, monkeyTowerClass: value })}
        />
        <OptionsSection
          camoDetection={config.camoDetection}
          leadPopping={config.leadPopping}
          onCamoChange={(c) => setConfig({ ...config, camoDetection: c })}
          onLeadChange={(c) => setConfig({ ...config, leadPopping: c })}
        />
        <SubmitButton isLoading={isLoading} />
      </form>
    </div>
  );
};
