# RailFare AI — Cinematic Landing Website

A high-performance, ultra-premium dark SaaS landing page built for **RailFare AI: Predictive Surge Pricing Engine & Railway Cockpit**.

---

## Stack & Architecture

- **Bundler & Tooling**: Vite + TypeScript (vanilla, no framework overhead for maximum rendering speed and 60fps responsiveness)
- **3D Graphics**: Three.js (custom GPU shader-driven light ribbons with additive blending, mouse perturbation, and scroll dynamics)
- **Smooth Scroll**: Lenis
- **Animations**: GSAP + ScrollTrigger (blur-to-sharp glitch/scramble text reveals, staggered card transitions, and active nav tracking)
- **Design System**: Strict adherence to the Holographic Cockpit design tokens (`#050B14`, `#00FF9C`, `#00E5FF`, `#8B5CFF`, hairline glass borders, and typography: Orbitron, Rajdhani, Inter, Instrument Serif, JetBrains Mono)

---

## Quickstart

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Streamlit App URL
Create or edit `.env` in the `/landing` folder:
```env
# URL of your running Streamlit cockpit application
VITE_APP_URL=http://localhost:8501
```
*Every "Launch app" and "Start tracking" CTA across the site automatically directs users to this target URL in a new tab.*

### 3. Run Development Server
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 4. Production Build
```bash
npm run build
npm run preview
```

---

## Features & Sections

1. **Full-Screen WebGL Light Ribbon**:
   - Fixed behind all content with additive blending (`THREE.AdditiveBlending`).
   - Flowing neon green (`#00FF9C`) → cyan (`#00E5FF`) → violet (`#8B5CFF`) gradient on `#050B14`.
   - Modulated smoothly by mouse position and scroll progress.
   - DPR capped at 1.75; pauses automatically when the tab is hidden (`visibilitychange`).
   - Graceful CSS gradient fallback if WebGL is unavailable or `prefers-reduced-motion` is active.

2. **Custom Inertial Cursor**:
   - High-tech neon ring and tracking dot that expands and glows over buttons, links, and cards.
   - Automatically disabled on touchscreens.

3. **Two-Column Hero & Live Telemetry Graph**:
   - Left: H1 with italic accent (*Instrument Serif*), subcopy, primary neon button, and demo walkthrough modal trigger.
   - Right: Tilted 3D glass card with animated SVG node graph pipeline (`[Live IRCTC API]` → `[Health Check]` → `[Random Forest Model]` / `[Master CSV]` → `[Dynamic Fare]`) and auto-appending live telemetry log table.

4. **Five-Column Mono Stat Strip**:
   - Verified facts from the project: 12,400+ trains, 3-stage zero-downtime fallback, 7-day forecast horizon, 100-tree Random Forest regressor, &lt;120ms benchmark inference latency.

5. **Dynamic Surge Problem & Live Dispatch Matrix**:
   - Deep explanation of IRCTC Flexi-fare rules (10% increments up to 1.50x) versus passenger uncertainty.
   - Mono table with real corridors (Shatabdi, Rajdhani, Duronto) showing occupancies, multipliers, and predicted fares.

6. **Six Modules, One Cockpit**:
   - Interactive module rows: 3D GIS Live Tracker, AI Operations Cockpit, Spatial AR Travel Hub, PNR & Live Tracking, Station Congestion, and Grievances & Admin.
   - Hovering any row updates the sticky glass preview card with real module metrics.

7. **Predictive Alerts & Final CTA**:
   - 3 glass cards for Surge Bucket Incursions, Waitlist Confirmation Odds, and Split-Route Alternatives.
   - High-impact closing CTA banner with team and capstone credits.

8. **Mobile & Android Native Experience**:
   - Responsive layout down to 390px (iPhone / Android) with stacked hero, adjusted graph, and fixed thumb bottom navigation bar matching `android_ux.py`.

