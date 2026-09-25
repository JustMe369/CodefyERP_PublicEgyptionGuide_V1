<?php
$page_title       = 'توزيع المهام (تعيين الجداول)';
$page_description = 'توزيع المهام وتعيين الجداول للسائقين والمركبات في نظام كوديفاي';
require __DIR__ . '/includes/config.php';
require __DIR__ . '/includes/head.php';
require __DIR__ . '/includes/header.php';
require __DIR__ . '/includes/sidebar.php';
$asset = $SITE['assets'];
$s     = $SECTIONS['assignments'];
?>
<main id="main-content" class="px-4 pt-6 pb-24 sm:px-6 lg:px-8 lg:ms-72 flex-grow min-h-screen">
    <?php require __DIR__ . '/includes/breadcrumb.php'; ?>

    <section id="assignments" class="mb-24 section-content reveal">
        <div class="flex items-start gap-4 mb-8">
            <div class="flex-shrink-0 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br <?= e($s['gradient']) ?> text-white text-2xl shadow-lg <?= e($s['shadow']) ?>" aria-hidden="true"><?= e($s['icon']) ?></div>
            <div>
                <div class="pill <?= e($s['pill_bg']) ?> <?= e($s['pill_text']) ?> mb-2"><?= e($s['pill']) ?></div>
                <h2 class="text-3xl sm:text-4xl font-black text-slate-900 m-0 leading-tight"><?= e($s['title']) ?></h2>
                <p class="text-slate-500 font-medium mt-1">تحديد المهام والمركبات لكل سائق</p>
            </div>
        </div>

        <div class="callout callout-info mb-8">
            <div class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0" aria-hidden="true">🎯</span>
                <div>
                    <div class="font-black text-blue-900 mb-1">ملخص</div>
                    <p class="text-slate-700 text-sm leading-relaxed m-0">التعيين هو عملية إسناد المهام إلى السائقين والمركبات المحددة. وبهذا يعرف كل سائق مساره والمركبة المخصصة له.</p>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 mb-6 shadow-sm">
            <h3 class="text-lg font-black text-slate-900 mb-5 flex items-center gap-2">
                <span class="text-xl" aria-hidden="true">🧩</span> عناصر التعيين
            </h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div class="p-3 rounded-xl bg-amber-50 border border-amber-100"><div class="text-xs font-bold text-amber-600 mb-1">مشروع النقل</div><div class="text-sm font-bold text-slate-800">العقد أو خدمة العميل</div></div>
                <div class="p-3 rounded-xl bg-amber-50 border border-amber-100"><div class="text-xs font-bold text-amber-600 mb-1">المسار</div><div class="text-sm font-bold text-slate-800">مسار الخدمة</div></div>
                <div class="p-3 rounded-xl bg-amber-50 border border-amber-100"><div class="text-xs font-bold text-amber-600 mb-1">الجدول</div><div class="text-sm font-bold text-slate-800">نمط الوقت المتكرر</div></div>
                <div class="p-3 rounded-xl bg-amber-50 border border-amber-100"><div class="text-xs font-bold text-amber-600 mb-1">المورد</div><div class="text-sm font-bold text-slate-800">مزوّد النقل</div></div>
                <div class="p-3 rounded-xl bg-amber-50 border border-amber-100"><div class="text-xs font-bold text-amber-600 mb-1">المركبة</div><div class="text-sm font-bold text-slate-800">المركبة الفعلية</div></div>
                <div class="p-3 rounded-xl bg-amber-50 border border-amber-100"><div class="text-xs font-bold text-amber-600 mb-1">السائق</div><div class="text-sm font-bold text-slate-800">السائق المسؤول</div></div>
            </div>
        </div>

        <div class="callout callout-example mb-8">
            <div class="flex items-start gap-3 mb-4">
                <span class="text-2xl flex-shrink-0" aria-hidden="true">🛡️</span>
                <div><div class="font-black text-green-900">الترتيب الآمن — اتبع هذه الخطوات</div></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                <div class="flex items-center gap-2 bg-white/70 rounded-lg p-2"><span class="num-dot bg-green-600 text-white">1</span><span class="text-slate-700">أنشئ كيان المورد</span></div>
                <div class="flex items-center gap-2 bg-white/70 rounded-lg p-2"><span class="num-dot bg-green-600 text-white">2</span><span class="text-slate-700">سجّل المركبات</span></div>
                <div class="flex items-center gap-2 bg-white/70 rounded-lg p-2"><span class="num-dot bg-green-600 text-white">3</span><span class="text-slate-700">سجّل السائقين</span></div>
                <div class="flex items-center gap-2 bg-white/70 rounded-lg p-2"><span class="num-dot bg-green-600 text-white">4</span><span class="text-slate-700">تأكد من الامتثال</span></div>
                <div class="flex items-center gap-2 bg-white/70 rounded-lg p-2"><span class="num-dot bg-green-600 text-white">5</span><span class="text-slate-700">حدّد المسار والجدول</span></div>
                <div class="flex items-center gap-2 bg-white/70 rounded-lg p-2"><span class="num-dot bg-green-600 text-white">6</span><span class="text-slate-700">نفّذ التعيين</span></div>
                <div class="flex items-center gap-2 bg-white/70 rounded-lg p-2 sm:col-span-2"><span class="num-dot bg-green-600 text-white">7</span><span class="text-slate-700">راقب المهام</span></div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden m-0 hover-lift">
                <div class="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                    <span class="text-lg" aria-hidden="true">🖼️</span><span class="font-bold text-slate-800 text-sm">واجهة التعيين</span>
                </div>
                <img src="<?= $asset ?>/img/dashboard.png" alt="واجهة التعيين" class="lightbox-trigger w-full h-auto max-h-[400px] object-contain" loading="lazy">
                <figcaption class="p-4 bg-slate-50/50 text-xs text-slate-600 border-t border-slate-100">يتم هنا ربط المورد والمركبة والسائق بالجدول.</figcaption>
            </figure>
            <figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden m-0 hover-lift">
                <div class="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                    <span class="text-lg" aria-hidden="true">🔍</span><span class="font-bold text-slate-800 text-sm">تفاصيل التعيين</span>
                </div>
                <img src="<?= $asset ?>/img/vvdr1.jpg" alt="تفاصيل التعيين" class="lightbox-trigger w-full h-auto max-h-[400px] object-contain" loading="lazy">
                <figcaption class="p-4 bg-slate-50/50 text-xs text-slate-600 border-t border-slate-100">تفاصيل ربط الموارد بالجداول.</figcaption>
            </figure>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden m-0 hover-lift">
                <div class="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                    <span class="text-lg" aria-hidden="true">✏️</span><span class="font-bold text-slate-800 text-sm">تعديل التعيينات — الجزء 1</span>
                </div>
                <img src="<?= $asset ?>/img/workflow.jpg" alt="تعديل جزء 1" class="lightbox-trigger w-full h-auto max-h-[300px] object-contain" loading="lazy">
            </figure>
            <figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden m-0 hover-lift">
                <div class="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                    <span class="text-lg" aria-hidden="true">✏️</span><span class="font-bold text-slate-800 text-sm">تعديل التعيينات — الجزء 2</span>
                </div>
                <img src="<?= $asset ?>/img/workflow1.jpg" alt="تعديل جزء 2" class="lightbox-trigger w-full h-auto max-h-[300px] object-contain" loading="lazy">
            </figure>
        </div>
    </section>
</main>
<?php require __DIR__ . '/includes/footer.php'; ?>
