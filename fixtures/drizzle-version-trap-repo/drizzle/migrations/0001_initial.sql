CREATE TABLE "users" (
  "id" integer PRIMARY KEY,
  "email" text NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT now()
);
