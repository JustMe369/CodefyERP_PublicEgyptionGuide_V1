BEGIN;

ALTER TABLE codefy_guide_sections
    DROP CONSTRAINT IF EXISTS codefy_guide_sections_slug_check;
ALTER TABLE codefy_guide_sections
    ADD CONSTRAINT codefy_guide_sections_slug_format_check
    CHECK (char_length(slug) <= 80 AND slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$');

ALTER TABLE codefy_guide_sections
    ADD COLUMN IF NOT EXISTS accent text;
UPDATE codefy_guide_sections SET accent = CASE slug
    WHEN 'bulk-import' THEN 'indigo'
    WHEN 'relationships' THEN 'emerald'
    WHEN 'assignments' THEN 'amber'
    WHEN 'pricing' THEN 'violet'
    WHEN 'readiness' THEN 'rose'
    WHEN 'analysis-config' THEN 'cyan'
    ELSE 'primary'
END WHERE accent IS NULL;
ALTER TABLE codefy_guide_sections ALTER COLUMN accent SET DEFAULT 'primary';
ALTER TABLE codefy_guide_sections ALTER COLUMN accent SET NOT NULL;
ALTER TABLE codefy_guide_sections
    ADD COLUMN IF NOT EXISTS content_mode text NOT NULL DEFAULT 'legacy';
ALTER TABLE codefy_guide_sections
    DROP CONSTRAINT IF EXISTS codefy_guide_sections_accent_check;
ALTER TABLE codefy_guide_sections
    ADD CONSTRAINT codefy_guide_sections_accent_check
    CHECK (accent IN ('primary', 'indigo', 'emerald', 'amber', 'violet', 'rose', 'cyan'));
ALTER TABLE codefy_guide_sections
    DROP CONSTRAINT IF EXISTS codefy_guide_sections_content_mode_check;
ALTER TABLE codefy_guide_sections
    ADD CONSTRAINT codefy_guide_sections_content_mode_check
    CHECK (content_mode IN ('legacy', 'builder'));
ALTER TABLE codefy_guide_sections
    DROP CONSTRAINT IF EXISTS codefy_guide_sections_slug_format_check;
ALTER TABLE codefy_guide_sections
    ADD CONSTRAINT codefy_guide_sections_slug_format_check
    CHECK (char_length(slug) <= 80 AND slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$');

CREATE TABLE IF NOT EXISTS codefy_section_blocks (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    section_slug text NOT NULL REFERENCES codefy_guide_sections(slug) ON UPDATE CASCADE ON DELETE CASCADE,
    block_type text NOT NULL CHECK (block_type IN (
        'heading', 'paragraph', 'list', 'steps', 'callout', 'image',
        'table', 'code', 'mermaid', 'link', 'divider'
    )),
    payload jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(payload) = 'object'),
    sort_order smallint NOT NULL CHECK (sort_order > 0),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (section_slug, sort_order)
);

CREATE INDEX IF NOT EXISTS codefy_section_blocks_order_idx
    ON codefy_section_blocks (section_slug, sort_order, id);

ALTER TABLE codefy_section_blocks ENABLE ROW LEVEL SECURITY;
DO $migration$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
        REVOKE ALL ON TABLE codefy_section_blocks FROM anon;
        REVOKE ALL ON SEQUENCE codefy_section_blocks_id_seq FROM anon;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
        REVOKE ALL ON TABLE codefy_section_blocks FROM authenticated;
        REVOKE ALL ON SEQUENCE codefy_section_blocks_id_seq FROM authenticated;
    END IF;
END
$migration$;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE codefy_section_blocks TO codefy_app;
GRANT USAGE, SELECT ON SEQUENCE codefy_section_blocks_id_seq TO codefy_app;
GRANT DELETE ON TABLE codefy_guide_sections TO codefy_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO codefy_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO codefy_app;
DROP POLICY IF EXISTS codefy_app_access ON codefy_section_blocks;
CREATE POLICY codefy_app_access ON codefy_section_blocks
    FOR ALL TO codefy_app USING (true) WITH CHECK (true);

ALTER TABLE codefy_site_settings
    DROP CONSTRAINT IF EXISTS codefy_site_settings_setting_key_check;

INSERT INTO codefy_site_settings (setting_key, setting_value) VALUES
    ('home_eyebrow', 'دليلك الشامل — الإصدار 3.0'),
    ('home_title', 'فهرس دليل نظام كوديفاي'),
    ('home_intro', 'اختر القسم الذي تريد استعراضه. تم تقسيم الدليل إلى صفحات مستقلة لسهولة التصفح والوصول السريع.'),
    ('navigation_label', 'دليلك'),
    ('search_placeholder', 'ابحث في الدليل... (Ctrl+K)')
ON CONFLICT (setting_key) DO NOTHING;

INSERT INTO codefy_schema_migrations (version)
VALUES ('003_visual_section_builder')
ON CONFLICT (version) DO NOTHING;

COMMIT;
