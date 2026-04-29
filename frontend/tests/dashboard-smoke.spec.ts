import { expect, test } from "@playwright/test";

test("dashboard shell exposes core agent/product views", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Agent Experiment OS Dashboard/);
  await expect(page.getByRole("button", { name: /Experiments/ })).toBeVisible();

  await page.getByRole("button", { name: /Agent Contract/ }).click();
  await expect(page.getByText("Must Load")).toBeVisible();
  await expect(page.getByText("dependsOn + Rules")).toBeVisible();

  await page.getByRole("button", { name: /Review Queue/ }).click();
  await expect(page.getByText("Review Action")).toBeVisible();

  await page.getByRole("button", { name: "Issue Evidence", exact: true }).click();
  await expect(page.getByText("GitHub Issue Ingestion")).toBeVisible();
});
