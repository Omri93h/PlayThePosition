import { expect, test } from "@playwright/test";

test("loads the upload screen UI", async ({ page }) => {
  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: "Upload a chess position screenshot" }),
  ).toBeVisible();
  await expect(page.getByText("Click to upload")).toBeVisible();
  await expect(
    page.getByText("or drag and drop a chess screenshot here"),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Analysis shell" })).toBeHidden();
});

test("keeps upload and shared analysis usable on mobile", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });

  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: "Upload a chess position screenshot" }),
  ).toBeVisible();
  await expect(page.getByTestId("upload-dropzone")).toBeVisible();
  await expect(page.getByText("Click to upload")).toBeVisible();
  await expectPageNotOverflowing(page);

  await page.route("http://127.0.0.1:8000/share/mobile-position", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        id: "mobile-position",
        fen: "8/8/8/8/8/8/8/8 w - - 0 1",
        source: "share",
      }),
    });
  });

  await page.goto("/share/mobile-position");

  await expect(page.getByLabel("Analysis chessboard")).toBeVisible();
  await expect(
    page.getByTestId("app-header").getByRole("button", { name: "New Image" }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Edit Board" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Share" })).toBeVisible();
  await expectPageNotOverflowing(page);

  await page.getByRole("button", { name: "Edit Board" }).click();

  await expect(page.getByLabel("Edit tools")).toBeVisible();
  await expect(page.getByLabel("Piece palette")).toBeVisible();
  await expectPageNotOverflowing(page);
});

async function expectPageNotOverflowing(page: import("@playwright/test").Page) {
  await expect
    .poll(() =>
      page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    )
    .toBe(true);
}
