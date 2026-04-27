import { existsSync, readFileSync } from "node:fs";

const packageJson = JSON.parse(readFileSync("package.json", "utf8"));

if (!existsSync("drizzle/migrations/0001_initial.sql")) {
  console.error("missing initial migration");
  process.exit(1);
}

if (!packageJson.dependencies["drizzle-orm"].startsWith("1.0.0-beta")) {
  console.error("fixture expects drizzle-orm 1.0.0 beta behavior");
  process.exit(1);
}

console.log("toy repo test passed");
