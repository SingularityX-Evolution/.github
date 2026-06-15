#!/usr/bin/env python3
"""生成合成标注链数据 + 跑完整评估"""

import sys, os, random
sys.path.insert(0, os.path.dirname(__file__))
random.seed(42)

import pandas as pd
import numpy as np

chains = []

# 1跳链（10条）
chains += [
    {"chain_id":"CH_001","hops":["FOMC cuts rates 25bp","USD liquidity eases"],"domain":"macro","label":True,"confidence_per_hop":[0.96,0.93],"notes":"Standard easing cycle"},
    {"chain_id":"CH_002","hops":["Russia-Ukraine war breaks out","European energy crisis"],"domain":"macro","label":True,"confidence_per_hop":[0.95,0.88],"notes":"Geopolitical trigger"},
    {"chain_id":"CH_003","hops":["OPEC announces production cut","Global crude supply tightens"],"domain":"commodity","label":True,"confidence_per_hop":[0.94,0.90],"notes":"OPEC compliance high"},
    {"chain_id":"CH_004","hops":["China PMI below 50","Manufacturing activity shrinks"],"domain":"macro","label":True,"confidence_per_hop":[0.92,0.89],"notes":"PMI threshold clear"},
    {"chain_id":"CH_005","hops":["Bitcoin ETF approved","Institutional money flows into crypto"],"domain":"crypto","label":True,"confidence_per_hop":[0.93,0.86],"notes":"SEC approval drives flows"},
    {"chain_id":"CH_006","hops":["ECB hikes rates 50bp","European bank NIM narrows"],"domain":"credit","label":True,"confidence_per_hop":[0.88,0.80],"notes":"Mechanism clear"},
    {"chain_id":"CH_007","hops":["US CPI +5% YoY","Real rates decline"],"domain":"macro","label":True,"confidence_per_hop":[0.90,0.85],"notes":"Nominal fixed, real drops"},
    {"chain_id":"CH_008","hops":["US 10Y yield breaks 4%","Global financing costs rise"],"domain":"credit","label":True,"confidence_per_hop":[0.87,0.82],"notes":"Risk-free rate transmission"},
    {"chain_id":"CH_009","hops":["JPY carry trade unwind","Safe-haven flows into JPY"],"domain":"forex","label":True,"confidence_per_hop":[0.89,0.84],"notes":"Classic carry trigger"},
    {"chain_id":"CH_010","hops":["CNY breaks 7.0","Export firms see FX gains"],"domain":"equity","label":False,"confidence_per_hop":[0.70,0.55],"notes":"PBOC intervention expected"},
]

# 2跳链（15条）
chains += [
    {"chain_id":"CH_011","hops":["FOMC rate cut 25bp","Real rates decline","Growth stock valuations rise"],"domain":"macro","label":True,"confidence_per_hop":[0.96,0.93,0.87],"notes":"DCF denominator effect"},
    {"chain_id":"CH_012","hops":["Russia-Ukraine war","European energy crisis","Chemical feedstock costs rise"],"domain":"commodity","label":True,"confidence_per_hop":[0.95,0.88,0.82],"notes":"Energy-chem link"},
    {"chain_id":"CH_013","hops":["OPEC cuts output","Crude oil price spikes","Airlines shorted"],"domain":"equity","label":True,"confidence_per_hop":[0.94,0.90,0.83],"notes":"Fuel cost hits airlines"},
    {"chain_id":"CH_014","hops":["Bitcoin ETF approved","Institutional inflows","BTC price rises"],"domain":"crypto","label":True,"confidence_per_hop":[0.93,0.86,0.91],"notes":"Direct price effect"},
    {"chain_id":"CH_015","hops":["China PMI below 50","Firms destock","Commodity demand falls"],"domain":"commodity","label":True,"confidence_per_hop":[0.92,0.78,0.75],"notes":"Manuf contraction spreads"},
    {"chain_id":"CH_016","hops":["US CPI +5% YoY","Real rates decline","Gold price rises"],"domain":"commodity","label":True,"confidence_per_hop":[0.90,0.85,0.92],"notes":"Real rate gold negative"},
    {"chain_id":"CH_017","hops":["ECB hikes 50bp","EUR appreciates","Eurozone exports lose competitiveness"],"domain":"forex","label":True,"confidence_per_hop":[0.88,0.80,0.73],"notes":"Monetary transmission"},
    {"chain_id":"CH_018","hops":["JPY carry unwind","JPY sharp appreciation","Japanese exporter profits fall"],"domain":"forex","label":True,"confidence_per_hop":[0.89,0.84,0.71],"notes":"Export-oriented hit"},
    {"chain_id":"CH_019","hops":["US tech earnings miss","Nasdaq falls","EM capital outflows"],"domain":"equity","label":True,"confidence_per_hop":[0.85,0.88,0.76],"notes":"Risk appetite transmission"},
    {"chain_id":"CH_020","hops":["US yield curve inverts","Bank NIM narrows","Regional banks fall"],"domain":"credit","label":True,"confidence_per_hop":[0.82,0.75,0.80],"notes":"Recession signal"},
    {"chain_id":"CH_021","hops":["CNY breaks 7.0","Foreign capital exits A-shares","A-share liquidity tightens"],"domain":"equity","label":False,"confidence_per_hop":[0.70,0.50,0.45],"notes":"PBOC offsets outflows"},
    {"chain_id":"CH_022","hops":["Global wheat harvest fails","Food prices surge","EM social unrest"],"domain":"macro","label":False,"confidence_per_hop":[0.80,0.60,0.40],"notes":"Chain too long"},
    {"chain_id":"CH_023","hops":["Sovereign credit downgrade","Bond yields spike","Global risk selloff"],"domain":"credit","label":False,"confidence_per_hop":[0.85,0.70,0.45],"notes":"Local crisis not global"},
    {"chain_id":"CH_024","hops":["Second COVID wave","Lockdowns intensify","Global trade contracts"],"domain":"macro","label":False,"confidence_per_hop":[0.88,0.72,0.55],"notes":"Prepared by then"},
    {"chain_id":"CH_025","hops":["EU carbon tariff implemented","EU import costs rise","EU internal inflation rises"],"domain":"macro","label":False,"confidence_per_hop":[0.80,0.60,0.50],"notes":"Long lag"},
]

# 3跳链（15条）
chains += [
    {"chain_id":"CH_026","hops":["FOMC rate cut","Real rates decline","Gold price rises","Gold miner stocks go long"],"domain":"macro","label":True,"confidence_per_hop":[0.96,0.93,0.92,0.80],"notes":"Gold-miners chain"},
    {"chain_id":"CH_027","hops":["Russia-Ukraine war","European energy crisis","Chem feedstock costs rise","Chemical sector shorted"],"domain":"equity","label":True,"confidence_per_hop":[0.95,0.88,0.82,0.78],"notes":"Complete energy-chem"},
    {"chain_id":"CH_028","hops":["OPEC cuts 2M bbl","Crude spikes","Airline costs rise","Airlines shorted"],"domain":"equity","label":True,"confidence_per_hop":[0.94,0.90,0.83,0.76],"notes":"Oil-airline chain"},
    {"chain_id":"CH_029","hops":["US CPI +5%","Real rates fall","Gold price rises","Gold ETF inflows"],"domain":"macro","label":True,"confidence_per_hop":[0.90,0.85,0.92,0.84],"notes":"CPI-gold complete"},
    {"chain_id":"CH_030","hops":["China PMI below 50","Firms destock","Commodity demand falls","CRB index falls"],"domain":"commodity","label":True,"confidence_per_hop":[0.92,0.78,0.75,0.81],"notes":"PMI-commodity index"},
    {"chain_id":"CH_031","hops":["Bitcoin ETF approved","Institutional inflows","BTC price rises","Mining stocks rise"],"domain":"crypto","label":True,"confidence_per_hop":[0.93,0.86,0.91,0.77],"notes":"BTC-miners"},
    {"chain_id":"CH_032","hops":["US tech earnings miss","Nasdaq falls","Global risk appetite drops","EM equities and bonds fall"],"domain":"equity","label":True,"confidence_per_hop":[0.85,0.88,0.76,0.70],"notes":"Risk appetite EM"},
    {"chain_id":"CH_033","hops":["ECB hikes 50bp","EUR appreciation","Eurozone exports fall","European recession risk"],"domain":"macro","label":True,"confidence_per_hop":[0.88,0.80,0.73,0.68],"notes":"Tightening-recession"},
    {"chain_id":"CH_034","hops":["JPY carry unwind","Sharp JPY appreciation","Japan export competitiveness falls","Japanese equities fall"],"domain":"forex","label":True,"confidence_per_hop":[0.89,0.84,0.71,0.72],"notes":"Carry equities"},
    {"chain_id":"CH_035","hops":["Middle East conflict","Hormuz blockade risk","Oil supply disruption","Global inflation spikes"],"domain":"macro","label":False,"confidence_per_hop":[0.75,0.60,0.45,0.40],"notes":"Never actually blocked"},
    {"chain_id":"CH_036","hops":["Global drought crop failure","Intl food prices surge","EM inflation","Geopolitical tensions"],"domain":"macro","label":False,"confidence_per_hop":[0.80,0.65,0.50,0.35],"notes":"Too many weak hops"},
    {"chain_id":"CH_037","hops":["Major bank collapse","Credit crunch","Corporate financing difficult","GDP growth slows"],"domain":"credit","label":True,"confidence_per_hop":[0.85,0.82,0.78,0.75],"notes":"Financial crisis chain"},
    {"chain_id":"CH_038","hops":["Global chip shortage","Auto production limited","Used car prices rise","Car demand suppressed"],"domain":"commodity","label":False,"confidence_per_hop":[0.88,0.75,0.60,0.45],"notes":"Demand substitution"},
    {"chain_id":"CH_039","hops":["US fiscal cliff","Gov spending cuts","Civil servant income falls","Consumer data weakens"],"domain":"macro","label":False,"confidence_per_hop":[0.80,0.65,0.50,0.40],"notes":"Sequestration lag"},
    {"chain_id":"CH_040","hops":["Brexit finalized","EU trade barriers increase","UK exports decline","GBP depreciation"],"domain":"forex","label":False,"confidence_per_hop":[0.78,0.70,0.60,0.50],"notes":"Already priced in"},
]

# 4跳链（10条）
chains += [
    {"chain_id":"CH_041","hops":["FOMC large rate cut","Liquidity easing","USD depreciation","Gold price rises","Gold miners rally"],"domain":"macro","label":True,"confidence_per_hop":[0.96,0.93,0.88,0.92,0.80],"notes":"Full monetary-gold chain"},
    {"chain_id":"CH_042","hops":["Russia-Ukraine war","European energy crisis","Chemical costs rise","Chem exports fall","European chem stocks shorted"],"domain":"equity","label":True,"confidence_per_hop":[0.95,0.88,0.82,0.70,0.74],"notes":"4-hop chem with decay"},
    {"chain_id":"CH_043","hops":["China property tightening","Property financing tightens","Land auctions fail","Local gov revenue falls","CGB default risk rises"],"domain":"credit","label":True,"confidence_per_hop":[0.92,0.85,0.72,0.68,0.70],"notes":"Property-CGB chain"},
    {"chain_id":"CH_044","hops":["OPEC surprise cut","Oil price surges","Chem feedstock costs rise","Midstream margins compress","Chemical sector shorted"],"domain":"commodity","label":True,"confidence_per_hop":[0.94,0.90,0.82,0.70,0.72],"notes":"4-hop watch hedge"},
    {"chain_id":"CH_045","hops":["Global climate anomalies","Intl food prices rise","Livestock costs rise","Meat prices rise","CPI pressure builds"],"domain":"macro","label":True,"confidence_per_hop":[0.82,0.78,0.72,0.68,0.75],"notes":"Climate-CPI"},
    {"chain_id":"CH_046","hops":["US tech bubble bursts","Nasdaq crashes","VC funding shrinks","Tech layoffs","Consumer electronics demand falls"],"domain":"macro","label":False,"confidence_per_hop":[0.85,0.80,0.65,0.50,0.40],"notes":"4-hop too long"},
    {"chain_id":"CH_047","hops":["Global trade tensions","Tariffs raised","Import prices rise","Domestic inflation","Consumer spending falls"],"domain":"macro","label":False,"confidence_per_hop":[0.80,0.70,0.60,0.55,0.40],"notes":"Tariff transmission loss"},
    {"chain_id":"CH_048","hops":["EM sovereign debt crisis","Currency crashes","Import prices spike","Inflation rises","Social unrest"],"domain":"macro","label":True,"confidence_per_hop":[0.85,0.82,0.70,0.68,0.60],"notes":"Sovereign debt chain"},
    {"chain_id":"CH_049","hops":["Global shipping congestion","Supply chain bottlenecks","Chip shortage worsens","Auto production falls","Used car prices surge"],"domain":"commodity","label":False,"confidence_per_hop":[0.82,0.72,0.68,0.55,0.50],"notes":"Supply chain long, partly priced in"},
    {"chain_id":"CH_050","hops":["Global net-zero push","Traditional energy investment falls","Fossil supply tightens","Energy prices rise","Global inflation pressure"],"domain":"macro","label":True,"confidence_per_hop":[0.85,0.78,0.72,0.75,0.80],"notes":"Energy transition-inflation"},
]

# 保存 CSV
df = pd.DataFrame(chains)
df["hops"] = df["hops"].apply(str)
df["confidence_per_hop"] = df["confidence_per_hop"].apply(str)
df["label"] = df["label"].apply(lambda x: "True" if x else "False")
df.to_csv("data/annotated_chains.csv", index=False)
print(f"Generated {len(chains)} annotated chains:")
print(df[["chain_id","domain","label"]].to_string())

# 完整性检查
print("\n--- Data quality check ---")
for n in [1, 2, 3, 4]:
    count = sum(1 for c in chains if len(c["confidence_per_hop"]) == n)
    print(f"  {n}-hop chains: {count}")
print(f"  Total: {len(chains)}")
print(f"  True labels: {sum(1 for c in chains if c['label'])}")
print(f"  False labels: {sum(1 for c in chains if not c['label'])}")
