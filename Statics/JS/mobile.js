(function() {
    "use strict";
    let isMobile = false;
    let sidebarOpen = false;

    function checkMobile() {
        isMobile = window.innerWidth < 1024;
        return isMobile;
    }

    /* Viewport height fix for mobile address bar issue */
    function fixMobileViewport() {
        if (!checkMobile()) return;
        const setVh = function() {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty("--vh", (vh * 100) + "px");
        };
        setVh();
        window.addEventListener("resize", setVh);
        window.addEventListener("orientationchange", function() {
            setTimeout(setVh, 100);
        });
    }

    function getElement(id) {
        return document.getElementById(id);
    }

    /* Track sidebar state via custom events from inline script */
    function trackSidebarState() {
        const sidebar = getElement("sidebar");
        if (!sidebar) return;

        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.attributeName === "class") {
                    const isOpen = !sidebar.classList.contains("translate-x-full") &&
                                   sidebar.classList.contains("translate-x-0");
                    if (isOpen !== sidebarOpen) {
                        sidebarOpen = isOpen;
                        if (sidebarOpen) {
                            document.body.style.overflow = "hidden";
                        } else {
                            document.body.style.overflow = "";
                        }
                    }
                }
            });
        });

        observer.observe(sidebar, { attributes: true, attributeFilter: ["class"] });
    }

    /* Touch swipe gestures for sidebar (complementary enhancement) */
    function initTouchGestures() {
        if (!checkMobile()) return;

        const mainContent = getElement("main-content");
        if (!mainContent) return;

        let touchStartX = 0, touchStartY = 0, touchEndX = 0, touchEndY = 0;

        mainContent.addEventListener("touchstart", function(e) {
            if (e.touches.length === 1) {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
            }
        }, { passive: true });

        mainContent.addEventListener("touchend", function(e) {
            if (typeof touchStartX === "number" && typeof touchEndX === "number") {
                touchEndX = e.changedTouches[0].clientX;
                touchEndY = e.changedTouches[0].clientY;

                const diffX = touchEndX - touchStartX;
                const diffY = touchEndY - touchStartY;

                /* Swipe from right edge to open sidebar */
                if (touchStartX < 30 && Math.abs(diffX) > 50 && Math.abs(diffY) < 50 && diffX > 0) {
                    const sidebar = getElement("sidebar");
                    if (sidebar && sidebar.classList.contains("translate-x-full")) {
                        const event = new CustomEvent("sidebar:toggle");
                        window.dispatchEvent(event);
                    }
                }

                /* Swipe to close sidebar */
                if (!sidebarOpen && Math.abs(diffX) > 100 && Math.abs(diffY) < 80) {
                    const event = new CustomEvent("sidebar:toggle");
                    window.dispatchEvent(event);
                }

                touchStartX = 0; touchStartY = 0; touchEndX = 0; touchEndY = 0;
            }
        }, { passive: true });
    }

    /* Enhanced theme toggle animation on mobile */
    function handleThemeToggleAnimation() {
        const themeToggleBtn = getElement("theme-toggle");
        if (!themeToggleBtn) return;

        themeToggleBtn.addEventListener("click", function() {
            this.style.transform = "rotate(360deg)";
            this.style.transition = "transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)";
            setTimeout(function() {
                themeToggleBtn.style.transform = "rotate(0deg)";
            }, 600);
        });
    }

    /* Handle hash changes to close sidebar */
    function initHashChange() {
        window.addEventListener("hashchange", function() {
            if (sidebarOpen) {
                const event = new CustomEvent("sidebar:close");
                window.dispatchEvent(event);
            }
        });
    }

    /* Initialize all mobile enhancements */
    function initMobileEnhancements() {
        fixMobileViewport();
        trackSidebarState();
        initTouchGestures();
        handleThemeToggleAnimation();
        initHashChange();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initMobileEnhancements);
    } else {
        initMobileEnhancements();
    }

    /* Public API for external use */
    window.CodefyMobile = {
        isMobile: checkMobile,
        isSidebarOpen: function() { return sidebarOpen; }
    };
})();
