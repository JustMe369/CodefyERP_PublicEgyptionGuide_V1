<?php
if (!isset($page_title))       $page_title = $SITE['name'];
if (!isset($page_description)) $page_description = 'دليل شامل لنظام كوديفاي';
$asset = $SITE['assets'];
?>
<!DOCTYPE html>
<html lang="ar" dir="rtl" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="<?= e($page_description) ?>">
    <meta name="theme-color" content="#2563eb">
    <title><?= e($page_title) ?> — <?= e($SITE['name']) ?></title>

    <script>
    (function () {
        try {
            var saved = localStorage.getItem('theme');
            document.documentElement.setAttribute('data-theme', saved === 'dark-blue' ? 'dark-blue' : 'light');
        } catch (e) {}
    })();
    </script>

    <script>
    function initJsReady() {
        document.documentElement.classList.add('js-ready');
        window.__jsReadyTimer = setTimeout(function () {
            if (!window.codefyAppLoaded) {
                document.documentElement.classList.remove('js-ready');
                var reveals = document.querySelectorAll('.reveal');
                for (var i = 0; i < reveals.length; i++) { reveals[i].classList.add('is-visible'); }
            }
        }, 3000);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initJsReady);
    } else { requestAnimationFrame(initJsReady); }
    </script>
    <noscript><style>.reveal{opacity:1!important;transform:none!important;}</style></noscript>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

    <?php if (!empty($page_needs_mermaid)): ?>
    <script defer src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <?php endif; ?>
    <?php if (!empty($page_needs_xlsx)): ?>
    <script defer src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
    <?php endif; ?>

    <link rel="stylesheet" href="<?= $asset ?>/CSS/tailwind.generated.css">
    <link rel="stylesheet" href="<?= $asset ?>/CSS/styles.css">
    <link rel="stylesheet" href="<?= $asset ?>/CSS/navbar.css">
    <link rel="stylesheet" href="<?= $asset ?>/CSS/global-theme.css">
    <link rel="stylesheet" href="<?= $asset ?>/CSS/mobile.css">
    <link rel="stylesheet" href="<?= $asset ?>/CSS/footer.css">
    <link rel="stylesheet" href="<?= $asset ?>/CSS/cms-content.css">
</head>
