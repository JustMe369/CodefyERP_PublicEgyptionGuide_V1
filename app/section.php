<?php
$page_title = 'القسم';
require __DIR__ . '/includes/config.php';
$slug = codefy_current_slug();
if (!isset($SECTIONS[$slug]) || empty($SECTIONS[$slug]['published'])) {
    http_response_code(404);
    require __DIR__ . '/includes/head.php';
    echo '<main class="mx-auto min-h-screen max-w-3xl p-10 text-center"><h1>الصفحة غير موجودة</h1><a href="index.php">العودة إلى الفهرس</a></main>';
    exit;
}
if (($SECTIONS[$slug]['content_mode'] ?? 'legacy') !== 'builder') {
    $legacyFile = __DIR__ . DIRECTORY_SEPARATOR . $slug . '.php';
    if (is_file($legacyFile)) { header('Location: ' . rawurlencode($slug) . '.php', true, 302); exit; }
}
$section = $SECTIONS[$slug];
$page_title = $section['title'];
$page_description = $section['subtitle'];
require __DIR__ . '/includes/head.php';
require __DIR__ . '/includes/header.php';
require __DIR__ . '/includes/sidebar.php';
require __DIR__ . '/includes/content-blocks.php';
codefy_render_section_content($slug);
require __DIR__ . '/includes/footer.php';
