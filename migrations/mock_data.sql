-- file: migrations/mock_data.sql

-- point at your schema
SET search_path TO grant_schema;

-- The seed is intentionally repeatable. Remove only these known demo rows
-- before inserting their current definitions, so a rerun updates seed content
-- without creating duplicate grants.
DELETE FROM grants
WHERE (name, program, type) IN (
  ('Continuations', 'VISTA', 'Non-competitive'),
  ('State Competitive Awards', 'State Grants', 'Competitive'),
  ('Senior Corps Renewal', 'Senior Corps', 'Non-competitive'),
  ('Education Grants', 'Education', 'Competitive'),
  ('Disaster Relief', 'Emergency Response', 'Competitive'),
  ('Community Development', 'Community', 'Non-competitive')
);

INSERT INTO grants (
  name,
  program,
  type,
  status,
  start_date,
  deadline,
  budget_range,
  created_at,
  updated_at,
  notes
) VALUES
  (
    'Continuations',
    'VISTA',
    'Non-competitive',
    'Open',
    '2023-06-01',
    '2023-07-31',
    '$12,000–$14,000',
    '2023-04-15T12:00:00Z',
    '2023-05-01T09:30:00Z',
    '20–25 applicants expected'
  ),
  (
    'State Competitive Awards',
    'State Grants',
    'Competitive',
    'Open',
    '2023-07-01',
    '2023-10-15',
    '$15,000–$20,000',
    '2023-05-01T08:30:00Z',
    '2023-08-16T14:00:00Z',
    '30–40 applicants expected'
  ),
  (
    'Senior Corps Renewal',
    'Senior Corps',
    'Non-competitive',
    'Closed',
    '2023-06-05',
    '2023-09-01',
    '$8,000–$12,000',
    '2023-04-20T11:00:00Z',
    '2023-09-02T10:15:00Z',
    '15–20 applicants processed'
  ),
  (
    'Education Grants',
    'Education',
    'Competitive',
    'Open',
    '2023-07-01',
    '2023-10-10',
    '$10,000–$15,000',
    '2023-05-10T09:45:00Z',
    '2023-07-02T13:20:00Z',
    '25–30 applicants expected'
  ),
  (
    'Disaster Relief',
    'Emergency Response',
    'Competitive',
    'Closed',
    '2023-07-05',
    '2023-10-01',
    '$20,000–$25,000',
    '2023-05-15T08:00:00Z',
    '2023-11-02T16:30:00Z',
    'High-priority timeline'
  ),
  (
    'Community Development',
    'Community',
    'Non-competitive',
    'Open',
    '2023-06-10',
    '2023-08-15',
    '$5,000–$8,000',
    '2023-04-25T15:00:00Z',
    '2023-06-11T12:10:00Z',
    '10–15 applicants expected'
  );
