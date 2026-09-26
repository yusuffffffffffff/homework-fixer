<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>EduFix AI · Broken code in. A patch you understand out.</title>
<meta name="description" content="EduFix AI turns tracebacks into readable patches with learner-first explanations. Diff-native, fast, and beautiful." />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
<style>
/* ================= DESIGN TOKENS ================= */
:root{
  --bg:#0A0B0F;--panel:#131519;--panel-2:#191C22;--panel-3:#20242C;
  --border:rgba(255,255,255,.08);--border-2:rgba(255,255,255,.16);
  --text:#E9EAEE;--muted:#8B8F9B;--dim:#5C606B;
  --add:#34D399;--add-bg:rgba(52,211,153,.12);--add-mark:rgba(52,211,153,.38);
  --remove:#F0525F;--remove-bg:rgba(240,82,95,.12);--remove-mark:rgba(240,82,95,.4);
  --accent:#F2A93B;--accent-dim:rgba(242,169,59,.16);
  --teal:#22D3EE;--pink:#EC4899;--violet:#8B5CF6;--blue:#38BDF8;
  --radius:16px;--radius-sm:10px;
  --shadow:0 20px 60px rgba(0,0,0,.5);
  --ease:cubic-bezier(.22,1,.36,1);
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:'Inter',system-ui,sans-serif;letter-spacing:-.01em;line-height:1.6;overflow-x:hidden}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif;font-weight:600;letter-spacing:-.03em;line-height:1.1;color:#fff}
code,pre,.mono{font-family:'JetBrains Mono',monospace}
a{color:inherit;text-decoration:none}
button{font-family:inherit;cursor:pointer}
::selection{background:var(--accent-dim);color:#fff}
::-webkit-scrollbar{width:8px}::-webkit-scrollbar-track{background:var(--bg)}::-webkit-scrollbar-thumb{background:var(--border-2);border-radius:8px}::-webkit-scrollbar-thumb:hover{background:var(--accent)}

/* ================= AMBIENT ================= */
.aurora{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden;animation:hue 90s linear infinite}
.blob{position:absolute;border-radius:50%;filter:blur(110px);opacity:.32;mix-blend-mode:screen;will-change:transform}
.b1{width:560px;height:560px;background:var(--accent);top:-180px;left:-120px;animation:d1 34s ease-in-out infinite}
.b2{width:500px;height:500px;background:var(--teal);top:28%;right:-180px;animation:d2 40s ease-in-out infinite}
.b3{width:420px;height:420px;background:var(--violet);bottom:-200px;left:30%;opacity:.24;animation:d3 46s ease-in-out infinite}
.b4{width:360px;height:360px;background:var(--pink);top:58%;left:44%;opacity:.18;animation:d4 52s ease-in-out infinite}
@keyframes d1{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(60px,-40px) scale(1.08)}66%{transform:translate(-30px,30px) scale(.94)}}
@keyframes d2{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(-70px,40px) scale(1.1)}}
@keyframes d3{0%,100%{transform:translate(0,0) scale(1)}40%{transform:translate(50px,-20px) scale(1.05)}70%{transform:translate(-40px,10px) scale(.96)}}
@keyframes d4{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(45px,35px) scale(1.12)}}
@keyframes hue{to{filter:hue-rotate(360deg)}}
.grain{position:fixed;inset:0;z-index:1;opacity:.04;pointer-events:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.grid-lines{position:fixed;inset:0;z-index:0;pointer-events:none;background-image:linear-gradient(var(--border) 1px,transparent 1px),linear-gradient(90deg,var(--border) 1px,transparent 1px);background-size:72px 72px;mask-image:radial-gradient(ellipse at 50% 0%,#000 20%,transparent 70%);opacity:.35}
main,nav,footer{position:relative;z-index:2}

/* ================= UTIL ================= */
.container{width:min(1180px,92vw);margin:0 auto}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--accent);background:var(--accent-dim);border:1px solid rgba(242,169,59,.28);padding:6px 12px;border-radius:999px;letter-spacing:.04em}
.eyebrow::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor;box-shadow:0 0 12px currentColor}
.shine{background:linear-gradient(100deg,var(--accent) 0%,var(--pink) 26%,var(--violet) 50%,var(--teal) 74%,var(--accent) 100%);background-size:300% auto;-webkit-background-clip:text;background-clip:text;color:transparent;animation:shine 9s linear infinite}
@keyframes shine{to{background-position:-300% center}}
.section{padding:120px 0}
.section-head{max-width:720px;margin-bottom:56px}
.section-head h2{font-size:clamp(34px,4.5vw,54px);margin:18px 0 16px}
.section-head p{color:var(--muted);font-size:18px}
.btn{display:inline-flex;align-items:center;gap:10px;padding:14px 24px;border-radius:12px;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:15px;border:1px solid transparent;transition:transform .2s var(--ease),box-shadow .2s,background-position .5s,border-color .2s;position:relative;overflow:hidden}
.btn-primary{background:linear-gradient(120deg,var(--accent),var(--pink));background-size:180% 180%;color:#14110A}
.btn-primary:hover{transform:translateY(-2px);background-position:100% 50%;box-shadow:0 10px 30px rgba(236,72,153,.3),0 4px 18px rgba(242,169,59,.28)}
.btn-ghost{background:rgba(255,255,255,.03);color:var(--text);border-color:var(--border-2);backdrop-filter:blur(8px)}
.btn-ghost:hover{border-color:var(--accent);transform:translateY(-2px)}
.btn-sm{padding:9px 16px;font-size:13px;border-radius:9px}
.kbd{font-family:'JetBrains Mono',monospace;font-size:11px;background:var(--panel-2);border:1px solid var(--border-2);border-bottom-width:2px;border-radius:5px;padding:1px 6px;color:var(--muted)}
.reveal{opacity:0;transform:translateY(28px);transition:opacity .8s var(--ease),transform .8s var(--ease)}
.reveal.in{opacity:1;transform:none}
.reveal[data-delay="1"]{transition-delay:.1s}.reveal[data-delay="2"]{transition-delay:.2s}.reveal[data-delay="3"]{transition-delay:.3s}.reveal[data-delay="4"]{transition-delay:.4s}
.glass{background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.01));border:1px solid var(--border);border-radius:var(--radius);backdrop-filter:blur(12px)}
.card{position:relative;overflow:hidden;transition:border-color .25s,transform .25s var(--ease),box-shadow .25s}
.card::before{content:"";position:absolute;inset:0;background:radial-gradient(400px circle at var(--mx,50%) var(--my,50%),rgba(255,255,255,.06),transparent 40%);opacity:0;transition:opacity .3s;pointer-events:none}
.card:hover{border-color:var(--border-2);transform:translateY(-4px);box-shadow:var(--shadow)}
.card:hover::before{opacity:1}

/* ================= NAV ================= */
nav{position:sticky;top:0;z-index:50;transition:background .3s,border-color .3s,backdrop-filter .3s;border-bottom:1px solid transparent}
nav.scrolled{background:rgba(10,11,15,.72);backdrop-filter:blur(18px);border-color:var(--border)}
.nav-inner{display:flex;align-items:center;justify-content:space-between;height:72px}
.logo{display:flex;align-items:center;gap:12px;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:19px}
.logo-badge{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;background:linear-gradient(135deg,var(--accent),var(--pink));box-shadow:0 0 22px rgba(242,169,59,.35);font-size:18px}
.nav-links{display:flex;gap:32px;font-size:14px;color:var(--muted);font-weight:500}
.nav-links a{position:relative;transition:color .2s}
.nav-links a:hover{color:#fff}
.nav-links a::after{content:"";position:absolute;left:0;right:100%;bottom:-4px;height:1px;background:var(--accent);transition:right .3s var(--ease)}
.nav-links a:hover::after{right:0}
@media(max-width:860px){.nav-links{display:none}}

/* ================= HERO ================= */
.hero{padding:110px 0 90px;position:relative}
.hero-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:64px;align-items:center}
@media(max-width:980px){.hero-grid{grid-template-columns:1fr}}
.hero h1{font-size:clamp(46px,6.2vw,84px);margin:26px 0 22px;letter-spacing:-.045em}
.hero p.lead{font-size:20px;color:var(--muted);max-width:540px;margin-bottom:36px}
.hero-actions{display:flex;gap:14px;flex-wrap:wrap;align-items:center}
.hero-meta{margin-top:40px;display:flex;gap:28px;flex-wrap:wrap;color:var(--muted);font-size:13px}
.hero-meta b{display:block;color:#fff;font-family:'Space Grotesk',sans-serif;font-size:26px;letter-spacing:-.03em}
/* terminal */
.terminal{border:1px solid var(--border-2);border-radius:18px;overflow:hidden;background:#0E0F13;box-shadow:var(--shadow),0 0 0 1px rgba(255,255,255,.02) inset;transform:perspective(1400px) rotateY(-6deg) rotateX(3deg);transition:transform .6s var(--ease);position:relative}
.terminal:hover{transform:perspective(1400px) rotateY(0) rotateX(0)}
.terminal::after{content:"";position:absolute;inset:-1px;border-radius:18px;padding:1px;background:linear-gradient(135deg,rgba(242,169,59,.5),transparent 40%,transparent 60%,rgba(34,211,238,.5));-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;pointer-events:none}
.t-bar{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:var(--panel-2);border-bottom:1px solid var(--border)}
.dots{display:flex;gap:7px}.dots span{width:11px;height:11px;border-radius:50%;opacity:.75}
.dots .r{background:#ff5f56}.dots .y{background:#ffbd2e}.dots .g{background:#27c93f}
.t-title{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--muted)}
.tag{font-family:'JetBrains Mono',monospace;font-size:10.5px;padding:2px 8px;border-radius:5px;border:1px solid}
.tag.amber{color:var(--accent);background:var(--accent-dim);border-color:rgba(242,169,59,.3)}
.tag.red{color:var(--remove);background:var(--remove-bg);border-color:rgba(240,82,95,.3)}
.tag.green{color:var(--add);background:var(--add-bg);border-color:rgba(52,211,153,.3)}
.tag.violet{color:var(--violet);background:rgba(139,92,246,.16);border-color:rgba(139,92,246,.3)}
.t-body{padding:18px;font-family:'JetBrains Mono',monospace;font-size:13px;min-height:300px}
.t-line{display:flex;gap:12px;padding:2px 6px;border-radius:4px;white-space:pre;opacity:0;transform:translateX(-6px);animation:tin .35s var(--ease) forwards}
.t-line .n{color:var(--dim);width:20px;text-align:right;user-select:none}
.t-line.rm{background:var(--remove-bg)}.t-line.rm .m{color:var(--remove)}
.t-line.ad{background:var(--add-bg)}.t-line.ad .m{color:var(--add)}
.t-line.hk{color:var(--accent);background:var(--panel-2)}
.t-line.ok{color:var(--add)}
.cursor{display:inline-block;width:8px;height:15px;background:var(--accent);vertical-align:-2px;animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
@keyframes tin{to{opacity:1;transform:none}}
.float-pill{position:absolute;padding:10px 14px;border-radius:12px;font-family:'JetBrains Mono',monospace;font-size:12px;box-shadow:var(--shadow);animation:floaty 6s ease-in-out infinite}
.fp1{top:-22px;right:28px;background:var(--panel-2);border:1px solid rgba(52,211,153,.35);color:var(--add)}
.fp2{bottom:-18px;left:-18px;background:var(--panel-2);border:1px solid rgba(242,169,59,.35);color:var(--accent);animation-delay:-3s}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}

/* ================= MARQUEE ================= */
.marquee{border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:22px 0;overflow:hidden;background:rgba(255,255,255,.015);mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent)}
.marquee-track{display:flex;gap:56px;width:max-content;animation:scroll 38s linear infinite}
.marquee:hover .marquee-track{animation-play-state:paused}
.marquee-track span{font-family:'JetBrains Mono',monospace;font-size:14px;color:var(--muted);display:inline-flex;align-items:center;gap:12px;white-space:nowrap}
.marquee-track span i{width:6px;height:6px;border-radius:50%;background:var(--accent);opacity:.6}
@keyframes scroll{to{transform:translateX(-50%)}}

/* ================= BENTO ================= */
.bento{display:grid;grid-template-columns:repeat(6,1fr);gap:16px}
.bento .card{padding:28px}
.span-2{grid-column:span 2}.span-3{grid-column:span 3}.span-4{grid-column:span 4}
@media(max-width:900px){.span-2,.span-3,.span-4{grid-column:span 6}}
.icon{width:44px;height:44px;border-radius:12px;display:grid;place-items:center;font-size:20px;margin-bottom:18px;border:1px solid var(--border-2);background:var(--panel-2)}
.card h3{font-size:20px;margin-bottom:8px}
.card p{color:var(--muted);font-size:15px}
.mini-diff{margin-top:20px;border:1px solid var(--border);border-radius:10px;overflow:hidden;font-family:'JetBrains Mono',monospace;font-size:12px}
.mini-diff div{padding:4px 12px;white-space:pre}
.mini-diff .rm{background:var(--remove-bg);color:var(--remove)}.mini-diff .ad{background:var(--add-bg);color:var(--add)}
.mini-diff mark{background:var(--add-mark);color:#fff;border-radius:3px}.mini-diff .rm mark{background:var(--remove-mark)}
.lang-cloud{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.lang-cloud span{font-family:'JetBrains Mono',monospace;font-size:12px;padding:5px 11px;border-radius:7px;background:var(--panel-2);border:1px solid var(--border);color:var(--muted);transition:all .2s}
.card:hover .lang-cloud span{border-color:var(--border-2);color:#fff}
.stat-big{font-family:'Space Grotesk',sans-serif;font-size:56px;letter-spacing:-.04em;line-height:1;margin:6px 0 4px}

/* ================= STEPS ================= */
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;position:relative}
@media(max-width:900px){.steps{grid-template-columns:1fr}}
.steps::before{content:"";position:absolute;top:44px;left:12%;right:12%;height:1px;background:linear-gradient(90deg,transparent,var(--accent),var(--pink),var(--teal),transparent);opacity:.5}
@media(max-width:900px){.steps::before{display:none}}
.step{padding:28px;text-align:left}
.step-num{width:56px;height:56px;border-radius:16px;display:grid;place-items:center;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:20px;margin-bottom:22px;background:var(--bg);border:1px solid var(--border-2);position:relative}
.step-num::after{content:"";position:absolute;inset:-1px;border-radius:16px;background:linear-gradient(135deg,var(--accent),var(--pink));z-index:-1;opacity:.7;filter:blur(8px)}

/* ================= STUDIO ================= */
.studio{padding:0;background:var(--panel);border:1px solid var(--border);border-radius:22px;overflow:hidden;box-shadow:var(--shadow)}
.studio-bar{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid var(--border);background:var(--panel-2);flex-wrap:wrap;gap:10px}
.studio-bar .left{display:flex;align-items:center;gap:14px}
.status{display:inline-flex;align-items:center;gap:8px;font-family:'JetBrains Mono',monospace;font-size:12px;padding:6px 12px;border-radius:999px;border:1px solid}
.status i{width:7px;height:7px;border-radius:50%;background:currentColor;animation:pulse 2s infinite}
.status.on{color:var(--add);background:var(--add-bg);border-color:rgba(52,211,153,.3)}
.status.off{color:var(--accent);background:var(--accent-dim);border-color:rgba(242,169,59,.3)}
@keyframes pulse{0%{box-shadow:0 0 0 0 currentColor}70%{box-shadow:0 0 0 7px transparent}100%{box-shadow:0 0 0 0 transparent}}
select{background:#0E0F13;color:var(--text);border:1px solid var(--border-2);border-radius:9px;padding:8px 12px;font-family:'JetBrains Mono',monospace;font-size:12.5px;outline:none}
select:focus{border-color:var(--accent)}
.studio-grid{display:grid;grid-template-columns:3fr 2fr;gap:0}
@media(max-width:900px){.studio-grid{grid-template-columns:1fr}}
.pane{display:flex;flex-direction:column;border-right:1px solid var(--border)}
.pane:last-child{border-right:none}
.pane-head{display:flex;justify-content:space-between;align-items:center;padding:10px 16px;background:var(--panel-2);border-bottom:1px solid var(--border)}
.pane-head .t-title{display:flex;gap:10px;align-items:center}
textarea{width:100%;min-height:320px;background:#0E0F13;color:var(--text);border:none;padding:16px 18px;font-family:'JetBrains Mono',monospace;font-size:13.5px;line-height:1.6;resize:vertical;outline:none;tab-size:4}
textarea:focus{box-shadow:inset 0 0 0 1px var(--accent)}
textarea::placeholder{color:var(--dim)}
.studio-actions{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-top:1px solid var(--border);flex-wrap:wrap;gap:12px}
.hint{color:var(--muted);font-size:13px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.line-badge{font-family:'JetBrains Mono',monospace;font-size:11.5px;color:var(--remove);background:var(--remove-bg);border:1px solid rgba(240,82,95,.3);padding:3px 10px;border-radius:6px;display:none}
.line-badge.show{display:inline-block}
.btn-primary.loading{pointer-events:none;opacity:.8}
.spinner{width:14px;height:14px;border:2px solid rgba(0,0,0,.25);border-top-color:#14110A;border-radius:50%;animation:spin .8s linear infinite;display:none}
.loading .spinner{display:inline-block}
@keyframes spin{to{transform:rotate(360deg)}}
/* result */
.result{display:none;border-top:1px solid var(--border);animation:fade .5s var(--ease)}
.result.show{display:block}
@keyframes fade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.patch-head{display:flex;justify-content:space-between;align-items:center;padding:12px 20px;background:var(--panel-2);border-bottom:1px solid var(--border);position:relative;flex-wrap:wrap;gap:10px}
.patch-head::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--accent),var(--pink),var(--violet),var(--teal))}
.patch-name{font-family:'JetBrains Mono',monospace;font-size:13px;display:flex;gap:10px;align-items:center}
.stats{font-family:'JetBrains Mono',monospace;font-size:12.5px}.stats .a{color:var(--add)}.stats .r{color:var(--remove);margin-left:8px}
.seg{display:inline-flex;gap:4px;background:var(--panel);padding:4px;border-radius:10px;border:1px solid var(--border)}
.seg button{background:transparent;border:none;color:var(--muted);padding:6px 14px;border-radius:7px;font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:12.5px;transition:all .2s}
.seg button.active{background:linear-gradient(120deg,var(--accent),var(--pink));color:#14110A}
.diff-wrap{padding:16px 20px;background:#0E0F13;max-height:560px;overflow:auto}
.diff{font-family:'JetBrains Mono',monospace;font-size:12.5px;border:1px solid var(--border);border-radius:10px;overflow:hidden}
.row{display:flex;align-items:flex-start;min-height:22px}
.row.ad{background:var(--add-bg)}.row.rm{background:var(--remove-bg)}
.row.hk{background:var(--panel-2);color:var(--accent);padding:6px 12px;font-size:11.5px}
.ln{width:40px;text-align:right;padding:2px 8px 2px 0;color:var(--dim);user-select:none;flex-shrink:0}
.mk{width:16px;text-align:center;flex-shrink:0;padding-top:2px}
.ad .mk{color:var(--add)}.rm .mk{color:var(--remove)}
.tx{white-space:pre-wrap;word-break:break-word;padding:2px 12px 2px 0;flex:1}
.tx mark.a{background:var(--add-mark);color:#fff;border-radius:3px}.tx mark.r{background:var(--remove-mark);color:#fff;border-radius:3px}
.split{display:grid;grid-template-columns:1fr 1fr;font-family:'JetBrains Mono',monospace;font-size:12.5px;border:1px solid var(--border);border-radius:10px;overflow:hidden}
.split .ch{position:sticky;top:0;background:var(--panel-2);padding:6px 12px;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;border-bottom:1px solid var(--border)}
.split .cell{display:flex;min-height:22px;border-bottom:1px solid rgba(255,255,255,.03)}
.split .cell.l{border-right:1px solid var(--border)}
.split .cell.ad{background:var(--add-bg)}.split .cell.rm{background:var(--remove-bg)}
.split .cell.em{background:repeating-linear-gradient(45deg,transparent,transparent 6px,rgba(255,255,255,.025) 6px,rgba(255,255,255,.025) 12px)}
@media(max-width:800px){.split{grid-template-columns:1fr}.split .ch:nth-child(2){display:none}}
pre.code{background:#0E0F13;padding:0;font-size:13px;line-height:1.6;white-space:pre-wrap}
.explain{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;padding:20px}
@media(max-width:900px){.explain{grid-template-columns:1fr}}
.ex{padding:18px;border-radius:14px;background:var(--panel-2);border:1px solid var(--border)}
.ex h5{font-family:'Space Grotesk',sans-serif;font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px}
.ex p{font-size:14px;color:var(--text);line-height:1.6}
.ex.what h5{color:var(--remove)}.ex.why h5{color:var(--accent)}.ex.how h5{color:var(--add)}
.result-actions{display:flex;gap:10px;padding:0 20px 20px;flex-wrap:wrap}
.toast{position:fixed;bottom:24px;left:50%;transform:translate(-50%,20px);background:var(--panel-2);border:1px solid var(--border-2);padding:12px 18px;border-radius:12px;font-size:13.5px;opacity:0;transition:all .3s var(--ease);z-index:99;box-shadow:var(--shadow)}
.toast.show{opacity:1;transform:translate(-50%,0)}

/* ================= SHOWCASE ================= */
.showcase{display:grid;grid-template-columns:280px 1fr;gap:20px}
@media(max-width:900px){.showcase{grid-template-columns:1fr}}
.case-list{display:flex;flex-direction:column;gap:8px}
.case{padding:16px 18px;border-radius:12px;border:1px solid var(--border);background:var(--panel);text-align:left;color:var(--muted);transition:all .2s;display:flex;justify-content:space-between;align-items:center}
.case:hover{border-color:var(--border-2);color:#fff}
.case.active{border-color:rgba(242,169,59,.5);color:#fff;background:linear-gradient(90deg,var(--accent-dim),transparent)}
.case b{display:block;font-family:'Space Grotesk',sans-serif;font-size:15px}
.case small{font-family:'JetBrains Mono',monospace;font-size:11px}

/* ================= TESTIMONIALS ================= */
.testi{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
@media(max-width:900px){.testi{grid-template-columns:1fr}}
.quote{padding:28px}
.quote p{font-size:16px;color:var(--text);margin-bottom:22px}
.quote p::before{content:"“";color:var(--accent);font-family:'Space Grotesk';font-size:36px;line-height:0;vertical-align:-14px;margin-right:4px}
.who{display:flex;align-items:center;gap:12px}
.avatar{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,var(--violet),var(--teal));display:grid;place-items:center;font-family:'Space Grotesk';font-weight:700;color:#fff}
.who small{display:block;color:var(--muted);font-size:12.5px}
.stars{color:var(--accent);letter-spacing:2px;margin-bottom:14px;font-size:13px}

/* ================= PRICING ================= */
.pricing{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;align-items:stretch}
@media(max-width:900px){.pricing{grid-template-columns:1fr}}
.plan{padding:32px;display:flex;flex-direction:column}
.plan.featured{border-color:rgba(242,169,59,.5);background:linear-gradient(180deg,rgba(242,169,59,.08),rgba(236,72,153,.04));transform:scale(1.03)}
.plan.featured:hover{transform:scale(1.03) translateY(-4px)}
.price{font-family:'Space Grotesk';font-size:52px;letter-spacing:-.04em;margin:14px 0 4px}
.price small{font-size:16px;color:var(--muted);letter-spacing:0}
.plan ul{list-style:none;margin:24px 0 28px;display:flex;flex-direction:column;gap:12px;flex:1}
.plan li{display:flex;gap:10px;font-size:14.5px;color:var(--text)}
.plan li::before{content:"✓";color:var(--add);font-weight:700}
.ribbon{position:absolute;top:18px;right:-34px;transform:rotate(38deg);background:linear-gradient(90deg,var(--accent),var(--pink));color:#14110A;font-family:'Space Grotesk';font-weight:700;font-size:11px;padding:5px 44px;letter-spacing:.06em}

/* ================= FAQ ================= */
.faq{max-width:820px;margin:0 auto;display:flex;flex-direction:column;gap:10px}
.q{border:1px solid var(--border);border-radius:14px;background:var(--panel);overflow:hidden;transition:border-color .2s}
.q.open{border-color:var(--border-2)}
.q button{width:100%;display:flex;justify-content:space-between;align-items:center;gap:20px;padding:20px 22px;background:none;border:none;color:#fff;font-family:'Space Grotesk';font-size:16.5px;font-weight:600;text-align:left}
.q button span{width:26px;height:26px;border-radius:50%;border:1px solid var(--border-2);display:grid;place-items:center;font-size:16px;transition:transform .3s var(--ease),background .2s;flex-shrink:0}
.q.open button span{transform:rotate(45deg);background:var(--accent);color:#14110A;border-color:transparent}
.q .a{max-height:0;overflow:hidden;transition:max-height .4s var(--ease)}
.q .a p{padding:0 22px 20px;color:var(--muted);font-size:15px}

/* ================= CTA & FOOTER ================= */
.cta{position:relative;padding:80px 40px;text-align:center;border-radius:28px;overflow:hidden;border:1px solid var(--border-2);background:radial-gradient(ellipse at 50% 120%,rgba(242,169,59,.25),transparent 60%),radial-gradient(ellipse at 10% 0%,rgba(139,92,246,.2),transparent 50%),radial-gradient(ellipse at 90% 0%,rgba(34,211,238,.18),transparent 50%),var(--panel)}
.cta h2{font-size:clamp(34px,5vw,60px);margin-bottom:16px}
.cta p{color:var(--muted);font-size:18px;margin-bottom:34px}
footer{border-top:1px solid var(--border);padding:56px 0 32px;color:var(--muted);font-size:14px}
.foot{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:32px;margin-bottom:40px}
@media(max-width:800px){.foot{grid-template-columns:1fr 1fr}}
.foot h4{font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:#fff;margin-bottom:14px}
.foot a{display:block;margin-bottom:10px;transition:color .2s}.foot a:hover{color:#fff}
.foot-bottom{display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;padding-top:24px;border-top:1px solid var(--border);font-family:'JetBrains Mono';font-size:12px}

@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}.reveal{opacity:1;transform:none}}
</style>
</head>
<body>
<div class="aurora"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div><div class="blob b4"></div></div>
<div class="grid-lines"></div><div class="grain"></div>

<!-- ================= NAV ================= -->
<nav id="nav"><div class="container nav-inner">
  <a href="#" class="logo"><span class="logo-badge">🩹</span>EduFix <span class="shine">AI</span></a>
  <div class="nav-links">
    <a href="#features">Features</a><a href="#how">How it works</a><a href="#studio">Studio</a><a href="#showcase">Examples</a><a href="#pricing">Pricing</a><a href="#faq">FAQ</a>
  </div>
  <a href="#studio" class="btn btn-primary btn-sm">Open Studio →</a>
</div></nav>

<main>
<!-- ================= HERO ================= -->
<section class="hero"><div class="container hero-grid">
  <div>
    <span class="eyebrow reveal in">v2.0 · diff-native tutoring</span>
    <h1 class="reveal in" data-delay="1">Broken code in.<br/>A <span class="shine">patch you understand</span> out.</h1>
    <p class="lead reveal in" data-delay="2">EduFix reads your traceback, rewrites the failing lines, and explains every change in plain language. Learn from the diff, not from a wall of text.</p>
    <div class="hero-actions reveal in" data-delay="3">
      <a href="#studio" class="btn btn-primary">🩹 Fix my code</a>
      <a href="#how" class="btn btn-ghost">See how it works</a>
      <span class="hint"><span class="kbd">Ctrl</span>+<span class="kbd">Enter</span> in the editor</span>
    </div>
    <div class="hero-meta reveal in" data-delay="4">
      <div><b data-count="128400">0</b>patches shipped</div>
      <div><b data-count="11">0</b>languages</div>
      <div><b data-count="1.8" data-suffix="s">0</b>median fix time</div>
      <div><b data-count="4.9" data-suffix="★">0</b>learner rating</div>
    </div>
  </div>
  <div style="position:relative">
    <div class="terminal">
      <div class="t-bar"><div class="dots"><span class="r"></span><span class="y"></span><span class="g"></span></div><span class="t-title">main.py · edufix diagnose</span><span class="tag amber">LIVE</span></div>
      <div class="t-body" id="heroTerm"></div>
    </div>
    <div class="float-pill fp1">✓ 3 tests passing</div>
    <div class="float-pill fp2">TypeError → fixed in 1.4s</div>
  </div>
</div></section>

<!-- ================= MARQUEE ================= -->
<div class="marquee"><div class="marquee-track" id="marquee">
  <span><i></i>Python</span><span><i></i>JavaScript</span><span><i></i>TypeScript</span><span><i></i>Java</span><span><i></i>C / C++</span><span><i></i>Go</span><span><i></i>Rust</span><span><i></i>SQL</span><span><i></i>Bash</span><span><i></i>Kotlin</span><span><i></i>Swift</span>
</div></div>

<!-- ================= FEATURES ================= -->
<section class="section" id="features"><div class="container">
  <div class="section-head reveal">
    <span class="eyebrow">Why EduFix</span>
    <h2>Built like a code review, not a chatbot.</h2>
    <p>Every answer is a real patch. Red lines out, green lines in, with the reasoning attached where you can see it.</p>
  </div>
  <div class="bento">
    <div class="glass card span-4 reveal"><div class="icon">⇄</div><h3>Character-precise diffs</h3><p>Unified and side-by-side views highlight exactly which tokens changed, so a one-character typo never hides inside a rewritten line.</p>
      <div class="mini-diff"><div class="rm">- for i in range(len(items) <mark>+ 1</mark>):</div><div class="ad">+ for i in range(len(items)):</div><div class="rm">-     total =<mark> </mark>items[i]</div><div class="ad">+     total <mark>+</mark>= items[i]</div></div></div>
    <div class="glass card span-2 reveal" data-delay="1"><div class="icon">🎓</div><h3>What · Why · How</h3><p>Three short cards per fix: what was wrong, why it failed, and how the patch resolves it. Designed for learners, not for skimming.</p></div>
    <div class="glass card span-2 reveal"><div class="icon">⚡</div><div class="stat-big shine">1.8s</div><p>Median time from paste to patch. Streaming responses keep you reading while the model finishes.</p></div>
    <div class="glass card span-2 reveal" data-delay="1"><div class="icon">🧭</div><h3>Traceback aware</h3><p>Paste a stack trace and EduFix pins the failing line, error type, and likely root cause before it starts editing.</p></div>
    <div class="glass card span-2 reveal" data-delay="2"><div class="icon">🌐</div><h3>Polyglot</h3><p>Auto-detects the language and adapts idioms, from list comprehensions to Rust borrows.</p>
      <div class="lang-cloud"><span>py</span><span>js</span><span>ts</span><span>java</span><span>c</span><span>cpp</span><span>go</span><span>rs</span><span>sql</span><span>sh</span></div></div>
    <div class="glass card span-3 reveal"><div class="icon">🕘</div><h3>History that teaches</h3><p>Every fix is saved locally with a shareable link. Revisit old mistakes, restore the original, and watch your error patterns shrink over the semester.</p></div>
    <div class="glass card span-3 reveal" data-delay="1"><div class="icon">🔒</div><h3>Private by default</h3><p>Runs against your own backend. Nothing leaves your machine unless you choose a hosted model. Ideal for classrooms and take-home assignments.</p></div>
  </div>
</div></section>

<!-- ================= HOW ================= -->
<section class="section" id="how" style="padding-top:40px"><div class="container">
  <div class="section-head reveal"><span class="eyebrow">Workflow</span><h2>Three steps. Zero context switching.</h2></div>
  <div class="steps">
    <div class="glass card step reveal"><div class="step-num">1</div><h3>Paste</h3><p>Drop in the broken snippet and, optionally, the exact error output your terminal gave you.</p></div>
    <div class="glass card step reveal" data-delay="1"><div class="step-num">2</div><h3>Diagnose</h3><p>EduFix parses the traceback, locates the failing line, and drafts a minimal patch that preserves your intent.</p></div>
    <div class="glass card step reveal" data-delay="2"><div class="step-num">3</div><h3>Learn</h3><p>Read the diff, read the reasoning, apply or download the patch. Ask follow-ups in the tutor chat.</p></div>
  </div>
</div></section>

<!-- ================= STUDIO ================= -->
<section class="section" id="studio"><div class="container">
  <div class="section-head reveal"><span class="eyebrow">Live Studio</span><h2>Try it right here.</h2><p>Connected to your local <code>/fix-code</code> backend. If it's offline, a built-in demo shows the experience.</p></div>
  <div class="studio reveal">
    <div class="studio-bar">
      <div class="left"><span class="status off" id="status"><i></i>checking backend…</span>
        <select id="lang"><option value="auto">auto-detect</option><option>python</option><option>javascript</option><option>typescript</option><option>java</option><option>c</option><option>cpp</option><option>go</option><option>rust</option><option>sql</option><option>bash</option></select></div>
      <div class="hint"><span class="line-badge" id="lineBadge"></span><button class="btn btn-ghost btn-sm" id="loadExample">Load example</button></div>
    </div>
    <div class="studio-grid">
      <div class="pane"><div class="pane-head"><span class="t-title"><span class="dots"><span class="r"></span><span class="y"></span><span class="g"></span></span>main · workspace</span><span class="tag amber">EDITOR</span></div>
        <textarea id="code" spellcheck="false" placeholder="# Paste your broken code here"></textarea></div>
      <div class="pane"><div class="pane-head"><span class="t-title"><span class="dots"><span class="r"></span><span class="y"></span><span class="g"></span></span>stderr</span><span class="tag red">TRACEBACK</span></div>
        <textarea id="error" spellcheck="false" placeholder="Paste the traceback or error output (optional, but it sharpens the fix)"></textarea></div>
    </div>
    <div class="studio-actions">
      <span class="hint">Press <span class="kbd">Ctrl</span>+<span class="kbd">Enter</span> to diagnose · <span id="charCount">0 chars</span></span>
      <button class="btn btn-primary" id="fixBtn"><span class="spinner"></span>🩹 Diagnose &amp; Patch</button>
    </div>
    <div class="result" id="result">
      <div class="patch-head">
        <span class="patch-name" id="patchName">main.py <span class="tag violet">python</span><span class="tag green" id="srcTag">via backend</span></span>
        <div style="display:flex;gap:14px;align-items:center"><span class="stats" id="stats"></span>
          <div class="seg" id="seg"><button class="active" data-v="unified">Unified</button><button data-v="split">Split</button><button data-v="code">Fixed</button></div></div>
      </div>
      <div class="diff-wrap" id="diffWrap"></div>
      <div class="explain" id="explain"></div>
      <div class="result-actions">
        <button class="btn btn-primary btn-sm" id="applyBtn">✅ Apply to editor</button>
        <button class="btn btn-ghost btn-sm" id="copyBtn">📋 Copy fixed code</button>
        <button class="btn btn-ghost btn-sm" id="patchBtn">⬇️ Download .patch</button>
        <button class="btn btn-ghost btn-sm" id="mdBtn">📝 Export Markdown</button>
      </div>
    </div>
  </div>
</div></section>

<!-- ================= SHOWCASE ================= -->
<section class="section" id="showcase" style="padding-top:40px"><div class="container">
  <div class="section-head reveal"><span class="eyebrow">Examples</span><h2>Common bugs, uncommon clarity.</h2><p>Click a case to preview the patch EduFix produces.</p></div>
  <div class="showcase reveal">
    <div class="case-list" id="caseList"></div>
    <div class="terminal" style="transform:none"><div class="t-bar"><div class="dots"><span class="r"></span><span class="y"></span><span class="g"></span></div><span class="t-title" id="caseTitle"></span><span class="tag green" id="caseStats"></span></div>
      <div class="diff-wrap" id="caseDiff" style="padding:14px"></div></div>
  </div>
</div></section>

<!-- ================= TESTIMONIALS ================= -->
<section class="section"><div class="container">
  <div class="section-head reveal"><span class="eyebrow">Loved by learners</span><h2>The diff is the lesson.</h2></div>
  <div class="testi">
    <div class="glass card quote reveal"><div class="stars">★★★★★</div><p>I stopped copy-pasting fixes I didn't understand. Seeing the red and green lines next to the "why" finally made recursion click.</p><div class="who"><div class="avatar">A</div><div>Aanya R.<small>CS101 student</small></div></div></div>
    <div class="glass card quote reveal" data-delay="1"><div class="stars">★★★★★</div><p>We run it against a local model in the lab. Students get instant, private feedback and I get a heatmap of the error types the cohort struggles with.</p><div class="who"><div class="avatar" style="background:linear-gradient(135deg,var(--accent),var(--pink))">M</div><div>Prof. M. Okafor<small>Intro to Programming</small></div></div></div>
    <div class="glass card quote reveal" data-delay="2"><div class="stars">★★★★★</div><p>The traceback parsing is uncanny. It pointed at the exact off-by-one three files deep before I'd finished reading the error.</p><div class="who"><div class="avatar" style="background:linear-gradient(135deg,var(--teal),var(--blue))">J</div><div>Jonas K.<small>Bootcamp grad</small></div></div></div>
  </div>
</div></section>

<!-- ================= PRICING ================= -->
<section class="section" id="pricing" style="padding-top:40px"><div class="container">
  <div class="section-head reveal"><span class="eyebrow">Pricing</span><h2>Free to learn. Fair to scale.</h2></div>
  <div class="pricing">
    <div class="glass card plan reveal"><span class="tag amber" style="width:fit-content">Learner</span><div class="price">$0<small>/mo</small></div><p style="color:var(--muted)">Everything you need to pass the course.</p>
      <ul><li>50 fixes / day</li><li>Unified &amp; split diffs</li><li>What · Why · How explanations</li><li>Local history</li></ul><a href="#studio" class="btn btn-ghost">Start free</a></div>
    <div class="glass card plan featured reveal" data-delay="1"><div class="ribbon">POPULAR</div><span class="tag violet" style="width:fit-content">Pro</span><div class="price">$9<small>/mo</small></div><p style="color:var(--muted)">For daily builders and serious students.</p>
      <ul><li>Unlimited fixes</li><li>Streaming tutor chat</li><li>Shareable patch links</li><li>Priority models</li><li>Export to Markdown &amp; .patch</li></ul><a href="#studio" class="btn btn-primary">Go Pro</a></div>
    <div class="glass card plan reveal" data-delay="2"><span class="tag green" style="width:fit-content">Classroom</span><div class="price">$4<small>/seat</small></div><p style="color:var(--muted)">Self-hosted, private, with cohort insights.</p>
      <ul><li>Bring your own backend</li><li>Error-pattern analytics</li><li>SSO &amp; roster sync</li><li>Dedicated support</li></ul><a href="#faq" class="btn btn-ghost">Talk to us</a></div>
  </div>
</div></section>

<!-- ================= FAQ ================= -->
<section class="section" id="faq" style="padding-top:40px"><div class="container">
  <div class="section-head reveal" style="text-align:center;margin-left:auto;margin-right:auto"><span class="eyebrow">FAQ</span><h2>Questions, patched.</h2></div>
  <div class="faq reveal">
    <div class="q"><button>Does EduFix just give me the answer?<span>+</span></button><div class="a"><p>It gives you a minimal patch and a three-part explanation. The goal is that you could have written the fix yourself next time. Classroom mode can also hide the patch until you attempt an explanation.</p></div></div>
    <div class="q"><button>Which backend does the Studio call?<span>+</span></button><div class="a"><p>A FastAPI endpoint at <code>POST http://127.0.0.1:8000/fix-code</code> accepting <code>{"{"}code, error, language, user_id{"}"}</code> and returning <code>fixed_code</code> plus an explanation. Change the URL at the top of the script.</p></div></div>
    <div class="q"><button>Is my code sent anywhere?<span>+</span></button><div class="a"><p>Only to the backend you configure. Self-hosted classroom deployments never leave the campus network.</p></div></div>
    <div class="q"><button>What languages are supported?<span>+</span></button><div class="a"><p>Python, JavaScript, TypeScript, Java, C, C++, Go, Rust, SQL, Bash and Kotlin, with automatic detection and manual override.</p></div></div>
  </div>
</div></section>

<!-- ================= CTA ================= -->
<section class="section" style="padding-top:20px"><div class="container">
  <div class="cta reveal"><span class="eyebrow">Ready?</span><h2 style="margin-top:18px">Ship the fix. <span class="shine">Keep the lesson.</span></h2><p>Paste your first broken snippet and watch it turn green.</p>
    <a href="#studio" class="btn btn-primary" style="font-size:16px;padding:16px 30px">🩹 Open the Studio</a></div>
</div></section>
</main>

<footer><div class="container">
  <div class="foot">
    <div><a href="#" class="logo" style="margin-bottom:14px"><span class="logo-badge">🩹</span>EduFix AI</a><p style="max-width:300px">Diff-native code tutoring for learners and the people who teach them.</p></div>
    <div><h4>Product</h4><a href="#features">Features</a><a href="#studio">Studio</a><a href="#pricing">Pricing</a><a href="#showcase">Examples</a></div>
    <div><h4>Resources</h4><a href="#how">How it works</a><a href="#faq">FAQ</a><a href="#">API docs</a><a href="#">Changelog</a></div>
    <div><h4>Company</h4><a href="#">About</a><a href="#">Privacy</a><a href="#">Terms</a><a href="#">Contact</a></div>
  </div>
  <div class="foot-bottom"><span>© <span id="year"></span> EduFix AI. All patches reserved.</span><span>built with diffs, coffee, and JetBrains Mono</span></div>
</div></footer>
<div class="toast" id="toast"></div>

<script>
/* ================= CONFIG ================= */
const BACKEND_URL = "http://127.0.0.1:8000/fix-code";
const USER_ID = "00000000-0000-0000-0000-000000000001";
const LANG_EXT = {python:"py",javascript:"js",typescript:"ts",java:"java",c:"c",cpp:"cpp",go:"go",rust:"rs",sql:"sql",bash:"sh"};
const esc = s => s.replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const $ = id => document.getElementById(id);

/* ================= DIFF ENGINE ================= */
function lcsOps(a, b) {                      // returns [[op, ai, bi], ...] op: '=', '-', '+'
  const n = a.length, m = b.length, dp = Array.from({length:n+1}, () => new Uint16Array(m+1));
  for (let i = n-1; i >= 0; i--) for (let j = m-1; j >= 0; j--)
    dp[i][j] = a[i] === b[j] ? dp[i+1][j+1] + 1 : Math.max(dp[i+1][j], dp[i][j+1]);
  const ops = []; let i = 0, j = 0;
  while (i < n && j < m) {
    if (a[i] === b[j]) { ops.push(["=", i, j]); i++; j++; }
    else if (dp[i+1][j] >= dp[i][j+1]) { ops.push(["-", i, j]); i++; }
    else { ops.push(["+", i, j]); j++; }
  }
  while (i < n) ops.push(["-", i++, j]); while (j < m) ops.push(["+", i, j++]);
  return ops;
}
function groupOps(ops) {                     // collapse into blocks: {type:'equal'|'change', del:[], add:[]}
  const blocks = []; let cur = null;
  for (const [op, ai, bi] of ops) {
    if (op === "=") { if (!cur || cur.type !== "equal") blocks.push(cur = {type:"equal", pairs:[]}); cur.pairs.push([ai, bi]); }
    else { if (!cur || cur.type !== "change") blocks.push(cur = {type:"change", del:[], add:[]}); (op === "-" ? cur.del : cur.add).push(op === "-" ? ai : bi); }
  }
  return blocks;
}
function inlineMarks(a, b) {                 // char-level highlighting for a replaced pair
  if (a.length * b.length > 40000) return [esc(a), esc(b)];
  const ops = lcsOps([...a], [...b]); let l = "", r = "", lb = "", rb = "";
  const flush = () => { if (lb) l += `<mark class="r">${esc(lb)}</mark>`; if (rb) r += `<mark class="a">${esc(rb)}</mark>`; lb = rb = ""; };
  for (const [op, ai, bi] of ops) { if (op === "=") { flush(); l += esc(a[ai]); r += esc(b[bi]); } else if (op === "-") lb += a[ai]; else rb += b[bi]; }
  flush(); return [l, r];
}
function diffStats(a, b) { let add = 0, rm = 0; for (const [op] of lcsOps(a.split("\n"), b.split("\n"))) { if (op === "+") add++; else if (op === "-") rm++; } return {add, rm}; }
function renderUnified(orig, fixed) {
  const a = orig.split("\n"), b = fixed.split("\n");
  if (orig === fixed) return `<div class="tx" style="color:var(--muted);padding:14px;font-style:italic">No changes detected.</div>`;
  const blocks = groupOps(lcsOps(a, b)); let out = "", CTX = 3;
  const row = (cls, la, lb, mk, tx) => `<div class="row ${cls}"><span class="ln">${la}</span><span class="ln">${lb}</span><span class="mk">${mk}</span><span class="tx">${tx}</span></div>`;
  blocks.forEach((blk, idx) => {
    if (blk.type === "equal") {
      let pairs = blk.pairs;
      const first = idx === 0, last = idx === blocks.length - 1;
      if (pairs.length > CTX * 2 && !first && !last) { const head = pairs.slice(0, CTX), tail = pairs.slice(-CTX); head.forEach(([x, y]) => out += row("", x+1, y+1, " ", esc(a[x]))); out += `<div class="row hk">@@ … ${pairs.length - CTX*2} unchanged lines …</div>`; pairs = tail; }
      else if (first && pairs.length > CTX) { out += `<div class="row hk">@@ … ${pairs.length - CTX} unchanged lines …</div>`; pairs = pairs.slice(-CTX); }
      else if (last && pairs.length > CTX) { pairs = pairs.slice(0, CTX); pairs.forEach(([x, y]) => out += row("", x+1, y+1, " ", esc(a[x]))); out += `<div class="row hk">@@ … end of file …</div>`; return; }
      pairs.forEach(([x, y]) => out += row("", x+1, y+1, " ", esc(a[x])));
    } else {
      const paired = Math.min(blk.del.length, blk.add.length);
      for (let k = 0; k < Math.max(blk.del.length, blk.add.length); k++) {
        if (k < paired) { const [l, r] = inlineMarks(a[blk.del[k]], b[blk.add[k]]); out += row("rm", blk.del[k]+1, "", "-", l) + row("ad", "", blk.add[k]+1, "+", r); }
        else if (k < blk.del.length) out += row("rm", blk.del[k]+1, "", "-", esc(a[blk.del[k]]));
        else out += row("ad", "", blk.add[k]+1, "+", esc(b[blk.add[k]]));
      }
    }
  });
  return `<div class="diff">${out}</div>`;
}
function renderSplit(orig, fixed) {
  const a = orig.split("\n"), b = fixed.split("\n");
  if (orig === fixed) return renderUnified(orig, fixed);
  const cell = (side, cls, no, tx) => `<div class="cell ${side} ${cls}"><span class="ln">${no}</span><span class="tx">${tx}</span></div>`;
  let out = `<div class="ch">Original</div><div class="ch">Fixed</div>`;
  for (const blk of groupOps(lcsOps(a, b))) {
    if (blk.type === "equal") blk.pairs.forEach(([x, y]) => out += cell("l", "", x+1, esc(a[x])) + cell("r", "", y+1, esc(b[y])));
    else for (let k = 0; k < Math.max(blk.del.length, blk.add.length); k++) {
      const hl = k < blk.del.length, hr = k < blk.add.length; let l = hl ? esc(a[blk.del[k]]) : "", r = hr ? esc(b[blk.add[k]]) : "";
      if (hl && hr) [l, r] = inlineMarks(a[blk.del[k]], b[blk.add[k]]);
      out += cell("l", hl ? "rm" : "em", hl ? blk.del[k]+1 : "", l) + cell("r", hr ? "ad" : "em", hr ? blk.add[k]+1 : "", r);
    }
  }
  return `<div class="split">${out}</div>`;
}
function unifiedPatchText(orig, fixed, name) {
  const a = orig.split("\n"), b = fixed.split("\n"); let out = `--- a/${name}\n+++ b/${name}\n@@ -1,${a.length} +1,${b.length} @@\n`;
  for (const [op, ai, bi] of lcsOps(a, b)) out += (op === "=" ? " " + a[ai] : op === "-" ? "-" + a[ai] : "+" + b[bi]) + "\n";
  return out;
}

/* ================= HELPERS ================= */
function detectLang(c) {
  if (/^\s*(def |import |from \w+ import|print\()/m.test(c)) return "python";
  if (/\b(interface|type \w+ =|: (string|number|boolean))\b/.test(c)) return "typescript";
  if (/\b(const|let|=>|console\.log|function)\b/.test(c)) return "javascript";
  if (/\bpublic (static )?(class|void)\b|System\.out/.test(c)) return "java";
  if (/#include\s*<|int main\s*\(/.test(c)) return /std::|cout/.test(c) ? "cpp" : "c";
  if (/\bfunc main\(\)|package main/.test(c)) return "go";
  if (/\bfn main\(\)|let mut\b/.test(c)) return "rust";
  if (/\b(SELECT|INSERT|UPDATE|DELETE)\b[\s\S]*\b(FROM|INTO|SET)\b/i.test(c)) return "sql";
  if (/^#!|\becho\b/.test(c)) return "bash";
  return "python";
}
const errLine = t => { const m = [...t.matchAll(/\bline (\d+)/gi)]; return m.length ? +m[m.length-1][1] : null; };
const errType = t => { const last = t.trim().split("\n").pop() || ""; const m = last.match(/^(\w+(?:Error|Exception|Warning))\b/); return m ? m[1] : "Error"; };
function normalize(d, orig) {
  if (typeof d === "string") { try { d = JSON.parse(d); } catch { d = {fixed_code: d}; } }
  let fixed = d.fixed_code || d.corrected_code || d.code || d.fix || orig;
  fixed = String(fixed).trim().replace(/^```[\w+-]*\n/, "").replace(/\n```$/, "");
  let ex = d.explanation || {}; if (typeof ex === "string") ex = {how: ex};
  return {fixed_code: fixed, what: ex.what || d.what_was_wrong || "", why: ex.why || d.why_it_failed || "", how: ex.how || d.how_fixed || d.message || ""};
}
let toastT; function toast(msg) { const t = $("toast"); t.textContent = msg; t.classList.add("show"); clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 2200); }
function download(name, text, mime="text/plain") { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([text], {type: mime})); a.download = name; a.click(); URL.revokeObjectURL(a.href); }

/* ================= DEMO DATA ================= */
const CASES = [
  {title:"Off-by-one in loop", err:"IndexError", lang:"python",
   orig:`def total(items):\n    result = 0\n    for i in range(len(items) + 1):\n        result = items[i]\n    return result`,
   fixed:`def total(items):\n    result = 0\n    for i in range(len(items)):\n        result += items[i]\n    return result`,
   error:`Traceback (most recent call last):\n  File "main.py", line 4, in total\n    result = items[i]\nIndexError: list index out of range`,
   what:"The loop ran one step past the end of the list, and the accumulator was overwritten instead of added to.",
   why:"range(len(items) + 1) yields an index equal to len(items), which does not exist. Separately, = replaces the running total on every iteration.",
   how:"Remove the + 1 so indices stay in bounds, and use += to accumulate values."},
  {title:"Mutable default argument", err:"Logic bug", lang:"python",
   orig:`def add_tag(tag, tags=[]):\n    tags.append(tag)\n    return tags`,
   fixed:`def add_tag(tag, tags=None):\n    if tags is None:\n        tags = []\n    tags.append(tag)\n    return tags`,
   error:"", what:"The default list is shared between every call, so tags leak across invocations.",
   why:"Default argument values are evaluated once at function definition, not per call. A mutable default is therefore a single shared object.",
   how:"Default to None and create a fresh list inside the function body when needed."},
  {title:"Async without await", err:"TypeError", lang:"javascript",
   orig:`async function load() {\n  const res = fetch('/api/user');\n  const data = res.json();\n  return data.name;\n}`,
   fixed:`async function load() {\n  const res = await fetch('/api/user');\n  const data = await res.json();\n  return data.name;\n}`,
   error:"TypeError: res.json is not a function", what:"fetch returns a Promise, and the code treated it like a Response object.",
   why:"Without await, res holds a pending Promise which has no json method. The same happens on the next line.",
   how:"Await both asynchronous calls so each variable holds the resolved value."},
  {title:"Null pointer on map lookup", err:"NullPointerException", lang:"java",
   orig:`String name = users.get(id).getName();\nreturn name.toUpperCase();`,
   fixed:`User user = users.get(id);\nif (user == null) {\n    return "";\n}\nreturn user.getName().toUpperCase();`,
   error:`Exception in thread "main" java.lang.NullPointerException\n\tat Main.lookup(Main.java:1)`,
   what:"Map.get returns null when the key is missing, and the code immediately dereferenced it.",
   why:"Chaining a method on a possibly-null value throws a NullPointerException at runtime.",
   how:"Store the lookup, guard the null case explicitly, then call methods on the checked reference."},
];

/* ================= HERO TERMINAL ================= */
(function heroTerminal() {
  const lines = [
    ["hk", "", "$ edufix diagnose main.py"], ["", "", "→ parsing traceback … IndexError at line 4"], ["", "", "→ drafting minimal patch"], ["hk", "", "@@ -3,2 +3,2 @@"],
    ["rm", "3", "-    for i in range(len(items) + 1):"], ["ad", "3", "+    for i in range(len(items)):"], ["rm", "4", "-        result = items[i]"], ["ad", "4", "+        result += items[i]"],
    ["ok", "", "✓ patch applied · 3 tests passing · 1.4s"],
  ];
  const el = $("heroTerm"); let i = 0;
  const cur = document.createElement("div"); cur.className = "t-line"; cur.style.opacity = 1; cur.innerHTML = `<span class="n"></span><span class="cursor"></span>`;
  function step() {
    if (i < lines.length) { const [cls, n, tx] = lines[i++]; const d = document.createElement("div"); d.className = `t-line ${cls}`;
      d.innerHTML = `<span class="n">${n}</span><span class="m">${cls === "rm" ? "-" : cls === "ad" ? "+" : ""}</span>${esc(tx.replace(/^[-+]/, cls === "rm" || cls === "ad" ? "" : "$&"))}`; el.appendChild(d); el.appendChild(cur); setTimeout(step, i < 4 ? 650 : 380); }
    else setTimeout(() => { el.innerHTML = ""; i = 0; step(); }, 5000);
  }
  step();
})();

/* ================= UX: nav, reveal, counters, spotlight, marquee, faq ================= */
window.addEventListener("scroll", () => $("nav").classList.toggle("scrolled", scrollY > 20), {passive: true});
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), {threshold: .12});
document.querySelectorAll(".reveal").forEach(el => io.observe(el));
const cio = new IntersectionObserver(es => es.forEach(e => { if (!e.isIntersecting) return; const el = e.target, end = +el.dataset.count, suf = el.dataset.suffix || "", dec = String(end).includes(".") ? 1 : 0, t0 = performance.now();
  (function tick(now) { const p = Math.min(1, (now - t0) / 1600), v = end * (1 - Math.pow(1 - p, 3)); el.textContent = (dec ? v.toFixed(1) : Math.round(v).toLocaleString()) + suf; if (p < 1) requestAnimationFrame(tick); })(t0); cio.unobserve(el); }));
document.querySelectorAll("[data-count]").forEach(el => cio.observe(el));
document.addEventListener("pointermove", e => { const c = e.target.closest(".card"); if (!c) return; const r = c.getBoundingClientRect(); c.style.setProperty("--mx", (e.clientX - r.left) + "px"); c.style.setProperty("--my", (e.clientY - r.top) + "px"); });
$("marquee").innerHTML += $("marquee").innerHTML;
document.querySelectorAll(".q button").forEach(b => b.addEventListener("click", () => { const q = b.parentElement, open = q.classList.toggle("open"); q.querySelector(".a").style.maxHeight = open ? q.querySelector(".a p").offsetHeight + 24 + "px" : 0; }));
$("year").textContent = new Date().getFullYear();

/* ================= SHOWCASE ================= */
CASES.forEach((c, i) => { const b = document.createElement("button"); b.className = "case" + (i === 0 ? " active" : ""); b.innerHTML = `<div><b>${c.title}</b><small>${c.err}</small></div><span class="tag violet">${c.lang}</span>`; b.onclick = () => showCase(i); $("caseList").appendChild(b); });
function showCase(i) { const c = CASES[i]; document.querySelectorAll(".case").forEach((b, k) => b.classList.toggle("active", k === i)); $("caseTitle").textContent = `main.${LANG_EXT[c.lang]} · ${c.err}`; const s = diffStats(c.orig, c.fixed); $("caseStats").textContent = `+${s.add} -${s.rm}`; $("caseDiff").innerHTML = renderUnified(c.orig, c.fixed); }
showCase(0);

/* ================= STUDIO ================= */
let backendUp = false, current = null, view = "unified";
(async function ping() { try { await fetch(BACKEND_URL.replace(/\/[^/]*$/, "/docs"), {mode: "no-cors", signal: AbortSignal.timeout(1500)}); backendUp = true; } catch { backendUp = false; }
  const s = $("status"); s.className = "status " + (backendUp ? "on" : "off"); s.innerHTML = `<i></i>${backendUp ? "backend online" : "backend offline · demo mode"}`; })();
const codeEl = $("code"), errEl = $("error");
function updateMeta() { $("charCount").textContent = `${codeEl.value.length} chars · ${codeEl.value.split("\n").length} lines`; const ln = errLine(errEl.value), badge = $("lineBadge");
  if (ln && codeEl.value) { const src = (codeEl.value.split("\n")[ln-1] || "").trim(); badge.textContent = `↳ ${errType(errEl.value)} at line ${ln}${src ? ": " + src.slice(0, 40) : ""}`; badge.classList.add("show"); } else badge.classList.remove("show"); }
[codeEl, errEl].forEach(el => { el.addEventListener("input", updateMeta); el.addEventListener("keydown", e => { if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); fix(); } if (e.key === "Tab" && el === codeEl) { e.preventDefault(); const s = el.selectionStart; el.setRangeText("    ", s, el.selectionEnd, "end"); } }); });
$("loadExample").onclick = () => { const c = CASES[0]; codeEl.value = c.orig; errEl.value = c.error; $("lang").value = "auto"; updateMeta(); toast("Example loaded"); };
$("fixBtn").onclick = fix;
async function fix() {
  const code = codeEl.value; if (!code.trim()) return toast("Paste some code first");
  const lang = $("lang").value === "auto" ? detectLang(code) : $("lang").value, btn = $("fixBtn"); btn.classList.add("loading");
  try {
    let res, src;
    if (backendUp) { const r = await fetch(BACKEND_URL, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({user_id: USER_ID, code, error: errEl.value, language: lang}), signal: AbortSignal.timeout(60000)}); if (!r.ok) throw new Error(`Backend ${r.status}`); res = normalize(await r.json(), code); src = "backend"; }
    else { await new Promise(r => setTimeout(r, 900)); const c = CASES.find(x => x.orig.trim() === code.trim()) || CASES[0]; res = {fixed_code: code.trim() === c.orig.trim() ? c.fixed : code, what: c.what, why: c.why, how: c.how + (code.trim() === c.orig.trim() ? "" : " (Demo mode: start the backend to patch your own code.)")}; src = "demo"; }
    current = {...res, orig: code, lang, name: `main.${LANG_EXT[lang] || "txt"}`}; renderResult(src); $("result").scrollIntoView({behavior: "smooth", block: "start"});
  } catch (e) { toast("Fix failed: " + e.message); } finally { btn.classList.remove("loading"); }
}
function renderResult(src) {
  const s = diffStats(current.orig, current.fixed_code); $("stats").innerHTML = `<span class="a">+${s.add}</span><span class="r">-${s.rm}</span>`;
  $("patchName").innerHTML = `${current.name} <span class="tag violet">${current.lang}</span><span class="tag ${src === "backend" ? "green" : "amber"}">via ${src}</span>`;
  const hasEx = current.what || current.why || current.how;
  $("explain").innerHTML = hasEx ? `<div class="ex what"><h5>What was wrong</h5><p>${esc(current.what || "—")}</p></div><div class="ex why"><h5>Why it failed</h5><p>${esc(current.why || "—")}</p></div><div class="ex how"><h5>How it's fixed</h5><p>${esc(current.how || "—")}</p></div>` : "";
  drawDiff(); $("result").classList.add("show");
}
function drawDiff() { const w = $("diffWrap"); w.innerHTML = view === "unified" ? renderUnified(current.orig, current.fixed_code) : view === "split" ? renderSplit(current.orig, current.fixed_code) : `<pre class="code">${esc(current.fixed_code)}</pre>`; }
$("seg").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; view = b.dataset.v; [...$("seg").children].forEach(x => x.classList.toggle("active", x === b)); drawDiff(); });
$("applyBtn").onclick = () => { codeEl.value = current.fixed_code; updateMeta(); toast("Patch applied to editor"); codeEl.scrollIntoView({behavior: "smooth", block: "center"}); };
$("copyBtn").onclick = async () => { await navigator.clipboard.writeText(current.fixed_code); toast("Fixed code copied"); };
$("patchBtn").onclick = () => download(current.name.replace(/\.\w+$/, ".patch"), unifiedPatchText(current.orig, current.fixed_code, current.name), "text/x-diff");
$("mdBtn").onclick = () => download("edufix-report.md", `### EduFix patch \`${current.name}\`\n\n**What:** ${current.what}\n\n**Why:** ${current.why}\n\n**How:** ${current.how}\n\n\`\`\`${current.lang}\n${current.fixed_code}\n\`\`\`\n`, "text/markdown");
updateMeta();
</script>
</body>
</html>
