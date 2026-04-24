#!/usr/bin/env python3
"""Dump astropy constants to JSON for the web frontend."""
import json
import sys
import os

from astropy import constants

con_list = [
    'G', 'N_A', 'R', 'Ryd', 'a0', 'alpha', 'atm', 'b_wien', 'c', 'g0',
    'h', 'hbar', 'k_B', 'm_e', 'm_n', 'm_p', 'e', 'eps0', 'mu0', 'muB',
    'sigma_T', 'sigma_sb', 'GM_earth', 'GM_jup', 'GM_sun',
    'L_bol0', 'L_sun', 'M_earth', 'M_jup', 'M_sun', 'R_earth', 'R_jup',
    'R_sun', 'au', 'kpc', 'pc'
]

out = []
for name in con_list:
    try:
        c = getattr(constants, name)
        out.append({
            "symbol": name,
            "name": c.name,
            "value": float(c.value),
            "unit": str(c.unit),
            "uncertainty": float(c.uncertainty) if c.uncertainty else 0,
            "ref": c.reference if hasattr(c, 'reference') else "CODATA 2018"
        })
    except AttributeError:
        print(f"Warning: constant {name} not found", file=sys.stderr)

out_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'data')
os.makedirs(out_dir, exist_ok=True)

with open(os.path.join(out_dir, 'constants.json'), 'w') as f:
    json.dump(out, f, indent=2)

print(f"Wrote {len(out)} constants to src/data/constants.json")
