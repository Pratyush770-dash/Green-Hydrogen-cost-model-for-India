"""LCOH model for green hydrogen (INR). Basis: LHV (33.33 kWh/kg)."""
from dataclasses import dataclass, replace

LHV_KWH_PER_KG = 33.33

@dataclass(frozen=True)
class Params:
    capex_per_kw: float = 65_000      # INR/kW installed (system incl. BoP)  [ASSUMPTION - verify]
    tariff: float = 3.25              # INR/kWh delivered RE power           [ASSUMPTION - verify]
    capacity_factor: float = 0.45     # fraction
    efficiency_lhv: float = 0.62      # stack+system, LHV basis
    discount_rate: float = 0.10       # WACC
    life_years: int = 20
    om_frac: float = 0.025            # fixed O&M, fraction of capex per year
    stack_cost_frac: float = 0.30     # stack replacement cost, fraction of capex
    stack_life_h: float = 70_000
    degradation: float = 0.05         # avg efficiency loss over life
    water_cost_per_kg: float = 1.0    # INR/kg H2 (~9-10 L/kg)
    other_cost_per_kg: float = 0.0    # compression/storage etc. INR/kg

def crf(r, n):
    return 1 / n if r == 0 else r * (1 + r) ** n / ((1 + r) ** n - 1)

def lcoh(p: Params, breakdown=False):
    """Return INR/kg (or dict of components)."""
    kwh_per_kg = LHV_KWH_PER_KG / (p.efficiency_lhv * (1 - p.degradation))
    hours = 8760 * p.capacity_factor
    kg_per_kw_yr = hours / kwh_per_kg
    capital = crf(p.discount_rate, p.life_years) * p.capex_per_kw / kg_per_kw_yr
    om = p.om_frac * p.capex_per_kw / kg_per_kw_yr
    stack = p.stack_cost_frac * p.capex_per_kw * (hours / p.stack_life_h) / kg_per_kw_yr
    power = p.tariff * kwh_per_kg
    parts = dict(capital=capital, om=om, stack=stack, electricity=power,
                 water=p.water_cost_per_kg, other=p.other_cost_per_kg)
    parts["total"] = sum(parts.values())
    return parts if breakdown else parts["total"]

def vary(p: Params, **kw):
    return replace(p, **kw)
