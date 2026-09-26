# Admin access control

The admin panel uses application roles stored in PostgreSQL. These roles control PHP routes and actions; they do not change PostgreSQL login privileges.

## Built-in roles

| Role | Capabilities |
| --- | --- |
| Superuser | Full control, including system roles and other superuser accounts. The last active superuser is protected. |
| Admin | User, custom-role, section, settings, and database management. Cannot change system roles or superuser accounts. |
| Section author | View the dashboard and sections, create unpublished sections, and edit only their own unpublished drafts. |
| Viewer | Read-only dashboard and section access. |

Custom roles can combine the available capabilities. The server checks permissions on every route and POST action. Changing a role or password revokes existing sessions. A new section authored without `sections.publish` is always saved as an unpublished draft.

## Apply the Supabase migration

Run from the repository root:

```powershell
.\scripts\migrate-supabase.ps1
```

Enter the Supabase `postgres` database password into the secure prompt. The script applies the idempotent files in `database/migrations/`, verifies all four migrations, confirms the role and permission catalogs, and verifies that `codefy_app` can read the migration ledger needed by database exports. It does not rotate the existing `codefy_app` password or write credentials to `.env`.

For local PostgreSQL, use `.scriptsmigrate-postgres.ps1` after configuring the migration-owner credentials in `.env`.

## Database export

Supabase backup connections on the transaction-pooler port `6543` are normalized to session-pooler port `5432`. The runtime application role receives read access to all `public.codefy_*` tables, including the migration ledger. If `pg_dump` reports a permission error, configure `CODEFY_BACKUP_DATABASE_URL` with a same-project session or direct connection that has `SELECT` on all exported tables.
