import { expect, test } from "@playwright/test";

test("loads the foundation app shell", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByText("Frontend foundation")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Play The Position" })).toBeVisible();
});
