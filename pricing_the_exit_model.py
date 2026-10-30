#!/usr/bin/env python3
"""Replication script for 'Pricing the Exit: A Naive Cost Estimate for
Norway's Digital Sovereignty Transition' (ICDS 2026, revised version).

Every number reported in Sections 5-6 and Appendix A is produced here.
All monetary values in NOK billion (bn) unless stated. Edit any assumption
in the ASSUMPTIONS block and re-run to obtain a modified model.
"""
from itertools import product

# ----------------------------- ASSUMPTIONS ---------------------------------
C_CLOUD = dict(lo=6.0, pt=11.6, hi=17.0)   # A1 public-sector cloud spend, bn/yr
ALPHA   = dict(lo=0.6, pt=0.7, hi=0.8)     # A2 North American share
R_SOV   = 6.5                               # A3 sovereignty premium, bn (one-off)
K       = dict(lo=1.0, pt=1.5, hi=3.0)     # A4 migration multiplier
DELTA   = dict(lo=0.10, hi=0.30)           # A5 operating premium (sensitivity only)
COST_PY = 1.2e-3                            # A6 bn per person-year (NOK 1.2 m)
S_LAB   = dict(lo=0.4, pt=0.5, hi=0.6)     # A7 labour share of R_mig
BETA    = dict(lo=0.02, pt=0.035, hi=0.05) # A8 share of public output disrupted
DAYS    = dict(lo=3, pt=6.5, hi=10)        # A8 denial duration, days
LAMBDA  = dict(lo=0.1, hi=1.0)             # A9 incidents per year
PHI     = 1/3                               # critical-tier share (NSM KVU benchmark)
T       = dict(lo=5, hi=8)                 # transition horizon, years
RATE    = 0.04                              # state calculation rate (R-109/2021)
B_IT    = 22.0                              # state IT expenditure 2025 (~21.9), bn (lower floor)
B_PUB   = 1228.0                            # general government consumption 2024, bn
E_ROUND = (7.0, 9.0)                        # rounded exposure carried forward

def rng(a, b): return f"{a:,.2f}-{b:,.2f}"

# ----------------------------- (1) Exposure --------------------------------
E_lo, E_hi = ALPHA['lo']*C_CLOUD['pt'], ALPHA['hi']*C_CLOUD['pt']
E_pt = ALPHA['pt']*C_CLOUD['pt']
print(f"(1) E = alpha*C  : {rng(E_lo,E_hi)} bn/yr (central {E_pt:.2f}); carried as 7-9")
print(f"    E_broad (22bn base): {rng(ALPHA['lo']*22, ALPHA['hi']*22)} bn/yr")

# ----------------------------- (2) Transition cost -------------------------
def R(k, E, phi=1.0): return R_SOV + k*phi*E
Rf = (R(K['lo'], E_ROUND[0]), R(K['hi'], E_ROUND[1]))
Rc = (R(K['lo'], E_ROUND[0], PHI), R(K['hi'], E_ROUND[1], PHI))
print(f"(2) R full scope    : {rng(*Rf)} bn  -> reported 13-34")
print(f"    R critical tier : {rng(*Rc)} bn  -> reported 9-16")
Rf_ann = (13/T['hi'], 34/T['lo']); Rc_ann = (9/T['hi'], 16/T['lo'])
print(f"    annualised full : {rng(*Rf_ann)} bn/yr ; critical {rng(*Rc_ann)} bn/yr")
af = lambda n: sum((1+RATE)**-t for t in range(1, n+1))/n
print(f"    PV factor even spend: T=5 {af(5):.4f}, T=8 {af(8):.4f}")
print(f"    PV full: {rng(Rf[0]*af(8), Rf[1]*af(5))} bn ; critical {rng(Rc[0]*af(8), Rc[1]*af(5))} bn")
# joint envelope
corners = [R(k, a*c) for k,a,c in product((K['lo'],K['hi']),(ALPHA['lo'],ALPHA['hi']),(C_CLOUD['lo'],C_CLOUD['hi']))]
print(f"    joint envelope (all corners): {rng(min(corners), max(corners))} bn")

# ----------------------------- A5 operating premium ------------------------
dO = (DELTA['lo']*E_ROUND[0]*T['lo'], DELTA['hi']*E_ROUND[1]*T['hi'])
print(f"A5  operating premium over horizon: {rng(*dO)} bn")
print(f"    R + premium (full): {rng(Rf[0]+dO[0], Rf[1]+dO[1])} bn")

# ----------------------------- (3) Human resources -------------------------
def H(s, k, E, phi=1.0): return s*k*phi*E/COST_PY
Hc = H(S_LAB['pt'], K['pt'], 8.0)
print(f"(3) H corners full  : {rng(H(S_LAB['lo'],K['lo'],7), H(S_LAB['hi'],K['hi'],9))} py")
print(f"    H central full  : {Hc:,.0f} py ; s-band {H(S_LAB['lo'],K['pt'],8):,.0f}-{H(S_LAB['hi'],K['pt'],8):,.0f}")
print(f"    FTE full        : {4000/T['hi']:.0f}-{6000/T['lo']:.0f}")
Hcc = (H(S_LAB['lo'],K['pt'],8,PHI), H(S_LAB['hi'],K['pt'],8,PHI))
print(f"    H critical s-band: {Hcc[0]:,.0f}-{Hcc[1]:,.0f} py ; FTE {Hcc[0]/T['hi']:.0f}-{Hcc[1]/T['lo']:.0f}")
print(f"    workforce share (2030, 128k): {500/128000*100:.2f}%-{1200/128000*100:.2f}%")

# ----------------------------- Sensitivity (Table 3) -----------------------
cen = dict(C=C_CLOUD['pt'], a=ALPHA['pt'], k=K['pt'])
base = R(cen['k'], cen['a']*cen['C'])
print(f"Sens central R = {base:.2f}")
for name, key, d in (("C",'C',C_CLOUD),("alpha",'a',ALPHA),("k",'k',K)):
    vals=[]
    for v in (d['lo'], d['hi']):
        p=dict(cen); p[key]=v; vals.append(R(p['k'], p['a']*p['C']))
    print(f"    {name:5s}: {rng(*vals)} swing {vals[1]-vals[0]:.2f}")

# ----------------------------- (4)-(5) Service denial ----------------------
def V(beta, d, B): return beta*d/365*B
for lab, B in (("IT-spend floor", B_IT), ("public-output", B_PUB)):
    lo, pt, hi = V(BETA['lo'],DAYS['lo'],B), V(BETA['pt'],DAYS['pt'],B), V(BETA['hi'],DAYS['hi'],B)
    print(f"(4) V_incident {lab:15s}: {lo*1e3:,.1f}-{hi*1e3:,.1f} M (central {pt*1e3:,.1f} M)")
    print(f"(5) V_annual   {lab:15s}: {lo*LAMBDA['lo']*1e3:,.2f}-{hi*LAMBDA['hi']*1e3:,.1f} M/yr")
    for rlab, ra in (("R_ann low",Rf_ann[0]),("R_ann central",18.7/6.5)):
        print(f"    break-even lambda vs {rlab:13s}: at V_hi {ra/hi:.2f}/yr, at V_central {ra/pt:.2f}/yr")
vb_lo = V(BETA['lo'],DAYS['lo'],B_PUB)*LAMBDA['lo']; vb_hi = V(BETA['hi'],DAYS['hi'],B_PUB)*LAMBDA['hi']
vi_lo = V(BETA['lo'],DAYS['lo'],B_IT)*LAMBDA['lo']
import math
print(f"Gap: narrowest cost/benefit = {Rf_ann[0]/vb_hi:.2f}; widest (public) = {Rf_ann[1]/vb_lo:,.0f} "
      f"({math.log10(Rf_ann[1]/vb_lo):.1f} orders); widest (IT floor) = {Rf_ann[1]/vi_lo:,.0f} ({math.log10(Rf_ann[1]/vi_lo):.1f} orders)")
print(f"Sanity: R/state IT = {13.5/22:.2f}-{33.5/22:.2f} yrs of IT spend")
