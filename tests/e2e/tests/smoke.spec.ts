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
});
