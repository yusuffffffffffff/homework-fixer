"""
EduFix AI | Code Studio  (premium single-file edition)

Run:  streamlit run app.py
Env:  GROQ_API_KEY (optional, enables offline fallback + chat tutor)

Backend contract (POST BACKEND_URL, JSON):
  request : {"user_id": str, "code": str, "error": str, "language": str}
  response: {"fixed_code": str, "explanation": str | {"what": str, "why": str, "how": str}}
  Any of these keys are also accepted for the code: corrected_code, code, fix
"""

import difflib
import html
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st

try:
    from groq import Groq
except ImportError:  # groq is optional
    Groq = None

# ============================================================
#  PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="EduFix AI | Code Studio",
    page_icon="🩹",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DEFAULT_BACKEND_URL = "http://127.0.0.1:8000/fix-code"
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"
HISTORY_FILE = Path(__file__).with_name("edufix_history.json")
GROQ_MODEL = "llama-3.3-70b-versatile"

LANGUAGES = ["auto", "python", "javascript", "typescript", "java", "c", "cpp", "go", "rust", "sql", "bash"]
LANG_EXT = {
    "python": "py", "javascript": "js", "typescript": "ts", "java": "java", "c": "c",
    "cpp": "cpp", "go": "go", "rust": "rs", "sql": "sql", "bash": "sh",
}

# ============================================================
#  SESSION STATE
# ============================================================
def load_history() -> list:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_history(items: list) -> None:
    try:
        HISTORY_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")
    except OSError:
        pass


defaults = {
    "messages": [],
    "history": load_history(),
    "current_diagnosis": None,
    "undo_code": None,
    "backend_url": DEFAULT_BACKEND_URL,
    "groq_key": os.getenv("GROQ_API_KEY", ""),
    "reduced_motion": False,
    "history_query": "",
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# Apply deferred edits to widgets BEFORE they are instantiated.
for src, dst in (("_restore_code", "code_input_area"), ("_restore_error", "error_input_area"),
                 ("_restore_lang", "lang_select")):
    if src in st.session_state:
        st.session_state[dst] = st.session_state.pop(src)

# Shareable link: ?fix=<id>
shared_id = st.query_params.get("fix")
if shared_id and not st.session_state.current_diagnosis:
    match = next((h for h in st.session_state.history if h["id"] == shared_id), None)
    if match:
        st.session_state.current_diagnosis = match

# ============================================================
#  DESIGN SYSTEM
# ============================================================
MOTION_OVERRIDE = """
.aurora-bg, .aurora-blob, .shine-text, .pulse-dot, .patch-card, .skeleton { animation: none !important; }
""" if st.session_state.reduced_motion else ""

CUSTOM_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {{
  --bg:#0A0B0F; --panel:#131519; --panel-raised:#191C22;
  --border:rgba(255,255,255,.08); --border-strong:rgba(255,255,255,.16);
  --text-main:#E9EAEE; --text-muted:#8B8F9B;
  --add:#34D399; --add-bg:rgba(52,211,153,.12); --add-strong:rgba(52,211,153,.35);
  --remove:#F0525F; --remove-bg:rgba(240,82,95,.12); --remove-strong:rgba(240,82,95,.38);
  --accent:#F2A93B; --accent-dim:rgba(242,169,59,.16);
  --teal:#22D3EE; --pink:#EC4899; --violet:#8B5CF6; --blue:#38BDF8;
  --shadow-soft:0 12px 32px rgba(0,0,0,.35);
}}
* {{ box-sizing:border-box; }}
html, body, [class*="css"] {{ font-family:'Inter',-apple-system,sans-serif !important; letter-spacing:-.01em; }}
html, body {{ background:var(--bg); }}
[data-testid="stAppViewContainer"] {{ background:transparent; color:var(--text-main); }}
.stApp {{ background:transparent; }}
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background:var(--bg); }}
::-webkit-scrollbar-thumb {{ background:var(--border-strong); border-radius:10px; }}
::-webkit-scrollbar-thumb:hover {{ background:var(--accent); }}

/* Ambient background */
.aurora-bg {{ position:fixed; inset:0; overflow:hidden; z-index:0; pointer-events:none; animation:hue-shift 90s linear infinite; }}
.aurora-blob {{ position:absolute; border-radius:50%; filter:blur(100px); opacity:.34; mix-blend-mode:screen; will-change:transform; }}
.blob-1 {{ width:520px;height:520px;background:var(--accent);top:-160px;left:-100px;animation:drift-a 34s ease-in-out infinite; }}
.blob-2 {{ width:460px;height:460px;background:var(--teal);top:30%;right:-160px;animation:drift-b 40s ease-in-out infinite; }}
.blob-3 {{ width:380px;height:380px;background:var(--violet);bottom:-180px;left:28%;opacity:.26;animation:drift-c 46s ease-in-out infinite; }}
.blob-4 {{ width:340px;height:340px;background:var(--pink);top:55%;left:42%;opacity:.2;animation:drift-d 52s ease-in-out infinite; }}
@keyframes drift-a {{ 0%,100%{{transform:translate(0,0) scale(1)}} 33%{{transform:translate(60px,-40px) scale(1.08)}} 66%{{transform:translate(-30px,30px) scale(.94)}} }}
@keyframes drift-b {{ 0%,100%{{transform:translate(0,0) scale(1)}} 50%{{transform:translate(-70px,40px) scale(1.1)}} }}
@keyframes drift-c {{ 0%,100%{{transform:translate(0,0) scale(1)}} 40%{{transform:translate(50px,-20px) scale(1.05)}} 70%{{transform:translate(-40px,10px) scale(.96)}} }}
@keyframes drift-d {{ 0%,100%{{transform:translate(0,0) scale(1)}} 50%{{transform:translate(45px,35px) scale(1.12)}} }}
@keyframes hue-shift {{ from{{filter:hue-rotate(0)}} to{{filter:hue-rotate(360deg)}} }}
.grain-overlay {{ position:fixed; inset:0; z-index:1; opacity:.035; pointer-events:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }}
@media (prefers-reduced-motion: reduce) {{
  .aurora-bg, .aurora-blob, .shine-text, .pulse-dot, .patch-card, .skeleton {{ animation:none !important; }}
}}
{MOTION_OVERRIDE}

h1,h2,h3,h4 {{ font-family:'Space Grotesk',sans-serif !important; color:#fff !important; font-weight:600 !important; letter-spacing:-.02em !important; }}
.shine-text {{ background:linear-gradient(100deg,var(--accent) 0%,var(--pink) 26%,var(--violet) 50%,var(--teal) 74%,var(--accent) 100%);
  background-size:300% auto; -webkit-background-clip:text; background-clip:text; color:transparent; animation:shine 9s linear infinite; }}
@keyframes shine {{ to{{background-position:-300% center}} }}

/* Tabs */
[data-testid="stTabPanel"] {{ background:var(--panel); padding:26px; border-radius:0 0 14px 14px; border:1px solid var(--border); border-top:none; margin-bottom:20px; }}
[data-testid="stTabs"] [data-baseweb="tab-list"] {{ gap:4px; background:var(--panel-raised); padding:6px; border-radius:14px 14px 0 0; border:1px solid var(--border); border-bottom:none; }}
[data-testid="stTabs"] [data-baseweb="tab"] {{ height:44px; border-radius:9px; color:var(--text-muted) !important; font-family:'Space Grotesk',sans-serif !important;
  font-weight:600 !important; font-size:13.5px !important; border:none !important; padding:0 22px !important; position:relative !important; transition:color .2s,background .2s !important; }}
[data-testid="stTabs"] [aria-selected="true"] {{ background:var(--panel) !important; color:#fff !important; }}
[data-testid="stTabs"] [aria-selected="true"]::after {{ content:""; position:absolute; left:14px; right:14px; bottom:0; height:2px; border-radius:2px; background:linear-gradient(90deg,var(--accent),var(--pink),var(--teal)); }}

/* Header */
.header-wrapper {{ display:flex; justify-content:space-between; align-items:center; padding:14px 0 20px; border-bottom:1px solid var(--border); margin-bottom:18px; flex-wrap:wrap; gap:12px; }}
.brand-title {{ display:flex; align-items:center; gap:16px; }}
.logo-badge {{ background:linear-gradient(135deg,var(--accent),var(--pink)); border:1px solid rgba(255,255,255,.25); box-shadow:0 0 26px rgba(242,169,59,.3);
  width:56px; height:56px; border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:26px; }}
.status-badge {{ border:1px solid; padding:7px 14px; border-radius:20px; font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:500; display:inline-flex; align-items:center; gap:8px; }}
.status-online {{ background:var(--add-bg); border-color:rgba(52,211,153,.3); color:var(--add); }}
.status-offline {{ background:var(--remove-bg); border-color:rgba(240,82,95,.3); color:var(--remove); }}
.status-fallback {{ background:var(--accent-dim); border-color:rgba(242,169,59,.3); color:var(--accent); }}
.pulse-dot {{ width:7px; height:7px; background:currentColor; border-radius:50%; animation:pulse 2s infinite; }}
@keyframes pulse {{ 0%{{box-shadow:0 0 0 0 rgba(255,255,255,.35)}} 70%{{box-shadow:0 0 0 7px rgba(255,255,255,0)}} 100%{{box-shadow:0 0 0 0 rgba(255,255,255,0)}} }}

/* Stats */
.stats-row {{ display:flex; gap:10px; margin:0 0 26px; flex-wrap:wrap; }}
.stat-chip {{ background:var(--panel-raised); border:1px solid var(--border); border-left:3px solid var(--border-strong); border-radius:10px; padding:10px 16px;
  font-family:'JetBrains Mono',monospace; font-size:11.5px; color:var(--text-muted); transition:border-color .15s,transform .15s; min-width:130px; }}
.stat-chip:hover {{ border-color:var(--border-strong); transform:translateY(-1px); }}
.stat-chip b {{ color:#fff; font-family:'Space Grotesk',sans-serif; font-size:15px; display:block; margin-top:3px; }}
.stat-chip.c-amber {{ border-left-color:var(--accent); }} .stat-chip.c-amber b {{ color:var(--accent); }}
.stat-chip.c-violet {{ border-left-color:var(--violet); }} .stat-chip.c-violet b {{ color:var(--violet); }}
.stat-chip.c-teal {{ border-left-color:var(--teal); }} .stat-chip.c-teal b {{ color:var(--teal); }}
.stat-chip.c-green {{ border-left-color:var(--add); }} .stat-chip.c-green b {{ color:var(--add); }}

/* Chat */
[data-testid="stChatMessage"] {{ background:var(--panel-raised) !important; border:1px solid var(--border) !important; border-radius:12px !important; padding:16px !important;
  margin-bottom:14px !important; position:relative !important; overflow:hidden !important; transition:border-color .15s; }}
[data-testid="stChatMessage"]:hover {{ border-color:var(--border-strong) !important; }}
[data-testid="stChatMessage"]::before {{ content:""; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,var(--teal),var(--accent)); }}

/* Buttons */
.stButton>button, .stFormSubmitButton>button {{ font-family:'Space Grotesk',sans-serif !important; background:linear-gradient(120deg,var(--accent) 0%,var(--pink) 100%) !important;
  background-size:180% 180% !important; background-position:0% 50% !important; color:#14110A !important; border:none !important; padding:13px 22px !important;
  font-weight:700 !important; font-size:14.5px !important; border-radius:10px !important; transition:transform .15s,box-shadow .15s,background-position .5s !important; }}
.stButton>button:hover, .stFormSubmitButton>button:hover {{ transform:translateY(-1px) !important; background-position:100% 50% !important;
  box-shadow:0 8px 26px rgba(236,72,153,.3),0 4px 18px rgba(242,169,59,.25) !important; }}
.stButton>button:focus-visible {{ outline:2px solid var(--teal) !important; outline-offset:2px !important; }}
.stButton>button[kind="secondary"] {{ background:var(--panel-raised) !important; color:var(--text-main) !important; border:1px solid var(--border-strong) !important; font-weight:600 !important; }}
.stButton>button[kind="secondary"]:hover {{ border-color:var(--accent) !important; box-shadow:none !important; }}
.stDownloadButton>button {{ font-family:'Space Grotesk',sans-serif !important; background:var(--panel-raised) !important; color:var(--text-main) !important;
  border:1px solid var(--border-strong) !important; border-radius:10px !important; font-weight:600 !important; transition:border-color .15s,transform .15s !important; }}
.stDownloadButton>button:hover {{ border-color:var(--accent) !important; transform:translateY(-1px) !important; }}

/* Inputs */
textarea, [data-baseweb="input"], [data-baseweb="select"] {{ background-color:#0E0F13 !important; color:var(--text-main) !important; border:1px solid var(--border) !important;
  border-radius:0 0 10px 10px !important; font-family:'JetBrains Mono',monospace !important; font-size:13.5px !important; }}
[data-baseweb="select"], [data-baseweb="input"] {{ border-radius:10px !important; }}
textarea:focus {{ border-color:var(--accent) !important; box-shadow:0 0 0 1px var(--accent) !important; }}
[data-testid="stChatInput"] {{ border-radius:12px !important; border:1px solid var(--border-strong) !important; background:var(--panel-raised) !important; }}
[data-testid="stRadio"] > div {{ flex-direction:row; gap:4px; background:var(--panel-raised); padding:4px; border-radius:10px; border:1px solid var(--border); width:fit-content; }}
[data-testid="stRadio"] label {{ padding:6px 14px !important; border-radius:7px !important; margin:0 !important; font-family:'Space Grotesk',sans-serif !important; font-size:12.5px !important; }}
[data-testid="stRadio"] label:has(input:checked) {{ background:linear-gradient(120deg,var(--accent),var(--pink)) !important; color:#14110A !important; }}

/* Terminal chrome */
.mac-header {{ background:var(--panel-raised); padding:10px 16px; border-radius:10px 10px 0 0; border:1px solid var(--border); border-bottom:none; display:flex;
  align-items:center; justify-content:space-between; margin-bottom:-1rem; position:relative; z-index:10; }}
.mac-dots {{ display:flex; align-items:center; gap:7px; }}
.mac-btn {{ width:10px; height:10px; border-radius:50%; display:inline-block; opacity:.6; }}
.mac-close {{ background:#ff5f56; }} .mac-min {{ background:#ffbd2e; }} .mac-max {{ background:#27c93f; }}
.mac-title {{ color:var(--text-muted); font-family:'JetBrains Mono',monospace; font-size:12px; }}
.mac-status-tag {{ font-family:'JetBrains Mono',monospace; font-size:10.5px; color:var(--accent); background:var(--accent-dim); padding:2px 8px; border-radius:5px; border:1px solid rgba(242,169,59,.25); }}
.mac-status-tag.err {{ color:var(--remove); background:var(--remove-bg); border-color:rgba(240,82,95,.3); }}

/* Patch card */
.patch-card {{ border:1px solid var(--border); border-radius:12px; overflow:hidden; margin-bottom:18px; animation:fadeIn .4s ease; transition:border-color .2s,box-shadow .2s; }}
.patch-card:hover {{ border-color:var(--border-strong); box-shadow:var(--shadow-soft); }}
@keyframes fadeIn {{ from{{opacity:0;transform:translateY(4px)}} to{{opacity:1;transform:translateY(0)}} }}
.patch-header {{ background:var(--panel-raised); border-bottom:1px solid var(--border); padding:12px 18px; display:flex; align-items:center; justify-content:space-between; position:relative; flex-wrap:wrap; gap:8px; }}
.patch-header::before {{ content:""; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,var(--accent),var(--pink),var(--violet),var(--teal)); }}
.patch-filename {{ font-family:'JetBrains Mono',monospace; font-size:13px; color:var(--text-main); }}
.patch-stats {{ font-family:'JetBrains Mono',monospace; font-size:12px; }}
.patch-stats .add {{ color:var(--add); }} .patch-stats .remove {{ color:var(--remove); margin-left:6px; }}
.patch-body {{ background:#0E0F13; padding:14px; }}

/* Diff: unified */
.diff-unified {{ font-family:'JetBrains Mono',monospace; font-size:12.5px; border-radius:10px; overflow:auto; border:1px solid var(--border); max-height:520px; }}
.diff-row {{ display:flex; align-items:flex-start; }}
.diff-row.add {{ background:var(--add-bg); }} .diff-row.remove {{ background:var(--remove-bg); }}
.diff-row.hunk {{ background:var(--panel-raised); color:var(--accent); padding:6px 12px; font-size:11.5px; }}
.diff-lineno {{ width:38px; text-align:right; padding:2px 8px 2px 0; color:var(--text-muted); user-select:none; flex-shrink:0; }}
.diff-marker {{ width:16px; text-align:center; flex-shrink:0; padding-top:2px; }}
.diff-marker.add {{ color:var(--add); }} .diff-marker.remove {{ color:var(--remove); }}
.diff-text {{ white-space:pre-wrap; word-break:break-word; padding:2px 12px 2px 0; }}
.diff-empty {{ color:var(--text-muted); font-size:13px; padding:14px; font-style:italic; }}
.diff-text mark.add {{ background:var(--add-strong); color:#fff; border-radius:3px; }}
.diff-text mark.remove {{ background:var(--remove-strong); color:#fff; border-radius:3px; }}

/* Diff: split */
.diff-split {{ display:grid; grid-template-columns:1fr 1fr; gap:0; font-family:'JetBrains Mono',monospace; font-size:12.5px; border:1px solid var(--border); border-radius:10px; overflow:auto; max-height:520px; }}
.diff-split .col-head {{ position:sticky; top:0; background:var(--panel-raised); padding:6px 12px; font-size:11px; color:var(--text-muted); text-transform:uppercase; letter-spacing:.08em; border-bottom:1px solid var(--border); z-index:2; }}
.diff-split .cell {{ display:flex; align-items:flex-start; min-height:22px; border-bottom:1px solid rgba(255,255,255,.03); }}
.diff-split .cell.left {{ border-right:1px solid var(--border); }}
.diff-split .cell.add {{ background:var(--add-bg); }} .diff-split .cell.remove {{ background:var(--remove-bg); }}
.diff-split .cell.empty {{ background:repeating-linear-gradient(45deg,transparent,transparent 6px,rgba(255,255,255,.02) 6px,rgba(255,255,255,.02) 12px); }}
@media (max-width: 900px) {{ .diff-split {{ grid-template-columns:1fr; }} .diff-split .col-head:nth-child(2) {{ display:none; }} }}

/* Explanation cards */
.explain-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:12px; margin-top:6px; }}
.explain-card {{ background:var(--panel-raised); border:1px solid var(--border); border-radius:12px; padding:16px 18px; animation:fadeIn .5s ease; }}
.explain-card h5 {{ margin:0 0 8px; font-family:'Space Grotesk',sans-serif; font-size:12px; letter-spacing:.1em; text-transform:uppercase; }}
.explain-card p {{ margin:0; color:var(--text-main); font-size:13.5px; line-height:1.55; }}
.explain-card.what h5 {{ color:var(--remove); }} .explain-card.why h5 {{ color:var(--accent); }} .explain-card.how h5 {{ color:var(--add); }}

/* Misc */
.line-badge {{ display:inline-block; font-family:'JetBrains Mono',monospace; font-size:11.5px; color:var(--remove); background:var(--remove-bg); border:1px solid rgba(240,82,95,.3); padding:3px 10px; border-radius:6px; margin:6px 0; }}
.lang-tag {{ display:inline-block; font-family:'JetBrains Mono',monospace; font-size:10.5px; padding:2px 8px; border-radius:5px; background:rgba(139,92,246,.16); color:var(--violet); border:1px solid rgba(139,92,246,.3); }}
.hist-card {{ background:var(--panel-raised); border:1px solid var(--border); border-radius:12px; padding:14px 16px; margin-bottom:6px; transition:border-color .15s; }}
.hist-card:hover {{ border-color:var(--border-strong); }}
.hist-meta {{ color:var(--text-muted); font-family:'JetBrains Mono',monospace; font-size:11.5px; display:flex; gap:12px; flex-wrap:wrap; }}
.skeleton {{ height:14px; border-radius:6px; background:linear-gradient(90deg,var(--panel-raised) 25%,#22262e 50%,var(--panel-raised) 75%); background-size:200% 100%; animation:shimmer 1.4s infinite; margin:8px 0; }}
@keyframes shimmer {{ from{{background-position:200% 0}} to{{background-position:-200% 0}} }}
.offline-banner {{ background:var(--remove-bg); border:1px solid rgba(240,82,95,.3); color:var(--text-main); border-radius:10px; padding:12px 16px; margin-bottom:16px; font-size:13.5px; }}
.kbd {{ font-family:'JetBrains Mono',monospace; font-size:11px; background:var(--panel-raised); border:1px solid var(--border-strong); border-radius:5px; padding:1px 6px; color:var(--text-muted); }}
.section-title {{ font-family:'Space Grotesk',sans-serif; font-size:13px; text-transform:uppercase; letter-spacing:.1em; color:var(--text-muted); margin:18px 0 8px; }}
"""
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)
st.markdown(
    '<div class="aurora-bg"><div class="aurora-blob blob-1"></div><div class="aurora-blob blob-2"></div>'
    '<div class="aurora-blob blob-3"></div><div class="aurora-blob blob-4"></div></div><div class="grain-overlay"></div>',
    unsafe_allow_html=True,
)


# ============================================================
#  HELPERS
# ============================================================
def detect_language(code: str) -> str:
    c = code.strip()
    if not c:
        return "python"
    if re.search(r"^\s*(def |import |from \w+ import|print\()", c, re.M):
        return "python"
    if re.search(r"\b(interface|type \w+ =|: (string|number|boolean))\b", c):
        return "typescript"
    if re.search(r"\b(const|let|=>|console\.log|function)\b", c):
        return "javascript"
    if re.search(r"\bpublic (static )?(class|void)\b|System\.out", c):
        return "java"
    if re.search(r"#include\s*<|int main\s*\(", c):
        return "cpp" if "std::" in c or "cout" in c else "c"
    if re.search(r"\bfunc main\(\)|package main", c):
        return "go"
    if re.search(r"\bfn main\(\)|let mut\b", c):
        return "rust"
    if re.search(r"\b(SELECT|INSERT|UPDATE|DELETE)\b.*\b(FROM|INTO|SET)\b", c, re.I):
        return "sql"
    if c.startswith("#!") or re.search(r"\becho\b|\$\{?\w+\}?", c):
        return "bash"
    return "python"


def parse_error_line(error_text: str) -> int | None:
    """Pull the most relevant line number out of a traceback / compiler error."""
    if not error_text:
        return None
    nums = re.findall(r"\bline (\d+)", error_text, re.I) or re.findall(r":(\d+):\d+", error_text)
    return int(nums[-1]) if nums else None


def parse_error_type(error_text: str) -> str:
    m = re.search(r"^(\w+(?:Error|Exception|Warning))\b", error_text.strip().splitlines()[-1] if error_text.strip() else "")
    return m.group(1) if m else "Error"


def diff_stats(original: str, fixed: str) -> tuple[int, int]:
    added = removed = 0
    for line in difflib.unified_diff(original.splitlines(), fixed.splitlines(), lineterm="", n=0):
        if line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return added, removed


def _inline_marks(a: str, b: str) -> tuple[str, str]:
    """Character-level highlighting inside a replaced line pair."""
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    left, right = [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            left.append(html.escape(a[i1:i2]))
            right.append(html.escape(b[j1:j2]))
        else:
            if i2 > i1:
                left.append(f'<mark class="remove">{html.escape(a[i1:i2])}</mark>')
            if j2 > j1:
                right.append(f'<mark class="add">{html.escape(b[j1:j2])}</mark>')
    return "".join(left), "".join(right)


def render_unified_diff(original: str, fixed: str) -> str:
    a, b = original.splitlines(), fixed.splitlines()
    if a == b:
        return '<div class="diff-empty">No changes detected.</div>'
    rows = []
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for group in sm.get_grouped_opcodes(n=3):
        i1, j1 = group[0][1], group[0][3]
        i2, j2 = group[-1][2], group[-1][4]
        rows.append(f'<div class="diff-row hunk">@@ -{i1 + 1},{i2 - i1} +{j1 + 1},{j2 - j1} @@</div>')
        for op, ai, aj, bi, bj in group:
            if op == "equal":
                for k in range(aj - ai):
                    rows.append(f'<div class="diff-row"><span class="diff-lineno">{ai + k + 1}</span><span class="diff-lineno">{bi + k + 1}</span>'
                                f'<span class="diff-marker"> </span><span class="diff-text">{html.escape(a[ai + k])}</span></div>')
            elif op == "replace" and (aj - ai) == (bj - bi):
                for k in range(aj - ai):
                    l, r = _inline_marks(a[ai + k], b[bi + k])
                    rows.append(f'<div class="diff-row remove"><span class="diff-lineno">{ai + k + 1}</span><span class="diff-lineno"></span>'
                                f'<span class="diff-marker remove">-</span><span class="diff-text">{l}</span></div>')
                    rows.append(f'<div class="diff-row add"><span class="diff-lineno"></span><span class="diff-lineno">{bi + k + 1}</span>'
                                f'<span class="diff-marker add">+</span><span class="diff-text">{r}</span></div>')
            else:
                for k in range(ai, aj):
                    rows.append(f'<div class="diff-row remove"><span class="diff-lineno">{k + 1}</span><span class="diff-lineno"></span>'
                                f'<span class="diff-marker remove">-</span><span class="diff-text">{html.escape(a[k])}</span></div>')
                for k in range(bi, bj):
                    rows.append(f'<div class="diff-row add"><span class="diff-lineno"></span><span class="diff-lineno">{k + 1}</span>'
                                f'<span class="diff-marker add">+</span><span class="diff-text">{html.escape(b[k])}</span></div>')
    return f'<div class="diff-unified">{"".join(rows)}</div>'


def render_split_diff(original: str, fixed: str) -> str:
    a, b = original.splitlines(), fixed.splitlines()
    if a == b:
        return '<div class="diff-empty">No changes detected.</div>'
    cells = ['<div class="col-head">Original</div>', '<div class="col-head">Fixed</div>']

    def cell(side, cls, no, text):
        return (f'<div class="cell {side} {cls}"><span class="diff-lineno">{no}</span>'
                f'<span class="diff-text">{text}</span></div>')

    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                cells.append(cell("left", "", i1 + k + 1, html.escape(a[i1 + k])))
                cells.append(cell("right", "", j1 + k + 1, html.escape(b[j1 + k])))
        else:
            n = max(i2 - i1, j2 - j1)
            for k in range(n):
                has_l, has_r = k < (i2 - i1), k < (j2 - j1)
                if has_l and has_r:
                    l, r = _inline_marks(a[i1 + k], b[j1 + k])
                else:
                    l = html.escape(a[i1 + k]) if has_l else ""
                    r = html.escape(b[j1 + k]) if has_r else ""
                cells.append(cell("left", "remove" if has_l else "empty", i1 + k + 1 if has_l else "", l))
                cells.append(cell("right", "add" if has_r else "empty", j1 + k + 1 if has_r else "", r))
    return f'<div class="diff-split">{"".join(cells)}</div>'


def make_patch_text(original: str, fixed: str, filename: str) -> str:
    return "\n".join(difflib.unified_diff(original.splitlines(), fixed.splitlines(),
                                          fromfile=f"a/{filename}", tofile=f"b/{filename}", lineterm="")) + "\n"


@st.cache_data(ttl=15, show_spinner=False)
def backend_online(url: str) -> bool:
    try:
        base = url.rsplit("/", 1)[0]
        requests.get(base + "/docs", timeout=1.5)
        return True
    except requests.RequestException:
        return False


def normalize_response(data, original_code: str) -> dict:
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            data = {"fixed_code": data}
    fixed = next((data.get(k) for k in ("fixed_code", "corrected_code", "code", "fix") if data.get(k)), original_code)
    # Strip accidental markdown fences
    fixed = re.sub(r"^```[\w+-]*\n|\n```$", "", str(fixed).strip())
    exp = data.get("explanation") or {}
    if isinstance(exp, str):
        exp = {"what": data.get("what_was_wrong", ""), "why": data.get("why_it_failed", ""), "how": exp}
    return {
        "fixed_code": fixed,
        "what": exp.get("what") or data.get("what_was_wrong", ""),
        "why": exp.get("why") or data.get("why_it_failed", ""),
        "how": exp.get("how") or data.get("how_fixed", "") or data.get("message", ""),
    }


def call_backend(code: str, error: str, language: str) -> dict:
    resp = requests.post(
        st.session_state.backend_url,
        json={"user_id": DEFAULT_USER_ID, "code": code, "error": error, "language": language},
        timeout=60,
    )
    resp.raise_for_status()
    return normalize_response(resp.json(), code)


def call_groq(code: str, error: str, language: str) -> dict:
    if not (Groq and st.session_state.groq_key):
        raise RuntimeError("Groq fallback unavailable: install `groq` and set a GROQ_API_KEY in Settings.")
    client = Groq(api_key=st.session_state.groq_key)
    prompt = (
        "You are a patient programming tutor. Fix the code and explain it for a learner.\n"
        'Respond ONLY with JSON: {"fixed_code": str, "what_was_wrong": str, "why_it_failed": str, "how_fixed": str}\n'
        f"Language: {language}\n\nCODE:\n{code}\n\nERROR:\n{error or '(none provided)'}"
    )
    out = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return normalize_response(out.choices[0].message.content, code)


def run_fix(code: str, error: str, language: str) -> tuple[dict, str]:
    """Returns (result, source) where source is 'backend' or 'groq'."""
    try:
        return call_backend(code, error, language), "backend"
    except requests.RequestException:
        backend_online.clear()
        return call_groq(code, error, language), "groq"


def push_history(entry: dict) -> None:
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:100]
    save_history(st.session_state.history)


# ============================================================
#  HEADER
# ============================================================
online = backend_online(st.session_state.backend_url)
has_groq = bool(Groq and st.session_state.groq_key)
if online:
    status_html = '<div class="status-badge status-online"><span class="pulse-dot"></span>backend online</div>'
elif has_groq:
    status_html = '<div class="status-badge status-fallback"><span class="pulse-dot"></span>backend offline · groq fallback</div>'
else:
    status_html = '<div class="status-badge status-offline"><span class="pulse-dot"></span>backend offline</div>'

st.markdown(f"""
<div class="header-wrapper">
  <div class="brand-title">
    <div class="logo-badge">🩹</div>
    <div>
      <h1 style="margin:0;font-size:28px;">EduFix <span class="shine-text">AI</span></h1>
      <div style="color:var(--text-muted);font-size:13px;margin-top:2px;">Broken code in. A patch you understand out.</div>
    </div>
  </div>
  {status_html}
</div>
""", unsafe_allow_html=True)

hist = st.session_state.history
total_added = sum(h.get("added", 0) for h in hist)
total_removed = sum(h.get("removed", 0) for h in hist)
top_lang = max((h.get("language", "python") for h in hist), key=[h.get("language") for h in hist].count, default="none")
st.markdown(f"""
<div class="stats-row">
  <div class="stat-chip c-amber">fixes<b>{len(hist)}</b></div>
  <div class="stat-chip c-green">lines added<b>+{total_added}</b></div>
  <div class="stat-chip c-violet">lines removed<b>-{total_removed}</b></div>
  <div class="stat-chip c-teal">top language<b>{html.escape(top_lang)}</b></div>
  <div class="stat-chip">shortcut<b><span class="kbd">Ctrl</span> + <span class="kbd">Enter</span></b></div>
</div>
""", unsafe_allow_html=True)

if not online and not has_groq:
    st.markdown('<div class="offline-banner">⚠️ Backend unreachable and no Groq key configured. Start the FastAPI server or add a key in <b>Settings</b>.</div>',
                unsafe_allow_html=True)

# ============================================================
#  TABS
# ============================================================
tab_studio, tab_history, tab_chat, tab_settings = st.tabs(["🩹 Studio", "🕘 History", "💬 Tutor", "⚙️ Settings"])

# ------------------------------------------------------------ STUDIO
with tab_studio:
    with st.form("fix_form", clear_on_submit=False):
        col_code, col_err = st.columns([3, 2], gap="large")
        with col_code:
            lang_choice = st.selectbox("Language", LANGUAGES, key="lang_select", label_visibility="collapsed")
            st.markdown("""<div class="mac-header"><div class="mac-dots"><span class="mac-btn mac-close"></span><span class="mac-btn mac-min"></span>
              <span class="mac-btn mac-max"></span><span class="mac-title" style="margin-left:8px">main · workspace</span></div>
              <span class="mac-status-tag">EDITOR</span></div>""", unsafe_allow_html=True)
            code_input = st.text_area("Code", key="code_input_area", height=340, label_visibility="collapsed",
                                      placeholder="# Paste your broken code here")
        with col_err:
            st.markdown('<div style="height:38px"></div>', unsafe_allow_html=True)
            st.markdown("""<div class="mac-header"><div class="mac-dots"><span class="mac-btn mac-close"></span><span class="mac-btn mac-min"></span>
              <span class="mac-btn mac-max"></span><span class="mac-title" style="margin-left:8px">stderr</span></div>
              <span class="mac-status-tag err">TRACEBACK</span></div>""", unsafe_allow_html=True)
            error_input = st.text_area("Error", key="error_input_area", height=340, label_visibility="collapsed",
                                       placeholder="Paste the traceback or error output (optional but helps a lot)")
        submitted = st.form_submit_button("🩹  Diagnose & Patch", use_container_width=True)

    err_line = parse_error_line(error_input)
    if err_line and code_input:
        lines = code_input.splitlines()
        snippet = html.escape(lines[err_line - 1].strip()) if 0 < err_line <= len(lines) else ""
        st.markdown(f'<span class="line-badge">↳ {html.escape(parse_error_type(error_input))} points to line {err_line}'
                    f'{": <code>" + snippet + "</code>" if snippet else ""}</span>', unsafe_allow_html=True)

    if submitted:
        if not code_input.strip():
            st.warning("Paste some code first.")
        else:
            language = detect_language(code_input) if lang_choice == "auto" else lang_choice
            placeholder = st.empty()
            placeholder.markdown('<div class="skeleton" style="width:60%"></div><div class="skeleton"></div><div class="skeleton" style="width:85%"></div>',
                                 unsafe_allow_html=True)
            try:
                result, source = run_fix(code_input, error_input, language)
                added, removed = diff_stats(code_input, result["fixed_code"])
                entry = {
                    "id": uuid.uuid4().hex[:10],
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "language": language,
                    "error_type": parse_error_type(error_input),
                    "original": code_input,
                    "error": error_input,
                    "source": source,
                    "added": added,
                    "removed": removed,
                    **result,
                }
                st.session_state.current_diagnosis = entry
                push_history(entry)
                st.query_params["fix"] = entry["id"]
                placeholder.empty()
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                placeholder.empty()
                st.error(f"Fix failed: {exc}")

    diag = st.session_state.current_diagnosis
    if diag:
        filename = f"main.{LANG_EXT.get(diag['language'], 'txt')}"
        st.markdown(f"""
        <div class="patch-card"><div class="patch-header">
          <span class="patch-filename">{filename} <span class="lang-tag">{html.escape(diag['language'])}</span>
            <span class="lang-tag" style="margin-left:6px">{'via ' + html.escape(diag.get('source', 'backend'))}</span></span>
          <span class="patch-stats"><span class="add">+{diag['added']}</span><span class="remove">-{diag['removed']}</span></span>
        </div></div>""", unsafe_allow_html=True)

        view = st.radio("View", ["Unified", "Split", "Fixed code"], horizontal=True, label_visibility="collapsed", key="diff_view")
        if view == "Unified":
            st.markdown(render_unified_diff(diag["original"], diag["fixed_code"]), unsafe_allow_html=True)
        elif view == "Split":
            st.markdown(render_split_diff(diag["original"], diag["fixed_code"]), unsafe_allow_html=True)
        else:
            st.code(diag["fixed_code"], language=diag["language"], line_numbers=True)

        b1, b2, b3, b4 = st.columns(4)
        with b1:
            if st.button("✅ Apply to workspace", use_container_width=True):
                st.session_state.undo_code = st.session_state.get("code_input_area", "")
                st.session_state["_restore_code"] = diag["fixed_code"]
                st.rerun()
        with b2:
            if st.button("↩️ Undo apply", use_container_width=True, type="secondary", disabled=st.session_state.undo_code is None):
                st.session_state["_restore_code"] = st.session_state.undo_code
                st.session_state.undo_code = None
                st.rerun()
        with b3:
            st.download_button("⬇️ Download .patch", make_patch_text(diag["original"], diag["fixed_code"], filename),
                               file_name=f"edufix-{diag['id']}.patch", mime="text/x-diff", use_container_width=True)
        with b4:
            md = f"### EduFix patch `{filename}`\n\n**What:** {diag['what']}\n\n**Why:** {diag['why']}\n\n**How:** {diag['how']}\n\n```{diag['language']}\n{diag['fixed_code']}\n```"
            st.download_button("📋 Export Markdown", md, file_name=f"edufix-{diag['id']}.md", mime="text/markdown", use_container_width=True)

        if any(diag.get(k) for k in ("what", "why", "how")):
            st.markdown('<div class="section-title">Explanation</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="explain-grid">
              <div class="explain-card what"><h5>What was wrong</h5><p>{html.escape(diag.get('what') or '—')}</p></div>
              <div class="explain-card why"><h5>Why it failed</h5><p>{html.escape(diag.get('why') or '—')}</p></div>
              <div class="explain-card how"><h5>How it's fixed</h5><p>{html.escape(diag.get('how') or '—')}</p></div>
            </div>""", unsafe_allow_html=True)

        st.caption(f"Shareable link: add `?fix={diag['id']}` to this page's URL (works on this machine's history).")

# ------------------------------------------------------------ HISTORY
with tab_history:
    hc1, hc2 = st.columns([4, 1])
    with hc1:
        st.text_input("Search", key="history_query", placeholder="Search by error type, language or code…", label_visibility="collapsed")
    with hc2:
        if st.button("🗑 Clear all", use_container_width=True, type="secondary", disabled=not st.session_state.history):
            st.session_state.history = []
            save_history([])
            st.rerun()

    q = st.session_state.history_query.lower().strip()
    items = [h for h in st.session_state.history if not q or q in json.dumps(h).lower()]
    if not items:
        st.markdown('<div class="diff-empty">No fixes yet. Your patches will show up here.</div>', unsafe_allow_html=True)
    for h in items:
        st.markdown(f"""
        <div class="hist-card">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
            <div><b style="font-family:'Space Grotesk'">{html.escape(h.get('error_type', 'Error'))}</b>
              <span class="lang-tag" style="margin-left:8px">{html.escape(h.get('language', ''))}</span></div>
            <span class="patch-stats"><span class="add">+{h.get('added', 0)}</span><span class="remove">-{h.get('removed', 0)}</span></span>
          </div>
          <div class="hist-meta" style="margin-top:6px"><span>{h['timestamp'].replace('T', ' ')}</span><span>#{h['id']}</span><span>via {h.get('source', 'backend')}</span></div>
        </div>""", unsafe_allow_html=True)
        c1, c2, c3, _ = st.columns([1, 1, 1, 3])
        if c1.button("Open", key=f"open_{h['id']}", use_container_width=True, type="secondary"):
            st.session_state.current_diagnosis = h
            st.query_params["fix"] = h["id"]
            st.rerun()
        if c2.button("Restore", key=f"restore_{h['id']}", use_container_width=True, type="secondary"):
            st.session_state["_restore_code"] = h["original"]
            st.session_state["_restore_error"] = h["error"]
            st.session_state["_restore_lang"] = h["language"] if h["language"] in LANGUAGES else "auto"
            st.session_state.current_diagnosis = h
            st.rerun()
        if c3.button("Delete", key=f"del_{h['id']}", use_container_width=True, type="secondary"):
            st.session_state.history = [x for x in st.session_state.history if x["id"] != h["id"]]
            save_history(st.session_state.history)
            if st.session_state.current_diagnosis and st.session_state.current_diagnosis["id"] == h["id"]:
                st.session_state.current_diagnosis = None
            st.rerun()

# ------------------------------------------------------------ TUTOR CHAT
with tab_chat:
    diag = st.session_state.current_diagnosis
    if not has_groq:
        st.info("Add a Groq API key in Settings to enable the tutor chat.")
    elif not diag:
        st.info("Run a fix first, then ask follow-up questions about it here.")
    else:
        st.caption(f"Discussing fix #{diag['id']} ({diag['language']}, {diag['error_type']})")
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
        if prompt := st.chat_input("Ask why this fix works, request an alternative, or ask for a quiz…"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                try:
                    client = Groq(api_key=st.session_state.groq_key)
                    system = (
                        "You are a friendly programming tutor. Keep answers short and concrete. Context:\n"
                        f"ORIGINAL:\n{diag['original']}\n\nERROR:\n{diag['error']}\n\nFIXED:\n{diag['fixed_code']}\n\n"
                        f"WHAT: {diag['what']}\nWHY: {diag['why']}\nHOW: {diag['how']}"
                    )
                    stream = client.chat.completions.create(
                        model=GROQ_MODEL, stream=True, temperature=0.4,
                        messages=[{"role": "system", "content": system}, *st.session_state.messages[-10:]],
                    )
                    answer = st.write_stream(chunk.choices[0].delta.content or "" for chunk in stream)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Tutor unavailable: {exc}")
        if st.session_state.messages and st.button("Clear conversation", type="secondary"):
            st.session_state.messages = []
            st.rerun()

# ------------------------------------------------------------ SETTINGS
with tab_settings:
    s1, s2 = st.columns(2)
    with s1:
        st.text_input("Backend URL", key="backend_url")
        st.text_input("Groq API key (fallback + tutor)", key="groq_key", type="password")
    with s2:
        st.toggle("Reduce motion (disable aurora & animations)", key="reduced_motion")
        st.caption(f"History file: `{HISTORY_FILE}`")
        st.caption(f"Groq SDK: {'installed' if Groq else 'not installed (pip install groq)'}")
    if st.button("Re-check backend", type="secondary"):
        backend_online.clear()
        st.rerun()
