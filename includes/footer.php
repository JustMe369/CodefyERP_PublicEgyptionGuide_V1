<?php $asset = $SITE['assets']; ?>
</div><!-- /.flex -->

<button id="float-help" type="button" aria-label="مساعدة"
    class="fixed bottom-6 start-6 z-40 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-primary-700 text-white shadow-xl shadow-primary-600/40 hover:scale-110 transition-transform">
    <span class="text-xl" aria-hidden="true">💬</span>
</button>

<button id="back-to-top" type="button" aria-label="العودة إلى الأعلى"
    class="fixed bottom-6 end-6 z-40 flex h-11 w-11 items-center justify-center rounded-full bg-primary-600 text-white shadow-lg shadow-primary-600/30 opacity-0 translate-y-3 pointer-events-none transition-all duration-300 hover:bg-primary-700 focus:outline-none">
    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true" focusable="false">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
    </svg>
</button>

<div id="lightbox" role="dialog" aria-modal="true" aria-label="عرض الصورة بالحجم الكامل"
    class="fixed inset-0 z-[100] hidden items-center justify-center bg-black/95 backdrop-blur-md opacity-0 transition-all duration-300 ease-out">
    <button id="lightbox-close" type="button" aria-label="إغلاق"
        class="absolute top-6 start-6 text-white/80 hover:text-white focus:outline-none p-2 bg-white/10 hover:bg-white/20 rounded-full transition-all duration-200 backdrop-blur-sm">
        <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true" focusable="false">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
        </svg>
    </button>
    <div class="w-full h-full flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <img id="lightbox-img" src="" alt="عرض مكبر"
            class="max-w-[85vw] max-h-[85vh] w-auto h-auto rounded-2xl shadow-2xl object-contain transform scale-95 transition-transform duration-300 ease-out ring-1 ring-white/10">
    </div>
</div>

<?php if (!empty($page_needs_mermaid)): ?>
<script>
(function () {
    'use strict';
    function initMermaid() {
        if (!window.mermaid) return;
        try {
            if (typeof window.mermaid.run === 'function') window.mermaid.run({ querySelector: '.mermaid' });
            else if (typeof window.mermaid.contentLoaded === 'function') window.mermaid.contentLoaded();
        } catch (e) {}
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initMermaid);
    else initMermaid();
})();
</script>
<?php endif; ?>

<style>
    .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;}
    .focus\:not-sr-only:focus{position:static;width:auto;height:auto;padding:0;margin:0;overflow:visible;clip:auto;white-space:normal;}
    .severity-critical{color:#dc3545;font-weight:bold;}
    .severity-warning{color:#856404;}
    .severity-info{color:#17a2b8;}
    .summary-item{flex:1;min-width:120px;text-align:center;padding:15px;margin:5px;border-radius:8px;}
    .summary-item.critical{background-color:#ffeef0;border-left:4px solid #dc3545;}
    .summary-item.warning{background-color:#fff3cd;border-left:4px solid #ffc107;}
    .summary-item.info{background-color:#d1ecf1;border-left:4px solid #17a2b8;}
    .upload-btn{background:#4f46e5;color:white;padding:12px 24px;border:none;border-radius:4px;cursor:pointer;font-size:16px;margin:10px;}
    .upload-btn:hover{background:#4338ca;}
</style>

<script src="<?= $asset ?>/JS/navbar.js"></script>
<script src="<?= $asset ?>/JS/footer.js"></script>
<?php if (!empty($page_needs_analyzer)): ?>
<script src="<?= $asset ?>/JS/analyzer_import_sheets.js"></script>
<?php endif; ?>
<script src="<?= $asset ?>/JS/scripts.js?v=20260925-2"></script>
<script src="<?= $asset ?>/JS/mobile.js"></script>
</body>
</html>