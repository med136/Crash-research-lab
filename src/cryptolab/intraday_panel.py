"""Offline interactive research matrix, with French default / English toggle."""
from __future__ import annotations
import json
from .localize import bilingual_html


def render_timeframe_panel(report: dict) -> str:
    if report.get("study")!="CRYPTO_LAB_MULTI_TIMEFRAME_V1":
        raise ValueError("Unsupported multi-timeframe report")
    raw=json.dumps(report,ensure_ascii=False,allow_nan=False)
    raw=(raw.replace("<","\\u003c").replace(">","\\u003e")
         .replace("&","\\u0026").replace("\u2028","\\u2028").replace("\u2029","\\u2029"))
    html = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>CryptoLab — Multi-timeframe research</title>
<style>
:root{font-family:Inter,ui-sans-serif,system-ui,Segoe UI,Arial;background:#09101f;color:#e9f0ff;--muted:#99a9c5;--panel:#17243a;--border:#2a3a55}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 15% 0%,#1a3657 0,#09101f 48%) fixed}
header{padding:19px max(20px,calc((100vw - 1280px)/2));border-bottom:1px solid #2c3b58;display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:12px}.logo{background:linear-gradient(135deg,#52f3bb,#659afb);color:#05182d;border-radius:13px;width:42px;height:42px;font-weight:900;display:grid;place-items:center}
h1{font-size:21px;margin:0;letter-spacing:-.7px}h2{font-size:19px;margin:0 0 10px}small,.muted{color:var(--muted)}main{max-width:1330px;margin:auto;padding:28px 25px 70px}
.flag{color:#ffce83;border:1px solid #816d43;border-radius:50px;padding:8px 11px;font-size:11px;font-weight:800}
.hero h2{font-size:31px;letter-spacing:-1px}.hero p{max-width:850px;line-height:1.6;color:var(--muted);font-size:14px}
.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;margin:22px 0}
.box{background:linear-gradient(145deg,#172640,#101d32);border:1px solid var(--border);border-radius:16px;padding:18px}
.eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:1.4px;font-weight:700;color:#91b1cf}.value{font-size:31px;font-weight:800;margin:6px 0;color:#8ae4bc}
.meta{color:var(--muted);font-size:12px}.filters{display:flex;gap:12px;flex-wrap:wrap;margin:14px 0 19px}
select,input{border:1px solid #385271;background:#0d192d;color:#e8f1ff;border-radius:10px;padding:10px 13px;font:inherit;font-size:13px}
table{width:100%;border-collapse:collapse;white-space:nowrap}th,td{border-bottom:1px solid #2b3850;padding:13px 12px;font-size:13px;text-align:right}th{text-transform:uppercase;font-size:11px;letter-spacing:.45px;color:#94a7c7}td:first-child,th:first-child{text-align:left}
.tablewrap{overflow:auto}.pos{color:#6ae3aa}.neg{color:#ff8797}.pill{display:inline-block;border-radius:7px;padding:4px 8px;background:#253854;font-size:12px;font-weight:750}
.info{background:#112c32;border:1px solid #2c6467;color:#c7f5e7;border-radius:12px;padding:15px;font-size:13px;line-height:1.7;margin-top:15px}
.notice{color:#b1bfd6;line-height:1.7;font-size:12px;margin-top:15px}
.error{padding:9px 12px;background:#472733;border-radius:10px;border:1px solid #8b5269;color:#ffc1cc;overflow-wrap:anywhere;margin-top:8px;font-size:12px}
@media(max-width:900px){.cards{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:520px){header{padding:12px}main{padding:18px 12px 50px}.cards{gap:8px}.box{padding:13px}.hero h2{font-size:25px}}
</style></head>
<body>
<header><div class="brand"><div class="logo">∿</div><div><h1>CryptoLab / Intraday</h1><small>Crypto multi-timeframe diagnostics</small></div></div>
<div class="flag">● PAPER ONLY · NO REAL ORDERS</div></header>
<main>
<div class="hero"><div class="eyebrow">Multi-timeframe research laboratory</div>
<h2>Small timeframes, strict evidence.</h2>
<p>Compare BTC, ETH and altcoins across 5m, 15m, 1h and 4h. All historical outcomes are hypothetical.</p></div>
<div class="cards">
<div class="box"><div class="eyebrow">Requested combinations</div><div class="value" id="total">—</div><div class="meta">Symbol × timeframe</div></div>
<div class="box"><div class="eyebrow">Validated market/frames</div><div class="value" id="success">—</div><div class="meta">Completed OHLCV only</div></div>
<div class="box"><div class="eyebrow">Positive relative median</div><div class="value" id="positive">—</div><div class="meta">Exploratory, not predictive</div></div>
<div class="box"><div class="eyebrow">Failed combinations</div><div class="value" id="failed">—</div><div class="meta">Errors are not hidden</div></div>
</div>
<div class="box">
<h2>Research matrix</h2>
<div class="filters">
<select id="frame" aria-label="Select timeframe"><option value="all">All frames</option></select>
<select id="symbol" aria-label="Select asset"><option value="all">All assets</option></select>
</div>
<div class="tablewrap"><table>
<thead><tr><th>Market</th><th>Timeframe</th><th>Periods</th><th>Average trend return</th><th>Passive return</th><th>Median excess</th><th>Mean drawdown improvement</th><th>Adverse-cost excess</th><th>Trading activity</th></tr></thead>
<tbody id="bodyRows"></tbody>
</table></div>
<div class="info"><strong>How to read these results</strong><p>Ninety 5-minute bars cover 7.5 hours; ninety 4-hour bars cover 15 days. Never rank raw returns across those windows.</p></div>
</div>
<div class="box" style="margin-top:16px"><h2>Run details</h2>
<div class="meta" id="summary"></div><h3>Data coverage</h3><p id="coverage" class="notice"></p>
<h3>Raw results with errors included</h3><div id="errors"></div>
</div>
<p class="notice">No live trades · No proven profitable strategy. Public Binance spot OHLCV, raw response hashes saved with JSON data. The model is a pre-existing heuristic, not a trained AI or execution-capable signal.</p>
</main>
<script>
"use strict";
const DATA=__REPORT_DATA__;
const $=id=>document.getElementById(id);
const records=Object.entries(DATA.results||{}).map(([key,val])=>({key,symbol:val.data.symbol,frame:val.data.timeframe,data:val}));
const pct=x=>(Number(x)>0?"+":"")+Number(x).toFixed(2)+"%";
const create=(node,name,text,cls="")=>{const element=document.createElement(name);element.textContent=text;if(cls)element.className=cls;node.appendChild(element);return element};
$("total").textContent=DATA.symbols_requested.length*DATA.frames_requested.length;
$("success").textContent=DATA.successful_markets;
$("positive").textContent=records.filter(r=>r.data.analysis.scenarios.base.excess_median_pp>0).length;
$("failed").textContent=DATA.failed_markets;
DATA.frames_requested.forEach(f=>{const op=create($("frame"),"option",f);op.value=f});
DATA.symbols_requested.forEach(s=>{const op=create($("symbol"),"option",s);op.value=s});
function populate(){
 let frame=$("frame").value,symbol=$("symbol").value,tbody=$("bodyRows");
 tbody.replaceChildren();
 let rows=records.filter(x=>(frame==="all"||x.frame===frame)&&(symbol==="all"||x.symbol===symbol));
 rows.sort((a,b)=>a.frame.localeCompare(b.frame)||a.symbol.localeCompare(b.symbol));
 rows.forEach(row=>{
   const stats=row.data.analysis.scenarios.base,adverse=row.data.analysis.scenarios.high_slippage;
   const tr=document.createElement("tr");
   create(tr,"td",row.symbol);
   create(tr,"td",row.frame);
   create(tr,"td",stats.fold_count);
   create(tr,"td",pct(stats.strategy_mean_pct),stats.strategy_mean_pct>=0?"pos":"neg");
   create(tr,"td",pct(stats.passive_mean_pct));
   create(tr,"td",pct(stats.excess_median_pp),stats.excess_median_pp>=0?"pos":"neg");
   create(tr,"td",pct(stats.drawdown_improvement_pp),stats.drawdown_improvement_pp>=0?"pos":"neg");
   create(tr,"td",pct(adverse.excess_mean_pp),adverse.excess_mean_pp>=0?"pos":"neg");
   create(tr,"td",stats.trades);
   tbody.appendChild(tr);
 });
 if(!rows.length){const tr=document.createElement("tr");const td=create(tr,"td","No results for selected filters");td.colSpan=9;tbody.appendChild(tr);}
}
$("frame").addEventListener("change",populate);$("symbol").addEventListener("change",populate);
$("summary").textContent="Cutoff: "+DATA.cutoff_utc+" · "+DATA.bars_per_market+" bars / symbol / frame · "+DATA.fold_size_bars+" bars / fold";
$("coverage").textContent=DATA.limitations.join(" · ");
Object.entries(DATA.errors||{}).forEach(([market,err])=>{create($("errors"),"div",market+": "+err,"error")});
populate();
</script></body></html>""".replace("__REPORT_DATA__",raw)
    return bilingual_html(html)
