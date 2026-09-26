# Admin database operations

The database operations page is available at `/admin/database.php` to active administrator accounts only. It reports the database used by the PHP application and the tables visible to that runtime role. It does not show database passwords or accept arbitrary connection URLs in browser forms.

## Connection security

Change the application's database target in the hosting provider's encrypted environment settings. Supported application configuration is `DATABASE_URL`, `CODEFY_DATABASE_DSN` plus `PGUSER` and `PGPASSWORD`, or the `PGHOST`/`PGPORT`/`PGDATABASE`/`PGUSER`/`PGPASSWORD` variables. Redeploy after changing environment settings. Do not put credentials in frontend code or paste them into the admin panel.

The page intentionally operates on the server-configured application database. Connecting an arbitrary host from a browser field would turn an administrator page into a server-side request forgery path and expose cloud credentials. To switch cloud projects, replace the environment secrets and redeploy.

## Application backup

The page produces a signed, downloadable PostgreSQL custom-format archive for `public.codefy_*` tables, limited to 100 MB. It excludes Supabase Auth, Storage objects, provider internals, and tables that do not belong to the Codefy application. Supabase Storage file contents are not in PostgreSQL backups. Use Supabase's managed backups/PITR or its migration tooling for a complete project-level backup. Vercel's documented proxied request timeout is 120 seconds; if a dump takes longer, use the provider's backup tooling or run `pg_dump` from an operations machine.

The backup operation needs `pg_dump` and `tar` in the container. `app/Dockerfile.vercel` installs the PostgreSQL client utilities. Set `CODEFY_BACKUP_SIGNING_KEY` to a private random value of at least 32 characters in the hosting provider's secret environment settings. For production, a signing key was generated and added as a Vercel Production secret. Backups created with a different signing key cannot be restored; rotate it only when intended.

If `CODEFY_BACKUP_DATABASE_URL` is not set, backup uses the application's existing database credentials. When the application uses Supabase's transaction pooler on port 6543, the backup connection switches to the matching session pooler port 5432. An optional dedicated backup URL can be set instead; it should be read-only for the Codefy tables and use a direct connection or session pooler, not the transaction pooler.

## Restore

Restore is disabled until `CODEFY_RESTORE_DATABASE_URL` is set as an encrypted server-side secret. Use a connection on the same database project and database name, with a role that owns the Codefy tables. Do not use the regular application role for restore. The page accepts only intact, HMAC-signed backup bundles produced by this application and checks the embedded target identity before restoring.

Restore replaces the Codefy application tables in `public` using `pg_restore --clean --if-exists --single-transaction`. It requires typing `RESTORE DATABASE`, and PostgreSQL rolls back the restore transaction if an item fails. Take a fresh backup before restoring. This does not create a database or a Supabase project.

## Provider-level operations

Create a new Supabase project/database, download Supabase-managed backups, or restore to a point in time in the Supabase Dashboard. Those are provider control-plane actions; the app's restricted PostgreSQL runtime role cannot create projects, change managed backups, or alter provider configuration. Supabase's database backup guidance is at <https://supabase.com/docs/guides/platform/backups> and its backup/restore workflow is at <https://supabase.com/docs/guides/platform/migrating-within-supabase/backup-restore>.

## Required Vercel secrets

| Variable | Purpose |
| --- | --- |
| `CODEFY_BACKUP_SIGNING_KEY` | Signs and validates Codefy backup bundles. |
| `CODEFY_BACKUP_DATABASE_URL` | Optional session/direct read connection for dumps; defaults to the app connection. |
| `CODEFY_RESTORE_DATABASE_URL` | Required session/direct owner connection for destructive restore. |

Use port 5432 with the Supabase session pooler or a direct connection for `pg_dump` and `pg_restore`; port 6543 is transaction-pooler mode and is rejected for these operations. After changing a Vercel variable, redeploy so the PHP container receives it.
