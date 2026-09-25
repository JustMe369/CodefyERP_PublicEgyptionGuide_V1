<?php
/**
 * Codefy Documentation — Global configuration & section registry.
 * Every page requires this file first.
 */

$SITE = [
    'name'         => 'كوديفاي',
    'brand_suffix' => '.',
    'subtitle'     => 'دليل المستخدم الشامل',
    'copyright'    => 'كوديفاي مصر © 2026 — جميع الحقوق محفوظة',
    'version'      => '3.0',
    'assets'       => 'Statics',
];

$SECTIONS = [
    'login' => [
        'title'    => 'تسجيل الدخول',
        'subtitle' => 'الخطوة الأولى بكلمة المرور',
        'icon'     => '🔐',
        'number'   => 1,
        'pill'     => 'أولاً',
        'pill_bg'  => 'bg-primary-50',
        'pill_text'=> 'text-primary-700',
        'gradient' => 'from-primary-500 to-primary-700',
        'shadow'   => 'shadow-primary-500/30',
        'accent'   => 'primary',
    ],
    'bulk-import' => [
        'title'    => 'تحديثات جماعية',
        'subtitle' => 'ملف الإكسل ينجز المهمة في ثوانٍ',
        'icon'     => '📦',
        'number'   => 2,
        'pill'     => 'القسم الثاني',
        'pill_bg'  => 'bg-indigo-50',
        'pill_text'=> 'text-indigo-700',
        'gradient' => 'from-indigo-500 to-purple-600',
        'shadow'   => 'shadow-indigo-500/30',
        'accent'   => 'indigo',
    ],
    'relationships' => [
        'title'    => 'المورد والمركبة والسائق',
        'subtitle' => 'ربط المشاريع بالموردين والمركبات',
        'icon'     => '🤝',
        'number'   => 3,
        'pill'     => 'القسم الثالث',
        'pill_bg'  => 'bg-emerald-50',
        'pill_text'=> 'text-emerald-700',
        'gradient' => 'from-emerald-500 to-teal-600',
        'shadow'   => 'shadow-emerald-500/30',
        'accent'   => 'emerald',
    ],
    'assignments' => [
        'title'    => 'توزيع المهام (الجداول)',
        'subtitle' => 'تحديد المهام لكل سائق',
        'icon'     => '📋',
        'number'   => 4,
        'pill'     => 'القسم الرابع',
        'pill_bg'  => 'bg-amber-50',
        'pill_text'=> 'text-amber-700',
        'gradient' => 'from-amber-500 to-orange-600',
        'shadow'   => 'shadow-amber-500/30',
        'accent'   => 'amber',
    ],
    'pricing' => [
        'title'    => 'حساب التسعير والهامش الربحي',
        'subtitle' => 'معادلة بسيطة بين المورد والعميل',
        'icon'     => '💰',
        'number'   => 5,
        'pill'     => 'القسم الخامس',
        'pill_bg'  => 'bg-violet-50',
        'pill_text'=> 'text-violet-700',
        'gradient' => 'from-violet-500 to-fuchsia-600',
        'shadow'   => 'shadow-violet-500/30',
        'accent'   => 'violet',
    ],
    'readiness' => [
        'title'    => 'مراجعة الجاهزية',
        'subtitle' => 'التأكد من اكتمال جميع المتطلبات قبل الانطلاق',
        'icon'     => '✅',
        'number'   => 6,
        'pill'     => 'القسم السادس',
        'pill_bg'  => 'bg-rose-50',
        'pill_text'=> 'text-rose-700',
        'gradient' => 'from-rose-500 to-red-600',
        'shadow'   => 'shadow-rose-500/30',
        'accent'   => 'rose',
    ],
    'analysis-config' => [
        'title'    => 'إعدادات تحليل الإكسل',
        'subtitle' => 'تخصيص قواعد التحقق والمعالجة',
        'icon'     => '⚙️',
        'number'   => 7,
        'pill'     => 'إعدادات متقدمة',
        'pill_bg'  => 'bg-cyan-50',
        'pill_text'=> 'text-cyan-700',
        'gradient' => 'from-cyan-500 to-teal-600',
        'shadow'   => 'shadow-cyan-500/30',
        'accent'   => 'cyan',
    ],
];

require_once __DIR__ . '/admin-db.php';
codefy_apply_database_content();

/** Return the current page slug (filename without .php) */
function codefy_current_slug(): string {
    return basename($_SERVER['PHP_SELF'] ?? 'index.php', '.php');
}

/** Return ['prev'=>slug|null, 'next'=>slug|null] for a given slug */
function codefy_neighbors(array $sections, string $current): array {
    $keys = array_keys($sections);
    $idx  = array_search($current, $keys, true);
    if ($idx === false) return ['prev' => null, 'next' => null];
    return [
        'prev' => $keys[$idx - 1] ?? null,
        'next' => $keys[$idx + 1] ?? null,
    ];
}

/** Escape helper */
function e(?string $v): string {
    return htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8');
}
