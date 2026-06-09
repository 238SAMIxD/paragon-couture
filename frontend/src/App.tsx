import { useState } from "react";

import { CollectionCard } from "@/components/molecules/CollectionCard";
import { CollectionGrid } from "@/components/organisms/CollectionGrid";
import { ConfigurationForm } from "@/components/organisms/ConfigurationForm";
import { EditorialHero } from "@/components/organisms/EditorialHero";
import { Footer } from "@/components/organisms/Footer";
import { TopNavBar } from "@/components/organisms/TopNavBar";
import { generateParagonCouture } from "@/services/coutureService";

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
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  // Increment to trigger CollectionGrid re-fetch after a successful generation
  const [gridRefreshKey, setGridRefreshKey] = useState(0);

  const handleSubmit = async () => {
    setIsLoading(true);
    setResult(null);
    setErrorMsg(null);
    try {
      const res = await generateParagonCouture(config);
      setResult(res);
      setGridRefreshKey((k) => k + 1);
    } catch (error) {
      console.error(error);
      setErrorMsg(error instanceof Error ? error.message : "An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-surface text-primary antialiased min-h-screen flex flex-col font-body-md">
      <TopNavBar />

      <main className="grow w-full max-w-400 mx-auto px-margin-mobile md:px-margin-desktop py-16 grid grid-cols-1 lg:grid-cols-12 gap-gutter">
        <EditorialHero />

        <ConfigurationForm
          config={config}
          setConfig={setConfig}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />

        {/* Results Card with fade in transition */}
        <div
          className={`lg:col-span-12 mt-16 transition-opacity duration-1000 ${result || errorMsg ? "opacity-100" : "opacity-0 invisible h-0"}`}
        >
          {errorMsg && (
            <div className="max-w-md mx-auto p-4 border border-red-500 bg-red-50 text-red-700 text-center">
              {errorMsg}
            </div>
          )}
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
          {/* key forces a remount (and re-fetch) after each generation */}
          <CollectionGrid key={gridRefreshKey} />
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;
