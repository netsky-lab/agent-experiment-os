import { readFileSync } from "node:fs";

const schema = readFileSync("src/db/schema.ts", "utf8");

if (!schema.includes("defaultNow()")) {
  console.error("schema lost the expected defaultNow() convention");
  process.exit(1);
}

console.log("drizzle generation fixture passed");
