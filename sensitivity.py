import os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE); sys.path.insert(0, BASE)
os.makedirs("figures", exist_ok=True)

import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lcoh.model import Params, lcoh, vary

OUT = "figures/"
base = Params()
T = pd.read_csv("data/targets.csv")
T = T[T.inr_per_kg > 0]

def overlay(ax):
    for _, r in T.iterrows():
        ax.axhline(r.inr_per_kg, ls="--", lw=1)
        ax.text(ax.get_xlim()[0], r.inr_per_kg, f" {r['name']}", va="bottom", fontsize=7)

# 1. Base breakdown
b = lcoh(base, True); b.pop("total")
fig, ax = plt.subplots(figsize=(5,3.5))
ax.bar(b.keys(), b.values()); ax.set_ylabel("INR/kg")
ax.set_title(f"Base LCOH = {lcoh(base):.1f} INR/kg"); plt.xticks(rotation=30)
plt.tight_layout(); plt.savefig(OUT+"1_breakdown.png", dpi=200); plt.close()

# 2. Tornado (+/-25%)
rows = []
for f in ["capex_per_kw","tariff","capacity_factor","efficiency_lhv","discount_rate",
          "om_frac","stack_cost_frac","stack_life_h","water_cost_per_kg"]:
    v = getattr(base, f)
    lo = lcoh(vary(base, **{f: v*0.75})); hi = lcoh(vary(base, **{f: v*1.25}))
    rows.append((f, lo, hi))
rows.sort(key=lambda x: abs(x[2]-x[1]))
b0 = lcoh(base)
fig, ax = plt.subplots(figsize=(6,4))
for i,(f,lo,hi) in enumerate(rows):
    ax.barh(i, lo-b0, left=b0, color="tab:green"); ax.barh(i, hi-b0, left=b0, color="tab:red")
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows])
ax.axvline(b0, color="k"); ax.set_xlabel("LCOH (INR/kg)"); ax.set_title("Tornado: -25% (green) / +25% (red)")
plt.tight_layout(); plt.savefig(OUT+"2_tornado.png", dpi=200); plt.close()

# 3/4. Heatmaps
def heat(xn, xs, yn, ys, fname, xl, yl):
    Z = np.array([[lcoh(vary(base, **{xn:x, yn:y})) for x in xs] for y in ys])
    fig, ax = plt.subplots(figsize=(6,4.5))
    im = ax.imshow(Z, origin="lower", aspect="auto", extent=[xs[0],xs[-1],ys[0],ys[-1]])
    lv = [l for l in sorted(T.inr_per_kg) if Z.min() < l < Z.max()]
    if lv:
        cs = ax.contour(xs, ys, Z, levels=lv, colors="w"); ax.clabel(cs, fmt="%d")
    plt.colorbar(im, label="LCOH (INR/kg)")
    ax.set_xlabel(xl); ax.set_ylabel(yl); plt.tight_layout(); plt.savefig(OUT+fname, dpi=200); plt.close()
heat("tariff", np.linspace(1.5,6,40), "capex_per_kw", np.linspace(25000,80000,40),
     "3_heat_tariff_capex.png", "Tariff (INR/kWh)", "Capex (INR/kW)")
heat("tariff", np.linspace(1.5,6,40), "capacity_factor", np.linspace(0.25,0.9,40),
     "4_heat_tariff_cf.png", "Tariff (INR/kWh)", "Capacity factor")

# 5. Scenarios (sources in data/sources.csv)
sc = {"Today": base,
      "2030": vary(base, capex_per_kw=43500, tariff=2.5, capacity_factor=0.60, efficiency_lhv=0.64),
      "Optimistic": vary(base, capex_per_kw=30450, tariff=2.0, capacity_factor=0.60, efficiency_lhv=0.66, discount_rate=0.08)}
vals = {k: lcoh(v) for k,v in sc.items()}
fig, ax = plt.subplots(figsize=(5,3.5)); ax.bar(vals.keys(), vals.values())
ax.set_ylabel("INR/kg"); ax.set_ylim(0, max(vals.values())*1.2); overlay(ax)
plt.tight_layout(); plt.savefig(OUT+"5_scenarios.png", dpi=200); plt.close()

# 6. Break-even tariff vs capex for each target
cap = np.linspace(25000,80000,50)
fig, ax = plt.subplots(figsize=(6,4))
for _, r in T.iterrows():
    be = []
    for c in cap:
        p = vary(base, capex_per_kw=c)
        fixed = lcoh(vary(p, tariff=0))
        kwh = lcoh(vary(p, tariff=1)) - fixed
        be.append((r.inr_per_kg - fixed)/kwh)
    ax.plot(cap, be, label=f"{r['name']} ({r.inr_per_kg:.0f})")
ax.set_xlabel("Capex (INR/kW)"); ax.set_ylabel("Max tariff to hit target (INR/kWh)"); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig(OUT+"6_breakeven.png", dpi=200); plt.close()

pd.DataFrame(vals, index=["LCOH_INR_per_kg"]).T.to_csv(OUT+"scenarios.csv")
print("Base:", round(b0,1), "Scenarios:", {k: round(v,1) for k,v in vals.items()})
