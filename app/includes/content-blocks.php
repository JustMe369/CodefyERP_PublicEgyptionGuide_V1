<?php
/** Safe server-side renderer for the visual section builder. */
function codefy_content_e($value): string {
    return htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function codefy_content_url($value, bool $image = false): ?string {
    if (!is_string($value)) return null;
    $url = trim($value);
    if ($url === '' || preg_match('/[\x00-\x20]/', $url)) return null;
    if (preg_match('#^https://#i', $url) && filter_var($url, FILTER_VALIDATE_URL)) return $url;
    if (preg_match('#^(?:/)?Statics/[A-Za-z0-9_./-]+$#', $url) && !str_contains($url, '..')) return $url;
    if (!$image && preg_match('/^#[A-Za-z][A-Za-z0-9_-]*$/', $url)) return $url;
    return null;
}

function codefy_render_content_block(array $block): void {
    $data = is_array($block['data'] ?? null) ? $block['data'] : [];
    $type = (string)($block['type'] ?? '');
    $layout = is_array($data['layout'] ?? null) ? $data['layout'] : [];
    $width = in_array(($layout['width'] ?? 'full'), ['full', 'wide', 'half', 'third'], true) ? ($layout['width'] ?? 'full') : 'full';
    $align = in_array(($layout['align'] ?? 'start'), ['start', 'center', 'end'], true) ? ($layout['align'] ?? 'start') : 'start';
    echo '<div class="cms-block cms-block--' . $width . ' cms-block--align-' . $align . '">';
    switch ($type) {
        case 'heading':
            $level = (int)($data['level'] ?? 2);
            if (!in_array($level, [2, 3, 4], true)) $level = 2;
            $text = trim((string)($data['text'] ?? ''));
            if ($text !== '') echo '<h' . $level . ' class="cms-block-heading">' . codefy_content_e($text) . '</h' . $level . '>';
            break;
        case 'paragraph':
            $text = trim((string)($data['text'] ?? ''));
            if ($text !== '') echo '<p class="cms-block-paragraph">' . nl2br(codefy_content_e($text), false) . '</p>';
            break;
        case 'list':
            $items = array_slice(array_filter((array)($data['items'] ?? []), 'is_scalar'), 0, 80);
            $tag = !empty($data['ordered']) ? 'ol' : 'ul';
            if ($items) {
                echo '<' . $tag . ' class="cms-block-list">';
                foreach ($items as $item) echo '<li>' . nl2br(codefy_content_e($item), false) . '</li>';
                echo '</' . $tag . '>';
            }
            break;
        case 'steps':
            $items = array_slice((array)($data['items'] ?? []), 0, 40);
            if ($items) {
                echo '<ol class="cms-block-steps">';
                foreach ($items as $item) {
                    if (!is_array($item)) continue;
                    echo '<li><strong>' . codefy_content_e($item['title'] ?? '') . '</strong><p>' . nl2br(codefy_content_e($item['text'] ?? ''), false) . '</p></li>';
                }
                echo '</ol>';
            }
            break;
        case 'callout':
            $tone = (string)($data['tone'] ?? 'info');
            if (!in_array($tone, ['info', 'tip', 'warning', 'example'], true)) $tone = 'info';
            echo '<aside class="cms-callout cms-callout--' . $tone . '">';
            if (trim((string)($data['title'] ?? '')) !== '') echo '<h3>' . codefy_content_e($data['title']) . '</h3>';
            echo '<p>' . nl2br(codefy_content_e($data['text'] ?? ''), false) . '</p></aside>';
            break;
        case 'image':
            $src = codefy_content_url($data['src'] ?? '', true);
            if ($src) {
                echo '<figure class="cms-block-image"><img src="' . codefy_content_e($src) . '" alt="' . codefy_content_e($data['alt'] ?? '') . '" loading="lazy">';
                if (trim((string)($data['caption'] ?? '')) !== '') echo '<figcaption>' . codefy_content_e($data['caption']) . '</figcaption>';
                echo '</figure>';
            }
            break;
        case 'table':
            $headers = array_slice(array_filter((array)($data['headers'] ?? []), 'is_scalar'), 0, 12);
            $rows = array_slice((array)($data['rows'] ?? []), 0, 80);
            if ($headers) {
                echo '<div class="cms-table-wrap"><table class="cms-block-table"><thead><tr>';
                foreach ($headers as $cell) echo '<th scope="col">' . codefy_content_e($cell) . '</th>';
                echo '</tr></thead><tbody>';
                foreach ($rows as $row) {
                    if (!is_array($row)) continue;
                    echo '<tr>';
                    foreach ($headers as $index => $_) echo '<td>' . codefy_content_e($row[$index] ?? '') . '</td>';
                    echo '</tr>';
                }
                echo '</tbody></table></div>';
            }
            break;
        case 'code':
            $language = preg_replace('/[^a-zA-Z0-9_+-]/', '', (string)($data['language'] ?? 'text')) ?: 'text';
            echo '<pre class="cms-block-code"><code class="language-' . codefy_content_e($language) . '">' . codefy_content_e($data['code'] ?? '') . '</code></pre>';
            break;
        case 'mermaid':
            $source = trim((string)($data['source'] ?? ''));
            if ($source !== '') echo '<pre class="mermaid cms-block-diagram">' . codefy_content_e($source) . '</pre>';
            break;
        case 'link':
            $url = codefy_content_url($data['url'] ?? '');
            if ($url) echo '<p class="cms-block-link"><a href="' . codefy_content_e($url) . '"' . (str_starts_with($url, 'https://') ? ' rel="noopener noreferrer" target="_blank"' : '') . '>' . codefy_content_e($data['label'] ?? $url) . ' <span aria-hidden="true">←</span></a></p>';
            break;
        case 'divider':
            echo '<hr class="cms-block-divider">';
            break;
    }
    echo '</div>';
}

function codefy_render_section_content(string $slug): void {
    global $SECTIONS, $SITE;
    if (!isset($SECTIONS[$slug])) return;
    $section = $SECTIONS[$slug];
    $blocks = codefy_db()->prepare('SELECT block_type AS type, payload AS data FROM codefy_section_blocks WHERE section_slug = :slug ORDER BY sort_order, id');
    $blocks->execute(['slug' => $slug]);
    echo '<main id="main-content" class="px-4 pt-6 pb-24 sm:px-6 lg:px-8 lg:ms-72 flex-grow min-h-screen">';
    require __DIR__ . '/breadcrumb.php';
    echo '<section class="cms-section-page mb-24">';
    echo '<header class="cms-section-hero"><div class="cms-section-icon" aria-hidden="true">' . codefy_content_e($section['icon']) . '</div><div><span class="cms-section-kicker">' . codefy_content_e($SITE['name']) . ' · ' . (int)$section['number'] . '</span><h1>' . codefy_content_e($section['title']) . '</h1><p>' . codefy_content_e($section['subtitle']) . '</p></div></header>';
    echo '<div class="cms-section-content">';
    foreach ($blocks as $block) {
        $payload = $block['data'];
        if (is_string($payload)) $payload = json_decode($payload, true);
        $block['data'] = is_array($payload) ? $payload : [];
        codefy_render_content_block($block);
    }
    echo '</div></section></main>';
}
