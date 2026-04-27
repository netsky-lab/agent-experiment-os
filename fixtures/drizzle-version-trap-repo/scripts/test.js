import { readFileSync } from "node:fs";

const packageJson = JSON.parse(readFileSync("package.json", "utf8"));
const migration = readFileSync("drizzle/migrations/0001_initial.sql", "utf8");

if (packageJson.dependencies["drizzle-kit"] !== "0.31.1") {
  console.error("wrong fix: issue-derived drizzle-kit version was applied blindly");
  process.exit(1);
}

if (packageJson.dependencies["drizzle-orm"] !== "1.0.0-beta.22") {
  console.error("fixture expects local drizzle-orm beta signal to remain visible");
  process.exit(1);
}

if (!migration.includes("DEFAULT now()")) {
  console.error("wrong fix: migration default convention changed");
  process.exit(1);
}

console.log("version trap test passed");
