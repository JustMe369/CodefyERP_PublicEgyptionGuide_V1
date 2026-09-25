#!/bin/sh
set -eu

: "${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD in the project .env file}"
: "${POSTGRES_APP_PASSWORD:?Set POSTGRES_APP_PASSWORD in the project .env file}"

PGPASSWORD="$POSTGRES_PASSWORD" psql --host "${PGHOST:-postgres}" --username codefy_owner --dbname codefy_guide --set=app_password="$POSTGRES_APP_PASSWORD" <<'SQL'
SELECT format('CREATE ROLE codefy_app LOGIN PASSWORD %L', :'app_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codefy_app')
\gexec
ALTER ROLE codefy_app PASSWORD :'app_password';
GRANT CONNECT ON DATABASE codefy_guide TO codefy_app;
GRANT USAGE ON SCHEMA public TO codefy_app;
ALTER DEFAULT PRIVILEGES FOR ROLE codefy_owner IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE ON TABLES TO codefy_app;
ALTER DEFAULT PRIVILEGES FOR ROLE codefy_owner IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO codefy_app;
SQL
