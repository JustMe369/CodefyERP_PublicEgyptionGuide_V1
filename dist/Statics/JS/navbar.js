/**
 * Navbar standalone companion script
 * Works cleanly whether loaded as standalone navbar component or alongside scripts.js
 */
document.addEventListener('DOMContentLoaded', function() {
    // If scripts.js is already running and handling the app, avoid redundant double initialization
    if (window.codefyAppLoaded || window.codefyNavbarLoaded) {
        // Still initialize smart theme toggle even if scripts.js is loaded
        initializeSmartThemeToggle();
        // Initialize sidebar functionality regardless
        initializeCollapsibleSidebar();
        initSidebar();
        return;
    }
    window.codefyAppLoaded = true;
    window.codefyNavbarLoaded = true;

    // Initialize all navbar functionality
    initializeCollapsibleSidebar();
    initSidebar();
    
    // Smart theme toggle functionality
    initializeSmartThemeToggle();
});

// Collapsible Sidebar Management System
function initializeCollapsibleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const collapseToggle = document.getElementById('sidebar-collapse-toggle');
    const collapseIcon = document.getElementById('collapse-icon');
    
    // Initialize sidebar collapsed state from localStorage
    const isSidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (isSidebarCollapsed) {
        sidebar.classList.add('sidebar-collapsed');
        if (collapseIcon) {
            collapseIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />';
        }
    }

    // Handle sidebar collapse/expand functionality
    if (collapseToggle && sidebar) {
        collapseToggle.addEventListener('click', function() {
            const isCollapsed = sidebar.classList.contains('sidebar-collapsed');
            
            if (isCollapsed) {
                // Expand sidebar
                sidebar.classList.remove('sidebar-collapsed');
                localStorage.setItem('sidebarCollapsed', 'false');
                if (collapseIcon) {
                    collapseIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />';
                }
            } else {
                // Collapse sidebar
                sidebar.classList.add('sidebar-collapsed');
                localStorage.setItem('sidebarCollapsed', 'true');
                if (collapseIcon) {
                    collapseIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />';
                }
            }
        });
    }
}

// Sidebar Navigation & Mobile Drawer
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (!sidebar || !mobileMenuBtn || !sidebarOverlay) return;
    
    // Toggle sidebar on mobile menu button click
    mobileMenuBtn.addEventListener('click', function() {
        openSidebar();
    });
    
    // Close sidebar when clicking overlay
    sidebarOverlay.addEventListener('click', function() {
        closeSidebar();
    });
    
    // Close sidebar when clicking outside
    document.addEventListener('click', function(e) {
        if (sidebar.classList.contains('translate-x-0') && 
            !sidebar.contains(e.target) && 
            e.target !== mobileMenuBtn &&
            !mobileMenuBtn.contains(e.target)) {
            closeSidebar();
        }
    });
    
    // Close sidebar on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('translate-x-0')) {
            closeSidebar();
        }
    });
    
    // Initialize active section highlighting
    updateActiveSection();
}

function openSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (!sidebar || !sidebarOverlay) return;
    
    sidebar.classList.remove('-translate-x-full');
    sidebar.classList.add('translate-x-0');
    sidebarOverlay.classList.remove('hidden');
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (!sidebar || !sidebarOverlay) return;
    
    sidebar.classList.remove('translate-x-0');
    sidebar.classList.add('-translate-x-full');
    sidebarOverlay.classList.add('hidden');
    
    // Restore body scroll
    document.body.style.overflow = '';
}

function updateActiveSection() {
    const currentHash = window.location.hash.substring(1) || 'login';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const sectionId = link.getAttribute('data-section');
        if (sectionId === currentHash) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

function initializeSmartThemeToggle() {
    const smartThemeButton = document.getElementById('smart-theme-toggle');
    const smartThemeIcon = document.getElementById('smart-theme-icon');
    const smartSunPath = document.getElementById('smart-sun-path');
    const smartMoonPath = document.getElementById('smart-moon-path');
    
    // Check for saved theme preference or respect OS preference
    const currentTheme = localStorage.getItem('theme') || 
                         (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark-blue' : 'light');
    
    // Apply the saved theme on page load
    if (currentTheme === 'dark-blue') {
        document.documentElement.setAttribute('data-theme', 'dark-blue');
        // Update smart theme icon
        if (smartSunPath && smartMoonPath) {
            smartSunPath.classList.add('hidden');
            smartMoonPath.classList.remove('hidden');
        }
    } else {
        document.documentElement.removeAttribute('data-theme');
        // Update smart theme icon
        if (smartSunPath && smartMoonPath) {
            smartSunPath.classList.remove('hidden');
            smartMoonPath.classList.add('hidden');
        }
    }
    
    // Function to update theme elements
    function updateThemeDisplay(isDark) {
        if (isDark) {
            // Dark theme active
            if (smartSunPath && smartMoonPath) {
                smartSunPath.classList.add('hidden');
                smartMoonPath.classList.remove('hidden');
            }
        } else {
            // Light theme active
            if (smartSunPath && smartMoonPath) {
                smartSunPath.classList.remove('hidden');
                smartMoonPath.classList.add('hidden');
            }
        }
    }
    
    // Function to update theme display for light theme
    function updateThemeDisplayLight() {
        // Regular light theme active (same as regular light)
        if (smartSunPath && smartMoonPath) {
            smartSunPath.classList.remove('hidden');
            smartMoonPath.classList.add('hidden');
        }
    }
    
    // Toggle theme when smart button is clicked
    if (smartThemeButton) {
        smartThemeButton.addEventListener('click', function() {
            // Add enhanced animation effect for smart button
            smartThemeButton.style.transform = 'rotate(360deg)';
            smartThemeButton.style.transition = 'transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
            
            // Show a brief visual feedback
            const originalBg = smartThemeButton.style.background || '';
            smartThemeButton.style.background = 'linear-gradient(135deg, #4f46e5, #7c3aed)';
            
            setTimeout(() => {
                toggleSmartCodefyTheme();
                // Reset transform and background
                smartThemeButton.style.transform = 'rotate(0deg)';
                smartThemeButton.style.background = originalBg;
            }, 300);
        });
    }
    
    // Enhanced toggle function with unique name
    function toggleSmartCodefyTheme() {
        const currentThemeAttribute = document.documentElement.getAttribute('data-theme');
        
        if (currentThemeAttribute === 'dark-blue') {
            // Switch to Regular light theme
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
            updateThemeDisplayLight();
        } else if (currentThemeAttribute === 'light') {
            // Switch to regular light theme
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
            updateThemeDisplay(false);
        } else {
            // Switch to dark blue theme
            document.documentElement.setAttribute('data-theme', 'dark-blue');
            localStorage.setItem('theme', 'dark-blue');
            updateThemeDisplay(true);
        }
        
        // Optional: Add a subtle transition effect
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    }
}
