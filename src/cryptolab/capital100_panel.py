"""Static, interactive FR-first / EN $100 historical study dashboard.

Never represents past returns as a forecast of $100 capital.
"""
from __future__ import annotations
import json
from .localize import bilingual_html

def render_capital_panel(report:dict) -> str:
    if report.get("study")!="CRYPTO_LAB_100_USD_EXPLORATORY_V1":
        raise ValueError("Unexpected research report")
    raw=json.dumps(report,ensure_ascii=False,allow_nan=False)
    raw=(raw.replace("<","\\u003c").replace(">","\\u003e")
         .replace("&","\\u0026").replace("\u2028","\\u2028").replace("\u2029","\\u2029"))
    html="""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark"><title>CryptoLab | 100 USD Research</title>
<style>
:root{font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;background:#081122;color:#ecf3ff;--panel:#16243a;--muted:#9aaec9;--border:#31405b;--green:#71e0b0;--red:#ff899c}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top left,#172d4b,#081122 52%) fixed}
header{padding:19px max(18px,calc((100vw - 1290px)/2));display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:18px;border-bottom:1px solid var(--border)}
header h1{font-size:22px;letter-spacing:-.7px;margin:0}.tag{border-radius:30px;padding:8px 12px;color:#fbd38e;border:1px solid #685538;background:#2d261b;font-weight:800;font-size:11px}
small,.muted{color:var(--muted)}main{max-width:1320px;margin:auto;padding:25px 20px 70px}h2{font-size:24px;letter-spacing:-.5px;margin:0 0 7px}h3{font-size:17px;margin:0 0 9px}
.intro{color:var(--muted);max-width:890px;line-height:1.7;margin:4px 0 23px}
.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:18px}
.card,.panel{background:linear-gradient(140deg,#172840,#0f1c31);border:1px solid var(--border);border-radius:16px;padding:19px}
.k{font-size:11px;color:#9cafc6;letter-spacing:1px;text-transform:uppercase;font-weight:800}.v{font-size:30px;font-weight:800;color:var(--green);margin:6px 0}
.controls{display:flex;flex-wrap:wrap;gap:12px;margin:16px 0}label{font-size:11px;color:#a4b9d4;display:flex;flex-direction:column;gap:6px;font-weight:700}
select{background:#081629;color:#fff;border:1px solid #415570;border-radius:9px;padding:10px 12px;min-width:160px;font:inherit}
.grid{display:grid;grid-template-columns:2fr 1fr;gap:14px}.hero-value{font-size:40px;letter-spacing:-1px;font-weight:800;margin:0}
.summary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.summary div{border:1px solid #35465d;background:#101e31;border-radius:11px;padding:12px}
.summary span{display:block;color:var(--muted);font-size:11px}.summary b{font-size:20px;font-variant-numeric:tabular-nums}
.range{display:flex;align-items:center;height:30px;margin:19px 0 22px;position:relative}.track{width:100%;height:6px;border-radius:8px;background:#294660;position:relative}
.range .marker{position:absolute;top:-8px;border-radius:7px;padding:5px 6px;background:#70dcb2;color:#082220;font-weight:900;font-size:10px;transform:translateX(-50%);white-space:nowrap}
.range .edge{position:absolute;top:11px;font-size:11px;color:#aebfce;white-space:nowrap}
.tablewrap{overflow:auto}table{width:100%;border-collapse:collapse;white-space:nowrap}td,th{text-align:right;border-bottom:1px solid #324059;padding:13px 11px;font-size:12px}td:first-child,th:first-child{text-align:left}th{font-size:10px;color:#9baec8;letter-spacing:.4px;text-transform:uppercase}
tr.selected{background:#213b52}tbody tr{cursor:pointer}tbody tr:hover{background:#233b53}
.pos{color:var(--green)}.neg{color:var(--red)}
.note{background:#162e31;border:1px solid #326966;border-radius:11px;padding:14px;line-height:1.7;font-size:12px;color:#c7ece3}
.risk{color:#ffc4cc;font-size:12px;background:#3b2831;padding:9px 12px;border-radius:8px;margin:8px 0;word-break:break-word}
@media(max-width:950px){.grid{grid-template-columns:1fr}.cards{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){header{padding:14px}main{padding:17px 11px 42px}.cards{gap:8px}.card,.panel{padding:13px}.summary{grid-template-columns:1fr 1fr}.v{font-size:26px}}
</style></head><body>
<header><div><h1>CryptoLab <span style="color:#64edbf">/ $100 Research</span></h1><small>Risk-focused historical simulations</small></div><div class="tag">● PAPER ONLY · NO REAL ORDERS</div></header>
<main><h2>What could $100 have become?</h2>
<p class="intro">Results below show past, separate simulations starting with $100. They are NOT predictions of what your real $100 will be worth after 1, 3, 6 or 12 months. All virtual trades include costs and are not real fills.</p>
<div class="cards">
<div class="card"><div class="k">Initial virtual capital</div><div class="v">$100</div><small>Each experiment restarts with this amount</small></div>
<div class="card"><div class="k">Validated markets</div><div class="v" id="validated">—</div><small>Separate tests, not a portfolio</small></div>
<div class="card"><div class="k">Candidate models</div><div class="v" id="candidates">—</div><small>Including cash and buy-and-hold controls</small></div>
<div class="card"><div class="k">Data cutoff</div><div class="v" style="font-size:19px" id="cutoff">—</div><small>Frozen historical UTC cutoff</small></div></div>
<div class="panel">
<h3>Historical window explorer</h3>
<div class="controls">
<label>Market<select id="asset"></select></label>
<label>Horizon<select id="horizon"></select></label>
<label>Costs<select id="cost"><option value="base">Base costs</option><option value="double_cost">Double costs</option><option value="adverse_slippage">Adverse slippage</option></select></label>
<label>Model<select id="model"></select></label>
</div>
<div class="grid"><div>
<div class="k">Historical median from $100</div><p class="hero-value" id="median">—</p>
<div class="summary"><div><span>Worst simulated window</span><b id="worst">—</b></div><div><span>Best simulated window</span><b id="best">—</b></div><div><span>Mean final balance</span><b id="mean">—</b></div><div><span>Positive windows</span><b id="positive">—</b></div><div><span>Beats Buy &amp; Hold</span><b id="beats">—</b></div><div><span>Mean max drawdown</span><b id="dd">—</b></div></div>
<div class="range"><div class="track" id="track"></div></div>
</div><div class="note"><strong>Important statistical caveats</strong><p>The 365-day horizon contains only about two non-overlapping windows per market. Assets are strongly correlated, current listings create survivorship bias, and model selection after seeing this table would overfit history.</p><p>Historical median and best outcome are descriptive, not expected return or guaranteed range.</p></div></div></div>
<div class="panel" style="margin-top:16px"><h3>All strategies under identical assumptions</h3><div class="tablewrap"><table><thead><tr><th>Candidate strategy</th><th>Historical mean $</th><th>Median $</th><th>Worst $</th><th>Best $</th><th>Beats hold</th><th>Mean max DD</th><th>Rebalances</th></tr></thead><tbody id="results"></tbody></table></div></div>
<div class="panel" style="margin-top:16px"><h3>Data errors and limitations</h3><div id="errors"></div><p class="intro" id="limitations"></p></div>
<p class="intro">Source: publicly visible Binance spot historical daily OHLCV with a fixed cutoff and recorded response hashes. All results assume next-open simulated execution, a $5 minimum trade approximation, no leverage, and liquidation at the window's last close.</p>
</main>
<script>
"use strict";
const DATA=__REPORT_DATA__;
const $=id=>document.getElementById(id);
const money=n=>"$"+Number(n).toFixed(2);
const cell=(tr,s,cls)=>{const td=document.createElement("td");td.textContent=s;if(cls)td.className=cls;tr.appendChild(td)};
let chosenModel="defensive_ensemble";
const names={cash:"Cash only",buy_hold:"Buy & Hold",sma20_60:"SMA 20/60",sma50_200:"SMA 50/200",breakout55_20:"Breakout 55/20",volatility_trend:"Volatility Trend",defensive_ensemble:"Defensive ensemble"};
Object.keys(DATA.assets||{}).forEach(x=>{let o=document.createElement("option");o.value=x;o.textContent=x;$("asset").appendChild(o)});
Object.keys(DATA.horizons||{}).forEach(x=>{let o=document.createElement("option");o.value=x;const names={"1_month_30d":"1 month (30 days)","3_months_90d":"3 months (90 days)","6_months_180d":"6 months (180 days)","1_year_365d":"1 year (365 days)"};o.textContent=names[x]||x;$("horizon").appendChild(o)});
(DATA.strategies||[]).forEach(s=>{let o=document.createElement("option");o.value=s;o.textContent=names[s]||s;$("model").appendChild(o)});
$("model").value=chosenModel;
$("validated").textContent=DATA.successful_assets+"/"+DATA.assets_requested.length;
$("candidates").textContent=DATA.strategies.length;
$("cutoff").textContent=DATA.historical_cutoff_utc;
$("limitations").textContent=(DATA.limitations||[]).join(" · ");
Object.entries(DATA.errors||{}).forEach(([asset,error])=>{const d=document.createElement("div");d.className="risk";d.textContent=asset+": "+error;$("errors").appendChild(d)});
function update(){
 const asset=$("asset").value,horizon=$("horizon").value,cost=$("cost").value,model=$("model").value;
 if(!asset||!DATA.assets[asset])return;
 const data=DATA.assets[asset].analysis.scenarios[cost][horizon];
 const stat=data.models[model];
 $("median").textContent=money(stat.median_final_usd);
 $("median").className="hero-value "+(stat.median_final_usd>=100?"pos":"neg");
 $("worst").textContent=money(stat.worst_final_usd);
 $("best").textContent=money(stat.best_final_usd);
 $("mean").textContent=money(stat.mean_final_usd);
 $("positive").textContent=stat.positive_windows+"/"+stat.folds;
 $("beats").textContent=stat.beats_hold_windows+"/"+stat.folds;
 $("dd").textContent=stat.mean_max_drawdown_pct.toFixed(1)+"%";
 const track=$("track");track.replaceChildren();
 const min=Math.min(100,stat.worst_final_usd),max=Math.max(100,stat.best_final_usd);
 const place=(value)=>5+90*(value-min)/(max-min||1);
 for(const [value,label] of [[stat.worst_final_usd,"MIN"],[stat.median_final_usd,"MED"],[stat.best_final_usd,"MAX"]]){
  const marker=document.createElement("span");marker.className="marker";marker.style.left=place(value)+"%";marker.textContent=label;track.appendChild(marker);
 }
 const parent=$("results");parent.replaceChildren();
 for(const [name,s] of Object.entries(data.models)){
  const tr=document.createElement("tr");if(name===model)tr.className="selected";
  cell(tr,names[name]||name);cell(tr,money(s.mean_final_usd),s.mean_final_usd>=100?"pos":"neg");
  cell(tr,money(s.median_final_usd),s.median_final_usd>=100?"pos":"neg");
  cell(tr,money(s.worst_final_usd));cell(tr,money(s.best_final_usd));
  cell(tr,s.beats_hold_windows+"/"+s.folds);cell(tr,s.mean_max_drawdown_pct.toFixed(1)+"%");
  cell(tr,String(s.mean_rebalances));
  tr.onclick=()=>{$("model").value=name;update()};parent.appendChild(tr);
 }
}
for(const x of ["asset","horizon","cost","model"])$(x).addEventListener("change",update);
update();
</script></body></html>""".replace("__REPORT_DATA__",raw)
    return bilingual_html(html)
