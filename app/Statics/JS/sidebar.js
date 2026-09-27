/**
 * CodefyERP — Sidebar State Controller (shadcn/ui SidebarProvider equivalent)
 *
 * Manages the single source of truth for sidebar state across desktop (icon
 * collapse) and mobile (off-canvas overlay).  Exposes window.CodefySidebar.
 *
 * shadcn mapping:
 *   <SidebarProvider>      ->  CodefySidebar singleton
 *   <Sidebar side collapsible> ->  <aside data-sidebar="sidebar" data-state="...">
 *   SidebarTrigger          ->  [data-sidebar="trigger"][data-sidebar-action="toggle"]
 *   SidebarRail             ->  [data-sidebar="rail"]
 *   useSidebar()            ->  window.CodefySidebar API
 */
(function () {
    'use strict';

    /* ------------------------------------------------------------------ */
    /* Configuration & constants                                          */
    /* ------------------------------------------------------------------ */
    var BREAKPOINT = 1024;                       /* lg — matches Tailwind + existing @media */
    var STORAGE_COLLAPSED = 'sidebar-collapsed'; /* backward-compat localStorage key */
    var STORAGE_MOBILE = 'sidebar-open-mobile';  /* new — mobile overlay state */

    /* ------------------------------------------------------------------ */
    /* Internal helpers                                                   */
    /* ------------------------------------------------------------------ */
    function $(id) { return document.getElementById(id); }

    /* ------------------------------------------------------------------ */
    /* The controller                                                     */
    /* ------------------------------------------------------------------ */
    var CodefySidebar = {
        /* — config (read from <aside> data-* on init)                    */
        variant: 'sidebar',
        side: 'right',
        collapsible: 'icon',

        /* — reactive state                                                */
        state: 'expanded',      /* 'expanded' | 'collapsed'  (desktop icon mode) */
        open: true,             /* desktop panel always rendered in default mode */
        openMobile: false,      /* mobile off-canvas overlay */
        _isMobile: false,

        /* — cached elements                                               */
        sidebar: null,
        overlay: null,
        trigger: null,          /* #mobile-menu-btn */
        collapseBtn: null,      /* #sidebar-collapse-toggle */
        rail: null,             /* #sidebar-rail */
        _boundResize: null,
        _boundKeydown: null,
        _boundToggle: null,
        _boundClose: null,
        _initialized: false,

        /* ---------------------------------------------------------------- */
        /* Public API                                                      */
        /* ---------------------------------------------------------------- */
        init: function (sidebarEl) {
            if (this._initialized) return;
            this.sidebar = sidebarEl || $('sidebar');
            if (!this.sidebar) return;

            /* read shadcn contract from the aside itself */
            this.variant     = this.sidebar.getAttribute('data-variant')     || 'sidebar';
            this.side         = this.sidebar.getAttribute('data-side')        || 'right';
            this.collapsible = this.sidebar.getAttribute('data-collapsible') || 'icon';

            /* cache companion elements */
            this.overlay      = $('sidebar-overlay');
            this.trigger      = $('mobile-menu-btn');
            this.collapseBtn  = $('sidebar-collapse-toggle');
            this.rail         = $('sidebar-rail');

            this._isMobile = this._computeIsMobile();

            /* restore persisted state */
            this._restoreState();

            /* apply to DOM */
            this._applyState();

            /* sync active nav link (server-rendered data-sidebar-active) */
            this._syncActiveState();

            /* bind event listeners */
            this._bindEvents();

            this._initialized = true;
            window.dispatchEvent(new CustomEvent('codefy:sidebar:ready'));
        },

        get isMobile() {
            return this._computeIsMobile();
        },

        getState: function () {
            return this.state;
        },

        setOpen: function (v) {
            this.open = !!v;
            this.openMobile = !!v;
            this._persistMobile();
            this._applyState();
        },

        setOpenMobile: function (v) {
            if (typeof v !== 'boolean') v = !this.openMobile;
            this.openMobile = !!v;
            this._persistMobile();
            this._applyState();
        },

        toggleSidebar: function () {
            if (this._computeIsMobile()) {
                this.toggleMobile();
            } else {
                this.state = (this.state === 'expanded') ? 'collapsed' : 'expanded';
                this._persist();
                this._applyState();
            }
        },

        toggleMobile: function (v) {
            if (typeof v === 'boolean') {
                this.openMobile = v;
            } else {
                this.openMobile = !this.openMobile;
            }
            this._persistMobile();
            this._applyState();
        },

        closeMobile: function () {
            if (this.openMobile) {
                this.openMobile = false;
                this._persistMobile();
                this._applyState();
            }
        },

        destroy: function () {
            if (this._boundResize)     window.removeEventListener('resize', this._boundResize);
            if (this._boundKeydown)    document.removeEventListener('keydown', this._boundKeydown);
            if (this._boundToggle)     window.removeEventListener('sidebar:toggle', this._boundToggle);
            if (this._boundClose)       window.removeEventListener('sidebar:close', this._boundClose);
            this._initialized = false;
        },

        /* ---------------------------------------------------------------- */
        /* State persistence                                               */
        /* ---------------------------------------------------------------- */
        _restoreState: function () {
            var saved = localStorage.getItem(STORAGE_COLLAPSED);
            this.state = (saved === 'true') ? 'collapsed' : 'expanded';
            this.open = true;

            var savedMobile = localStorage.getItem(STORAGE_MOBILE);
            this.openMobile = (savedMobile === 'true');
        },

        _persist: function () {
            try {
                localStorage.setItem(STORAGE_COLLAPSED, String(this.state === 'collapsed'));
            } catch (e) {}
        },

        _persistMobile: function () {
            try {
                localStorage.setItem(STORAGE_MOBILE, String(this.openMobile));
            } catch (e) {}
        },

        /* ---------------------------------------------------------------- */
        /* Apply state to DOM                                               */
        /* ---------------------------------------------------------------- */
        _applyState: function () {
            if (!this.sidebar) return;

            var mobile = this._computeIsMobile();
            var collapsed = (this.state === 'collapsed');

            /* aside data-state — the shadcn/state-machine attribute */
            this.sidebar.setAttribute('data-state', collapsed ? 'collapsed' : 'expanded');

            if (mobile) {
                /* off-canvas mode: translate-x controls transform */
                this.sidebar.setAttribute('data-sidebar-state', this.openMobile ? 'open' : 'closed');
                this.sidebar.classList.toggle('translate-x-full', !this.openMobile);
                this.sidebar.classList.toggle('translate-x-0', this.openMobile);
            } else {
                /* desktop icon mode: panel always rendered */
                this.sidebar.classList.remove('translate-x-full', 'translate-x-0');
                this.sidebar.setAttribute('data-sidebar-state', collapsed ? 'collapsed' : 'expanded');
            }

            /* legacy class on aside (styles.css backward-compat) */
            this.sidebar.classList.toggle('sidebar-collapsed', collapsed);

            /* body class for footer.css / styles.css backward-compat */
            document.body.classList.toggle('sidebar-is-collapsed', collapsed && !mobile);
            document.body.setAttribute('data-sidebar-state', collapsed && !mobile ? 'collapsed' : 'expanded');

            /* overlay (mobile only) */
            if (this.overlay) {
                var overlayHidden = !this.openMobile || !mobile;
                this.overlay.classList.toggle('hidden', overlayHidden);
                this.overlay.classList.toggle('opacity-0', overlayHidden);
                this.overlay.classList.toggle('opacity-100', !overlayHidden);
                this.overlay.classList.toggle('is-visible', !overlayHidden);
            }

            /* body scroll lock (mobile only) */
            if (this.openMobile && mobile) {
                document.body.style.overflow = 'hidden';
            } else if (!mobile) {
                document.body.style.overflow = '';
            }

            /* ARIA sync */
            if (this.trigger) {
                this.trigger.setAttribute('aria-expanded', String(this.openMobile && mobile));
            }
            if (this.collapseBtn) {
                this.collapseBtn.setAttribute('aria-expanded', String(!collapsed || mobile));
            }

            /* Toggle mobile menu button icons (icon-menu ↔ icon-close) */
            var iconMenu = this.trigger ? this.trigger.querySelector('#icon-menu') : null;
            var iconClose = this.trigger ? this.trigger.querySelector('#icon-close') : null;
            if (iconMenu && iconClose) {
                if (mobile && this.openMobile) {
                    iconMenu.classList.add('hidden');
                    iconClose.classList.remove('hidden');
                } else {
                    iconMenu.classList.remove('hidden');
                    iconClose.classList.add('hidden');
                }
            }

            /* collapse-button icon + animation */
            this._syncCollapseButton(collapsed, mobile);
        },

        /* ---------------------------------------------------------------- */
        /* Collapse button — branded particle-burst / ripple / tooltip     */
        /* ---------------------------------------------------------------- */
        _syncCollapseButton: function (collapsed, mobile) {
            var btn = this.collapseBtn;
            if (!btn) return;

            /* hide on mobile (CSS already hides via @media) */
            btn.style.display = mobile ? 'none' : '';

            /* ARIA + server-rendered icon swap via aria-expanded */
            /* The visual icon swap is driven by [aria-expanded] CSS in styles.css */
            /* We also sync inline opacity for the two SVG layers */
            var expandedIcon = btn.querySelector('.collapse-icon-expanded');
            var collapsedIcon = btn.querySelector('.collapse-icon-collapsed');
            if (expandedIcon && collapsedIcon) {
                expandedIcon.style.opacity = collapsed ? '0' : '1';
                collapsedIcon.style.opacity = collapsed ? '1' : '0';
            }
        },

        _createParticleBurst: function () {
            var btn = this.collapseBtn;
            if (!btn) return;
            var container = btn.querySelector('.collapse-particles');
            if (!container) return;

            var count = 12;
            var particles = [];
            for (var i = 0; i < count; i++) {
                var p = document.createElement('div');
                p.className = 'collapse-particle';
                var angle = (i / count) * Math.PI * 2;
                var dist = 40 + Math.random() * 30;
                p.style.setProperty('--tx', Math.cos(angle) * dist + 'px');
                p.style.setProperty('--ty', Math.sin(angle) * dist + 'px');
                var hue = 200 + Math.random() * 80;
                p.style.background = 'hsl(' + hue + ', 80%, 60%)';
                var size = 4 + Math.random() * 6;
                p.style.width = size + 'px';
                p.style.height = size + 'px';
                container.appendChild(p);
                particles.push(p);
            }
            setTimeout(function () {
                particles.forEach(function (p) { p.remove(); });
            }, 800);
        },

        _createRipple: function (event) {
            var btn = this.collapseBtn;
            if (!btn) return;
            var ripple = document.createElement('div');
            ripple.className = 'collapse-ripple';
            var rect = btn.getBoundingClientRect();
            var size = Math.max(rect.width, rect.height);
            ripple.style.width = size + 'px';
            ripple.style.height = size + 'px';
            ripple.style.left = (event.clientX - rect.left - size / 2) + 'px';
            ripple.style.top = (event.clientY - rect.top - size / 2) + 'px';
            btn.appendChild(ripple);
            setTimeout(function () { ripple.remove(); }, 500);
        },

        _animateCollapseButton: function (event) {
            /* particle burst + ripple = branded UX preserved */
            this._createParticleBurst();
            this._createRipple(event);
        },

        /* ---------------------------------------------------------------- */
        /* Active nav link sync (server is source of truth)               */
        /* ---------------------------------------------------------------- */
        _syncActiveState: function () {
            if (!this.sidebar) return;
            var current = document.body.getAttribute('data-section') || '';
            var visited = [];
            try { visited = JSON.parse(localStorage.getItem('visited-sections') || '[]'); } catch (e) {}

            var links = this.sidebar.querySelectorAll('[data-sidebar="menu-button"]');
            links.forEach(function (link) {
                var section = link.getAttribute('data-section') || '';
                var isActive = (section === current);
                link.classList.toggle('active', isActive);
                link.setAttribute('data-sidebar-active', String(isActive));
                link.setAttribute('aria-current', isActive ? 'page' : 'false');

                /* Badge: current or visited section → ✓, otherwise → ○ */
                var badge = link.querySelector('.section-check-badge');
                if (badge) {
                    if (isActive || visited.indexOf(section) !== -1) {
                        badge.textContent = '✓';
                        badge.classList.add('is-done');
                    } else {
                        badge.textContent = '○';
                        badge.classList.remove('is-done');
                    }
                }
            });

            /* Scroll active link into view */
            var activeLink = this.sidebar.querySelector('[data-sidebar="menu-button"][data-sidebar-active="true"]');
            if (activeLink && typeof activeLink.scrollIntoView === 'function') {
                activeLink.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        },

        /* ---------------------------------------------------------------- */
        /* Event binding                                                    */
        /* ---------------------------------------------------------------- */
        _bindEvents: function () {
            var self = this;

            /* Mobile SidebarTrigger (#mobile-menu-btn) */
            if (this.trigger) {
                this.trigger.addEventListener('click', function (e) {
                    e.preventDefault();
                    if (self._computeIsMobile()) {
                        self.toggleMobile();
                    }
                });
            }

            /* Collapse button — SidebarTrigger for desktop icon toggle */
            if (this.collapseBtn) {
                this.collapseBtn.addEventListener('click', function (e) {
                    if (self._computeIsMobile()) return;
                    self._animateCollapseButton(e);
                    self.toggleSidebar();
                });
                /* keyboard accessibility */
                this.collapseBtn.addEventListener('keydown', function (e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        if (!self._computeIsMobile()) {
                            self._animateCollapseButton(e);
                            self.toggleSidebar();
                        }
                    }
                });
                /* tooltip hover */
                this.collapseBtn.addEventListener('mouseenter', function () {
                    var tip = this.querySelector('.collapse-tooltip');
                    if (tip) {
                        tip.style.opacity = '1';
                        tip.style.visibility = 'visible';
                        tip.style.transform = 'translateY(-50%) translateX(0)';
                    }
                });
                this.collapseBtn.addEventListener('mouseleave', function () {
                    var tip = this.querySelector('.collapse-tooltip');
                    if (tip) {
                        tip.style.opacity = '0';
                        tip.style.visibility = 'hidden';
                        tip.style.transform = 'translateY(-50%) translateX(8px)';
                    }
                });
            }

            /* SidebarRail — clickable edge toggle */
            if (this.rail) {
                this.rail.addEventListener('click', function (e) {
                    if (self._computeIsMobile()) return;
                    self.toggleSidebar();
                });
            }

            /* Overlay click → close mobile */
            if (this.overlay) {
                this.overlay.addEventListener('click', function () {
                    if (self.openMobile) self.closeMobile();
                });
            }

            /* Nav link clicks — close mobile overlay + track visited */
            var navLinks = this.sidebar.querySelectorAll('[data-sidebar="menu-button"]');
            navLinks.forEach(function (link) {
                link.addEventListener('click', function () {
                    if (self._computeIsMobile() && self.openMobile) {
                        self.closeMobile();
                    }
                    /* Track visited section for badge completion */
                    var slug = link.getAttribute('data-section');
                    if (slug) {
                        var v = [];
                        try { v = JSON.parse(localStorage.getItem('visited-sections') || '[]'); } catch (e) {}
                        if (v.indexOf(slug) === -1) {
                            v.push(slug);
                            try { localStorage.setItem('visited-sections', JSON.stringify(v)); } catch (e) {}
                        }
                    }
                });
            });

            /* Resize — recalc breakpoint + cross-boundary sync */
            this._boundResize = function () { self._onResize(); };
            window.addEventListener('resize', this._boundResize);

            /* Keyboard — Ctrl/Cmd+B toggle, Esc close */
            this._boundKeydown = function (e) { self._onKeyDown(e); };
            document.addEventListener('keydown', this._boundKeydown);

            /* External events from mobile.js / legacy scripts */
            this._boundToggle = function () { self.toggleSidebar(); };
            this._boundClose  = function () { self.closeMobile(); };
            window.addEventListener('sidebar:toggle', this._boundToggle);
            window.addEventListener('sidebar:close',  this._boundClose);
        },

        _computeIsMobile: function () {
            return window.innerWidth < BREAKPOINT;
        },

        _onResize: function () {
            var wasMobile = this._isMobile;
            this._isMobile = this._computeIsMobile();

            if (wasMobile !== this._isMobile) {
                /* cross-breakpoint: sync mobile overlay to desktop icon state */
                if (this._isMobile) {
                    /* entering mobile — openMobile is already false by default */
                } else {
                    /* entering desktop — reset translate classes, keep icon state */
                    if (this.openMobile) {
                        this.openMobile = false;
                        this._persistMobile();
                    }
                }
            }
            this._applyState();
        },

        _onKeyDown: function (e) {
            /* Ctrl/Cmd+B — toggle sidebar */
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                if (this._computeIsMobile()) {
                    this.toggleMobile();
                } else {
                    this.toggleSidebar();
                }
            }
            /* Escape — close mobile overlay */
            if (e.key === 'Escape') {
                if (this._computeIsMobile() && this.openMobile) {
                    this.closeMobile();
                }
            }
        }
    };

    /* ------------------------------------------------------------------ */
    /* Expose globally for debugging + other modules                     */
    /* ------------------------------------------------------------------ */
    window.CodefySidebar = CodefySidebar;

    /* ------------------------------------------------------------------ */
    /* Auto-init on DOM ready                                              */
    /* ------------------------------------------------------------------ */
    function _autoInit() {
        var sb = $('sidebar');
        if (sb) CodefySidebar.init(sb);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', _autoInit);
    } else {
        _autoInit();
    }
})();
