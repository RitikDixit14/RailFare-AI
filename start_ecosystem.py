#!/usr/bin/env python3
"""
RailFare AI — Unified Dual-Server Ecosystem Launcher
===================================================
Launches both the Streamlit Holographic Cockpit and the
Vite + Three.js Cinematic Landing Website in parallel.
"""

import os
import sys
import subprocess
import time
import signal

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LANDING_DIR = os.path.join(ROOT_DIR, "landing")

# Find virtualenv python / streamlit executable
VENV_STREAMLIT = os.path.join(ROOT_DIR, "ir_env", "Scripts", "streamlit.exe")
if not os.path.exists(VENV_STREAMLIT):
    VENV_STREAMLIT = "streamlit"

print("=" * 72)
print("  ⚡ RAILFARE AI — INTEGRATED COCKPIT & LANDING ECOSYSTEM")
print("=" * 72)
print("  1. Streamlit Holographic Cockpit : http://localhost:8501")
print("  2. Cinematic Landing Website     : http://localhost:5173")
print("  Press Ctrl+C to stop both servers gracefully.")
print("=" * 72)

processes = []

try:
    # 1. Start Streamlit Cockpit
    print("\n[+] Launching Streamlit Holographic Cockpit on port 8501...")
    app_path = os.path.join(ROOT_DIR, "app.py")
    streamlit_cmd = [VENV_STREAMLIT, "run", app_path]
    st_proc = subprocess.Popen(streamlit_cmd, cwd=ROOT_DIR)
    processes.append(st_proc)

    # 2. Start Vite Landing Server
    print("[+] Launching Vite + Three.js Landing Website on port 5173...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    landing_cmd = [npm_cmd, "run", "dev"]
    landing_proc = subprocess.Popen(landing_cmd, cwd=LANDING_DIR)
    processes.append(landing_proc)

    print("\n" + "─" * 72)
    print("  🚀 BOTH SERVERS RUNNING IN HARMONY!")
    print("  🌐 Landing Page : http://localhost:5173")
    print("  🎛️  Main Cockpit : http://localhost:8501")
    print("─" * 72 + "\n")

    # Monitor loop
    while True:
        time.sleep(1)
        for p in processes:
            if p.poll() is not None:
                # One process exited
                raise KeyboardInterrupt

except KeyboardInterrupt:
    print("\n[!] Shutting down RailFare AI servers...")
    for p in processes:
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
            else:
                p.terminate()
        except Exception:
            pass
    print("[✓] All servers stopped cleanly.")

