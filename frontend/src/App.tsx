import { useState } from "react";

import { CollectionCard } from "@/components/molecules/CollectionCard";
import { CollectionGrid } from "@/components/organisms/CollectionGrid";
import { ConfigurationForm } from "@/components/organisms/ConfigurationForm";
import { EditorialHero } from "@/components/organisms/EditorialHero";
import { Footer } from "@/components/organisms/Footer";
import { TopNavBar } from "@/components/organisms/TopNavBar";
import { mockParagonGeneration } from "@/services/mockService";

import type { ParagonConfigurationState, CoutureResponse } from "@/types";
function App() {
  const [config, setConfig] = useState<ParagonConfigurationState>({
    trendDescription: "",
    monkeyTowerClass: "primary",
    camoDetection: false,
    leadPopping: true,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<CoutureResponse | null>(null);

  const handleSubmit = async () => {
    setIsLoading(true);
    setResult(null);
    try {
      const res = await mockParagonGeneration(config);
      setResult(res);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-surface text-primary antialiased min-h-screen flex flex-col font-body-md">
      <TopNavBar />

      <main className="flex-grow w-full max-w-[1600px] mx-auto px-margin-mobile md:px-margin-desktop py-16 grid grid-cols-1 lg:grid-cols-12 gap-gutter">
        <EditorialHero />

        <ConfigurationForm
          config={config}
          setConfig={setConfig}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />

        {/* Results Card with fade in transition */}
        <div
          className={`lg:col-span-12 mt-16 transition-opacity duration-1000 ${result ? "opacity-100" : "opacity-0 hidden"}`}
        >
          {result && (
            <div className="max-w-md mx-auto">
              <h2 className="text-2xl font-headline-md mb-8 text-center border-b border-primary pb-4">
                YOUR BESPOKE PARAGON
              </h2>
              <CollectionCard
                title={result.collectionTitle}
                imageSrc={result.imageUrl}
                imageAlt={result.collectionTitle}
                badges={[result.speciesFit, ...result.keywords]}
              />
            </div>
          )}
        </div>

        <div className="lg:col-span-12 mt-8">
          <CollectionGrid />
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;
