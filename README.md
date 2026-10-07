# Green-Hydrogen-cost-model-for-India
The project is a Python calculator for the levelised cost of hydrogen (LCOH). You feed it electrolyser capex, electricity tariff, capacity factor and stack efficiency, and it gives back a cost in ₹/kg. Around that sits a set of sensitivity plots and a check against a published study.

With the inputs I picked, the base case lands at about ₹334/kg. My 2030 case gives ₹213/kg and the optimistic one gives ₹153/kg. So even in the best case I tried, the ₹100/kg goal mentioned by the MNRE minister stays out of reach. The report in this repo (`Green_Hydrogen_LCOH_Report.docx`) explains why, with sources.

## How the model works

The idea is the usual one. Capital cost gets spread over the life of the plant using a capital recovery factor. Fixed O&M and a share of the stack replacement cost are added, and the total is divided by the hydrogen produced in a year. Electricity, water and other per-kg costs are added on top.

```
CRF      = r(1+r)^n / ((1+r)^n - 1)
kWh/kg   = 33.33 / (efficiency x (1 - degradation))      # LHV basis
LCOH     = (CRF x capex + O&M + stack replacement) / annual kg
           + tariff x kWh/kg + water + other
```

Default inputs are in `lcoh/model.py`. Where each one came from is written down in `data/sources.csv`. 

## Running it

You'll need Python 3. From the project folder:

```
py -m pip install -r requirements.txt
py -m pytest
py sensitivity.py
py validate.py
```


## What you get

`sensitivity.py` makes six plots. There's a cost breakdown, a tornado chart where each input moves by 25%, two heat maps (tariff against capex, and tariff against capacity factor), a scenario chart with the target lines drawn on it, and a break-even chart that shows the highest tariff that still meets each target.

`validate.py` runs the model on the inputs of a 2030 scenario from a CSEP paper (Tongia and Patel, 2024), which are stored in `data/benchmark.csv`. The paper reports ₹209/kg and my model gives ₹203.2/kg, about 2.8% lower. One caveat: the paper doesn't say what discount rate it used, so I went with 10% and left it alone. If you change it to 8% or 12%, the gap becomes −6.4% or +1.1%.

## Limitations

A few things are worth knowing before you use the numbers for anything.

The cost targets in `data/targets.csv` aren't all the same sort of thing. One is a stated aim, one is a USD figure converted to rupees, one is a real tender price, and one is a grey hydrogen estimate from 2022. Tender prices also come with incentives built in, so they don't line up neatly with an unsubsidised cost.

Compression, storage and transport are left at zero, so the results are production costs and not delivered costs. There's no inflation, no tax and a fixed exchange rate of ₹87 to the dollar. The sensitivity plots change one input at a time, which ignores that some inputs move together in real projects.

The benchmark shows that the equations behave sensibly. It doesn't show that my base case inputs are right, since the CSEP scenario is an optimistic 2030 one.

## Sources

The main ones are CSEP (Tongia and Patel, 2024), IEEFA and JMK Research (2024), S&P Global on the Numaligarh tender, IMARC Engineering, CEEW, CRISIL, and KPMG as reported by pv magazine India. Links are in the three CSV files in `data/` and in the report's reference list.

## Repository structure

```
lcoh_project/
├── README.md
├── requirements.txt
├── sensitivity.py                  # makes all the plots
├── validate.py                     # sanity checks and the benchmark
├── Green_Hydrogen_LCOH_Report.docx # technical report
├── lcoh/
│   ├── __init__.py
│   └── model.py                    # the LCOH calculator
├── data/
│   ├── sources.csv                 # where each input came from
│   ├── targets.csv                 # cost reference points in ₹/kg
│   └── benchmark.csv               # published study used for validation
├── tests/
│   └── test_model.py               # hand calculation and trend tests
└── figures/                        # created when sensitivity.py 
figures
    ├── 1_breakdown.png
    ├── 2_tornado.png
    ├── 3_heat_tariff_capex.png
    ├── 4_heat_tariff_cf.png
    ├── 5_scenarios.png
    ├── 6_breakeven.png
    └── scenarios.csv
```

## Author

**Pratyush Dash**

B.Tech Chemical Engineering, KIIT University, Bhubaneswar

