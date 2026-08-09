-- 1) Create the schema
CREATE SCHEMA IF NOT EXISTS grant_schema;

-- 2) Switch into that schema
SET search_path TO grant_schema;

-- 3) Create the grants table
CREATE TABLE IF NOT EXISTS grants (
  id             SERIAL PRIMARY KEY,
  name           VARCHAR(255)   NOT NULL,
  program        VARCHAR(255)   NOT NULL,
  type           VARCHAR(100)   NOT NULL,
  status         VARCHAR(50)    NOT NULL,
  start_date     DATE           NOT NULL,
  deadline       DATE           NOT NULL,
  budget_range   VARCHAR(50)    NOT NULL,
  created_at     TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
  updated_at     TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
  notes          TEXT
);

-- 4) Trigger function for updated_at
CREATE OR REPLACE FUNCTION grant_schema.update_timestamp()
  RETURNS TRIGGER
  LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

-- 5) Attach trigger to auto‐update updated_at on modifications
DROP TRIGGER IF EXISTS set_updated_at ON grant_schema.grants;
CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON grant_schema.grants
  FOR EACH ROW
  EXECUTE PROCEDURE grant_schema.update_timestamp();

-- Knowledge used by the portfolio AI assistant. Kept separate from grants so
-- the grantmaking consumer remains isolated.
CREATE SCHEMA IF NOT EXISTS portfolio_schema;

CREATE TABLE IF NOT EXISTS portfolio_schema.knowledge_documents (
  id                SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
  content           JSONB NOT NULL,
  source_site_url   TEXT NOT NULL,
  source_resume_url TEXT,
  source_hash       TEXT NOT NULL,
  generated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
