import Lenis from 'lenis';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

import { initRibbon } from './ribbon';
import { initCustomCursor } from './cursor';
import { initPipelineGraph } from './graph';

gsap.registerPlugin(ScrollTrigger);

// ── 1. ENVIRONMENT CONFIG & CTA BINDING ──────────────────────────────────────
const APP_URL = (import.meta.env.VITE_APP_URL as string) || 'http://localhost:8501';

function bindLaunchCTAs() {
  document.querySelectorAll<HTMLAnchorElement>('.cta-launch-app').forEach((el) => {
    const screen = el.dataset.screen;
    const train = el.dataset.train;
    const params = new URLSearchParams();
    if (screen) params.set('screen', screen);
    if (train) params.set('train', train);
    const qs = params.toString() ? `?${params.toString()}` : '';
    el.href = `${APP_URL}/${qs}`;
    el.target = '_blank';
    el.rel = 'noopener noreferrer';
  });
}

// ── 2. LENIS SMOOTH SCROLL & SCROLLTRIGGER SYNC ──────────────────────────────
const lenis = new Lenis({
  duration: 1.1,
  easing: (t: number) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smoothWheel: true,
  touchMultiplier: 1.8,
});

lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add((time: number) => {
  lenis.raf(time * 1000);
});
gsap.ticker.lagSmoothing(0);

// Smooth scroll to in-page anchors
document.querySelectorAll<HTMLAnchorElement>('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener('click', (e) => {
    const targetId = anchor.getAttribute('href');
    if (!targetId || targetId === '#') return;
    const target = document.querySelector(targetId);
    if (target) {
      e.preventDefault();
      lenis.scrollTo(target as HTMLElement, { offset: -70 });
    }
  });
});

// ── 3. THREE.JS LIGHT RIBBON BACKGROUND ──────────────────────────────────────
const ribbon = initRibbon('webgl-canvas');

lenis.on('scroll', (e: { progress: number }) => {
  ribbon?.setScrollProgress(e.progress);
});

// ── 4. CUSTOM CURSOR & HERO PIPELINE ─────────────────────────────────────────
initCustomCursor();
initPipelineGraph();
bindLaunchCTAs();

// ── 5. SCRAMBLE / GLITCH + BLUR-TO-SHARP TEXT ENTRY EFFECT ───────────────────
const GLYPHS = '01アイウエオカキサシスセソ0123456789!<>-_/[]{}—=+*^?#_';

function scrambleText(element: HTMLElement) {
  const originalHTML = element.innerHTML;
  const originalText = element.textContent || '';
  const length = originalText.length;
  let frame = 0;
  const totalFrames = 30;

  // Preserve HTML structure if it contains <em>
  const hasEm = originalHTML.includes('<em>');
  let beforeEm = '';
  let insideEm = '';
  let afterEm = '';

  if (hasEm) {
    const match = originalHTML.match(/(.*?)<em>(.*?)<\/em>(.*)/s);
    if (match) {
      beforeEm = match[1];
      insideEm = match[2];
      afterEm = match[3];
    }
  }

  const interval = setInterval(() => {
    frame++;
    const progress = frame / totalFrames;

    if (!hasEm) {
      let output = '';
      for (let i = 0; i < length; i++) {
        if (i < length * progress) {
          output += originalText[i];
        } else {
          output += GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
        }
      }
      element.textContent = output;
    } else {
      let outBefore = '';
      for (let i = 0; i < beforeEm.length; i++) {
        outBefore += i < beforeEm.length * progress
          ? beforeEm[i]
          : GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
      }

      let outInside = '';
      for (let i = 0; i < insideEm.length; i++) {
        outInside += i < insideEm.length * progress
          ? insideEm[i]
          : GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
      }

      element.innerHTML = `${outBefore}<em>${outInside}</em>${afterEm}`;
    }

    if (frame >= totalFrames) {
      clearInterval(interval);
      element.innerHTML = originalHTML;
    }
  }, 25);
}

// GSAP ScrollTrigger for section titles: Blur-to-sharp + slight horizontal shift
document.querySelectorAll<HTMLElement>('[data-scramble]').forEach((titleEl) => {
  gsap.fromTo(
    titleEl,
    {
      filter: 'blur(12px)',
      x: -24,
      opacity: 0.1,
    },
    {
      filter: 'blur(0px)',
      x: 0,
      opacity: 1,
      duration: 1.0,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: titleEl,
        start: 'top 85%',
        once: true,
        onEnter: () => {
          scrambleText(titleEl);
        },
      },
    }
  );
});

// Staggered reveal for cards and stat items
gsap.utils.toArray<HTMLElement>('.glass-card, .stat-col, .module-row').forEach((el) => {
  gsap.fromTo(
    el,
    { y: 35, opacity: 0 },
    {
      y: 0,
      opacity: 1,
      duration: 0.8,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: el,
        start: 'top 90%',
        once: true,
      },
    }
  );
});

// ── 6. SIX MODULES INTERACTIVE PREVIEW ───────────────────────────────────────
const moduleData = [
  {
    screen: 'tracker',
    title: '3D GIS Live Tracker',
    sub: 'Corridor Map with Satellite GPS & Speed Routes',
    src: 'RailRadar Satellite Uplink',
    status: 'CONNECTED (100% ONLINE)',
    target: '#12004 NDLS → LKO (PLATFORM #1)',
  },
  {
    screen: 'cockpit',
    title: 'AI Cockpit & Operations',
    sub: 'Real-Time Surge Dispatch Matrix & Operational Gauges',
    src: 'Live IRCTC & Flexi-Rule Matrix',
    status: '76.5/100 CRITICAL PRESSURE',
    target: 'FLEET VELOCITY: 94.2 KM/H',
  },
  {
    screen: 'travel',
    title: 'Spatial AR Travel Hub (Fare AI)',
    sub: '7-Day Dynamic Fare Matrix & Multiplier Forecaster',
    src: 'Scikit-Learn Random Forest (100 Trees)',
    status: 'INFERENCE ACTIVE (<120ms)',
    target: '1A / 2A / 3A / SL CLASS MULTIPLIERS',
  },
  {
    screen: 'pnr',
    title: 'PNR & Live Tracking',
    sub: 'Confirmation Odds, Coach Layouts & GPS Route Halts',
    src: 'IRCTC Charting & Waitlist DB',
    status: '82% CONFIRMATION CHANCE',
    target: 'PNR #2419827361 (WL 14 → RAC)',
  },
  {
    screen: 'station',
    title: 'Station Congestion',
    sub: 'Junction Rush Dynamics & Platform Crowd Indices',
    src: '36 Major Indian Railway Hubs',
    status: 'PEAK RUSH HOUR (7-10 AM)',
    target: 'NDLS PLATFORM 1-16 (DENSITY: 82%)',
  },
  {
    screen: 'grievance',
    title: 'Grievances & Admin',
    sub: 'Passenger Feedback Pipeline & Rapid Resolution Logs',
    src: 'Real-Time Grievance Engine',
    status: 'RAPID RESOLUTION STREAM',
    target: 'CATERING / AC / CLEANLINESS LOGS',
  },
];

const moduleRows = document.querySelectorAll<HTMLElement>('.module-row');
const previewTitle = document.getElementById('preview-title');
const previewSub = document.getElementById('preview-sub');
const previewSrc = document.getElementById('preview-src');
const previewStatus = document.getElementById('preview-status');
const previewTarget = document.getElementById('preview-target');
const previewCtaBtn = document.getElementById('preview-cta-btn') as HTMLAnchorElement | null;

moduleRows.forEach((row) => {
  const modIndex = parseInt(row.dataset.module || '0', 10);
  const data = moduleData[modIndex];

  const activateModule = () => {
    moduleRows.forEach((r) => r.classList.remove('active'));
    row.classList.add('active');

    if (data && previewTitle && previewSub && previewSrc && previewStatus && previewTarget) {
      previewTitle.textContent = data.title;
      previewSub.textContent = data.sub;
      previewSrc.textContent = data.src;
      previewStatus.textContent = data.status;
      previewTarget.textContent = data.target;
      if (previewCtaBtn && data.screen) {
        previewCtaBtn.href = `${APP_URL}/?screen=${data.screen}`;
        previewCtaBtn.dataset.screen = data.screen;
      }
    }
  };

  row.addEventListener('mouseenter', activateModule);
  row.addEventListener('focus', activateModule);
  row.addEventListener('click', activateModule);
  row.addEventListener('dblclick', () => {
    if (data?.screen) {
      window.open(`${APP_URL}/?screen=${data.screen}`, '_blank');
    }
  });
});

// Activate first module initially
if (moduleRows.length > 0) {
  moduleRows[0].classList.add('active');
  const firstData = moduleData[0];
  if (previewCtaBtn && firstData?.screen) {
    previewCtaBtn.href = `${APP_URL}/?screen=${firstData.screen}`;
  }
}

// Interactive Table Row Clicks (opens train in live cockpit)
document.querySelectorAll<HTMLTableRowElement>('.mono-table tbody tr').forEach((tr) => {
  const text = tr.textContent || '';
  const match = text.match(/#(\d+)/);
  if (match) {
    const trainNo = match[1];
    tr.style.cursor = 'pointer';
    tr.title = `⚡ Click to inspect train #${trainNo} in live cockpit`;
    tr.addEventListener('click', () => {
      window.open(`${APP_URL}/?screen=tracker&train=${trainNo}`, '_blank');
    });
  }
});

// ── 7. DEMO MODAL CONTROLS ───────────────────────────────────────────────────
const openDemoBtn = document.getElementById('open-demo-modal');
const closeDemoBtn = document.getElementById('close-demo-modal');
const demoModal = document.getElementById('demo-modal');
const modalBackdrop = document.getElementById('modal-backdrop');

function openModal() {
  if (demoModal) {
    demoModal.removeAttribute('hidden');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal() {
  if (demoModal) {
    demoModal.setAttribute('hidden', '');
    document.body.style.overflow = '';
  }
}

openDemoBtn?.addEventListener('click', openModal);
closeDemoBtn?.addEventListener('click', closeModal);
modalBackdrop?.addEventListener('click', closeModal);

window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && demoModal && !demoModal.hasAttribute('hidden')) {
    closeModal();
  }
});

// ── 8. STICKY NAV SCROLL DETECTION ───────────────────────────────────────────
const siteHeader = document.getElementById('site-header');
window.addEventListener('scroll', () => {
  if (siteHeader) {
    siteHeader.classList.toggle('scrolled', window.scrollY > 40);
  }
}, { passive: true });

// ── 9. MOBILE BOTTOM NAV HIGHLIGHT ───────────────────────────────────────────
const mobileNavItems = document.querySelectorAll<HTMLAnchorElement>('.mobile-nav-item');
window.addEventListener('scroll', () => {
  const sections = ['hero', 'product', 'modules'];
  const scrollPos = window.scrollY + 200;

  sections.forEach((secId, idx) => {
    const el = document.getElementById(secId);
    if (el) {
      const top = el.offsetTop;
      const height = el.offsetHeight;
      if (scrollPos >= top && scrollPos < top + height) {
        mobileNavItems.forEach((item) => item.classList.remove('active'));
        if (mobileNavItems[idx]) {
          mobileNavItems[idx].classList.add('active');
        }
      }
    }
  });
}, { passive: true });

console.log('⚡ RailFare AI Landing Page Initialized. Target App:', APP_URL);

