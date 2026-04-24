#!/usr/bin/env python3
"""Dump astropy units to JSON for the web frontend."""
import json
import sys
import os

from astropy import units as u

unit_categories = {
    'Length': ['m', 'cm', 'mm', 'um', 'nm', 'Angstrom', 'km', 'au', 'AU', 'pc', 'kpc', 'Mpc', 'lyr'],
    'Mass': ['kg', 'g', 'M_sun', 'Msun'],
    'Density': ['mpcc'],
    'Time': ['s', 'yr', 'Myr', 'Gyr'],
    'Energy': ['J', 'erg', 'eV', 'keV', 'MeV', 'GeV'],
    'Power': ['W'],
    'Pressure': ['Pa', 'bar', 'mbar'],
    'Frequency': ['Hz', 'kHz', 'MHz', 'GHz'],
    'Temperature': ['K'],
    'Angular size': ['deg', 'radian', 'arcmin', 'arcsec', 'arcsec2'],
    'Astronomy': ['Lsun', 'Jy', 'mJy', 'MJy'],
    'Composite': ['m2', 'm3', 'cm2', 'cm3', 's2', 'pc2', 'pc3']
}

out = []
for category, unit_names in unit_categories.items():
    for name in unit_names:
        try:
            _ = getattr(u, name)
            out.append({
                "name": name,
                "category": category
            })
        except AttributeError:
            print(f"Warning: unit {name} not found", file=sys.stderr)

# Add custom derived units
custom_units = ['Ang', 'Gauss', 'esu', 'degrees']
for name in custom_units:
    out.append({"name": name, "category": "Derived"})

out_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'data')
os.makedirs(out_dir, exist_ok=True)

with open(os.path.join(out_dir, 'units.json'), 'w') as f:
    json.dump(out, f, indent=2)

print(f"Wrote {len(out)} units to src/data/units.json")
