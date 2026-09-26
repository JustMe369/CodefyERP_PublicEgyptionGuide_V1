<?php
$activeNav = (string)($activeNav ?? '');
$navItems = [
    ['dashboard.view', 'index.php', 'dashboard', '◈', 'نظرة عامة'],
    ['sections.view', 'sections.php', 'sections', '▤', 'محرر الأقسام'],
    ['settings.manage', 'index.php#settings', 'settings', '⚙', 'إعدادات الموقع'],
    ['users.view', 'users.php', 'users', '♙', 'المستخدمون'],
    ['roles.view', 'roles.php', 'roles', '✦', 'الأدوار والصلاحيات'],
    ['database.view', 'database.php', 'database', '▣', 'قاعدة البيانات'],
    ['audit.view', 'index.php#activity', 'activity', '◷', 'سجل النشاط'],
];
?>
<nav aria-label="أقسام الإدارة">
    <?php foreach ($navItems as [$permission, $href, $key, $icon, $label]): if (!admin_can($permission, $user)) continue; ?>
        <a class="side-link<?= $activeNav === $key ? ' active' : '' ?>" href="<?= admin_e($href) ?>"<?= $activeNav === $key ? ' aria-current="page"' : '' ?>><?= admin_e($icon) ?> <span><?= admin_e($label) ?></span></a>
    <?php endforeach; ?>
</nav>
