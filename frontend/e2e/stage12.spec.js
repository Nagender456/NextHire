import { expect, test } from "@playwright/test";

test("user can create an account and reach the protected dashboard", async ({
  page,
}) => {
  const suffix = Date.now();
  await page.goto("/signup");
  await page.getByLabel("Name").fill("Browser Candidate");
  await page.getByLabel("Email").fill(`stage12-browser-${suffix}@example.com`);
  await page.getByLabel("Password").fill("correct horse battery staple");
  await page.getByRole("button", { name: "Sign up" }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByText("Profile completeness")).toBeVisible();
});

test("unauthenticated users are prompted to sign in", async ({ page }) => {
  await page.goto("/applications");

  await expect(page.getByRole("heading", { name: "Sign in to continue." }))
    .toBeVisible();
  await expect(page.getByRole("link", { name: "Create an account" }))
    .toBeVisible();
});

test("user can log out and sign back in with the same credentials", async ({
  page,
}) => {
  const suffix = Date.now();
  const email = `stage12-login-${suffix}@example.com`;
  const password = "correct horse battery staple";

  await page.goto("/signup");
  await page.getByLabel("Name").fill("Login Candidate");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign up" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole("button", { name: /Sign out/ }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: "Sign in to continue." }))
    .toBeVisible();

  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText("Profile completeness")).toBeVisible();
});
