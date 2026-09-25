<?php
$page_title       = 'إعدادات تحليل الإكسل';
$page_description = 'تخصيص قواعد التحقق والمعالجة التلقائية لملفات الإكسل في نظام كوديفاي';
require __DIR__ . '/includes/config.php';
require __DIR__ . '/includes/head.php';
require __DIR__ . '/includes/header.php';
require __DIR__ . '/includes/sidebar.php';
$s = $SECTIONS['analysis-config'];
?>
<main id="main-content" class="px-4 pt-6 pb-24 sm:px-6 lg:px-8 lg:ms-72 flex-grow min-h-screen">
    <?php require __DIR__ . '/includes/breadcrumb.php'; ?>

    <section id="analysis-config" class="mb-24 section-content reveal">
        <div class="flex items-start gap-4 mb-8">
            <div class="flex-shrink-0 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br <?= e($s['gradient']) ?> text-white text-2xl shadow-lg <?= e($s['shadow']) ?>" aria-hidden="true"><?= $s['icon'] ?></div>
            <div>
                <div class="pill <?= e($s['pill_bg']) ?> <?= e($s['pill_text']) ?> mb-2"><?= e($s['pill']) ?></div>
                <h2 class="text-3xl sm:text-4xl font-black text-slate-900 m-0 leading-tight"><?= e($s['title']) ?></h2>
                <p class="text-slate-500 font-medium mt-1">تخصيص قواعد التحقق والمعالجة التلقائية</p>
            </div>
        </div>

        <div class="callout callout-info mb-8">
            <div class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0" aria-hidden="true">🎯</span>
                <div>
                    <div class="font-black text-blue-900 mb-1">ملخص</div>
                    <p class="text-slate-700 text-sm leading-relaxed m-0">هنا يمكنك تخصيص كيفية تحليل ملفات الإكسل: تفعيل/تعطيل محركات التحقق، إعداد قواعد تنسيق التواريخ والأرقام، وحفظ ملفات تعريف مكررة لسيناريوهات مختلفة.</p>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 mb-8 shadow-sm">
            <h3 class="text-lg font-black text-slate-900 mb-6 flex items-center gap-2">
                <span class="text-xl" aria-hidden="true">⚡</span> الإعدادات السريعة
            </h3>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                <label class="flex items-center gap-2 cursor-pointer p-4 rounded-xl bg-slate-50 border border-slate-200 hover:border-primary-300 transition-colors">
                    <input type="checkbox" id="cfg-shift-engine" checked class="w-4 h-4 text-primary-600 rounded">
                    <span class="text-sm font-medium text-slate-700">محرك الورديات</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer p-4 rounded-xl bg-slate-50 border border-slate-200 hover:border-primary-300 transition-colors">
                    <input type="checkbox" id="cfg-time-conflict" checked class="w-4 h-4 text-primary-600 rounded">
                    <span class="text-sm font-medium text-slate-700">تعارضات الوقت</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer p-4 rounded-xl bg-slate-50 border border-slate-200 hover:border-primary-300 transition-colors">
                    <input type="checkbox" id="cfg-time-normalize" checked class="w-4 h-4 text-primary-600 rounded">
                    <span class="text-sm font-medium text-slate-700">تطبيع الوقت</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer p-4 rounded-xl bg-slate-50 border border-slate-200 hover:border-primary-300 transition-colors">
                    <input type="checkbox" id="cfg-12h-format" checked class="w-4 h-4 text-primary-600 rounded">
                    <span class="text-sm font-medium text-slate-700">تنسيق 12 ساعة</span>
                </label>
                <div class="flex flex-col gap-1.5 cursor-pointer p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <label class="text-xs font-bold text-slate-500" for="cfg-offset">تعويض الوقت:</label>
                    <select id="cfg-offset" class="text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500">
                        <option value="15">15 دقيقة</option>
                        <option value="30" selected>30 دقيقة</option>
                        <option value="45">45 دقيقة</option>
                        <option value="60">60 دقيقة</option>
                    </select>
                </div>
                <div class="flex flex-col gap-1.5 cursor-pointer p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <label class="text-xs font-bold text-slate-500" for="cfg-target">الهدف:</label>
                    <select id="cfg-target" class="text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500">
                        <option value="dropoff_arrival_time" selected>وصول</option>
                        <option value="dropoff_departure_time">مغادرة</option>
                    </select>
                </div>
            </div>
            <div class="flex flex-wrap gap-3 pt-4 border-t border-slate-200">
                <button type="button" id="cfg-save-profile" class="px-4 py-2 bg-primary-600 text-white font-bold rounded-xl hover:bg-primary-700 transition-colors">💾 حفظ كملف تعريف</button>
                <button type="button" id="cfg-reset" class="px-4 py-2 bg-slate-100 text-slate-700 font-bold rounded-xl hover:bg-slate-200 transition-colors">↩️ إعادة للتعيين الافتراضي</button>
            </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 mb-8 shadow-sm">
            <h3 class="text-lg font-black text-slate-900 mb-6 flex items-center gap-2">
                <span class="text-xl" aria-hidden="true">📋</span> ملفات التعريف المحفوظة
            </h3>
            <div id="cfg-profiles-list" class="space-y-3 min-h-[100px]">
                <div class="text-center text-slate-500 py-8" id="cfg-empty-profiles">
                    <div class="text-4xl mb-2">📭</div>
                    <p>لا توجد ملفات تعريف محفوظة بعد</p>
                    <p class="text-xs mt-1">اضبط الإعدادات واضغط "حفظ كملف تعريف"</p>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
            <h3 class="text-lg font-black text-slate-900 mb-6 flex items-center gap-2">
                <span class="text-xl" aria-hidden="true">🔄</span> استيراد / تصدير الإعدادات
            </h3>
            <div class="flex flex-wrap gap-3">
                <button type="button" id="cfg-export" class="px-4 py-2 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors">📤 تصدير (JSON)</button>
                <input type="file" id="cfg-import-file" accept=".json" class="hidden">
                <button type="button" id="cfg-import" class="px-4 py-2 bg-violet-600 text-white font-bold rounded-xl hover:bg-violet-700 transition-colors" onclick="document.getElementById('cfg-import-file').click()">📥 استيراد</button>
            </div>
            <p class="text-xs text-slate-500 mt-3">شارك إعداداتك مع الزملاء أو انقلها بين الأجهزة</p>
        </div>

        <?php require __DIR__ . '/includes/section-pager.php'; ?>
    </section>
</main>
<?php require __DIR__ . '/includes/footer.php'; ?>