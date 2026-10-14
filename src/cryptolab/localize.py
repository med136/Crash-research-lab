"""Built-in bilingual French/English localization for offline report panels.

Text-node translation means all original English labels remain available.
There is no external translation service, third-party JS, or user tracking.
"""
from __future__ import annotations


def bilingual_html(html: str) -> str:
    if "<body>" not in html or "</body>" not in html or "</header>" not in html:
        raise ValueError("Expected a complete HTML dashboard")
    html = html.replace('<html lang="en">','<html lang="fr">',1)
    widget = """<nav class="locale-switch" aria-label="Langue / Language">
<button type="button" id="locale-fr" aria-pressed="true" aria-label="Français">FR</button>
<button type="button" id="locale-en" aria-pressed="false" aria-label="English">EN</button>
</nav>"""
    html=html.replace("</header>", widget+"</header>",1)
    css="""<style>
.locale-switch{display:flex;gap:4px;background:#0e192d;border:1px solid #334864;padding:4px;border-radius:11px}
.locale-switch button{border:0;background:transparent;color:#9eb2d0;padding:8px 12px;border-radius:7px;cursor:pointer;font-size:12px;font-weight:800}
.locale-switch button[aria-pressed="true"]{background:#287a78;color:#fff}
.locale-switch button:focus-visible{outline:2px solid #a1f0dc;outline-offset:2px}
</style>
"""
    html=html.replace("</head>",css+"</head>",1)
    js=r"""<script>
"use strict";
(function(){
 const D={
 "Research Cockpit":"Tableau de recherche",
 "Multi-asset quantitative diagnostics":"Diagnostics quantitatifs multi-actifs",
 "● PAPER ONLY · NO REAL ORDERS":"● SIMULATION UNIQUEMENT · AUCUN ORDRE RÉEL",
 "Cross-sectional risk laboratory · fixed historical data":"Laboratoire de risque multi-actifs · données historiques figées",
 "Market intelligence, without guesswork.":"Analyse des marchés fondée sur des données.",
 "Transparent regime signals and apples-to-apples BTC/altcoin backtests. This is a historical research report, not a profit forecast or active trading account.":"Signaux transparents et tests comparables sur BTC et les altcoins. Rapport de recherche historique, sans prévision de bénéfice ni compte de trading actif.",
 "Requested assets":"Actifs demandés",
 "USDT spot pairs in predefined universe":"Paires USDT spot de l'univers prédéfini",
 "Validated histories":"Historiques validés",
 "Strict daily OHLCV and frozen end date":"OHLCV validées et date finale fixe",
 "Better than passive":"Meilleurs que l'achat-conservation",
 "Assets with positive median fold excess":"Actifs à surperformance médiane positive",
 "Incomplete / failed":"Données incomplètes / échecs",
 "Never silently exclude missing histories":"Les données manquantes restent visibles",
 "Strategy comparison by asset":"Comparaison des stratégies par actif",
 "Daily Volatility Trend vs simple Buy & Hold. Each fold starts at the same virtual capital; base fees 0.10%, slippage 0.05%. Returns below are mean PER WINDOW, not annualized.":"Tendance à volatilité ciblée contre achat-conservation. Chaque période utilise le même capital virtuel ; frais 0,10 %, glissement 0,05 %. Rendements moyens PAR PÉRIODE, non annualisés.",
 "Market":"Marché",
 "Advisor regime":"Régime détecté",
 "Signal votes":"Votes des signaux",
 "Trend return":"Rendement de la tendance",
 "Buy & Hold":"Achat-conservation",
 "Return gap":"Écart de rendement",
 "DD improvement":"Réduction du drawdown",
 "Double-cost excess":"Écart avec frais doublés",
 "Wins / folds":"Gains / périodes",
 "Click a row to inspect fold-by-fold returns. A positive historical gap does not establish a statistically reliable trading edge.":"Cliquez sur une ligne pour analyser chaque période. Un écart positif historique ne prouve pas un avantage statistiquement fiable.",
 "Asset breakdown":"Analyse de l'actif",
 "Select a verified asset to inspect the decision signals.":"Sélectionnez un actif validé pour examiner les signaux.",
 "EXPLORATORY":"EXPLORATOIRE",
 "Relative 90-day return by chronological fold":"Rendement relatif par période chronologique de 90 jours",
 "Trailing 200-day trend":"Tendance SMA 200 périodes",
 "30-day momentum":"Momentum 30 périodes",
 "Realized annualized volatility":"Volatilité réalisée annualisée",
 "Suggested *maximum virtual* exposure":"Exposition virtuelle maximale proposée",
 "Evidence & risk controls":"Preuves et contrôles des risques",
 "No validated profitability claim.":"Aucune rentabilité démontrée.",
 "We explicitly retain losing crypto pairs and adverse cost results. The 0–100 advisor vote score is NOT a probability of profit and is not a trained AI model.":"Les actifs perdants et scénarios de frais défavorables restent visibles. Le score 0–100 n'est ni une probabilité de gain ni un modèle d'IA entraîné.",
 "Validation provenance":"Traçabilité des données",
 "Cutoff, UTC":"Date limite UTC",
 "Daily candles / symbol":"Bougies par actif",
 "Fold bars":"Bougies par période",
 "Mode":"Mode",
 "NO REAL ORDERS":"AUCUN ORDRE RÉEL",
 "Known study limitations":"Limites connues de l'étude",
 "Failed or excluded markets":"Marchés échoués ou exclus",
 "Source: public Binance spot daily OHLCV. Fixed historical cutoff and raw JSON SHA-256 are stored in the companion JSON manifest. Research is exploratory; transaction fills and market impact are modeled, not observed. Historical assets were selected from currently listed markets, which introduces survivorship bias.":"Source : OHLCV publiques Binance Spot. La date de référence et le SHA-256 des données figurent dans le JSON associé. Recherche exploratoire : prix d'exécution et impact de marché simulés. Sélection d'actifs actuellement cotés = biais de survie.",
 "Sort: drawdown improvement":"Trier : réduction du drawdown",
 "Sort: return advantage":"Trier : avantage de rendement",
 "Sort: median advantage":"Trier : avantage médian",
 "Sort: symbol":"Trier : symbole",
 "No matching verified assets":"Aucun actif validé correspondant",
 "uptrend":"Tendance haussière","downtrend":"Tendance baissière","high_volatility":"Volatilité élevée",
 "Above 200d SMA":"Au-dessus de SMA 200","Below 200d SMA":"En dessous de SMA 200",
 "UNVALIDATED_RESEARCH_ONLY":"RECHERCHE NON VALIDÉE",
 "Crypto multi-timeframe diagnostics":"Diagnostic crypto multi-unités de temps",
 "Multi-timeframe research laboratory":"Laboratoire de recherche multi-unités de temps",
 "Small timeframes, strict evidence.":"Petites unités de temps, vérification rigoureuse.",
 "Compare BTC, ETH and altcoins across 5m, 15m, 1h and 4h. All historical outcomes are hypothetical.":"Comparez BTC, ETH et les altcoins en 5m, 15m, 1h et 4h. Tous les résultats sont des simulations historiques.",
 "Validated market/frames":"Marchés et unités validés",
 "Requested combinations":"Combinaisons demandées",
 "Positive relative median":"Médiane relative positive",
 "Failed combinations":"Combinaisons en échec",
 "Research matrix":"Matrice de recherche",
 "Timeframe":"Unité de temps",
 "Periods":"Périodes",
 "Average trend return":"Rendement moyen de la tendance",
 "Passive return":"Rendement de référence",
 "Median excess":"Surperformance médiane",
 "Mean drawdown improvement":"Réduction moyenne du drawdown",
 "Adverse-cost excess":"Écart avec frais défavorables",
 "Trading activity":"Activité simulée",
 "Select timeframe":"Choisir l'unité",
 "All frames":"Toutes les unités",
 "All assets":"Tous les actifs",
 "Select asset":"Choisir l'actif",
 "No results for selected filters":"Aucun résultat pour les filtres",
 "How to read these results":"Comment lire ces résultats",
 "Ninety 5-minute bars cover 7.5 hours; ninety 4-hour bars cover 15 days. Never rank raw returns across those windows.":"90 bougies de 5 minutes couvrent 7,5 heures ; 90 bougies de 4 heures couvrent 15 jours. Ne comparez pas directement ces rendements.",
 "No live trades · No proven profitable strategy":"Aucun ordre réel · Aucune stratégie rentable démontrée",
 "Data coverage":"Couverture des données",
 "Run details":"Détails de l'exécution",
 "Raw results with errors included":"Résultats bruts, erreurs incluses",
 "Current listed pairs create survivorship bias; not a historical universe.":"Les paires cotées aujourd'hui induisent un biais de survie.",
 "Asset returns are correlated: 15 pairs are not 15 independent experiments.":"Les rendements des actifs sont corrélés : 15 paires ne constituent pas 15 expériences indépendantes.",
 "Earlier BTC model development reused part of this history; NOT pristine validation.":"Le développement initial sur BTC a utilisé une partie de cet historique : validation non indépendante.",
 "All fills are hypothetical and depend on exchange costs and actual liquidity.":"Les exécutions sont hypothétiques et dépendent des frais et de la liquidité réelle.",
 "The advisor's vote score is an interpretable heuristic, NOT ML or calibrated probability.":"Le score du conseiller est une heuristique explicable, ni machine learning ni probabilité calibrée.",
 "Short 5m/15m histories are not multiple market cycles.":"Les courts historiques 5m/15m ne couvrent pas plusieurs cycles de marché.",
 "90-bar test windows represent different wall-clock periods for each frame.":"Les fenêtres de 90 bougies représentent des durées différentes selon l'unité.",
 "Annualized 5m realized volatility uses 105120 bars/year versus 365 for 1d.":"La volatilité annualisée en 5m utilise 105 120 bougies/an contre 365 en 1d.",
 "This technical diagnostic is not independent historical evidence of profitability.":"Ce diagnostic technique ne prouve aucune rentabilité historique indépendante.",
 "Fees and slippage are modeled; spreads, book impact and partial fills are not.":"Frais et glissement sont simulés ; spreads, impact sur le carnet et exécutions partielles ne le sont pas.",
 "Asset selection and model development can bias results; assets are correlated.":"La sélection des actifs et l'optimisation peuvent biaiser les résultats ; les actifs sont corrélés."
 };
 let language="fr";
 const memo=new WeakMap();
 function french(source) {
   const stripped=source.trim();
   if (Object.prototype.hasOwnProperty.call(D,stripped))return source.replace(stripped,D[stripped]);
   if (stripped.startsWith("Cutoff: "))return source.replace("Cutoff: ","Date limite : ");
   if (stripped.includes(" / Decision diagnostics"))return source.replace(" / Decision diagnostics"," / Diagnostic des signaux");
   if (stripped.startsWith("Causal signals from completed daily candles"))return source.replace("Causal signals from completed daily candles","Signaux causaux calculés sur des bougies clôturées");
   return source;
 }
 function translateNode(n){
   if(!n.parentElement || n.parentElement.closest("script,style,textarea"))return;
   const prev=memo.get(n);
   if(!prev || n.nodeValue!==prev.rendered) memo.set(n,{original:n.nodeValue,rendered:null});
   const data=memo.get(n),target=language==="fr"?french(data.original):data.original;
   if(n.nodeValue!==target)n.nodeValue=target;
   data.rendered=target;
 }
 let queued=false;
 function apply(){
   const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
   let n;while((n=walker.nextNode()))translateNode(n);
   const input=document.getElementById("filter");
   if(input)input.placeholder=language==="fr"?"Rechercher un symbole…":"Filter symbol…";
   document.documentElement.lang=language;
   document.getElementById("locale-fr").setAttribute("aria-pressed",String(language==="fr"));
   document.getElementById("locale-en").setAttribute("aria-pressed",String(language==="en"));
 }
 function schedule(){
   if(queued)return;
   queued=true;queueMicrotask(()=>{queued=false;apply()});
 }
 document.getElementById("locale-fr").addEventListener("click",()=>{language="fr";schedule()});
 document.getElementById("locale-en").addEventListener("click",()=>{language="en";schedule()});
 const observer=new MutationObserver(schedule);
 observer.observe(document.body,{characterData:true,childList:true,subtree:true});
 apply();
})();
</script>"""
    return html.replace("</body>",js+"\n</body>",1)
