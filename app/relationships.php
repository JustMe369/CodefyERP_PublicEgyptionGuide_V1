<?php
$page_title         = 'المورد والمركبة والسائق';
$page_description   = 'العلاقات بين المورد والمركبة والسائق في نظام كوديفاي';
$page_needs_mermaid = true;
require __DIR__ . '/includes/config.php';
require __DIR__ . '/includes/head.php';
require __DIR__ . '/includes/header.php';
require __DIR__ . '/includes/sidebar.php';
$asset = $SITE['assets'];
$s     = $SECTIONS['relationships'];
?>
<main id="main-content" class="px-4 pt-6 pb-24 sm:px-6 lg:px-8 lg:ms-72 flex-grow min-h-screen">
    <?php require __DIR__ . '/includes/breadcrumb.php'; ?>

    <section id="relationships" class="mb-24 section-content reveal">
        <div class="flex items-start gap-4 mb-8">
            <div class="flex-shrink-0 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br <?= e($s['gradient']) ?> text-white text-2xl shadow-lg <?= e($s['shadow']) ?>" aria-hidden="true"><?= $s['icon'] ?></div>
            <div>
                <div class="pill <?= e($s['pill_bg']) ?> <?= e($s['pill_text']) ?> mb-2"><?= e($s['pill']) ?></div>
                <h2 class="text-3xl sm:text-4xl font-black text-slate-900 m-0 leading-tight"><?= e($s['title']) ?></h2>
                <p class="text-slate-500 font-medium mt-1">من مرتبط بمن؟</p>
            </div>
        </div>

        <div class="callout callout-info mb-8">
            <div class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0" aria-hidden="true">🎯</span>
                <div>
                    <div class="font-black text-blue-900 mb-1">ملخص</div>
                    <p class="text-slate-700 text-sm leading-relaxed m-0">المورد هو الجهة المسؤولة عن توفير المركبات والسائقين. يمكنك الاختيار من ثلاثة نماذج حسب طبيعة العمل: نموذج الموظف (مركبات وسائقون تابعون لك)، نموذج المقاول (مورد خارجي يوفر جميع المتطلبات)، ونموذج الحرفي (سائق مستقل يمتلك مركبته ويعمل بنظام القطعة).</p>
                </div>
            </div>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm mb-8">
            <h3 class="text-base font-black text-slate-800 mb-4 flex items-center gap-2">
                <span class="text-lg" aria-hidden="true">🗺️</span> مخطط يوضح العلاقات بين الكيانات
            </h3>
            <div class="mermaid flex justify-center" dir="rtl">flowchart RL
    S["🏢 المورد"]
    V["🚐 المركبة"]
    D["👨‍✈️ السائق"]
    A["📋 تعيين"]
    T["🚏 الرحلة"]
    S --> V
    S --> D
    D --> A
    V --> A
    S --> A
    A --> T
    style S fill:#f0fdf4,stroke:#22c55e,stroke-width:2px
    style T fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
</div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
            <div class="bg-gradient-to-br from-blue-50 to-white p-6 rounded-2xl border border-blue-100 hover-lift">
                <div class="text-4xl mb-3" aria-hidden="true">👔</div>
                <h3 class="text-lg font-black text-blue-900 mb-1">نموذج الموظف</h3>
                <p class="text-xs text-blue-700 font-bold mb-4">الأسطول الخاص بك</p>
                <ul class="space-y-2 text-xs text-slate-700">
                    <li class="flex gap-2 items-start"><span class="text-blue-500" aria-hidden="true">●</span> السائق موظف لديك</li>
                    <li class="flex gap-2 items-start"><span class="text-blue-500" aria-hidden="true">●</span> المركبة مملوكة لك</li>
                    <li class="flex gap-2 items-start"><span class="text-blue-500" aria-hidden="true">●</span> حقل المورد فارغ</li>
                    <li class="flex gap-2 items-start"><span class="text-blue-500" aria-hidden="true">●</span> السائق يتقاضى راتباً شهرياً</li>
                </ul>
            </div>
            <div class="bg-gradient-to-br from-amber-50 to-white p-6 rounded-2xl border border-amber-100 hover-lift">
                <div class="text-4xl mb-3" aria-hidden="true">🏢</div>
                <h3 class="text-lg font-black text-amber-900 mb-1">نموذج المقاول</h3>
                <p class="text-xs text-amber-700 font-bold mb-4">مورد خارجي</p>
                <ul class="space-y-2 text-xs text-slate-700">
                    <li class="flex gap-2 items-start"><span class="text-amber-500" aria-hidden="true">●</span> السائق مقاول</li>
                    <li class="flex gap-2 items-start"><span class="text-amber-500" aria-hidden="true">●</span> المركبة مملوكة للمورد</li>
                    <li class="flex gap-2 items-start"><span class="text-amber-500" aria-hidden="true">●</span> حقل المورد مطلوب</li>
                </ul>
            </div>
            <div class="bg-gradient-to-br from-teal-50 to-white p-6 rounded-2xl border border-teal-100 hover-lift">
                <div class="text-4xl mb-3" aria-hidden="true">🧑‍🔧</div>
                <h3 class="text-lg font-black text-teal-900 mb-1">نموذج الحرفي</h3>
                <p class="text-xs text-teal-700 font-bold mb-4">سائق مستقل</p>
                <ul class="space-y-2 text-xs text-slate-700">
                    <li class="flex gap-2 items-start"><span class="text-teal-500" aria-hidden="true">●</span> السائق حرفي</li>
                    <li class="flex gap-2 items-start"><span class="text-teal-500" aria-hidden="true">●</span> المركبة مملوكة له</li>
                    <li class="flex gap-2 items-start"><span class="text-teal-500" aria-hidden="true">●</span> حقل المورد فارغ</li>
                    <li class="flex gap-2 items-start"><span class="text-teal-500" aria-hidden="true">●</span> الدفع لكل رحلة</li>
                </ul>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden m-0 hover-lift">
                <div class="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                    <span class="text-lg" aria-hidden="true">🔗</span>
                    <span class="font-bold text-slate-800 text-sm">شكل العلاقة</span>
                </div>
                <img src="<?= $asset ?>/img/vvdr0.jpg" alt="شكل العلاقة بين الكيانات" class="lightbox-trigger w-full h-auto max-h-[400px] object-contain" loading="lazy">
                <figcaption class="p-4 bg-slate-50/50 text-xs text-slate-600 border-t border-slate-100">مخطط يوضح العلاقات بين الكيانات في النظام.</figcaption>
            </figure>
            <figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden m-0 hover-lift">
                <div class="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                    <span class="text-lg" aria-hidden="true">👥</span>
                    <span class="font-bold text-slate-800 text-sm">نماذج التوظيف</span>
                </div>
                <img src="<?= $asset ?>/img/vvdr1.jpg" alt="نماذج التوظيف" class="lightbox-trigger w-full h-auto max-h-[400px] object-contain" loading="lazy">
                <figcaption class="p-4 bg-slate-50/50 text-xs text-slate-600 border-t border-slate-100">النماذج الثلاثة للتوظيف وملكية المركبات.</figcaption>
            </figure>
        </div>
    </section>
</main>
<?php require __DIR__ . '/includes/footer.php'; ?>