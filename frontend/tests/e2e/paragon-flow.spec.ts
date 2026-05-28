import { expect, test } from "@playwright/test";

test.describe('Paragon Couture E2E Flow', () => {
  test('Should generate a Paragon Couture collection', async ({ page }) => {
    // Mock the backend API response
    await page.route('**/api/generate', async route => {
      const json = {
        collection_title: "Aerodynamic Cloak Collection",
        species_fit: "Magic Monkeys",
        keywords: ["aerodynamic", "plasma", "stealth"],
        image_url: "http://localhost:5174/placeholder.png"
      };
      await route.fulfill({ json });
    });

    // Action 1: Navigate to home page
    await page.goto('/');

    // Debug: Log the page title and URL
    console.log('Page title:', await page.title());
    console.log('Page URL:', page.url());

    // Assertion 1: Verify the main heading or logo ("PARAGON COUTURE") is visible
    // Looking for the brand name in the nav bar (Logo component shows uppercase)
    // Target the logo specifically in the nav bar (first occurrence)
    await expect(page.getByRole('link', { name: 'PARAGON COUTURE' }).first()).toBeVisible();
    // Alternative: check for the editorial hero image or text content
    await expect(page.getByAltText('High-fashion monkey')).toBeVisible();

    // Action 2: Locate the trend description textarea and fill it
    const trendDescription = 'Aerodynamic plasma-woven cloaks';
    await page.getByPlaceholder('Articulate your vision...').fill(trendDescription);

    // Action 3: Select a "Monkey Tower Class" from the dropdown
    await page.getByLabel('MONKEY TOWER CLASS').selectOption('magic');

    // Action 4: Click/check the "Camo Detection Threading" toggle
    // Click on the label to toggle the checkbox (since the actual input is hidden but label wraps it)
    const camoLabel = page.getByLabel('CAMO DETECTION THREADING');
    await expect(camoLabel).toBeAttached({ timeout: 5000 });
    await camoLabel.click({ force: true });

    // Action 5: Click the submit button
    const submitButton = page.getByRole('button', { name: /REQUEST BESPOKE GENERATION/ });
    await expect(submitButton).toBeVisible({ timeout: 5000 });
    await submitButton.click();

    // Assertion 2: Wait for the results to appear
    // Wait for the results section to be visible (it starts hidden and becomes visible when result is set)
    await expect(page.getByText('YOUR BESPOKE PARAGON')).toBeVisible({ timeout: 10000 });

    // Assert that the collection title is visible in the CollectionCard
    await expect(page.getByRole('heading', { name: /YOUR BESPOKE PARAGON/i })).toBeVisible();

    // Assert that generated keyword badges are present
    // Looking for badges that would contain keywords from the generated collection
    const badgeCount = await page.getByTestId('badge').count();
    expect(badgeCount).toBeGreaterThan(0);

    // Additional verification: check that we have some result content
    await expect(page.getByText('Aerodynamic Cloak Collection')).toBeVisible();
  });
});