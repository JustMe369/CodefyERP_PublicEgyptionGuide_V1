<?php
$page_title       = 'حساب التسعير والهامش الربحي';
$page_description = 'تسعير الإمداد والمبيعات وحساب هامش الربح في نظام كوديفاي';
require __DIR__ . '/includes/config.php';
require __DIR__ . '/includes/head.php';
require __DIR__ . '/includes/header.php';
require __DIR__ . '/includes/sidebar.php';
$asset = $SITE['assets'];
$s     = $SECTIONS['pricing'];
?>
<main id="main-content" class="px-4 pt-6 pb-24 sm:px-6 lg:px-8 lg:ms-72 flex-grow min-h-screen">
    <?php require __DIR__ . '/includes/breadcrumb.php'; ?>

    <section id="pricing" class="mb-24 section-content reveal">
        <div class="flex items-start gap-4 mb-8">
            <div class="flex-shrink-0 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br <?= e($s['gradient']) ?> text-white text-2xl shadow-lg <?= e($s['shadow']) ?>" aria-hidden="true"><?= e($s['icon']) ?></div>
            <div>
                <div class="pill <?= e($s['pill_bg']) ?> <?= e($s['pill_text']) ?> mb-2"><?= e($s['pill']) ?></div>
                <h2 class="text-3xl sm:text-4xl font-black text-slate-900 m-0 leading-tight">التسعير</h2>
                <p class="text-slate-500 font-medium mt-1">لتحديد هامش الربح</p>
            </div>
        </div>

        <div class="callout callout-info mb-8">
            <div class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0" aria-hidden="true">🎯</span>
                <div>
                    <div class="font-black text-blue-900 mb-1">ملخص</div>
                    <p class="text-slate-700 text-sm leading-relaxed m-0">التسعير يعني تحديد تكلفة الإمداد المدفوعة للمورد، وسعر البيع المحصل من العميل. والفرق بينهما يمثل هامش الربح. معادلة بسيطة وواضحة.</p>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
            <div class="bg-gradient-to-br from-violet-50 to-white p-6 rounded-2xl border border-violet-100 hover-lift">
                <div class="flex items-center gap-3 mb-4">
                    <span class="text-3xl" aria-hidden="true">🛒</span>
                    <div>
                        <h3 class="text-lg font-black text-violet-900">تسعير الإمداد</h3>
                        <p class="text-xs text-violet-700 font-bold">المبلغ المدفوع للمورد</p>
                    </div>
                </div>
                <ul class="space-y-2 text-xs text-slate-700">
                    <li class="flex gap-2 items-start"><span class="text-violet-500" aria-hidden="true">●</span> المورد / مزوّد النقل</li>
                    <li class="flex gap-2 items-start"><span class="text-violet-500" aria-hidden="true">●</span> نوع المركبة: أتوبيس، فان، شاحنة</li>
                    <li class="flex gap-2 items-start"><span class="text-violet-500" aria-hidden="true">●</span> الخط: من نقطة إلى أخرى</li>
                    <li class="flex gap-2 items-start"><span class="text-violet-500" aria-hidden="true">●</span> الوردية: صباحية، مسائية، شهرية</li>
                    <li class="flex gap-2 items-start"><span class="text-violet-500" aria-hidden="true">●</span> الأساس: لكل رحلة، يومي، شهري</li>
                </ul>
            </div>
            <div class="bg-gradient-to-br from-rose-50 to-white p-6 rounded-2xl border border-rose-100 hover-lift">
                <div class="flex items-center gap-3 mb-4">
                    <span class="text-3xl" aria-hidden="true">💵</span>
                    <div>
                        <h3 class="text-lg font-black text-rose-900">تسعير المبيعات</h3>
                        <p class="text-xs text-rose-700 font-bold">المبلغ المحصل من العميل</p>
                    </div>
                </div>
                <ul class="space-y-2 text-xs text-slate-700">
                    <li class="flex gap-2 items-start"><span class="text-rose-500" aria-hidden="true">●</span> العميل / مشروع النقل</li>
                    <li class="flex gap-2 items-start"><span class="text-rose-500" aria-hidden="true">●</span> مستوى الخدمة: فئة المركبة، السعة</li>
                    <li class="flex gap-2 items-start"><span class="text-rose-500" aria-hidden="true">●</span> التكرار: يومي، أسبوعي، شهري</li>
                    <li class="flex gap-2 items-start"><span class="text-rose-500" aria-hidden="true">●</span> أساس الفوترة: لكل رحلة، لكل راكب</li>
                    <li class="flex gap-2 items-start"><span class="text-rose-500" aria-hidden="true">●</span> قواعد الإيراد: الغرامات، الضريبة</li>
                </ul>
            </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 mb-8 shadow-sm">
            <h3 class="text-lg font-black text-slate-900 mb-6 flex items-center gap-2">
                <span class="text-xl" aria-hidden="true">🧮</span> مثال توضيحي بالأرقام
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div class="text-center p-5 bg-gradient-to-br from-rose-50 to-white rounded-2xl border border-rose-100">
                    <div class="text-[11px] font-black text-rose-600 mb-2">سعر البيع للعميل</div>
                    <div class="text-3xl font-black text-rose-700">700 <span class="text-sm">ج.م</span></div>
                    <div class="text-[11px] text-slate-500 mt-1">/ رحلة</div>
                </div>
                <div class="text-center p-5 bg-gradient-to-br from-slate-50 to-white rounded-2xl border border-slate-200 flex flex-col justify-center">
                    <div class="text-2xl font-black text-slate-400" aria-hidden="true">−</div>
                    <div class="text-[11px] text-slate-500 mt-1">ناقص</div>
                </div>
                <div class="text-center p-5 bg-gradient-to-br from-violet-50 to-white rounded-2xl border border-violet-100">
                    <div class="text-[11px] font-black text-violet-600 mb-2">تكلفة الإمداد</div>
                    <div class="text-3xl font-black text-violet-700">500 <span class="text-sm">ج.م</span></div>
                    <div class="text-[11px] text-slate-500 mt-1">/ رحلة</div>
                </div>
            </div>
            <div class="text-center p-6 bg-gradient-to-br from-emerald-50 to-white rounded-2xl border-2 border-emerald-200">
                <div class="text-[11px] font-black text-emerald-600 mb-2">هامش الربح في الرحلة</div>
                <div class="text-5xl font-black text-emerald-600">200 <span class="text-xl">ج.م</span></div>
                <div class="text-xs text-slate-500 mt-2 font-bold">الهامش = 700 − 500</div>
            </div>
            <div class="mt-6 text-center">
                <div class="inline-block px-4 py-2 bg-slate-100 rounded-full text-xs font-bold text-slate-700">
                    💡 نسبة الهامش = 200 ÷ 700 = <span class="text-emerald-600">28.6%</span>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden m-0 hover-lift">
                <div class="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                    <span class="text-lg" aria-hidden="true">🛒</span><span class="font-bold text-slate-800 text-sm">واجهة الإمداد</span>
                </div>
                <img src="<?= $asset ?>/Presentation/3.png" alt="واجهة الإمداد" class="lightbox-trigger w-full h-auto max-h-[400px] object-contain" loading="lazy">
            </figure>
            <figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden m-0 hover-lift">
                <div class="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                    <span class="text-lg" aria-hidden="true">💵</span><span class="font-bold text-slate-800 text-sm">واجهة المبيعات</span>
                </div>
                <img src="<?= $asset ?>/Presentation/4.png" alt="واجهة المبيعات" class="lightbox-trigger w-full h-auto max-h-[400px] object-contain" loading="lazy">
            </figure>
        </div>
    </section>
</main>
<?php require __DIR__ . '/includes/footer.php'; ?>
