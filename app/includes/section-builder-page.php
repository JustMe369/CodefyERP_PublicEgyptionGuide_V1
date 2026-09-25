<?php
$sectionSlug = codefy_current_slug();
$section = $SECTIONS[$sectionSlug] ?? null;
if (!$section || empty($section['published'])) {
    http_response_code(404);
    exit('هذا القسم غير متاح حالياً.');
}
$page_title = $section['title'];
$page_description = $section['subtitle'];
require __DIR__ . '/head.php';
require __DIR__ . '/header.php';
require __DIR__ . '/sidebar.php';
require_once __DIR__ . '/content-blocks.php';
codefy_render_section_content($sectionSlug);
require __DIR__ . '/footer.php';
exit;
