<?php
$page_title          = 'تحديثات جماعية';
$page_description    = 'التحديثات الجماعية في نظام كوديفاي — رفع ملف الإكسل دفعة واحدة';
$page_needs_xlsx     = true;
$page_needs_analyzer = true;
require __DIR__ . '/includes/config.php';
require __DIR__ . '/includes/head.php';
require __DIR__ . '/includes/header.php';
require __DIR__ . '/includes/sidebar.php';
$asset = $SITE['assets'];
$s     = $SECTIONS['bulk-import'];
?>
<main id="main-content" class="px-4 pt-6 pb-24 sm:px-6 lg:px-8 lg:ms-72 flex-grow min-h-screen">
    <?php require __DIR__ . '/includes/breadcrumb.php'; ?>

    <section id="bulk-import" class="mb-24 section-content reveal">
        <div class="flex items-start gap-4 mb-8">
            <div class="flex-shrink-0 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br <?= e($s['gradient']) ?> text-white text-2xl shadow-lg <?= e($s['shadow']) ?>" aria-hidden="true"><?= $s['icon'] ?></div>
            <div>
                <div class="pill <?= e($s['pill_bg']) ?> <?= e($s['pill_text']) ?> mb-2"><?= e($s['pill']) ?></div>
                <h2 class="text-3xl sm:text-4xl font-black text-slate-900 m-0 leading-tight"><?= e($s['title']) ?></h2>
                <p class="text-slate-500 font-medium mt-1">التحميل المجمع لمشاريع النقل - توفير الوقت</p>
            </div>
        </div>

        <div class="callout callout-info mb-8">
            <div class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0" aria-hidden="true">🎯</span>
                <div>
                    <div class="font-black text-blue-900 mb-1">ملخص</div>
                    <p class="text-slate-700 text-sm leading-relaxed m-0">بدلاً من إدخال البيانات يدوياً بشكل منفصل، يمكنك إعداد ملف إكسل واحد يحتوي على جميع البيانات ورفعه دفعة واحدة. عملية تُنجز في ثوانٍ.</p>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-2 mb-6 shadow-sm">
            <div class="grid grid-cols-4 gap-2">
                <button type="button" class="tab-btn active rounded-xl py-3 px-3 text-sm font-bold transition-all" data-tab="validation"><span class="block text-lg mb-1" aria-hidden="true">🔍</span> التحقق</button>
                <button type="button" class="tab-btn rounded-xl py-3 px-3 text-sm font-bold transition-all" data-tab="routes"><span class="block text-lg mb-1" aria-hidden="true">🛣️</span> المسارات</button>
                <button type="button" class="tab-btn rounded-xl py-3 px-3 text-sm font-bold text-slate-600 hover:bg-slate-50 transition-all" data-tab="schedules"><span class="block text-lg mb-1" aria-hidden="true">📅</span> الجداول</button>
                <button type="button" class="tab-btn rounded-xl py-3 px-3 text-sm font-bold text-slate-600 hover:bg-slate-50 transition-all" data-tab="trips"><span class="block text-lg mb-1" aria-hidden="true">🚐</span> الرحلات</button>
            </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 mb-8 shadow-sm">
            <!-- Validation tab -->
            <div class="tab-content fade-in" data-content="validation">
                <div class="flex items-center gap-3 mb-4">
                    <span class="text-3xl" aria-hidden="true">🔍</span>
                    <div>
                        <h3 class="font-black text-slate-900 text-lg">التحقق من جودة البيانات</h3>
                        <p class="text-sm text-slate-500">افحص ملف الإكسل قبل الرفع للتأكد من جاهزيته</p>
                    </div>
                </div>
                <ul class="space-y-3 text-sm">
                    <li class="flex gap-3 items-start"><span class="check-dot bg-indigo-100 text-indigo-600">✓</span><span class="text-slate-700"><strong>التحقق من تنسيق الأرقام</strong> — التأكد من أرقام الهواتف المصرية</span></li>
                    <li class="flex gap-3 items-start"><span class="check-dot bg-indigo-100 text-indigo-600">✓</span><span class="text-slate-700"><strong>التحقق من التنسيقات التاريخية</strong> — تحويل التواريخ إلى الشكل الصحيح</span></li>
                    <li class="flex gap-3 items-start"><span class="check-dot bg-indigo-100 text-indigo-600">✓</span><span class="text-slate-700"><strong>تحليل الورديات</strong> — التحقق من تعارضات الورديات</span></li>
                    <li class="flex gap-3 items-start"><span class="check-dot bg-indigo-100 text-indigo-600">✓</span><span class="text-slate-700"><strong>إدارة الموردين</strong> — التحقق من معلومات الموردين</span></li>
                </ul>

                <div class="mt-4 flex items-center gap-3">
                    <a href="analysis-config.php" class="inline-flex items-center gap-2 px-4 py-2 bg-cyan-600 text-white font-bold rounded-xl hover:bg-cyan-700 transition-colors shadow-lg shadow-cyan-600/20">
                        <span class="text-lg" aria-hidden="true">⚙️</span><span>إعدادات التحليل المتقدمة</span>
                    </a>
                    <span class="text-xs text-slate-400">تخصيص القواعد وحفظ ملفات التعريف</span>
                </div>

                <div id="validation-container" class="mt-6">
                    <div class="upload-section" id="dropZone" style="text-align:center;padding:40px;border:2px dashed #ccc;border-radius:8px;margin-bottom:20px;transition:border-color 0.3s;">
                        <h4 style="margin-bottom:15px;">📁 رفع ملف الإكسل للتحليل</h4>
                        <p style="margin-bottom:20px;">اسحب الملف هنا أو انقر لاختياره</p>
                        <input type="file" id="fileInput" accept=".xlsx,.xls" style="display:none;">
                        <button type="button" class="upload-btn" onclick="document.getElementById('fileInput').click()" style="background:#4f46e5;color:white;padding:12px 24px;border:none;border-radius:4px;cursor:pointer;font-size:16px;margin:10px;">اختر ملف</button>
                    </div>

                    <div id="fileInfo" class="file-info" style="display:none;margin:15px 0;padding:10px;background:#f8f9fa;border-radius:4px;"></div>

                    <div class="progress-bar" id="progressBar" style="display:none;width:100%;height:20px;background-color:#e9ecef;border-radius:10px;overflow:hidden;margin:20px 0;">
                        <div class="progress-fill" id="progressFill" style="height:100%;background-color:#28a745;width:0%;transition:width 0.3s;"></div>
                    </div>

                    <div class="analysis-results" id="analysisResults" style="display:none;margin-top:20px;">
                        <h4 style="margin-bottom:15px;">📈 نتائج التحليل</h4>
                        <div class="summary-card" id="summaryCard" style="display:flex;justify-content:space-around;flex-wrap:wrap;gap:15px;margin:20px 0;"></div>
                        <div class="action-buttons" style="text-align:center;margin:20px 0;">
                            <button type="button" class="btn btn-primary" id="downloadCleanBtn" disabled style="padding:10px 20px;margin:0 10px;border:none;border-radius:4px;cursor:pointer;font-size:16px;background:#007bff;color:white;">📥 تحميل الملف بعد التنظيف</button>
                            <button type="button" class="btn btn-success" id="proceedImportBtn" disabled style="padding:10px 20px;margin:0 10px;border:none;border-radius:4px;cursor:pointer;font-size:16px;background:#28a745;color:white;">✅ الاستمرار في الرفع</button>
                            <button type="button" class="btn btn-secondary" id="resetBtn" style="padding:10px 20px;margin:0 10px;border:none;border-radius:4px;cursor:pointer;font-size:16px;background:#6c757d;color:white;">🔄 إعادة</button>
                        </div>
                        <h5 style="margin:20px 0 10px;">⚠️ المشاكل المكتشفة</h5>
                        <div style="overflow-x:auto;">
                            <table class="issues-table" id="issuesTable" style="width:100%;border-collapse:collapse;margin:10px 0;">
                                <thead>
                                    <tr style="background-color:#f8f9fa;">
                                        <th style="border:1px solid #ddd;padding:12px;text-align:left;">الشدة</th>
                                        <th style="border:1px solid #ddd;padding:12px;text-align:left;">النوع</th>
                                        <th style="border:1px solid #ddd;padding:12px;text-align:left;">الورقة</th>
                                        <th style="border:1px solid #ddd;padding:12px;text-align:left;">الصف</th>
                                        <th style="border:1px solid #ddd;padding:12px;text-align:left;">العمود</th>
                                        <th style="border:1px solid #ddd;padding:12px;text-align:left;">الوصف</th>
                                    </tr>
                                </thead>
                                <tbody id="issuesTableBody"></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Routes tab -->
            <div class="tab-content hidden fade-in" data-content="routes">
                <div class="flex items-center gap-3 mb-4">
                    <span class="text-3xl" aria-hidden="true">🛣️</span>
                    <div>
                        <h3 class="font-black text-slate-900 text-lg">رفع المسارات</h3>
                        <p class="text-sm text-slate-500">خطوط السير — من نقطة الانطلاق إلى نقطة الوصول</p>
                    </div>
                </div>
                <ul class="space-y-3 text-sm">
                    <li class="flex gap-3 items-start"><span class="check-dot bg-indigo-100 text-indigo-600">✓</span><span class="text-slate-700"><strong>ربط المسار بالمشروع</strong> — تحديد المشروع التابع له المسار</span></li>
                    <li class="flex gap-3 items-start"><span class="check-dot bg-indigo-100 text-indigo-600">✓</span><span class="text-slate-700"><strong>اسم الخط</strong> — مثل "خط المعادي - وسط البلد"</span></li>
                    <li class="flex gap-3 items-start"><span class="check-dot bg-indigo-100 text-indigo-600">✓</span><span class="text-slate-700"><strong>نقطة البداية والنهاية</strong> — تحديد موقع الانطلاق والوصول</span></li>
                    <li class="flex gap-3 items-start"><span class="check-dot bg-indigo-100 text-indigo-600">✓</span><span class="text-slate-700"><strong>الحالة</strong> — نشط أو متوقف</span></li>
                </ul>
            </div>

            <!-- Schedules tab -->
            <div class="tab-content hidden fade-in" data-content="schedules">
                <div class="flex items-center gap-3 mb-4">
                    <span class="text-3xl" aria-hidden="true">📅</span>
                    <div>
                        <h3 class="font-black text-slate-900 text-lg">رفع الجداول</h3>
                        <p class="text-sm text-slate-500">أوقات التشغيل — تحديد مواعيد انطلاق المركبات</p>
                    </div>
                </div>
                <ul class="space-y-3 text-sm">
                    <li class="flex gap-3 items-start"><span class="check-dot bg-purple-100 text-purple-600">✓</span><span class="text-slate-700"><strong>ربط الجدول بالمسار</strong> — تحديد الخط التابع له الجدول</span></li>
                    <li class="flex gap-3 items-start"><span class="check-dot bg-purple-100 text-purple-600">✓</span><span class="text-slate-700"><strong>أيام التشغيل</strong> — أيام محددة أم يومياً؟</span></li>
                    <li class="flex gap-3 items-start"><span class="check-dot bg-purple-100 text-purple-600">✓</span><span class="text-slate-700"><strong>وقت البداية والنهاية</strong> — من ساعة كذا إلى ساعة كذا</span></li>
                    <li class="flex gap-3 items-start"><span class="check-dot bg-purple-100 text-purple-600">✓</span><span class="text-slate-700"><strong>فترة الصلاحية</strong> — من تاريخ إلى تاريخ</span></li>
                </ul>
            </div>

            <!-- Trips tab -->
            <div class="tab-content hidden fade-in" data-content="trips">
                <div class="flex items-center gap-3 mb-4">
                    <span class="text-3xl" aria-hidden="true">🚐</span>
                    <div>
                        <h3 class="font-black text-slate-900 text-lg">رفع الرحلات</h3>
                        <p class="text-sm text-slate-500">السجلات التنفيذية — الرحلات الفعلية المنفذة</p>
                    </div>
                </div>
                <ul class="space-y-3 text-sm">
                    <li class="flex gap-3 items-start"><span class="check-dot bg-pink-100 text-pink-600">✓</span><span class="text-slate-700"><strong>وقت الرحلة</strong> — ساعة الانطلاق</span></li>
                    <li class="flex gap-3 items-start"><span class="check-dot bg-pink-100 text-pink-600">✓</span><span class="text-slate-700"><strong>ربط الرحلة بالجدول</strong> — الجدول التابعة له الرحلة</span></li>
                    <li class="flex gap-3 items-start"><span class="check-dot bg-pink-100 text-pink-600">✓</span><span class="text-slate-700"><strong>السائق والمركبة</strong> — تحديد السائق والمركبة المستخدمة</span></li>
                    <li class="flex gap-3 items-start"><span class="check-dot bg-pink-100 text-pink-600">✓</span><span class="text-slate-700"><strong>الحالة</strong> — مكتملة، ملغاة، أو متأخرة</span></li>
                </ul>
            </div>
        </div>

        <div class="callout callout-example mb-8">
            <div class="flex items-start gap-3 mb-4">
                <span class="text-2xl flex-shrink-0" aria-hidden="true">🎯</span>
                <div>
                    <h2 class="font-black text-blue-900">التحميل المجمع للجداول <span class="font-black text-blue-500">- اتبع الترتيب الصحيح للعمل</span></h2>
                    <p class="text-blue-400 text-xs mt-1">الترتيب الصحيح يضمن سير العمل بسلاسة. فكما في البناء، الأساس يأتي أولاً.</p>
                </div>
            </div>
            <ol class="space-y-2 text-sm text-slate-700">
                <li class="flex gap-3 items-start"><span class="num-dot bg-green-600 text-white">1</span><span>ارفع <strong>المسارات</strong> أولاً — الخطوط</span></li>
                <li class="flex gap-3 items-start"><span class="num-dot bg-green-600 text-white">2</span><span>ثم ارفع <strong>الجداول</strong> المرتبطة بهذه الخطوط</span></li>
                <li class="flex gap-3 items-start"><span class="num-dot bg-green-600 text-white">3</span><span><strong>راجع الأخطاء</strong> إن وُجدت</span></li>
                <li class="flex gap-3 items-start"><span class="num-dot bg-green-600 text-white">4</span><span>أنشئ <strong>الرحلات</strong> وعيّن السائقين والمركبات</span></li>
                <li class="flex gap-3 items-start"><span class="num-dot bg-green-600 text-white">5</span><span><strong>راجع الرحلات</strong> قبل تشغيلها فعلياً</span></li>
            </ol>
        </div>

        <figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden m-0 hover-lift">
            <div class="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                <span class="text-lg" aria-hidden="true">🖼️</span>
                <span class="font-bold text-slate-800 text-sm">شكل عملية الرفع</span>
            </div>
            <img src="<?= $asset ?>/img/BulkAll.png" alt="عملية رفع المشاريع" class="lightbox-trigger w-full h-auto max-h-[400px] object-contain" loading="lazy">
            <figcaption class="p-4 bg-slate-50/50 text-sm text-slate-600 border-t border-slate-100">توضح الصورة كيفية رفع ملف CSV يحتوي على جميع البيانات دفعة واحدة.</figcaption>
        </figure>

        <?php require __DIR__ . '/includes/section-pager.php'; ?>
    </section>
</main>
<?php require __DIR__ . '/includes/footer.php'; ?>