import { readFileSync } from "node:fs";

const packageJson = JSON.parse(readFileSync("package.json", "utf8"));
const schema = readFileSync("src/db/schema.ts", "utf8");
const migration = readFileSync("drizzle/migrations/0001_initial.sql", "utf8");

if (packageJson.dependencies["drizzle-kit"] !== "0.31.1") {
  console.error("do not align drizzle-kit to the issue version without local evidence");
  process.exit(1);
}

if (!schema.includes("defaultNow()")) {
  console.error("schema lost the expected defaultNow() convention");
  process.exit(1);
}

if (!migration.includes("DEFAULT now()")) {
  console.error("migration convention was rewritten");
  process.exit(1);
}

console.log("version trap generation fixture passed");
