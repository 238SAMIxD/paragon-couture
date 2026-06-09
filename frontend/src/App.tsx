import { useEffect, useRef, useState } from "react";

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
  const [gridRefreshKey, setGridRefreshKey] = useState(0);
  const resultRegionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (result || errorMsg) {
      resultRegionRef.current?.focus();
    }
  }, [result, errorMsg]);

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

        <div
          aria-live="polite"
          ref={resultRegionRef}
          tabIndex={-1}
          className={`lg:col-span-12 mt-16 transition-opacity duration-1000 ${result || errorMsg ? "opacity-100" : "opacity-0 invisible h-0"}`}
        >
          {errorMsg && (
            <div
              role="alert"
              className="max-w-md mx-auto p-4 border border-red-500 bg-red-50 text-red-700 text-center"
            >
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
              {result.fallbackUsed && (
                <p className="mt-4 text-center text-on-surface-variant font-body-md">
                  Image generation was unavailable, so a placeholder image was used.
                </p>
              )}
            </div>
          )}
        </div>

        <div className="lg:col-span-12 mt-8">
          <CollectionGrid key={gridRefreshKey} />
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;
