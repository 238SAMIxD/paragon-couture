import type { CoutureRequest, CoutureResponse } from "@/types";

export const mockParagonGeneration = async (
  _request: CoutureRequest,
): Promise<CoutureResponse> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        collectionTitle: "The Apex Plasma Masterpiece",
        speciesFit: "Dart Monkey",
        keywords: ["Cybernetic", "Plasma", "Aerodynamic", "High-Tech"],
        imageUrl:
          "https://images.unsplash.com/photo-1540228232483-1b64a7024923?auto=format&fit=crop&q=80&w=600",
      });
    }, 3000); // Simulate 3 seconds LLM generation time
  });
};
