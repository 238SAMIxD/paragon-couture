import { expect, test } from "@playwright/test";

test.describe("Paragon Couture E2E Flow", () => {
  test("Should generate a Paragon Couture collection", async ({ page }) => {
    await page.route("**/api/generate", async (route) => {
      const json = {
        collection_title: "Aerodynamic Cloak Collection",
        species_fit: "Magic Monkeys",
        keywords: ["aerodynamic", "plasma", "stealth"],
        image_url: "http://localhost:5174/placeholder.png",
      };
      await route.fulfill({ json });
    });

    await page.goto("/");

    console.warn("Page title:", await page.title());
    console.warn("Page URL:", page.url());

    await expect(page.getByRole("link", { name: "PARAGON COUTURE" }).first()).toBeVisible();

    await expect(page.getByAltText("High-fashion monkey")).toBeVisible();

    const trendDescription = "Aerodynamic plasma-woven cloaks";
    await page.getByPlaceholder("Articulate your vision...").fill(trendDescription);

    await page.getByLabel("MONKEY TOWER CLASS").selectOption("magic");

    const camoLabel = page.getByLabel("CAMO DETECTION THREADING");
    await expect(camoLabel).toBeAttached({ timeout: 5000 });
    await camoLabel.click({ force: true });

    const submitButton = page.getByRole("button", { name: /REQUEST BESPOKE GENERATION/ });
    await expect(submitButton).toBeVisible({ timeout: 5000 });
    await submitButton.click();

    await expect(page.getByText("YOUR BESPOKE PARAGON")).toBeVisible({ timeout: 10000 });

    await expect(page.getByRole("heading", { name: /YOUR BESPOKE PARAGON/i })).toBeVisible();

    const badgeCount = await page.getByTestId("badge").count();
    expect(badgeCount).toBeGreaterThan(0);

    await expect(page.getByText("Aerodynamic Cloak Collection")).toBeVisible();
  });
});
