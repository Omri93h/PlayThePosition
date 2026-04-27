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

test("loads the analysis shell UI", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Analysis shell" }).click();

  await expect(page.getByRole("heading", { name: "Position workspace" })).toBeVisible();
  await expect(page.getByTestId("static-board")).toBeVisible();
  await expect(page.getByRole("button", { name: "Edit mode" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Reset" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Flip" })).toBeVisible();
});
