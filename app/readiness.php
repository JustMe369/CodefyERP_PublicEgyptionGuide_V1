<?php
$page_title       = 'مراجعة الجاهزية';
$page_description = 'مراجعة الجاهزية قبل الانطلاق في نظام كوديفاي';
require __DIR__ . '/includes/config.php';
require __DIR__ . '/includes/head.php';
require __DIR__ . '/includes/header.php';
require __DIR__ . '/includes/sidebar.php';
$asset = $SITE['assets'];
$s     = $SECTIONS['readiness'];
$checks = [
    ['حالة المشروع', 'هل المشروع نشط ومعتمد (Active/Approved)؟'],
    ['تواريخ العقد', 'هل تاريخ الخدمة ضمن فترة صلاحية العقد؟'],
    ['المسارات', 'هل تم إنشاء الخطوط وهي نشطة؟'],
    ['الجداول', 'هل تم إنشاء الجداول لأيام وأوقات التشغيل؟'],
    ['التعيينات', 'هل تم تعيين الجداول فعلاً لمورد أو مركبة أو سائق؟'],
    ['التسعير', 'هل أسعار الإمداد والمبيعات مضبوطة؟'],
    ['السعة', 'هل المركبات مناسبة لعدد الركاب ومتطلبات الخط؟'],
    ['الاستثناءات', 'هل تم التعامل مع الأعياد والإجازات والتواريخ المحظورة؟'],
];
?>
<main id="main-content" class="px-4 pt-6 pb-24 sm:px-6 lg:px-8 lg:ms-72 flex-grow min-h-screen">
    <?php require __DIR__ . '/includes/breadcrumb.php'; ?>

    <section id="readiness" class="mb-24 section-content reveal">
        <div class="flex items-start gap-4 mb-8">
            <div class="flex-shrink-0 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br <?= e($s['gradient']) ?> text-white text-2xl shadow-lg <?= e($s['shadow']) ?>" aria-hidden="true"><?= $s['icon'] ?></div>
            <div>
                <div class="pill <?= e($s['pill_bg']) ?> <?= e($s['pill_text']) ?> mb-2"><?= e($s['pill']) ?></div>
                <h2 class="text-3xl sm:text-4xl font-black text-slate-900 m-0 leading-tight"><?= e($s['title']) ?></h2>
                <p class="text-slate-500 font-medium mt-1">قبل الانطلاق — تأكد من اكتمال جميع المتطلبات</p>
            </div>
        </div>

        <div class="callout callout-info mb-8">
            <div class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0" aria-hidden="true">🎯</span>
                <div>
                    <div class="font-black text-blue-900 mb-1">ملخص</div>
                    <p class="text-slate-700 text-sm leading-relaxed m-0">كما تراجع وقود سيارتك وزيتها وإطاراتها قبل الانطلاق على الطريق، يجب التأكد من جاهزية المشروع وعدم وجود أي نقص قبل التشغيل. مجموعة من النقاط البسيطة للمراجعة.</p>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 mb-8 shadow-sm">
            <h3 class="text-lg font-black text-slate-900 mb-6 flex items-center gap-2">
                <span class="text-xl" aria-hidden="true">📋</span> قائمة مراجعة الجاهزية
            </h3>
            <div class="space-y-3">
                <?php foreach ($checks as [$title, $desc]): ?>
                    <div class="checklist-item">
                        <div class="checklist-box"><span>✓</span></div>
                        <div class="flex-1">
                            <div class="font-bold text-slate-900 text-sm"><?= e($title) ?></div>
                            <p class="text-xs text-slate-500 mt-1"><?= e($desc) ?></p>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <div class="callout callout-tip">
                <div class="flex items-start gap-3">
                    <span class="text-xl flex-shrink-0" aria-hidden="true">💡</span>
                    <div>
                        <div class="font-black text-amber-900 text-sm mb-1">نصيحة سريعة</div>
                        <p class="text-amber-800 text-xs leading-relaxed m-0">قم بمراجعة الجاهزية قبل التشغيل بيوم كامل — لإتاحة الوقت الكافي لمعالجة أي نقص.</p>
                    </div>
                </div>
            </div>
            <div class="callout callout-warn">
                <div class="flex items-start gap-3">
                    <span class="text-xl flex-shrink-0" aria-hidden="true">⚠️</span>
                    <div>
                        <div class="font-black text-red-900 text-sm mb-1">لا تتسرع!</div>
                        <p class="text-red-800 text-xs leading-relaxed m-0">كون المشروع قائماً لا يعني أنه جاهز. يجب التحقق من جميع البنود المذكورة قبل اعتباره جاهزاً للتشغيل.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden m-0 hover-lift">
                <div class="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                    <span class="text-lg" aria-hidden="true">🖼️</span><span class="font-bold text-slate-800 text-sm">واجهة الجاهزية</span>
                </div>
                <img src="<?= $asset ?>/Presentation/5.png" alt="واجهة الجاهزية" class="lightbox-trigger w-full h-auto max-h-[400px] object-contain" loading="lazy">
            </figure>
            <figure class="bg-white rounded-2xl border border-slate-200 overflow-hidden m-0 hover-lift">
                <div class="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
                    <span class="text-lg" aria-hidden="true">🔗</span><span class="font-bold text-slate-800 text-sm">العلاقة مع المسارات</span>
                </div>
                <img src="<?= $asset ?>/Presentation/6.png" alt="العلاقة مع المسارات" class="lightbox-trigger w-full h-auto max-h-[400px] object-contain" loading="lazy">
            </figure>
        </div>
    </section>
</main>
<?php require __DIR__ . '/includes/footer.php'; ?>