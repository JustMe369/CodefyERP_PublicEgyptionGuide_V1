BEGIN;

CREATE TABLE IF NOT EXISTS codefy_schema_migrations (
    version text PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS codefy_admin_users (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email text NOT NULL UNIQUE,
    password_hash text NOT NULL,
    display_name text NOT NULL,
    role text NOT NULL DEFAULT 'admin' CHECK (role IN ('admin', 'editor')),
    is_active boolean NOT NULL DEFAULT true,
    session_version integer NOT NULL DEFAULT 1,
    last_login_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE codefy_admin_users ADD COLUMN IF NOT EXISTS session_version integer NOT NULL DEFAULT 1;
CREATE UNIQUE INDEX IF NOT EXISTS codefy_admin_email_lower_idx ON codefy_admin_users (lower(email));

CREATE TABLE IF NOT EXISTS codefy_site_settings (
    setting_key text PRIMARY KEY CHECK (setting_key IN ('name', 'brand_suffix', 'subtitle', 'copyright', 'version')),
    setting_value text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    updated_by bigint REFERENCES codefy_admin_users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS codefy_guide_sections (
    slug text PRIMARY KEY CHECK (slug IN ('login', 'bulk-import', 'relationships', 'assignments', 'pricing', 'readiness', 'analysis-config')),
    title text NOT NULL,
    subtitle text NOT NULL,
    icon text NOT NULL,
    sort_order smallint NOT NULL UNIQUE CHECK (sort_order > 0),
    is_published boolean NOT NULL DEFAULT true,
    updated_at timestamptz NOT NULL DEFAULT now(),
    updated_by bigint REFERENCES codefy_admin_users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS codefy_admin_audit_log (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    admin_id bigint REFERENCES codefy_admin_users(id) ON DELETE SET NULL,
    action text NOT NULL,
    entity_type text NOT NULL,
    entity_id text,
    details jsonb NOT NULL DEFAULT '{}'::jsonb,
    ip_address inet,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS codefy_admin_login_throttle (
    ip_hash char(64) PRIMARY KEY,
    failed_attempts smallint NOT NULL DEFAULT 0 CHECK (failed_attempts >= 0),
    window_started_at timestamptz NOT NULL DEFAULT now(),
    blocked_until timestamptz,
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS codefy_admin_audit_created_idx ON codefy_admin_audit_log (created_at DESC);
CREATE INDEX IF NOT EXISTS codefy_admin_audit_admin_created_idx ON codefy_admin_audit_log (admin_id, created_at DESC);
CREATE INDEX IF NOT EXISTS codefy_admin_login_throttle_updated_idx ON codefy_admin_login_throttle (updated_at);
GRANT DELETE ON codefy_admin_login_throttle TO codefy_app;

INSERT INTO codefy_site_settings (setting_key, setting_value) VALUES
    ('name', 'كوديفاي'),
    ('brand_suffix', '.'),
    ('subtitle', 'دليل المستخدم الشامل'),
    ('copyright', 'كوديفاي مصر © 2026 — جميع الحقوق محفوظة'),
    ('version', '3.0')
ON CONFLICT (setting_key) DO NOTHING;

INSERT INTO codefy_guide_sections (slug, title, subtitle, icon, sort_order) VALUES
    ('login', 'تسجيل الدخول', 'الخطوة الأولى بكلمة المرور', '🔐', 1),
    ('bulk-import', 'تحديثات جماعية', 'ملف الإكسل ينجز المهمة في ثوانٍ', '📦', 2),
    ('relationships', 'المورد والمركبة والسائق', 'ربط المشاريع بالموردين والمركبات', '🤝', 3),
    ('assignments', 'توزيع المهام (الجداول)', 'تحديد المهام لكل سائق', '📋', 4),
    ('pricing', 'حساب التسعير والهامش الربحي', 'معادلة بسيطة بين المورد والعميل', '💰', 5),
    ('readiness', 'مراجعة الجاهزية', 'التأكد من اكتمال جميع المتطلبات قبل الانطلاق', '✅', 6),
    ('analysis-config', 'إعدادات تحليل الإكسل', 'تخصيص قواعد التحقق والمعالجة', '⚙️', 7)
ON CONFLICT (slug) DO NOTHING;

INSERT INTO codefy_schema_migrations (version) VALUES ('001_admin_foundation') ON CONFLICT (version) DO NOTHING;

COMMIT;
