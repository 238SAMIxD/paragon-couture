import { useState } from "react";
import { TopNavBar } from "./components/organisms/TopNavBar";
import { EditorialHero } from "./components/organisms/EditorialHero";
import { ConfigurationForm } from "./components/organisms/ConfigurationForm";
import { CollectionGrid } from "./components/organisms/CollectionGrid";
import { Footer } from "./components/organisms/Footer";
import type { ParagonConfigurationState } from "./types";

function App() {
  const [config, setConfig] = useState<ParagonConfigurationState>({
    trendDescription: "",
    monkeyTowerClass: "primary",
    camoDetection: false,
    leadPopping: true,
  });

  const handleSubmit = () => {
    console.log("Configuration submitted:", config);
    // Add submission logic here
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
        />
        
        <CollectionGrid />
      </main>

      <Footer />
    </div>
  );
}

export default App;
