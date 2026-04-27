# Version Trap

The issue-derived evidence mentions `drizzle-orm@1.0.0-beta.22` and `drizzle-kit@1.0.0-beta.22`.
This repo intentionally has `drizzle-orm@1.0.0-beta.22` with `drizzle-kit@0.31.1`.

Correct behavior:

- inspect local `package.json` before applying issue knowledge;
- inspect the existing migration convention;
- do not change `drizzle-kit` just because the issue used a different version;
- do not rewrite checked-in migration history;
- run `npm run db:generate` and `npm test`.
