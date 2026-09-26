BEGIN;

CREATE TABLE IF NOT EXISTS codefy_admin_roles (
    role_key text PRIMARY KEY CHECK (role_key ~ '^[a-z][a-z0-9_]{1,47}$'),
    name text NOT NULL CHECK (char_length(name) BETWEEN 1 AND 80),
    description text NOT NULL DEFAULT '' CHECK (char_length(description) <= 500),
    is_system boolean NOT NULL DEFAULT false,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS codefy_admin_permissions (
    permission_key text PRIMARY KEY CHECK (permission_key ~ '^[a-z][a-z0-9_.]{1,79}$'),
    group_key text NOT NULL,
    label text NOT NULL,
    description text NOT NULL DEFAULT '',
    sort_order smallint NOT NULL UNIQUE CHECK (sort_order > 0)
);

CREATE TABLE IF NOT EXISTS codefy_admin_role_permissions (
    role_key text NOT NULL REFERENCES codefy_admin_roles(role_key) ON UPDATE CASCADE ON DELETE CASCADE,
    permission_key text NOT NULL REFERENCES codefy_admin_permissions(permission_key) ON UPDATE CASCADE ON DELETE CASCADE,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (role_key, permission_key)
);

INSERT INTO codefy_admin_roles (role_key, name, description, is_system) VALUES
    ('superuser', 'المستخدم الأعلى', 'صلاحيات كاملة لإدارة لوحة التحكم والأدوار والحسابات.', true),
    ('admin', 'مدير النظام', 'إدارة المستخدمين والأقسام والإعدادات وقاعدة البيانات.', true),
    ('section_author', 'مساهم الأقسام', 'قراءة لوحة التحكم وإنشاء مسودات أقسام وإدارة مسوداته فقط.', true),
    ('viewer', 'قارئ', 'استعراض لوحة التحكم ومحتوى الأقسام دون تعديل.', true)
ON CONFLICT (role_key) DO UPDATE SET name = EXCLUDED.name, description = EXCLUDED.description, is_system = true;

INSERT INTO codefy_admin_permissions (permission_key, group_key, label, description, sort_order) VALUES
    ('dashboard.view', 'dashboard', 'عرض لوحة التحكم', 'فتح ملخص المشروع.', 1),
    ('sections.view', 'sections', 'عرض الأقسام', 'استعراض قائمة الأقسام ومحتواها.', 10),
    ('sections.create', 'sections', 'إنشاء مسودة قسم', 'إضافة قسم جديد يبدأ غير منشور.', 11),
    ('sections.edit', 'sections', 'تعديل الأقسام', 'تعديل بيانات ومحتوى الأقسام.', 12),
    ('sections.edit_own_draft', 'sections', 'تعديل مسوداتي', 'تعديل المسودات التي أنشأها المستخدم فقط.', 13),
    ('sections.delete', 'sections', 'حذف الأقسام', 'حذف قسم ومحتواه نهائياً.', 14),
    ('sections.publish', 'sections', 'نشر الأقسام', 'تفعيل الأقسام وإظهارها للزوار.', 15),
    ('settings.manage', 'settings', 'إدارة إعدادات الموقع', 'تعديل هوية الموقع وإعداداته.', 20),
    ('database.view', 'database', 'عرض قاعدة البيانات', 'عرض حالة الاتصال وجرد الجداول.', 30),
    ('database.backup', 'database', 'إنشاء نسخة احتياطية', 'تصدير حزمة بيانات التطبيق.', 31),
    ('database.restore', 'database', 'استعادة نسخة احتياطية', 'استبدال بيانات التطبيق بنسخة موثوقة.', 32),
    ('users.view', 'users', 'عرض المستخدمين', 'استعراض حسابات لوحة التحكم.', 40),
    ('users.create', 'users', 'إنشاء المستخدمين', 'إضافة حسابات جديدة وتحديد أدوارها.', 41),
    ('users.update', 'users', 'تعديل المستخدمين', 'تعديل الحسابات أو تعطيلها أو إعادة كلمة المرور.', 42),
    ('users.delete', 'users', 'حذف المستخدمين', 'حذف حسابات لوحة التحكم.', 43),
    ('roles.view', 'roles', 'عرض الأدوار', 'استعراض الأدوار وصلاحياتها.', 50),
    ('roles.manage', 'roles', 'إدارة الأدوار', 'إنشاء الأدوار المخصصة وتعديل صلاحياتها.', 51),
    ('audit.view', 'audit', 'عرض سجل النشاط', 'استعراض سجل تغييرات لوحة التحكم.', 60)
ON CONFLICT (permission_key) DO UPDATE SET
    group_key = EXCLUDED.group_key, label = EXCLUDED.label,
    description = EXCLUDED.description, sort_order = EXCLUDED.sort_order;

INSERT INTO codefy_admin_role_permissions (role_key, permission_key)
SELECT 'superuser', permission_key FROM codefy_admin_permissions
ON CONFLICT DO NOTHING;

INSERT INTO codefy_admin_role_permissions (role_key, permission_key)
SELECT 'admin', permission_key FROM codefy_admin_permissions
ON CONFLICT DO NOTHING;

INSERT INTO codefy_admin_role_permissions (role_key, permission_key) VALUES
    ('section_author', 'dashboard.view'),
    ('section_author', 'sections.view'),
    ('section_author', 'sections.create'),
    ('section_author', 'sections.edit_own_draft'),
    ('viewer', 'dashboard.view'),
    ('viewer', 'sections.view')
ON CONFLICT DO NOTHING;

ALTER TABLE codefy_admin_users DROP CONSTRAINT IF EXISTS codefy_admin_users_role_check;
UPDATE codefy_admin_users SET role = 'section_author' WHERE role = 'editor';

DO $migration$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'codefy_admin_users_role_fkey') THEN
        ALTER TABLE codefy_admin_users
            ADD CONSTRAINT codefy_admin_users_role_fkey
            FOREIGN KEY (role) REFERENCES codefy_admin_roles(role_key)
            ON UPDATE CASCADE ON DELETE RESTRICT;
    END IF;
END
$migration$;

-- The first existing administrator is the installation owner; retain other administrators as administrators.
UPDATE codefy_admin_users
SET role = 'superuser', session_version = session_version + 1, updated_at = now()
WHERE id = (
    SELECT id FROM codefy_admin_users
    WHERE role = 'admin' AND is_active
    ORDER BY id
    LIMIT 1
)
AND NOT EXISTS (SELECT 1 FROM codefy_admin_users WHERE role = 'superuser' AND is_active);

ALTER TABLE codefy_guide_sections
    ADD COLUMN IF NOT EXISTS created_by bigint REFERENCES codefy_admin_users(id) ON DELETE SET NULL;

-- The export includes this ledger along with all public.codefy_* tables.
GRANT SELECT ON codefy_schema_migrations TO codefy_app;

ALTER TABLE codefy_admin_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE codefy_admin_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE codefy_admin_role_permissions ENABLE ROW LEVEL SECURITY;

DO $migration$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
        REVOKE ALL ON TABLE codefy_admin_roles, codefy_admin_permissions, codefy_admin_role_permissions FROM anon;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
        REVOKE ALL ON TABLE codefy_admin_roles, codefy_admin_permissions, codefy_admin_role_permissions FROM authenticated;
    END IF;
END
$migration$;

GRANT SELECT, INSERT, UPDATE, DELETE ON
    codefy_admin_roles, codefy_admin_permissions, codefy_admin_role_permissions
TO codefy_app;
GRANT SELECT, UPDATE ON codefy_guide_sections TO codefy_app;

DROP POLICY IF EXISTS codefy_app_access ON codefy_admin_roles;
CREATE POLICY codefy_app_access ON codefy_admin_roles FOR ALL TO codefy_app USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS codefy_app_access ON codefy_admin_permissions;
CREATE POLICY codefy_app_access ON codefy_admin_permissions FOR ALL TO codefy_app USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS codefy_app_access ON codefy_admin_role_permissions;
CREATE POLICY codefy_app_access ON codefy_admin_role_permissions FOR ALL TO codefy_app USING (true) WITH CHECK (true);

INSERT INTO codefy_schema_migrations (version)
VALUES ('004_admin_roles_and_draft_sections')
ON CONFLICT (version) DO NOTHING;

COMMIT;
