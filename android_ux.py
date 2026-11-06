"""
RailFare AI — Android Native Experience Module
===============================================
Provides PWA setup, bottom navigation bar, touch gestures, haptic feedback,
Android system-chrome theming, and native-app-feel CSS/JS injection.
"""

import streamlit as st
import json
import os


# ── NAV CONFIG (mirrors app.py NAV_VIEWS) ─────────────────────────────────────
NAV_ITEMS = [
    {"key": "🛰️ 3D GIS LIVE TRACKER",    "icon": "🛰️", "label": "Track",    "emoji_code": "1F6F0"},
    {"key": "🎛️ AI COCKPIT & OPERATIONS", "icon": "🎛️", "label": "Cockpit",  "emoji_code": "1F39B"},
    {"key": "🚀 SPATIAL AR TRAVEL HUB",   "icon": "🚀", "label": "Fare AI",   "emoji_code": "1F680"},
    {"key": "🎫 PNR & LIVE TRACKING",     "icon": "🎫", "label": "PNR",       "emoji_code": "1F3AB"},
    {"key": "📊 STATION CONGESTION",      "icon": "📊", "label": "Station",   "emoji_code": "1F4CA"},
    {"key": "🛡️ GRIEVANCES & ADMIN",     "icon": "🛡️", "label": "Grievance", "emoji_code": "1F6E1"},
]


def inject_pwa_head() -> None:
    """Injects PWA manifest link, Android meta tags, and Apple touch meta into Streamlit <head>."""

    manifest_path = os.path.join(os.path.dirname(__file__), "assets", "manifest.json")
    manifest_b64 = ""
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.dumps(json.load(f))
        import base64
        manifest_b64 = base64.b64encode(manifest_data.encode()).decode()

    pwa_html = f"""
<script>
(function() {{
    try {{
        // ── Inject PWA Manifest ──────────────────────────────────────────────
        if (!document.querySelector('link[rel="manifest"]')) {{
            {f'''
            var manifestBlob = new Blob([atob("{manifest_b64}")], {{type: "application/json"}});
            var manifestURL = URL.createObjectURL(manifestBlob);
            var link = document.createElement("link");
            link.rel = "manifest";
            link.href = manifestURL;
            document.head.appendChild(link);
            ''' if manifest_b64 else ''}
        }}

        // ── Android Chrome / System UI Colour ───────────────────────────────
        var metaTheme = document.querySelector('meta[name="theme-color"]');
        if (!metaTheme) {{
            metaTheme = document.createElement("meta");
            metaTheme.name = "theme-color";
            document.head.appendChild(metaTheme);
        }}
        metaTheme.content = "#050B14";

        // ── Apple / iOS PWA Meta Tags ───────────────────────────────────────
        var metas = [
            ["apple-mobile-web-app-capable",        "yes"],
            ["apple-mobile-web-app-status-bar-style","black-translucent"],
            ["apple-mobile-web-app-title",           "RailFare AI"],
            ["mobile-web-app-capable",               "yes"],
            ["format-detection",                     "telephone=no"],
            ["msapplication-TileColor",              "#050B14"],
        ];
        metas.forEach(function(m) {{
            if (!document.querySelector('meta[name="' + m[0] + '"]')) {{
                var el = document.createElement("meta");
                el.name = m[0]; el.content = m[1];
                document.head.appendChild(el);
            }}
        }});

        // ── Viewport: safe-area insets for Android notch / punchhole ────────
        var viewport = document.querySelector('meta[name="viewport"]');
        if (viewport) {{
            viewport.content = "width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=5.0, viewport-fit=cover";
        }} else {{
            var v = document.createElement("meta");
            v.name = "viewport";
            v.content = "width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=5.0, viewport-fit=cover";
            document.head.appendChild(v);
        }}

        // ── Service Worker Registration (offline shell fallback) ────────────
        if ("serviceWorker" in navigator) {{
            var swCode = `
    self.addEventListener('install', e => self.skipWaiting());
    self.addEventListener('activate', e => clients.claim());
    self.addEventListener('fetch', function(e) {{
        if (e.request.method !== 'GET') return;
        e.respondWith(
            fetch(e.request).catch(function() {{
                return new Response(
                    '<html><body style="background:#050B14;color:#00E5FF;font-family:monospace;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;flex-direction:column;text-align:center;">'
                    + '<div style="font-size:3rem">⚡</div>'
                    + '<h2 style="letter-spacing:2px">RAILFARE AI</h2>'
                    + '<p style="color:#7F93A8">Connecting to Satellite Uplink...<br>Please check your connection.</p>'
                    + '</body></html>',
                    {{headers: {{'Content-Type': 'text/html'}}}}
                );
            }})
        );
    }});
    `;
            var blob = new Blob([swCode], {{type: "application/javascript"}});
            var swURL = URL.createObjectURL(blob);
            navigator.serviceWorker.register(swURL, {{scope: "/"}}).catch(function(){{}});
        }}
    }} catch(e) {{
        console.warn("PWA Head init warning:", e);
    }}
}})();
</script>
"""
    st.html(pwa_html, unsafe_allow_javascript=True)


def inject_android_native_js() -> None:
    """
    Injects all Android-native UX JavaScript:
    - Touch ripple feedback on tappable elements
    - Swipe-left/right gesture to switch nav tabs
    - Pull-to-refresh visual indicator (cosmetic)
    - Long-press detection for context hints
    - Scroll momentum & over-scroll glow
    - Keyboard-aware viewport adjustment
    - Bottom nav scroll-hide on downscroll, show on upscroll
    """
    js = """
<script>
(function() {
"use strict";

// ── 1. TOUCH RIPPLE FEEDBACK ───────────────────────────────────────────────
function createRipple(e) {
    var el = e.currentTarget;
    var existing = el.querySelector('.agy-ripple');
    if (existing) existing.remove();

    var rect  = el.getBoundingClientRect();
    var touch = e.touches ? e.touches[0] : e;
    var x     = (touch.clientX - rect.left);
    var y     = (touch.clientY - rect.top);
    var size  = Math.max(rect.width, rect.height) * 2;

    var ripple       = document.createElement('span');
    ripple.className = 'agy-ripple';
    ripple.style.cssText = [
        'position:absolute',
        'border-radius:50%',
        'background:rgba(0,229,255,0.28)',
        'pointer-events:none',
        'transform:scale(0)',
        'animation:agy-ripple-anim 0.55s linear',
        'z-index:9999',
        'width:'  + size + 'px',
        'height:' + size + 'px',
        'left:'   + (x - size/2) + 'px',
        'top:'    + (y - size/2) + 'px',
    ].join(';');

    if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
    el.style.overflow = 'hidden';
    el.appendChild(ripple);
    setTimeout(function() { if (ripple.parentNode) ripple.remove(); }, 580);
}

// Inject ripple keyframes once
if (!document.getElementById('agy-ripple-style')) {
    var s = document.createElement('style');
    s.id  = 'agy-ripple-style';
    s.textContent = '@keyframes agy-ripple-anim { to { transform:scale(1); opacity:0; } }';
    document.head.appendChild(s);
}

function attachRipples() {
    var selectors = [
        'button',
        'label[data-baseweb="radio"]',
        '.glass-panel',
        '.train-cockpit-card',
        '.kpi-tile-wrap',
        '.class-pill-item',
        '.agy-bottom-nav-item',
    ];
    selectors.forEach(function(sel) {
        document.querySelectorAll(sel).forEach(function(el) {
            if (!el.dataset.ripple) {
                el.dataset.ripple = '1';
                el.addEventListener('touchstart', createRipple, {passive: true});
            }
        });
    });
}
setInterval(attachRipples, 1500);


// ── 2. HORIZONTAL SWIPE → SWITCH NAV TAB ─────────────────────────────────
var swipeStartX = null, swipeStartY = null, swipeLocked = false;

document.addEventListener('touchstart', function(e) {
    // Ignore swipe when interacting with maps, tables, charts, or form inputs
    if (e.target.closest('div[data-testid="stDeckGlJsonChart"], .stoppages-table-container, .multi-day-cal-strip, input, textarea, select, [data-baseweb="select"], .deck-widget, [data-testid="stDataFrame"], .plotly, .js-plotly-plot')) {
        swipeStartX = null;
        return;
    }
    var t = e.touches[0];
    swipeStartX = t.clientX;
    swipeStartY = t.clientY;
    swipeLocked = false;
}, {passive: true});

document.addEventListener('touchend', function(e) {
    if (swipeStartX === null) return;
    var dx = e.changedTouches[0].clientX - swipeStartX;
    var dy = e.changedTouches[0].clientY - swipeStartY;
    swipeStartX = swipeStartY = null;

    // Only trigger swipe if horizontal motion dominates & >= 60px
    if (Math.abs(dx) < 60 || Math.abs(dx) < Math.abs(dy) * 1.5) return;

    var radios = Array.from(document.querySelectorAll('div[data-testid="stRadio"] label[data-baseweb="radio"]'));
    if (radios.length === 0) return;

    var checkedIdx = radios.findIndex(function(r) {
        return r.querySelector('input[type="radio"]') &&
               r.querySelector('input[type="radio"]').checked;
    });

    var nextIdx = checkedIdx + (dx < 0 ? 1 : -1);
    nextIdx = Math.max(0, Math.min(radios.length - 1, nextIdx));

    if (nextIdx !== checkedIdx && radios[nextIdx]) {
        radios[nextIdx].click();
        // Brief haptic if supported
        if (navigator.vibrate) navigator.vibrate(18);
        window.scrollTo({top: 0, behavior: 'smooth'});
    }
}, {passive: true});


// ── 3. PULL-TO-REFRESH VISUAL (cosmetic glow at top) ─────────────────────
var pullStart = null, pullIndicator = null;

function getPullIndicator() {
    if (!pullIndicator) {
        pullIndicator = document.createElement('div');
        pullIndicator.id = 'agy-pull-indicator';
        pullIndicator.style.cssText = [
            'position:fixed','top:0','left:0','width:100%','height:3px',
            'background:linear-gradient(90deg,#00FF9C,#00E5FF,#8B5CFF)',
            'transform:scaleX(0)','transform-origin:left',
            'transition:transform 0.1s,opacity 0.4s',
            'opacity:0','z-index:99999','pointer-events:none',
            'box-shadow:0 0 8px rgba(0,229,255,0.8)',
        ].join(';');
        document.body.appendChild(pullIndicator);
    }
    return pullIndicator;
}

document.addEventListener('touchstart', function(e) {
    if (window.scrollY === 0) pullStart = e.touches[0].clientY;
}, {passive: true});

document.addEventListener('touchmove', function(e) {
    if (pullStart === null) return;
    var dy = e.touches[0].clientY - pullStart;
    if (dy > 0) {
        var ratio = Math.min(dy / 90, 1);
        var pi = getPullIndicator();
        pi.style.transform  = 'scaleX(' + ratio + ')';
        pi.style.opacity    = ratio;
    }
}, {passive: true});

document.addEventListener('touchend', function() {
    pullStart = null;
    var pi = getPullIndicator();
    pi.style.opacity = '0';
    setTimeout(function() { pi.style.transform = 'scaleX(0)'; }, 350);
}, {passive: true});


// ── 4. BOTTOM NAV: HIDE ON SCROLL DOWN, SHOW ON SCROLL UP ────────────────
var lastScrollY   = 0;
var bottomNavEl   = null;
var scrollTicking = false;

function getBottomNav() {
    if (!bottomNavEl) bottomNavEl = document.getElementById('agy-bottom-nav');
    return bottomNavEl;
}

window.addEventListener('scroll', function() {
    if (!scrollTicking) {
        window.requestAnimationFrame(function() {
            var nav = getBottomNav();
            if (nav && window.innerWidth <= 768) {
                var currentY = window.scrollY;
                if (currentY > lastScrollY + 10) {
                    nav.style.transform = 'translateY(100%)';    // scrolling down → hide
                } else if (currentY < lastScrollY - 5) {
                    nav.style.transform = 'translateY(0)';        // scrolling up → show
                }
                lastScrollY = currentY;
            }
            scrollTicking = false;
        });
        scrollTicking = true;
    }
}, {passive: true});


// ── 5. KEYBOARD AWARE: SCROLL FOCUSED INPUT INTO VIEW ────────────────────
function scrollInputIntoView(e) {
    var el = e.target;
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT') {
        setTimeout(function() {
            el.scrollIntoView({behavior: 'smooth', block: 'center'});
        }, 320);
    }
}
document.addEventListener('focus', scrollInputIntoView, true);


// ── 6. DOUBLE-TAP TOP TO SCROLL TO TOP ────────────────────────────────────
var lastTap = 0;
document.addEventListener('touchend', function(e) {
    var now = Date.now();
    if (e.target.closest('header, .cockpit-header') && (now - lastTap) < 350) {
        window.scrollTo({top: 0, behavior: 'smooth'});
        if (navigator.vibrate) navigator.vibrate(10);
    }
    lastTap = now;
}, {passive: true});


// ── 7. LONG-PRESS CONTEXT HINT ON TRAIN CARDS ─────────────────────────────
var lpTimer = null;
document.addEventListener('touchstart', function(e) {
    var card = e.target.closest('.train-cockpit-card');
    if (!card) return;
    lpTimer = setTimeout(function() {
        if (navigator.vibrate) navigator.vibrate([10, 30, 10]);
        card.style.boxShadow = '0 0 30px rgba(0,229,255,0.6), 0 0 60px rgba(139,92,255,0.3)';
        setTimeout(function() { card.style.boxShadow = ''; }, 700);
    }, 600);
}, {passive: true});
document.addEventListener('touchend', function() { clearTimeout(lpTimer); }, {passive: true});
document.addEventListener('touchmove', function() { clearTimeout(lpTimer); }, {passive: true});


// ── 8. BOTTOM NAV ACTIVE STATE SYNC ─────────────────────────────────────
function syncBottomNav() {
    var nav = getBottomNav();
    if (!nav || window.innerWidth > 768) return;

    var checked = document.querySelector('div[data-testid="stRadio"] input[type="radio"]:checked');
    if (!checked) return;

    var checkedLabel = checked.closest('label');
    if (!checkedLabel) return;
    var labelText = checkedLabel.textContent.trim();

    nav.querySelectorAll('.agy-bottom-nav-item').forEach(function(item) {
        var isActive = labelText.indexOf(item.dataset.navKey) !== -1 ||
                       item.dataset.navKey.indexOf(labelText.substring(0,8)) !== -1;
        item.classList.toggle('agy-nav-active', isActive);
    });
}
setInterval(syncBottomNav, 800);

})();
</script>
"""
    st.html(js, unsafe_allow_javascript=True)


def inject_bottom_nav(selected_view: str) -> str | None:
    """
    Renders the Android-style fixed bottom navigation bar.
    Returns the selected view key if a nav item was tapped,
    otherwise returns None.

    Usage in app.py (after selecting_view is set):
        android_ux.inject_bottom_nav(selected_view)
    """
    items_html = ""
    for item in NAV_ITEMS:
        active_class = "agy-nav-active" if item["key"] == selected_view else ""
        items_html += f"""
        <div class="agy-bottom-nav-item {active_class}" data-nav-key="{item['key']}">
            <span class="agy-nav-icon">{item['icon']}</span>
            <span class="agy-nav-label">{item['label']}</span>
        </div>
        """

    bottom_nav_css = """
<style>
/* ── BOTTOM NAV CONTAINER ─────────────────────────────────────── */
#agy-bottom-nav {
    display: none;  /* hidden on desktop */
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 10000;
    height: 60px;
    background: rgba(5, 11, 20, 0.97);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-top: 1px solid rgba(0, 229, 255, 0.2);
    box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.6), 0 -1px 0 rgba(0, 229, 255, 0.08);
    display: none;
    flex-direction: row;
    align-items: stretch;
    justify-content: space-around;
    transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    padding-bottom: env(safe-area-inset-bottom, 0px);
    will-change: transform;
}

/* Show only on mobile */
@media (max-width: 768px) {
    #agy-bottom-nav {
        display: flex !important;
    }
    /* Push main content up so it's not hidden behind bottom nav */
    .main .block-container {
        padding-bottom: 84px !important;
    }
}

/* ── NAV ITEMS ───────────────────────────────────────────────── */
.agy-bottom-nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 1;
    gap: 2px;
    padding: 6px 4px 8px;
    cursor: pointer;
    position: relative;
    border-top: 2px solid transparent;
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
    -webkit-tap-highlight-color: transparent;
    user-select: none;
    min-width: 0;
    overflow: hidden;
}

.agy-bottom-nav-item.agy-nav-active {
    border-top: 2px solid var(--neon-cyan);
}

.agy-bottom-nav-item.agy-nav-active .agy-nav-icon {
    filter: drop-shadow(0 0 6px rgba(0, 229, 255, 0.9));
    transform: translateY(-2px) scale(1.12);
}
.agy-bottom-nav-item.agy-nav-active .agy-nav-label {
    color: var(--neon-cyan) !important;
    font-weight: 800 !important;
}

.agy-nav-icon {
    font-size: 1.3rem;
    line-height: 1;
    transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), filter 0.22s;
    display: block;
}
.agy-nav-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #7F93A8;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
    transition: color 0.22s;
}

/* Active press state */
.agy-bottom-nav-item:active .agy-nav-icon {
    transform: scale(0.88);
}
</style>
"""

    bottom_nav_js = """
<script>
(function() {
    // Wire up bottom nav taps to click matching Streamlit radio button
    function attachBottomNavTaps() {
        var items = document.querySelectorAll('.agy-bottom-nav-item');
        items.forEach(function(item) {
            if (item.dataset.navWired) return;
            item.dataset.navWired = '1';
            item.addEventListener('click', function() {
                var navKey = item.dataset.navKey;
                var labels = document.querySelectorAll('div[data-testid="stRadio"] label[data-baseweb="radio"]');
                labels.forEach(function(label) {
                    var lText = label.textContent.trim();
                    if (lText.indexOf(navKey.substring(0, 10)) !== -1 ||
                        navKey.indexOf(lText.substring(0, 8)) !== -1) {
                        var inp = label.querySelector('input[type="radio"]');
                        label.click();
                        if (inp) {
                            inp.click();
                            inp.dispatchEvent(new Event('change', {bubbles: true}));
                        }
                        window.scrollTo({top: 0, behavior: 'smooth'});
                        if (navigator.vibrate) navigator.vibrate(14);
                    }
                });
            });
        });
    }
    // Run immediately and after Streamlit re-renders
    attachBottomNavTaps();
    setInterval(attachBottomNavTaps, 1000);
})();
</script>
"""

    st.html(bottom_nav_css + f'<nav id="agy-bottom-nav" role="navigation" aria-label="Main navigation">{items_html}</nav>' + bottom_nav_js, unsafe_allow_javascript=True)


def inject_android_overscroll_glow() -> None:
    """Adds a cyan glow at top/bottom over-scroll boundaries (Android rubber-band feel)."""
    st.markdown("""
<style>
/* Android-style overscroll glow at page boundaries */
html {
    overscroll-behavior-y: contain;
    scroll-behavior: smooth;
}

/* Smooth momentum scrolling on all scroll containers */
* {
    -webkit-overflow-scrolling: touch;
    scroll-behavior: smooth;
}

/* ── SCROLL SNAP on horizontal multi-day calendar strip ── */
.multi-day-cal-strip {
    scroll-snap-type: x mandatory;
    -webkit-scroll-snap-type: x mandatory;
}
.multi-day-cal-strip .glass-panel {
    scroll-snap-align: start;
}

/* ── Prevent iOS bounce that reveals white background ── */
body {
    overscroll-behavior: none;
    background: #050B14 !important;
}

/* ── Smooth radio nav swipe scroll with snap ── */
@media (max-width: 768px) {
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        scroll-snap-type: x mandatory;
        -webkit-scroll-snap-type: x mandatory;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] label {
        scroll-snap-align: start;
    }
}
</style>
""", unsafe_allow_html=True)


def inject_android_loading_skeleton() -> None:
    """Shows a brief shimmer skeleton on initial load — matches native Android skeleton pattern."""
    st.markdown("""
<style>
/* Shimmer skeleton for loading states */
@keyframes agy-shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}
.agy-skeleton {
    background: linear-gradient(
        90deg,
        rgba(10, 22, 36, 0.4) 0%,
        rgba(0, 229, 255, 0.08) 40%,
        rgba(10, 22, 36, 0.4) 80%
    );
    background-size: 800px 100%;
    animation: agy-shimmer 1.4s infinite linear;
    border-radius: 8px;
}

/* Apply skeleton effect to Streamlit spinner */
div[data-testid="stSpinner"] > div {
    background: linear-gradient(
        90deg,
        rgba(10, 22, 36, 0.4) 0%,
        rgba(0, 229, 255, 0.1) 40%,
        rgba(10, 22, 36, 0.4) 80%
    ) !important;
    background-size: 800px 100% !important;
    animation: agy-shimmer 1.4s infinite linear !important;
}
</style>
""", unsafe_allow_html=True)


def inject_android_safe_area() -> None:
    """
    Handles Android notch / punch-hole camera / navigation gesture bar.
    Uses CSS env() safe-area-inset-* to pad content away from system chrome.
    """
    st.markdown("""
<style>
/* Android notch / punch-hole / gesture-bar safe areas */
.cockpit-header {
    padding-left: max(14px, env(safe-area-inset-left)) !important;
    padding-right: max(14px, env(safe-area-inset-right)) !important;
}

.main .block-container {
    padding-left:  max(0.75rem, env(safe-area-inset-left)) !important;
    padding-right: max(0.75rem, env(safe-area-inset-right)) !important;
}

@media (max-width: 768px) {
    .stApp {
        /* Extend background behind status bar */
        min-height: calc(100vh + env(safe-area-inset-top));
    }
    #agy-bottom-nav {
        padding-bottom: max(8px, env(safe-area-inset-bottom, 8px)) !important;
        height: calc(60px + env(safe-area-inset-bottom, 0px)) !important;
    }
    .main .block-container {
        padding-top: max(0.75rem, env(safe-area-inset-top)) !important;
        padding-bottom: calc(76px + env(safe-area-inset-bottom, 0px)) !important;
    }
}
</style>
""", unsafe_allow_html=True)


def inject_touch_active_states() -> None:
    """Adds :active press feedback for all interactive elements (Android press ripple supplement)."""
    st.markdown("""
<style>
/* Android-native press states — instant feedback on tap */
button:active,
label[data-baseweb="radio"]:active,
.agy-bottom-nav-item:active,
.train-cockpit-card:active,
.class-pill-item:active,
.kpi-tile-wrap:active {
    transform: scale(0.96) !important;
    opacity: 0.85 !important;
    transition: transform 0.08s ease, opacity 0.08s ease !important;
}

/* Remove all :hover states on touch devices to avoid stuck hover */
@media (hover: none) and (pointer: coarse) {
    .glass-panel:hover,
    .train-cockpit-card:hover,
    .kpi-tile-wrap:hover,
    .class-pill-item:hover,
    button:hover,
    div[data-testid="stButton"] button:hover {
        transform: none !important;
        box-shadow: inherit !important;
        border-color: inherit !important;
    }
}

/* Android system font fallback stack */
@media (max-width: 768px) {
    body {
        -webkit-text-size-adjust: 100%;
        text-size-adjust: 100%;
    }
    input, select, textarea {
        font-size: 16px !important; /* Prevents iOS/Android auto-zoom on focus */
    }
}

/* Android dark mode scrollbars */
::-webkit-scrollbar {
    width: 3px;
    height: 3px;
}
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(0, 229, 255, 0.3);
    border-radius: 10px;
}

/* Smooth focus rings (accessibility) */
:focus-visible {
    outline: 2px solid var(--neon-cyan) !important;
    outline-offset: 2px !important;
    border-radius: 4px !important;
}

/* Selection colour */
::selection {
    background: rgba(0, 229, 255, 0.3);
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)


def inject_android_splash() -> None:
    """
    Shows a 1.4s holographic splash screen on first load
    (simulates Android Activity launch with app branding).
    Only fires once per session via Streamlit session_state + pure CSS lifecycle.
    """
    # Guard against repeated runs in the same Streamlit session
    if st.session_state.get("agy_splash_shown", False):
        return
    st.session_state["agy_splash_shown"] = True

    splash_html = """
<style>
#agy-splash {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    background: radial-gradient(circle at 50% 40%, #0c1b30 0%, #060e1c 50%, #03060c 100%) !important;
    z-index: 99999999 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 16px !important;
    pointer-events: none !important;
    animation: agy-splash-lifecycle 0.9s cubic-bezier(0.2, 0.8, 0.2, 1) forwards !important;
    will-change: opacity, transform;
}

@media (min-width: 769px) {
    #agy-splash {
        display: none !important;
    }
}

@keyframes agy-splash-lifecycle {
    0% {
        opacity: 1;
        visibility: visible;
        transform: scale(1);
    }
    68% {
        opacity: 1;
        visibility: visible;
        transform: scale(1);
    }
    90% {
        opacity: 0;
        visibility: visible;
        transform: scale(0.96);
    }
    100% {
        opacity: 0 !important;
        visibility: hidden !important;
        pointer-events: none !important;
        display: none !important;
    }
}

#agy-splash-icon {
    font-size: 4.5rem;
    animation: agy-splash-pulse 0.9s ease-in-out infinite alternate;
    filter: drop-shadow(0 0 24px rgba(0,229,255,0.95));
}
#agy-splash-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.6rem;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: 3px;
    text-shadow: 0 0 20px rgba(0,229,255,0.7);
}
#agy-splash-subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem;
    color: var(--neon-cyan, #00E5FF);
    letter-spacing: 2px;
    text-transform: uppercase;
}
#agy-splash-bar {
    width: 170px;
    height: 3px;
    background: rgba(0,229,255,0.15);
    border-radius: 3px;
    overflow: hidden;
    margin-top: 8px;
}
#agy-splash-bar-inner {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #00FF9C, #00E5FF, #8B5CFF);
    border-radius: 3px;
    animation: agy-splash-load 1.05s ease-out forwards;
    box-shadow: 0 0 10px rgba(0,229,255,0.9);
}
@keyframes agy-splash-pulse {
    0%   { transform: scale(1);    }
    100% { transform: scale(1.1); }
}
@keyframes agy-splash-load {
    0%   { width: 0%;   }
    100% { width: 100%; }
}
</style>
<div id="agy-splash">
    <div id="agy-splash-icon">⚡</div>
    <div id="agy-splash-title">RAILFARE AI</div>
    <div id="agy-splash-subtitle">Holographic Cockpit v5.0</div>
    <div id="agy-splash-bar"><div id="agy-splash-bar-inner"></div></div>
</div>
<script>
(function() {
    try {
        if (sessionStorage.getItem('agy_splashed')) {
            var sp = document.getElementById('agy-splash');
            if (sp) sp.style.display = 'none';
            return;
        }
        sessionStorage.setItem('agy_splashed', '1');
        setTimeout(function() {
            var sp = document.getElementById('agy-splash');
            if (sp) {
                sp.style.display = 'none';
                if (sp.parentNode) sp.parentNode.removeChild(sp);
            }
        }, 950);
    } catch(e) {}
})();
</script>
"""
    st.html(splash_html, unsafe_allow_javascript=True)


def inject_all(selected_view: str = "") -> None:
    """
    Master function — call once at the top of app.py right after CSS injection.
    Applies every Android native enhancement in the correct order.
    """
    inject_android_splash()
    inject_pwa_head()
    inject_android_safe_area()
    inject_android_overscroll_glow()
    inject_android_loading_skeleton()
    inject_touch_active_states()
    inject_android_native_js()
    if selected_view:
        inject_bottom_nav(selected_view)

