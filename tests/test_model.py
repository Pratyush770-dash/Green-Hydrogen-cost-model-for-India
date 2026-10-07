import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from lcoh.model import Params, lcoh, crf

def test_hand_calc():
    p = Params(capex_per_kw=50000, tariff=3, capacity_factor=0.5, efficiency_lhv=0.6,
               discount_rate=0.10, life_years=20, om_frac=0.02, stack_cost_frac=0.3,
               stack_life_h=60000, degradation=0, water_cost_per_kg=1, other_cost_per_kg=0)
    kwh = 33.33/0.6
    kg = 8760*0.5/kwh
    crf20 = 0.1*1.1**20/(1.1**20-1)
    exp = (crf20*50000 + 0.02*50000 + 0.3*50000*(4380/60000))/kg + 3*kwh + 1
    assert abs(lcoh(p) - exp) < 1e-6
    assert abs(crf(0.1,20) - 0.11746) < 1e-4

def test_monotonic():
    assert lcoh(Params(tariff=2)) < lcoh(Params(tariff=4))
    assert lcoh(Params(capacity_factor=0.6)) < lcoh(Params(capacity_factor=0.3))
