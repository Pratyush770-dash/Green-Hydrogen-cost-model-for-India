"""Sanity/benchmark checks. Run after sensitivity.py."""
import os, sys, pandas as pd
BASE = os.path.dirname(os.path.abspath(__file__)); os.chdir(BASE); sys.path.insert(0, BASE)
from lcoh.model import Params, lcoh

b = lcoh(Params(), True)
print(f"Base LCOH: {b['total']:.0f} INR/kg | electricity share: {b['electricity']/b['total']:.0%}")
print("Published: current Indian LCOH INR 380-520/kg (NITI via IEEFA 2024); RE = 60-70% of cost (IEEFA/NITI)")
print("Tender anchor: Numaligarh Feb 2026 = INR 279/kg excl. taxes (includes incentives/subsidies; check)")

f = "data/benchmark.csv"
if os.path.exists(f):
    r = pd.read_csv(f).iloc[0].to_dict()
    pub = r.pop("published_lcoh_inr_per_kg"); r.pop("study", None); r.pop("url", None); r.pop("notes", None)
    P = {k: (int(v) if k == "life_years" else float(v)) for k, v in r.items()}
    mine = lcoh(Params(**P))
    err = (mine - pub) / pub * 100
    for w in (0.08, 0.10, 0.12):
        m = lcoh(Params(**{**P, "discount_rate": w}))
        print(f"  WACC {w:.0%}: {m:.1f} INR/kg ({(m-pub)/pub*100:+.1f}%)")
    print(f"Benchmark: model {mine:.1f} vs published {pub:.1f} INR/kg -> error {err:+.1f}% ->", "PASS (<5%)" if abs(err) < 5 else "adjust/explain")
else:
    print("No data/benchmark.csv found.")
