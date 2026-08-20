import html
import json
import time
import uuid
import difflib
from datetime import datetime

import streamlit as st
import requests
from groq import Groq

# ============================================================
#  PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="EduFix AI | Code Studio",
    page_icon="🩹",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BACKEND_URL = "http://127.0.0.1:8000/fix-code"
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"

# ============================================================
#  SESSION STATE
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "current_diagnosis" not in st.session_state:
    st.session_state.current_diagnosis = None

# If a "Restore to workspace" button was clicked on the previous run, apply it
# now, before the text_area widgets below are created with these same keys.
if "_restore_code" in st.session_state:
    st.session_state["code_input_area"] = st.session_state.pop("_restore_code")
if "_restore_error" in st.session_state:
    st.session_state["error_input_area"] = st.session_state.pop("_restore_error")

# ============================================================
#  DESIGN SYSTEM
#  Concept: this tool's real output is a diff — broken code in, a patch out.
#  The visual language borrows from git diffs and real terminal chrome
#  instead of generic AI neon. One accent color carries the brand; motion
#  is spent deliberately (an ambient aurora, a blinking token cursor,
#  fade-ins) rather than glowing every element at once.
# ============================================================
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg: #0A0B0F;
  --panel: #131519;
  --panel-raised: #191C22;
  --border: rgba(255, 255, 255, 0.08);
  --border-strong: rgba(255, 255, 255, 0.16);
  --text-main: #E9EAEE;
  --text-muted: #8B8F9B;
  --add: #34D399;
  --add-bg: rgba(52, 211, 153, 0.12);
  --remove: #F0525F;
  --remove-bg: rgba(240, 82, 95, 0.12);
  --accent: #F2A93B;
  --accent-dim: rgba(242, 169, 59, 0.16);
  /* Decorative palette — used for brand flourishes (gradients, glows,
     language tags). Kept separate from --add/--remove so diff colors
     always stay semantic, never just decoration. */
  --teal: #22D3EE;
  --pink: #EC4899;
  --violet: #8B5CF6;
  --blue: #38BDF8;
  --shadow-soft: 0 12px 32px rgba(0, 0, 0, 0.35);
}

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
    letter-spacing: -0.01em;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ---------- Fluid ambient background ---------- */
.aurora-bg {
  position: fixed;
  inset: 0;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
  animation: hue-shift 90s linear infinite;
}
.aurora-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.34;
  mix-blend-mode: screen;
  will-change: transform;
}
.blob-1 {
  width: 520px; height: 520px;
  background: var(--accent);
  top: -160px; left: -100px;
  animation: drift-a 34s ease-in-out infinite;
}
.blob-2 {
  width: 460px; height: 460px;
  background: var(--teal);
  top: 30%; right: -160px;
  animation: drift-b 40s ease-in-out infinite;
}
.blob-3 {
  width: 380px; height: 380px;
  background: var(--violet);
  bottom: -180px; left: 28%;
  opacity: 0.26;
  animation: drift-c 46s ease-in-out infinite;
}
.blob-4 {
  width: 340px; height: 340px;
  background: var(--pink);
  top: 55%; left: 42%;
  opacity: 0.20;
  animation: drift-d 52s ease-in-out infinite;
}
@keyframes drift-a {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%      { transform: translate(60px, -40px) scale(1.08); }
  66%      { transform: translate(-30px, 30px) scale(0.94); }
}
@keyframes drift-b {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50%      { transform: translate(-70px, 40px) scale(1.1); }
}
@keyframes drift-c {
  0%, 100% { transform: translate(0, 0) scale(1); }
  40%      { transform: translate(50px, -20px) scale(1.05); }
  70%      { transform: translate(-40px, 10px) scale(0.96); }
}
@keyframes drift-d {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50%      { transform: translate(45px, 35px) scale(1.12); }
}
@keyframes hue-shift {
  from { filter: hue-rotate(0deg); }
  to   { filter: hue-rotate(360deg); }
}
.grain-overlay {
  position: fixed;
  inset: 0;
  z-index: 1;
  opacity: 0.035;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

html, body {
    background: var(--bg);
}

[data-testid="stAppViewContainer"] { background: transparent; color: var(--text-main); }
.stApp { background: transparent; }

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}

.shine-text {
  background: linear-gradient(100deg, var(--accent) 0%, var(--pink) 26%, var(--violet) 50%, var(--teal) 74%, var(--accent) 100%);
  background-size: 300% auto;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: shine 9s linear infinite;
}
@keyframes shine { to { background-position: -300% center; } }

/* ---------- Panels & tabs ---------- */
[data-testid="stTabPanel"] {
  background: var(--panel);
  padding: 26px;
  border-radius: 0 0 14px 14px;
  border: 1px solid var(--border);
  border-top: none;
  margin-bottom: 20px;
}
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 4px;
  background: var(--panel-raised);
  padding: 6px;
  border-radius: 14px 14px 0 0;
  border: 1px solid var(--border);
  border-bottom: none;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  height: 44px;
  border-radius: 9px;
  color: var(--text-muted) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 600 !important;
  font-size: 13.5px !important;
  border: none !important;
  padding: 0px 22px !important;
  position: relative !important;
  transition: color 0.2s ease, background 0.2s ease !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
  background: var(--panel) !important;
  color: #ffffff !important;
}
[data-testid="stTabs"] [aria-selected="true"]::after {
  content: "";
  position: absolute;
  left: 14px; right: 14px; bottom: 0;
  height: 2px;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--accent), var(--pink), var(--teal));
}

/* ---------- Header ---------- */
.header-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0 20px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 18px;
}
.brand-title { display: flex; align-items: center; gap: 16px; }
.logo-badge {
  background: linear-gradient(135deg, var(--accent), var(--pink));
  border: 1px solid rgba(255, 255, 255, 0.25);
  box-shadow: 0 0 26px rgba(242, 169, 59, 0.3);
  width: 56px; height: 56px;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 26px;
}
.status-badge {
  background: var(--add-bg);
  border: 1px solid rgba(79, 203, 124, 0.3);
  color: var(--add);
  padding: 7px 14px;
  border-radius: 20px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 500;
  display: inline-flex; align-items: center; gap: 8px;
}
.pulse-dot {
  width: 7px; height: 7px;
  background-color: var(--add);
  border-radius: 50%;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(79, 203, 124, 0.5); }
  70% { box-shadow: 0 0 0 7px rgba(79, 203, 124, 0); }
  100% { box-shadow: 0 0 0 0 rgba(79, 203, 124, 0); }
}

/* ---------- Stats row ---------- */
.stats-row { display: flex; gap: 10px; margin: 0 0 26px 0; flex-wrap: wrap; }
.stat-chip {
  background: var(--panel-raised);
  border: 1px solid var(--border);
  border-left: 3px solid var(--border-strong);
  border-radius: 10px;
  padding: 10px 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11.5px;
  color: var(--text-muted);
  transition: border-color .15s ease, transform .15s ease;
}
.stat-chip:hover { border-color: var(--border-strong); transform: translateY(-1px); }
.stat-chip b {
  color: #fff;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 15px;
  display: block;
  margin-top: 3px;
}
.stat-chip.c-amber  { border-left-color: var(--accent); }
.stat-chip.c-amber b  { color: var(--accent); }
.stat-chip.c-violet { border-left-color: var(--violet); }
.stat-chip.c-violet b { color: var(--violet); }
.stat-chip.c-teal   { border-left-color: var(--teal); }
.stat-chip.c-teal b   { color: var(--teal); }

/* ---------- Chat bubbles ---------- */
[data-testid="stChatMessage"] {
    background: var(--panel-raised) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin-bottom: 14px !important;
    position: relative !important;
    overflow: hidden !important;
    transition: border-color .15s ease;
}
[data-testid="stChatMessage"]:hover { border-color: var(--border-strong) !important; }
[data-testid="stChatMessage"]::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--teal), var(--accent));
}

/* ---------- Buttons ---------- */
.stButton>button {
  font-family: 'Space Grotesk', sans-serif !important;
  background: linear-gradient(120deg, var(--accent) 0%, var(--pink) 100%) !important;
  background-size: 180% 180% !important;
  background-position: 0% 50% !important;
  color: #14110A !important;
  border: none !important;
  padding: 15px 24px !important;
  font-weight: 700 !important;
  font-size: 15px !important;
  border-radius: 10px !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background-position 0.5s ease !important;
}
.stButton>button:hover {
  transform: translateY(-1px) !important;
  background-position: 100% 50% !important;
  box-shadow: 0 8px 26px rgba(236, 72, 153, 0.3), 0 4px 18px rgba(242, 169, 59, 0.25) !important;
}
.stButton>button:active { transform: translateY(0) !important; }

.stDownloadButton>button {
  font-family: 'Space Grotesk', sans-serif !important;
  background: var(--panel-raised) !important;
  color: var(--text-main) !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  transition: border-color .15s ease, transform .15s ease !important;
}
.stDownloadButton>button:hover { border-color: var(--accent) !important; transform: translateY(-1px) !important; }

/* ---------- Form controls ---------- */
textarea, [data-baseweb="input"], [data-baseweb="select"] {
    background-color: #0E0F13 !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 0 10px 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13.5px !important;
}
[data-baseweb="select"] { border-radius: 10px !important; }
textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 1px var(--accent) !important; }
[data-testid="stChatInput"] { border-radius: 12px !important; border: 1px solid var(--border-strong) !important; background: var(--panel-raised) !important; }

/* Radio pill toggle (diff view switch) */
[data-testid="stRadio"] > div {
  flex-direction: row;
  gap: 4px;
  background: var(--panel-raised);
  padding: 4px;
  border-radius: 10px;
  border: 1px solid var(--border);
  width: fit-content;
}
[data-testid="stRadio"] label {
  padding: 6px 14px !important;
  border-radius: 7px !important;
  margin: 0 !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 12.5px !important;
}
[data-testid="stRadio"] label:has(input:checked) {
  background: linear-gradient(120deg, var(--accent), var(--pink)) !important;
  color: #14110A !important;
}

/* ---------- Terminal chrome ---------- */
.mac-header {
    background: var(--panel-raised);
    padding: 10px 16px;
    border-radius: 10px 10px 0 0;
    border: 1px solid var(--border);
    border-bottom: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: -1rem;
    position: relative;
    z-index: 10;
}
.mac-dots { display: flex; align-items: center; gap: 7px; }
.mac-btn { width: 10px; height: 10px; border-radius: 50%; display: inline-block; opacity: 0.6; }
.mac-close { background: #ff5f56; }
.mac-min { background: #ffbd2e; }
.mac-max { background: #27c93f; }
.mac-title { color: var(--text-muted); font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.mac-status-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px;
    color: var(--accent);
    background: var(--accent-dim);
    padding: 2px 8px;
    border-radius: 5px;
    border: 1px solid rgba(242, 169, 59, 0.25);
}

/* ---------- Patch card ---------- */
.patch-card {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 18px;
    animation: fadeIn 0.4s ease;
    transition: border-color .2s ease, box-shadow .2s ease;
}
.patch-card:hover { border-color: var(--border-strong); box-shadow: var(--shadow-soft); }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
.patch-header { background: var(--panel-raised); border-bottom: 1px solid var(--border); padding: 12px 18px; display: flex; align-items: center; justify-content: space-between; position: relative; }
.patch-header::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), var(--pink), var(--violet), var(--teal));
}
.patch-filename { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: var(--text-main); }
.patch-stats { font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.patch-stats .add { color: var(--add); }
.patch-stats .remove { color: var(--remove); margin-left: 6px; }
.patch-body { background: #0E0F13; padding: 18px; }

/* ---------- Diff: unified ---------- */
.diff-unified { font-family: 'JetBrains Mono', monospace; font-size: 12.5px; border-radius: 10px; overflow: hidden; border: 1px solid var(--border); }
.diff-row { display: flex; align-items: flex-start; }
.diff-row.add { background: var(--add-bg); }
.diff-row.remove { background: var(--remove-bg); }
.diff-row.hunk { background: var(--panel-raised); color: var(--accent); padding: 6px 12px; font-size: 11.5px; }
.diff-lineno { width: 38px; text-align: right; padding: 2px 8px 2px 0; color: var(--text-muted); user-select: none; flex-shrink: 0; }
.diff-marker { width: 16px; text-align: center; flex-shrink: 0; padding-top: 2px; }
.diff-marker.add { color: var(--add); }
.diff-marker.remove { color: var(--remove); }
.diff-text { white-space: pre-wrap; word-break: break-word; padding: 2px 12px 2px 0; }
.diff-empty { color: var(--text-muted); font-size: 13px; padding: 14px; font-style: italic; }

/* ---------- Diff: side-by-side ---------- */
.diff-sbs { display: grid; grid-template-columns: 1fr 1fr; border: 1px solid var(--border); border-radius: 10px; overflow: hidden; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.diff-sbs-col:first-child { border-right: 1px solid var(--border); }
.diff-sbs-col { background: #0E0F13; }
.diff-sbs-header { background: var(--panel-raised); padding: 8px 14px; font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 11.5px; color: var(--text-muted); border-bottom: 1px solid var(--border); text-transform: uppercase; letter-spacing: 0.05em; }
.diff-sbs-col:first-child .diff-sbs-header { color: var(--remove); }
.diff-sbs-col:last-child .diff-sbs-header { color: var(--add); }
.diff-sbs-row { padding: 1px 12px; min-height: 18px; }
.diff-sbs-row.remove { background: var(--remove-bg); }
.diff-sbs-row.add { background: var(--add-bg); }
.diff-sbs-row.empty { background: rgba(255, 255, 255, 0.015); }
.diff-sbs .diff-text { white-space: pre-wrap; word-break: break-word; }

/* ---------- Token readout ---------- */
.token-readout {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13.5px;
    color: var(--accent);
    background: linear-gradient(120deg, var(--accent-dim), rgba(236, 72, 153, 0.12));
    border: 1px solid rgba(242, 169, 59, 0.3);
    border-radius: 8px;
    padding: 10px 16px;
    display: inline-flex; align-items: center; gap: 10px;
    margin-bottom: 16px;
}
.token-cursor { display: inline-block; width: 7px; height: 14px; background: var(--accent); animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }

/* ---------- History ---------- */
.history-card { background: var(--panel-raised); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; margin-bottom: 8px; transition: border-color .15s ease; }
.history-card:hover { border-color: var(--border-strong); }
.history-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.history-lang { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--accent); background: var(--accent-dim); padding: 2px 8px; border-radius: 5px; }
.history-time { font-size: 11px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }
.history-preview { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-muted); white-space: pre-wrap; overflow: hidden; max-height: 38px; margin-bottom: 4px; }

/* ---------- Misc ---------- */
.fade-divider { height: 1px; border: none; margin: 22px 0; background: linear-gradient(90deg, transparent, var(--border-strong), transparent); }
.thinking-dots span { display: inline-block; width: 6px; height: 6px; background: var(--accent); border-radius: 50%; margin: 0 2px; animation: bounce 1.2s infinite ease-in-out; }
.thinking-dots span:nth-child(2) { animation-delay: .15s; }
.thinking-dots span:nth-child(3) { animation-delay: .3s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0.6); opacity: .4; } 40% { transform: scale(1); opacity: 1; } }

.info-card { background: var(--panel-raised); border: 1px solid var(--border); border-left: 3px solid var(--border-strong); padding: 18px; border-radius: 12px; margin-bottom: 12px; transition: border-color .15s ease, transform .15s ease; }
.info-card:hover { border-color: var(--border-strong); transform: translateY(-1px); }
.info-card h4 { margin: 0; font-size: 14.5px; color: #E9EAEE; font-family: 'Space Grotesk', sans-serif !important; }
.info-card p { margin: 6px 0 0 0; font-size: 13px; color: var(--text-muted); }
.info-card:nth-of-type(4n+1) { border-left-color: var(--accent); }
.info-card:nth-of-type(4n+2) { border-left-color: var(--teal); }
.info-card:nth-of-type(4n+3) { border-left-color: var(--violet); }
.info-card:nth-of-type(4n+4) { border-left-color: var(--pink); }

.footer { color: var(--text-muted); font-size: 12.5px; text-align: center; padding: 36px 0 18px 0; font-weight: 500; }
.footer a { transition: opacity .15s ease; }
.footer a:hover { opacity: 0.75; }
"""

st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# Fluid ambient background — pure CSS, no external assets, renders every run
st.markdown(
    """
    <div class="aurora-bg">
        <div class="aurora-blob blob-1"></div>
        <div class="aurora-blob blob-2"></div>
        <div class="aurora-blob blob-3"></div>
        <div class="aurora-blob blob-4"></div>
    </div>
    <div class="grain-overlay"></div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
#  GROQ CLIENT
# ============================================================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ============================================================
#  SAMPLE BUG LIBRARY
# ============================================================
SAMPLE_BUGS = {
    "Select Sample...": ("", ""),
    "🐍 Python: Indentation & Type Error": (
        "def calculate_total(prices):\n    total = 0\n    for p in prices:\n    total += p\n    return total + 'USD'",
        "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
    ),
    "⚛️ React: Hook Dependency Loop": (
        "import { useState, useEffect } from 'react';\n\nfunction Counter() {\n  const [count, setCount] = useState(0);\n  useEffect(() => {\n    setCount(count + 1);\n  });\n  return <div>{count}</div>;\n}",
        "Warning: Maximum update depth exceeded."
    ),
    "🦀 Rust: Borrow Checker Bug": (
        "fn main() {\n    let mut s = String::from(\"hello\");\n    let r1 = &s;\n    let r2 = &s;\n    let r3 = &mut s;\n    println!(\"{}, {}, {}\", r1, r2, r3);\n}",
        "error[E0502]: cannot borrow `s` as mutable because it is also borrowed as immutable"
    ),
    "🗄️ SQL: JOIN Syntax Ambiguity": (
        "SELECT id, name, department_name \nFROM users \nJOIN departments ON users.dept_id = departments.id\nWHERE id = id;",
        "ERROR: column reference \"id\" is ambiguous"
    ),
    "⚡ JS: Scope & Async Error": (
        "async function fetchUserData(userId) {\n  let user = await api.getUser(userId);\n  console.log(user.name);\n}\nconsole.log(user.name);",
        "ReferenceError: user is not defined at line 5"
    ),
    "⚙️ C++: Off-by-One Array Bug": (
        "#include <iostream>\nusing namespace std;\n\nint main() {\n    int arr[5] = {1, 2, 3, 4, 5};\n    for(int i=0; i<=5; i++) {\n        cout << arr[i] << endl;\n    }\n    return 0;\n}",
        "Segmentation fault (core dumped)"
    )
}

# ============================================================
#  LANGUAGE COLORS
#  Each language gets its own recognizable accent (loosely brand-matched)
#  so color carries real meaning here, not just decoration — the source
#  terminal and history entries tint themselves to whatever you're
#  debugging.
# ============================================================
LANGUAGE_COLORS = {
    "Python": "#FFD43B",
    "JavaScript / React": "#61DAFB",
    "C++": "#5C9FE0",
    "Java": "#ED8B00",
    "Rust": "#E8590C",
    "SQL": "#4479A1",
    "Go": "#00ADD8",
}


def hex_to_rgba(hex_color: str, alpha: float = 0.15) -> str:
    """Convert a #RRGGBB color into an rgba(...) string at the given alpha,
    used to build tinted backgrounds/borders that match a solid accent."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


# ============================================================
#  HELPERS: extracting and diffing code
# ============================================================
def extract_fixed_code(response_text: str):
    """Pull the first fenced code block out of the AI's response, if any."""
    if not response_text or "```" not in response_text:
        return None
    parts = response_text.split("```")
    if len(parts) < 2:
        return None
    code_block = parts[1]
    code_lines = code_block.splitlines()
    if code_lines and code_lines[0].strip().isalpha():
        return "\n".join(code_lines[1:]).strip()
    return code_block.strip()


def compute_unified_diff_rows(original: str, fixed: str, context: int = 2):
    """Build tagged rows describing a real unified diff between two code
    strings, so the UI can color them like an actual patch: hunk headers,
    then add/remove/context lines, each carrying old/new line numbers."""
    original_lines = original.splitlines()
    fixed_lines = fixed.splitlines()
    raw_diff = difflib.unified_diff(original_lines, fixed_lines, lineterm="", n=context)

    rows = []
    old_no = 0
    new_no = 0
    for line in raw_diff:
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("@@"):
            rows.append({"type": "hunk", "text": line, "old_no": None, "new_no": None})
            try:
                ranges = line.split("@@")[1].strip()
                old_part, new_part = ranges.split(" ")
                old_no = int(old_part.split(",")[0].lstrip("-"))
                new_no = int(new_part.split(",")[0].lstrip("+"))
            except (ValueError, IndexError):
                pass
            continue
        if line.startswith("+"):
            rows.append({"type": "add", "text": line[1:], "old_no": None, "new_no": new_no})
            new_no += 1
        elif line.startswith("-"):
            rows.append({"type": "remove", "text": line[1:], "old_no": old_no, "new_no": None})
            old_no += 1
        else:
            text = line[1:] if line.startswith(" ") else line
            rows.append({"type": "context", "text": text, "old_no": old_no, "new_no": new_no})
            old_no += 1
            new_no += 1
    return rows


def render_unified_diff_html(rows):
    if not rows:
        return "<div class='diff-empty'>No line differences detected — the fix didn't change any lines.</div>"
    parts = ["<div class='diff-unified'>"]
    for row in rows:
        rtype = row["type"]
        if rtype == "hunk":
            parts.append(f"<div class='diff-row hunk'>{html.escape(row['text'])}</div>")
            continue
        text = html.escape(row["text"]) if row["text"] else "&nbsp;"
        marker = "+" if rtype == "add" else "-" if rtype == "remove" else "\u00a0"
        old_disp = row["old_no"] if row["old_no"] is not None else ""
        new_disp = row["new_no"] if row["new_no"] is not None else ""
        parts.append(
            f"<div class='diff-row {rtype}'>"
            f"<span class='diff-lineno'>{old_disp}</span>"
            f"<span class='diff-lineno'>{new_disp}</span>"
            f"<span class='diff-marker {rtype}'>{marker}</span>"
            f"<span class='diff-text'>{text}</span>"
            f"</div>"
        )
    parts.append("</div>")
    return "".join(parts)


def render_side_by_side_html(original: str, fixed: str):
    """Align original and fixed code into two columns using SequenceMatcher
    opcodes, so replaced/added/removed chunks land on matching rows."""
    original_lines = original.splitlines()
    fixed_lines = fixed.splitlines()
    matcher = difflib.SequenceMatcher(None, original_lines, fixed_lines)

    left_rows = []
    right_rows = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                left_rows.append(("context", original_lines[i1 + k]))
                right_rows.append(("context", fixed_lines[j1 + k]))
        elif tag == "replace":
            old_chunk = original_lines[i1:i2]
            new_chunk = fixed_lines[j1:j2]
            for k in range(max(len(old_chunk), len(new_chunk))):
                left_rows.append(("remove", old_chunk[k]) if k < len(old_chunk) else ("empty", ""))
                right_rows.append(("add", new_chunk[k]) if k < len(new_chunk) else ("empty", ""))
        elif tag == "delete":
            for k in range(i1, i2):
                left_rows.append(("remove", original_lines[k]))
                right_rows.append(("empty", ""))
        elif tag == "insert":
            for k in range(j1, j2):
                left_rows.append(("empty", ""))
                right_rows.append(("add", fixed_lines[k]))

    def render_col(rows):
        chunks = []
        for rtype, text in rows:
            safe_text = html.escape(text) if text else "&nbsp;"
            chunks.append(f"<div class='diff-sbs-row {rtype}'><span class='diff-text'>{safe_text}</span></div>")
        return "".join(chunks)

    return (
        "<div class='diff-sbs'>"
        "<div class='diff-sbs-col'>"
        "<div class='diff-sbs-header'>before</div>"
        f"{render_col(left_rows)}"
        "</div>"
        "<div class='diff-sbs-col'>"
        "<div class='diff-sbs-header'>after</div>"
        f"{render_col(right_rows)}"
        "</div>"
        "</div>"
    )


def render_diagnosis(diag: dict):
    """Render the current diagnosis: token readout, explanation, a real
    diff view (unified or side-by-side), export options, and the
    'explain simpler' follow-up. Reads from session state so it survives
    reruns triggered by other widgets (view toggle, restore, chat)."""
    st.markdown(
        f"""
        <div class='token-readout'>
            <span class='token-cursor'></span>
            tokens_remaining: {diag['tokens_remaining']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    fixed_code = diag.get("fixed_code")
    original_code = diag.get("original_code", "")
    lines_changed = len(fixed_code.splitlines()) if fixed_code else 0

    st.markdown(
        f"""
        <div class='patch-card'>
            <div class='patch-header'>
                <span class='patch-filename'>diagnosis.patch</span>
                <span class='patch-stats'><span class='add'>+{lines_changed}</span></span>
            </div>
            <div class='patch-body'>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(diag["response_text"])
    st.markdown("</div></div>", unsafe_allow_html=True)

    if fixed_code:
        st.markdown("<hr class='fade-divider'/>", unsafe_allow_html=True)
        st.markdown("#### Compare changes")
        view_mode = st.radio(
            "Diff view",
            ["Unified", "Side-by-side"],
            horizontal=True,
            key="diff_view_mode",
            label_visibility="collapsed",
        )
        if view_mode == "Unified":
            rows = compute_unified_diff_rows(original_code, fixed_code)
            st.markdown(render_unified_diff_html(rows), unsafe_allow_html=True)
        else:
            st.markdown(render_side_by_side_html(original_code, fixed_code), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        d_col1, d_col2, d_col3 = st.columns(3)
        with d_col1:
            st.download_button(
                "Download fixed code",
                data=fixed_code,
                file_name="fixed_code.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with d_col2:
            diff_text_lines = list(difflib.unified_diff(
                original_code.splitlines(),
                fixed_code.splitlines(),
                fromfile="before",
                tofile="after",
                lineterm="",
            ))
            st.download_button(
                "Download .diff",
                data="\n".join(diff_text_lines),
                file_name="fix.diff",
                mime="text/plain",
                use_container_width=True,
            )
        with d_col3:
            copy_id = "copy-btn-" + uuid.uuid4().hex
            copy_html = f"""
            <button id='{copy_id}' style='background:var(--panel-raised);color:#E9EAEE;border:1px solid var(--border-strong);border-radius:10px;padding:11px 10px;cursor:pointer;width:100%;font-weight:600;font-family:"Space Grotesk", sans-serif;'>Copy code</button>
            <script>
            const btn = document.getElementById('{copy_id}');
            if (btn) {{
              btn.addEventListener('click', async () => {{
                try {{
                  await navigator.clipboard.writeText({json.dumps(fixed_code)});
                  btn.innerText = 'Copied';
                  setTimeout(() => {{ btn.innerText = 'Copy code'; }}, 2000);
                }} catch(e) {{
                  btn.innerText = 'Copy failed';
                  setTimeout(() => {{ btn.innerText = 'Copy code'; }}, 2000);
                }}
              }});
            }}
            </script>
            """
            st.markdown(copy_html, unsafe_allow_html=True)
    else:
        st.markdown(
            "<div style='color:var(--text-muted); font-size:13px; font-style:italic;'>"
            "No fenced code block found in the response, so there's nothing to diff — "
            "the explanation above is all that came back."
            "</div>",
            unsafe_allow_html=True,
        )

    with st.expander("Explain like I'm new to coding"):
        if st.button("Simplify this explanation", key=f"simplify_{diag['id']}"):
            if not groq_client:
                st.error("GROQ_API_KEY is missing, so I can't generate a simpler explanation.")
            else:
                with st.spinner("Simplifying..."):
                    try:
                        simple = groq_client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "Rewrite the following programming explanation for a total "
                                        "beginner. Use everyday language and a short analogy. "
                                        "Keep it under 80 words."
                                    ),
                                },
                                {"role": "user", "content": diag["response_text"]},
                            ],
                            temperature=0.4,
                            max_tokens=200,
                        )
                        st.session_state["simple_explanation"] = simple.choices[0].message.content
                    except Exception as e:
                        st.error(f"Couldn't simplify that: {e}")
        if "simple_explanation" in st.session_state:
            st.info(st.session_state["simple_explanation"])


# ============================================================
#  HEADER
# ============================================================
st.markdown(
    """
    <div class='header-wrapper'>
        <div class='brand-title'>
            <div class='logo-badge'>🩹</div>
            <div>
                <h1 style='margin:0; font-size:26px;'>EduFix <span class="shine-text">AI</span></h1>
                <div style='color:#8B8F9B; font-size:13.5px; font-weight:500;'>Paste broken code. Get a real patch back.</div>
            </div>
        </div>
        <div class='status-badge'>
            <div class='pulse-dot'></div> backend connected
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

_total_diagnoses = len(st.session_state.history)
_tokens_spent = _total_diagnoses  # backend deducts exactly one token per successful run
_avg_time = (
    sum(h["elapsed"] for h in st.session_state.history) / _total_diagnoses
    if _total_diagnoses else 0.0
)

st.markdown(
    f"""
    <div class='stats-row'>
        <div class='stat-chip c-amber'>diagnoses this session<b>{_total_diagnoses}</b></div>
        <div class='stat-chip c-violet'>tokens spent<b>{_tokens_spent}</b></div>
        <div class='stat-chip c-teal'>avg response time<b>{_avg_time:.1f}s</b></div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
#  WORKSPACE COLUMNS
# ============================================================
left_col, right_col = st.columns([1.1, 1], gap="large")

# ---------------- LEFT: SOURCE INPUT ----------------
with left_col:
    st.markdown("### Your code")
    st.markdown("<div style='color:#8B8F9B; font-size:13.5px; margin-bottom:16px;'>Paste the broken snippet and, if you have one, the error it throws.</div>", unsafe_allow_html=True)

    ctrl_col1, ctrl_col2 = st.columns([1, 1.2])
    with ctrl_col1:
        language = st.selectbox("Language", ["Python", "JavaScript / React", "C++", "Java", "Rust", "SQL", "Go"], index=0)
    with ctrl_col2:
        sample_choice = st.selectbox("Try a sample bug", list(SAMPLE_BUGS.keys()))
        if sample_choice != "Select Sample...":
            sample_code, sample_err = SAMPLE_BUGS[sample_choice]
        else:
            sample_code, sample_err = "", ""

    code_val = sample_code if sample_code else ""
    err_val = sample_err if sample_err else ""

    lang_color = LANGUAGE_COLORS.get(language, "#F2A93B")
    st.markdown(
        f"""
        <div class="mac-header" style="border-top: 3px solid {lang_color};">
            <div class="mac-dots">
                <span class="mac-btn mac-close"></span>
                <span class="mac-btn mac-min"></span>
                <span class="mac-btn mac-max"></span>
                <span class="mac-title">source</span>
            </div>
            <div class="mac-status-tag" style="color:{lang_color}; background:{hex_to_rgba(lang_color, 0.16)}; border-color:{hex_to_rgba(lang_color, 0.4)};">{language.split()[0].upper()}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    broken_code_input = st.text_area(
        "Source Code Workspace",
        value=code_val,
        height=240,
        placeholder="Paste your source code here...",
        key="code_input_area",
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="mac-header">
            <div class="mac-dots">
                <span class="mac-btn mac-close"></span>
                <span class="mac-btn mac-min"></span>
                <span class="mac-btn mac-max"></span>
                <span class="mac-title">error.log</span>
            </div>
            <div class="mac-status-tag" style="color: var(--remove); background: var(--remove-bg); border-color: rgba(229, 103, 122, 0.3);">optional</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    error_input = st.text_area(
        "Traceback / Error Output (Optional)",
        value=err_val,
        height=90,
        placeholder="Paste compiler errors or logs here...",
        key="error_input_area",
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="mac-header">
            <div class="mac-dots">
                <span class="mac-btn mac-close"></span>
                <span class="mac-btn mac-min"></span>
                <span class="mac-btn mac-max"></span>
                <span class="mac-title">session</span>
            </div>
            <div class="mac-status-tag" style="color: #38bdf8; background: rgba(56, 189, 248, 0.1); border-color: rgba(56, 189, 248, 0.3);">supabase user</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    user_id_input = st.text_input(
        "User UUID (Supabase ID)",
        value=DEFAULT_USER_ID,
        key="user_id_input",
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Chat assistant settings"):
        st.markdown("<div style='color:var(--text-muted); font-size:12px; margin-bottom:10px;'>These only affect the Ask a question tab — the diagnosis backend uses its own fixed settings.</div>", unsafe_allow_html=True)
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
        with p_col2:
            max_tokens = st.slider("Max response length", min_value=256, max_value=2048, value=1024, step=64)

    st.markdown("<br>", unsafe_allow_html=True)
    analyze = st.button("Diagnose my code", use_container_width=True)

# ---------------- RIGHT: DIAGNOSIS / CHAT / HISTORY ----------------
with right_col:
    tab_diag, tab_chat, tab_history = st.tabs(["Diagnosis", "Ask a question", "History"])

    # ---------------- TAB: DIAGNOSIS ----------------
    with tab_diag:
        if analyze:
            if not broken_code_input or not broken_code_input.strip():
                st.warning("Paste some code before running a diagnosis.")
            else:
                with st.spinner("Requesting a fix from the backend..."):
                    try:
                        combined_snippet = broken_code_input
                        if error_input and error_input.strip():
                            combined_snippet += f"\n\n# Error message:\n{error_input.strip()}"
                        combined_snippet = f"# Language: {language}\n\n{combined_snippet}"

                        payload = {
                            "user_id": user_id_input.strip(),
                            "code_snippet": combined_snippet,
                        }

                        start_time = time.perf_counter()
                        response = requests.post(BACKEND_URL, json=payload, timeout=60)
                        elapsed = time.perf_counter() - start_time

                        if response.status_code == 200:
                            res_data = response.json()
                            response_text = res_data.get("fixed_code", "")
                            tokens_remaining = res_data.get("Tokens_remaining", 0)
                            fixed_code = extract_fixed_code(response_text)
                            diagnosis_id = uuid.uuid4().hex

                            st.session_state.current_diagnosis = {
                                "id": diagnosis_id,
                                "response_text": response_text,
                                "fixed_code": fixed_code,
                                "tokens_remaining": tokens_remaining,
                                "original_code": broken_code_input,
                                "language": language,
                            }
                            st.session_state.pop("simple_explanation", None)

                            st.session_state.history.insert(0, {
                                "id": diagnosis_id,
                                "timestamp": datetime.now().strftime("%H:%M:%S"),
                                "language": language,
                                "code_preview": broken_code_input.strip()[:120],
                                "code_full": broken_code_input,
                                "error_full": error_input,
                                "response_text": response_text,
                                "fixed_code": fixed_code,
                                "tokens_remaining": tokens_remaining,
                                "elapsed": elapsed,
                            })
                            st.session_state.history = st.session_state.history[:20]

                            try:
                                st.toast("Fix ready", icon="✨")
                            except Exception:
                                pass

                        elif response.status_code == 400:
                            st.error("Out of tokens. Top up your balance in Supabase to keep going.")
                        elif response.status_code == 404:
                            st.error(f"User ID (`{user_id_input}`) isn't in the Supabase `Profiles` table.")
                        else:
                            st.error(f"Backend error ({response.status_code}): {response.text}")

                    except requests.exceptions.ConnectionError:
                        st.error("Can't reach the backend. Make sure it's running locally at `http://127.0.0.1:8000`.")
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")

        diag = st.session_state.current_diagnosis
        if diag:
            render_diagnosis(diag)
        elif not analyze:
            st.markdown("### Waiting for code")
            st.markdown(
                "<div style='color:var(--text-muted); font-size:13.5px; margin-bottom:8px;'>"
                "Paste code on the left and click <b>Diagnose my code</b>. You'll get:"
                "</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<div class='thinking-dots' style='margin-bottom:20px;'><span></span><span></span><span></span></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                """
                <div class='info-card'><h4>One token spent</h4><p>Checked and deducted from your Supabase balance before the request runs.</p></div>
                <div class='info-card'><h4>What's actually wrong</h4><p>A plain-language explanation of the bug, not just a repeated error message.</p></div>
                <div class='info-card'><h4>A real diff</h4><p>Line-by-line before/after, viewable unified or side-by-side.</p></div>
                <div class='info-card'><h4>A working patch</h4><p>Corrected code you can copy, download, or turn into a .diff file.</p></div>
                """,
                unsafe_allow_html=True,
            )

    # ---------------- TAB: ASK A QUESTION ----------------
    with tab_chat:
        st.markdown("### Ask a question")
        st.markdown(
            "<div style='color:#8B8F9B; font-size:13.5px; margin-bottom:15px;'>"
            "Ask about the code in your workspace, or anything else CS-related."
            "</div>",
            unsafe_allow_html=True
        )

        chat_container = st.container()
        with chat_container:
            if not st.session_state.messages:
                st.info("Run a diagnosis or ask a question about your code to get started.")
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Ask a follow-up question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            if not groq_client:
                                st.error("GROQ_API_KEY is missing from Streamlit secrets. Add it to `.streamlit/secrets.toml`.")
                            else:
                                code_context = broken_code_input.strip() if broken_code_input else "No code loaded."
                                sys_prompt = (
                                    "You are a friendly, precise computer science tutor for EduFix AI. "
                                    f"Language context: {language}.\n\n"
                                    "Current code in the user's workspace:\n"
                                    "```\n"
                                    f"{code_context}\n"
                                    "```\n\n"
                                    "Answer clearly and concisely, with code examples when useful."
                                )
                                api_messages = [{"role": "system", "content": sys_prompt}]
                                for m in st.session_state.messages:
                                    api_messages.append({"role": m["role"], "content": m["content"]})

                                response = groq_client.chat.completions.create(
                                    model="llama-3.1-8b-instant",
                                    messages=api_messages,
                                    temperature=float(temp),
                                    max_tokens=int(max_tokens),
                                )
                                ai_reply = response.choices[0].message.content
                                st.markdown(ai_reply)
                                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                        except Exception as e:
                            st.error(f"Assistant error: {e}")

            st.rerun()

    # ---------------- TAB: HISTORY ----------------
    with tab_history:
        if not st.session_state.history:
            st.markdown(
                "<div style='color:var(--text-muted); font-size:13.5px;'>"
                "Nothing here yet — run a diagnosis and it'll show up in this list."
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            for entry in st.session_state.history:
                preview = html.escape(entry["code_preview"])
                ellipsis = "…" if len(entry["code_preview"]) >= 120 else ""
                entry_color = LANGUAGE_COLORS.get(entry["language"], "#F2A93B")
                st.markdown(
                    f"""
                    <div class='history-card' style="border-left: 3px solid {entry_color};">
                        <div class='history-meta'>
                            <span class='history-lang' style="color:{entry_color}; background:{hex_to_rgba(entry_color, 0.16)};">{html.escape(entry["language"])}</span>
                            <span class='history-time'>{entry["timestamp"]} · {entry["elapsed"]:.1f}s · {entry["tokens_remaining"]} left</span>
                        </div>
                        <div class='history-preview'>{preview}{ellipsis}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Restore to workspace", key=f"restore_{entry['id']}", use_container_width=True):
                    st.session_state["_restore_code"] = entry["code_full"]
                    st.session_state["_restore_error"] = entry["error_full"]
                    st.rerun()

# ============================================================
#  FOOTER
# ============================================================
st.markdown("<div class='footer'>Built by an 18-year-old founder · EduFix AI</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'><a href='https://discord.gg' target='_blank' style='color: var(--accent); text-decoration: none; font-weight: 600; font-size: 13px;'>Join the EduFix Discord →</a></p>", unsafe_allow_html=True)
