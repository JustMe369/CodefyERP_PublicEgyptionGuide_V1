BEGIN;

-- The PHP backend uses a restricted login role. Keep Supabase's exposed public
-- schema inaccessible through anon/authenticated Data API roles.
REVOKE ALL ON TABLE
    codefy_admin_users,
    codefy_site_settings,
    codefy_guide_sections,
    codefy_admin_audit_log,
    codefy_admin_login_throttle
FROM anon, authenticated;
REVOKE ALL ON SEQUENCE
    codefy_admin_users_id_seq,
    codefy_admin_audit_log_id_seq
FROM anon, authenticated;

GRANT SELECT, INSERT, UPDATE ON
    codefy_admin_users,
    codefy_site_settings,
    codefy_guide_sections,
    codefy_admin_audit_log,
    codefy_admin_login_throttle
TO codefy_app;
GRANT DELETE ON codefy_admin_login_throttle TO codefy_app;
GRANT USAGE, SELECT ON SEQUENCE codefy_admin_users_id_seq, codefy_admin_audit_log_id_seq TO codefy_app;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE ON TABLES TO codefy_app;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO codefy_app;

ALTER TABLE codefy_admin_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE codefy_site_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE codefy_guide_sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE codefy_admin_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE codefy_admin_login_throttle ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS codefy_app_access ON codefy_admin_users;
CREATE POLICY codefy_app_access ON codefy_admin_users FOR ALL TO codefy_app USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS codefy_app_access ON codefy_site_settings;
CREATE POLICY codefy_app_access ON codefy_site_settings FOR ALL TO codefy_app USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS codefy_app_access ON codefy_guide_sections;
CREATE POLICY codefy_app_access ON codefy_guide_sections FOR ALL TO codefy_app USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS codefy_app_access ON codefy_admin_audit_log;
CREATE POLICY codefy_app_access ON codefy_admin_audit_log FOR ALL TO codefy_app USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS codefy_app_access ON codefy_admin_login_throttle;
CREATE POLICY codefy_app_access ON codefy_admin_login_throttle FOR ALL TO codefy_app USING (true) WITH CHECK (true);

INSERT INTO codefy_schema_migrations (version)
VALUES ('002_runtime_role_security')
ON CONFLICT (version) DO NOTHING;

COMMIT;
