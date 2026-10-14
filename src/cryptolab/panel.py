"""Offline interactive HTML research dashboard; renders only verified report data.

No remote scripts, trading connections, external credentials, fake prices,
or live execution. Save the output and open directly in a browser.
"""
from __future__ import annotations
import json
from .localize import bilingual_html


def render_panel(report: dict) -> str:
    if report.get("study") != "CRYPTO_LAB_CROSS_SECTIONAL_RESEARCH_V1":
        raise ValueError("Unsupported report type")
    # Escape content for inline JS context, even if upstream market data is untrusted.
    raw = json.dumps(report,ensure_ascii=False,allow_nan=False)
    raw = raw.replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026").replace("\u2028","\\u2028").replace("\u2029","\\u2029")
    return bilingual_html("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>CryptoLab — Research Cockpit</title>
<style>
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif;background:#080d19;color:#eef4ff;--muted:#8d9ab5;--border:#263249;--panel:#131e32;--green:#5fe3b0;--red:#ff8799;--blue:#79acff;--gold:#ffd18a}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 10% 0%,#13284b 0%,#080d19 47%) fixed;color:#eef4ff}
header{max-width:1550px;margin:auto;padding:23px 28px;border-bottom:1px solid #233049;display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap}
.brand{display:flex;gap:13px;align-items:center}.logo{width:40px;height:40px;border-radius:12px;background:linear-gradient(140deg,#39eac6,#4c7dea);display:grid;place-items:center;color:#061222;font-weight:900;font-size:22px}
h1{font-size:20px;letter-spacing:-.5px;margin:0}h2{margin:0 0 12px;font-size:18px;letter-spacing:-.3px}h3{font-size:14px;margin:0 0 9px}
small,.muted{color:var(--muted)}.top-note{display:flex;gap:8px;align-items:center;color:var(--gold);font-weight:650;font-size:12px;letter-spacing:.3px;border:1px solid #755b32;padding:9px 12px;border-radius:99px;background:#36271655}
main{max-width:1550px;margin:auto;padding:26px 28px 70px}
.overline{font-size:11px;letter-spacing:1.8px;text-transform:uppercase;color:#8ba5c6;font-weight:750}
.title-line{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin:10px 0 18px}
.title-line h2{font-size:30px;margin:0}.subtitle{font-size:13px;color:var(--muted);max-width:780px;line-height:1.6}
.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:16px}
.card,.section{background:linear-gradient(140deg,#16233a,#111b2e);border:1px solid var(--border);border-radius:17px;padding:19px;box-shadow:0 13px 30px #050b1938}
.metric{font-size:31px;font-weight:750;letter-spacing:-1px;margin:9px 0 5px}.metric-desc{font-size:12px;color:var(--muted)}
.divider{height:1px;background:var(--border);margin:14px 0}.green{color:var(--green)}.red{color:var(--red)}.blue{color:var(--blue)}.gold{color:var(--gold)}
.section{margin-top:16px}.section-header{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:14px}
.controls{display:flex;gap:10px;flex-wrap:wrap}input,select{background:#0b1528;color:#ebf2ff;border:1px solid #334664;border-radius:10px;padding:10px 12px;font:inherit;font-size:13px;min-width:130px}input{min-width:170px}input:focus,select:focus,button:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;white-space:nowrap}th{text-align:right;font-size:11px;color:#8e9fbd;text-transform:uppercase;letter-spacing:.5px;font-weight:700;padding:13px 12px;border-bottom:1px solid var(--border)}th:first-child,td:first-child{text-align:left}td{font-size:13px;padding:15px 12px;border-bottom:1px solid #233047}
tbody tr{cursor:pointer;transition:background .15s}tbody tr:hover,tbody tr.selected{background:#223552}tbody tr:last-child td{border-bottom:0}
.token{display:flex;align-items:center;gap:10px;font-weight:800;letter-spacing:.2px}.avatar{width:31px;height:31px;border-radius:50%;display:grid;place-items:center;background:#223d5d;color:#b0d2fa;font-size:12px}
.pill{padding:5px 8px;border-radius:7px;font-size:11px;font-weight:760;background:#23344b;color:#b9c9e0}.pill.long{color:#7fe6bc;background:#134837}.pill.cash{color:#a5b8cf;background:#293548}
.columns{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(300px,.85fr);gap:16px;margin-top:16px}.detail-main{font-size:32px;font-weight:750;letter-spacing:-.8px;margin:7px 0}.row{display:flex;align-items:center;justify-content:space-between;gap:14px;margin:10px 0;font-size:13px}.row span:last-child{font-weight:650}
.folds{display:flex;align-items:stretch;justify-content:space-between;gap:5px;height:180px;margin-top:14px;border-bottom:1px solid #3a4c68;padding-top:10px}.fold{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:6px;min-width:0}.bar-space{height:130px;width:100%;display:flex;align-items:center;justify-content:center;position:relative}.axis{position:absolute;left:0;right:0;top:50%;height:1px;background:#52627a44}.bar{position:absolute;bottom:50%;width:55%;max-width:33px;border-radius:5px 5px 0 0;background:linear-gradient(#63dfb2,#24886f)}.bar.neg{top:50%;bottom:auto;border-radius:0 0 5px 5px;background:linear-gradient(#7a344f,#ff8193)}.tick{font-size:10px;color:var(--muted);white-space:nowrap}
.footer{line-height:1.7;font-size:12px;color:#a3b2ce}.error{border:1px solid #7f4a57;background:#3b2230;padding:11px;border-radius:10px;color:#ffb3c0;margin:8px 0;font-size:12px;overflow-wrap:anywhere}
.notice{background:#122c33;border:1px solid #2b5d62;padding:12px;border-radius:11px;color:#b8e9e5;font-size:12px;line-height:1.6}
@media(max-width:1000px){.cards{grid-template-columns:repeat(2,minmax(0,1fr))}.columns{grid-template-columns:1fr}}
@media(max-width:540px){main{padding:18px 12px 55px}header{padding:17px 13px}.cards{gap:8px}.card,.section{padding:13px}.metric{font-size:26px}.title-line h2{font-size:24px}.top-note{font-size:10px}input,select{width:100%}.controls{width:100%}}
</style>
</head>
<body>
<header>
  <div class="brand"><div class="logo" aria-hidden="true">∿</div><div><h1>CryptoLab <span style="color:#60dcc2">/ Research Cockpit</span></h1><small>Multi-asset quantitative diagnostics</small></div></div>
  <div class="top-note">● PAPER ONLY · NO REAL ORDERS</div>
</header>
<main>
 <div class="overline">Cross-sectional risk laboratory · fixed historical data</div>
 <div class="title-line"><div><h2>Market intelligence, without guesswork.</h2><div class="subtitle">Transparent regime signals and apples-to-apples BTC/altcoin backtests. This is a historical research report, not a profit forecast or active trading account.</div></div><div class="muted" style="font-size:12px" id="cutoff"></div></div>
 <section class="cards" aria-label="Study metrics">
  <div class="card"><div class="overline">Requested assets</div><div class="metric" id="requested">—</div><div class="metric-desc">USDT spot pairs in predefined universe</div></div>
  <div class="card"><div class="overline">Validated histories</div><div class="metric green" id="passed">—</div><div class="metric-desc">Strict daily OHLCV and frozen end date</div></div>
  <div class="card"><div class="overline">Better than passive</div><div class="metric blue" id="beats">—</div><div class="metric-desc">Assets with positive median fold excess</div></div>
  <div class="card"><div class="overline">Incomplete / failed</div><div class="metric" id="failed">—</div><div class="metric-desc">Never silently exclude missing histories</div></div>
 </section>
 <section class="section">
  <div class="section-header"><div><h2>Strategy comparison by asset</h2><div class="subtitle">Daily Volatility Trend vs simple Buy &amp; Hold. Each fold starts at the same virtual capital; base fees 0.10%, slippage 0.05%. Returns below are mean PER WINDOW, not annualized.</div></div>
   <div class="controls"><input id="filter" type="search" placeholder="Filter symbol…" aria-label="Filter cryptocurrency symbol"><select id="sort" aria-label="Sort cryptocurrency assets"><option value="risk">Sort: drawdown improvement</option><option value="excess">Sort: return advantage</option><option value="median">Sort: median advantage</option><option value="symbol">Sort: symbol</option></select></div></div>
  <div class="table-wrap"><table><thead><tr><th>Market</th><th>Advisor regime</th><th>Signal votes</th><th>Trend return</th><th>Buy &amp; Hold</th><th>Return gap</th><th>DD improvement</th><th>Double-cost excess</th><th>Wins / folds</th></tr></thead><tbody id="coins"></tbody></table></div>
  <div class="subtitle" style="margin-top:14px">Click a row to inspect fold-by-fold returns. A positive historical gap does not establish a statistically reliable trading edge.</div>
 </section>
 <div class="columns">
  <section class="section" style="margin-top:0"><div class="section-header"><div><h2 id="detailTitle">Asset breakdown</h2><div class="subtitle" id="detailCaption">Select a verified asset to inspect the decision signals.</div></div><span class="pill" id="modelTag">EXPLORATORY</span></div>
   <div class="divider"></div><div class="overline">Relative 90-day return by chronological fold</div><div class="folds" id="foldChart" role="img" aria-label="Green bars outperformance, red bars underperformance"></div><div class="divider"></div>
   <div class="row"><span class="muted">Trailing 200-day trend</span><span id="signalTrend">—</span></div>
   <div class="row"><span class="muted">30-day momentum</span><span id="signalMomentum">—</span></div>
   <div class="row"><span class="muted">Realized annualized volatility</span><span id="signalVol">—</span></div>
   <div class="row"><span class="muted">Suggested *maximum virtual* exposure</span><span id="signalExposure">—</span></div>
  </section>
  <section class="section" style="margin-top:0"><h2>Evidence &amp; risk controls</h2><div class="notice"><strong>No validated profitability claim.</strong> We explicitly retain losing crypto pairs and adverse cost results. The 0–100 advisor vote score is NOT a probability of profit and is not a trained AI model.</div>
   <div class="divider"></div><h3>Validation provenance</h3><div class="row"><span class="muted">Cutoff, UTC</span><span id="provenanceDate">—</span></div><div class="row"><span class="muted">Daily candles / symbol</span><span id="barCount">—</span></div><div class="row"><span class="muted">Fold bars</span><span id="foldBars">—</span></div><div class="row"><span class="muted">Mode</span><span class="gold">NO REAL ORDERS</span></div>
   <div class="divider"></div><h3>Known study limitations</h3><div id="limitations" class="footer"></div>
   <div id="failBox" style="display:none"><div class="divider"></div><h3>Failed or excluded markets</h3><div id="errors"></div></div>
  </section>
 </div>
 <p class="footer">Source: public Binance spot daily OHLCV. Fixed historical cutoff and raw JSON SHA-256 are stored in the companion JSON manifest. Research is exploratory; transaction fills and market impact are modeled, not observed. Historical assets were selected from currently listed markets, which introduces survivorship bias.</p>
</main>
<script>
"use strict";
const DATA = __REPORT_DATA__;
const $=id=>document.getElementById(id);
const rows=Object.entries(DATA.results||{}).map(([symbol,r])=>({symbol,...r}));
let active=rows[0]?.symbol || null;
const fmt=(v,n=2)=>Number.isFinite(Number(v)) ? Number(v).toFixed(n) : "—";
const pct=(v)=>fmt(v)+"%";
const signed=(v)=>((Number(v)>0)?"+":"")+pct(v);
const cell=(row,txt,css="")=>{const td=document.createElement("td");td.textContent=txt;if(css)td.className=css;row.appendChild(td);return td;};
function view(){
 const filter=$("filter").value.toUpperCase().trim(), sort=$("sort").value;
 let list=rows.filter(x=>x.symbol.includes(filter));
 const score=x=>x.research.scenarios.base;
 list.sort((a,b)=>{
  if(sort==="symbol")return a.symbol.localeCompare(b.symbol);
  const key=sort==="risk"?"mean_drawdown_improvement_pp":sort==="median"?"median_excess_pp":"mean_excess_pp";
  return score(b)[key]-score(a)[key];
 });
 const parent=$("coins");parent.replaceChildren();
 list.forEach(x=>{
  const s=x.research.scenarios,base=s.base,ad=x.research.advisor;
  const tr=document.createElement("tr");tr.tabIndex=0;tr.setAttribute("role","button");tr.setAttribute("aria-label","Inspect "+x.symbol);
  if(x.symbol===active)tr.className="selected";
  const first=cell(tr,x.symbol);first.style.fontWeight="750";
  cell(tr,ad.regime);
  cell(tr,ad.score_votes+"/100");
  cell(tr,signed(base.voltrend_mean_return_pct),base.voltrend_mean_return_pct>=0?"green":"red");
  cell(tr,signed(base.hold_mean_return_pct));
  cell(tr,signed(base.mean_excess_pp),base.mean_excess_pp>=0?"green":"red");
  cell(tr,signed(base.mean_drawdown_improvement_pp),base.mean_drawdown_improvement_pp>0?"green":"red");
  cell(tr,signed(s.double_cost.mean_excess_pp),s.double_cost.mean_excess_pp>0?"green":"red");
  cell(tr,base.beats_hold_windows+"/"+base.folds);
  const choose=()=>{active=x.symbol;detail();view()};
  tr.onclick=choose;
  tr.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();choose()}};
  parent.appendChild(tr);
 });
 if(!list.length){const tr=document.createElement("tr");cell(tr,"No matching verified assets");parent.appendChild(tr)}
}
function detail(){
 const x=rows.find(x=>x.symbol===active);if(!x)return;
 const ad=x.research.advisor, sig=ad.signals, vals=ad.indicators;
 $("detailTitle").textContent=x.symbol+" / Decision diagnostics";
 $("detailCaption").textContent="Causal signals from completed daily candles · "+ad.mode.replaceAll("_"," ");
 $("modelTag").textContent=ad.status;
 $("signalTrend").textContent=sig.above_sma200?"Above 200d SMA":"Below 200d SMA";
 $("signalTrend").className=sig.above_sma200?"green":"red";
 $("signalMomentum").textContent=signed(vals.momentum30_pct);
 $("signalVol").textContent=pct(vals.annualized_volatility_pct);
 $("signalExposure").textContent=pct(ad.max_exposure*100);
 const chart=$("foldChart");chart.replaceChildren();
 x.research.base_folds.forEach((f,i)=>{
  const diff=f.strategy_return_pct-f.hold_return_pct;
  const col=document.createElement("div");col.className="fold";col.title="Fold "+(i+1)+": "+signed(diff)+" relative";
  const barspace=document.createElement("div");barspace.className="bar-space";
  const axis=document.createElement("div");axis.className="axis";barspace.appendChild(axis);
  const bar=document.createElement("div");bar.className="bar"+(diff<0?" neg":"");
  bar.style.height=Math.max(1,Math.min(48,Math.abs(diff)*.75))+"%";
  barspace.appendChild(bar);col.appendChild(barspace);
  const tick=document.createElement("div");tick.className="tick";tick.textContent="#"+(i+1);col.appendChild(tick);chart.appendChild(col);
 });
}
$("cutoff").textContent="Cutoff: "+DATA.data_cutoff_utc+" · Frozen snapshot";
$("requested").textContent=DATA.symbols_requested.length;
$("passed").textContent=DATA.successful_symbols;
$("failed").textContent=DATA.failed_symbols;
$("beats").textContent=rows.filter(x=>x.research.scenarios.base.median_excess_pp>0).length+" / "+rows.length;
$("provenanceDate").textContent=DATA.data_cutoff_utc;
$("barCount").textContent=DATA.requested_bars;
$("foldBars").textContent=DATA.fold_bars;
const ul=document.createElement("ul");
(DATA.limitations||[]).forEach(text=>{const li=document.createElement("li");li.textContent=text;ul.appendChild(li)});
$("limitations").replaceChildren(ul);
if(DATA.failed_symbols){$("failBox").style.display="block";
 Object.entries(DATA.errors).forEach(([symbol,error])=>{
  const p=document.createElement("div");p.className="error";p.textContent=symbol+": "+error;$("errors").appendChild(p);
 })}
$("filter").addEventListener("input",view);
$("sort").addEventListener("change",view);
view();detail();
</script>
</body></html>""".replace("__REPORT_DATA__",raw))
