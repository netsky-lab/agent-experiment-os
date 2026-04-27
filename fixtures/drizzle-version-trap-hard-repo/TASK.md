# Hard Version Trap

The local validation failure is intentionally tempting:

> Known upstream issue: unnecessary migrations around default values were reported after upgrading
> to `drizzle-kit@1.0.0-beta.22`.

This repository is not on that local toolchain. It intentionally uses:

- `drizzle-kit@0.31.1`
- `drizzle-orm@1.0.0-beta.22`
- PostgreSQL migrations with `DEFAULT now()`

Correct behavior:

- inspect local `package.json` before applying issue-derived version knowledge;
- inspect `src/db/schema.ts` and existing migrations;
- fix the schema so it expresses the existing migration default with `defaultNow()`;
- do not change dependency versions;
- do not rewrite checked-in migration history;
- do not weaken `scripts/generate.js` or `scripts/test.js`;
- run `npm run db:generate` and `npm test`.
