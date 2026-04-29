# AstroCalculator Web — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Rewrite AstroCalculator as a client-side React web app with Pyodide-powered Python engine, Studio layout sidebar, and one-click equation templates.

**Architecture:** React + Vite + TypeScript single-page app in `web/` subdirectory. Pyodide runs the existing `AstroCalculator` Python class in a web worker. Build-time scripts dump astropy constants/units to JSON; a Vite plugin converts `equations/*.md` to a JSON manifest. Deployed to GitHub Pages via Actions.

**Tech Stack:** React 18, TypeScript 5, Vite 5, Pyodide 0.25+, KaTeX, vite-plugin-pwa

---

### Task 1: Scaffold Vite + React + TypeScript Project

**Files:**
- Create: `web/package.json`
- Create: `web/tsconfig.json`
- Create: `web/tsconfig.node.json`
- Create: `web/vite.config.ts`
- Create: `web/index.html`

- [x] **Step 1: Run Vite scaffolding**

Run: `cd /Users/u1149259/git/astrocalculator && npm create vite@latest web -- --template react-ts`
Expected: Creates `web/` directory with React + TypeScript template

- [x] **Step 2: Install all dependencies**

Run: `cd web && npm install pyodide@latest katex vite-plugin-pwa gray-matter comlink`
Run: `cd web && npm install -D @types/katex`

Expected: All packages installed successfully

- [x] **Step 3: Verify dev server starts**

Run: `cd web && npm run dev`
Expected: Dev server starts on http://localhost:5173, shows Vite + React default page

- [x] **Step 4: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/package.json web/package-lock.json web/tsconfig.json web/tsconfig.node.json web/vite.config.ts web/index.html web/src/ web/public/
git commit -m "feat: scaffold web app with Vite + React + TypeScript"
```

---

### Task 2: Create Type Definitions

**Files:**
- Create: `web/src/types/index.ts`

- [x] **Step 1: Write types file**

```typescript
// web/src/types/index.ts

export interface ConstantEntry {
  symbol: string;
  name: string;
  value: number;
  unit: string;
  uncertainty: number;
  ref: string;
}

export interface UnitEntry {
  name: string;
  category: string;
}

export interface EquationParam {
  symbol: string;
  default: string;
  description: string;
}

export interface EquationExpression {
  name: string;
  expression: string;
  latex?: string;
  description?: string;
}

export interface Equation {
  slug: string;
  title: string;
  category: string;
  tags: string[];
  params: EquationParam[];
  expressions: EquationExpression[];
  body?: string;
}

export interface CalculatorResult {
  parsed: string;
  si: string;
  cgs: string;
  converted?: string;
  targetUnit?: string;
}

export interface HistoryEntry {
  id: number;
  input: string;
  result: CalculatorResult;
  timestamp: number;
}

export type SidebarTab = 'constants' | 'units' | 'equations' | 'history';

export interface CalculatorWorkerAPI {
  evaluate: (expression: string) => Promise<CalculatorResult>;
  convert: (quantityStr: string, unit: string) => Promise<string>;
  ready: Promise<void>;
}
```

- [x] **Step 2: Verify types compile**

Run: `cd web && npx tsc --noEmit`
Expected: No TypeScript errors

- [x] **Step 3: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/src/types/index.ts
git commit -m "feat: add TypeScript type definitions"
```

---

### Task 3: Create Constants & Units Dump Scripts

**Files:**
- Create: `web/scripts/dump-constants.py`
- Create: `web/scripts/dump-units.py`

- [x] **Step 1: Write dump-constants.py**

```python
#!/usr/bin/env python3
"""Dump astropy constants to JSON for the web frontend."""
import json
import sys
import os

# Run from the project .venv which has astropy installed
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
```

- [x] **Step 2: Write dump-units.py**

```python
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
```

- [x] **Step 3: Run dump scripts**

Run: `cd /Users/u1149259/git/astrocalculator && .venv/bin/python web/scripts/dump-constants.py`
Expected: `Wrote N constants to src/data/constants.json`

Run: `cd /Users/u1149259/git/astrocalculator && .venv/bin/python web/scripts/dump-units.py`
Expected: `Wrote N units to src/data/units.json`

- [x] **Step 4: Verify JSON output is valid**

Run: `cd web && node -e "JSON.parse(require('fs').readFileSync('src/data/constants.json','utf8')); console.log('constants.json valid')"`
Run: `cd web && node -e "JSON.parse(require('fs').readFileSync('src/data/units.json','utf8')); console.log('units.json valid')"`
Expected: "constants.json valid" and "units.json valid"

- [x] **Step 5: Add npm scripts to package.json**

Read `web/package.json` and add these scripts:

```json
{
  "scripts": {
    "dump-constants": "python3 ../.venv/bin/python scripts/dump-constants.py",
    "dump-units": "python3 ../.venv/bin/python scripts/dump-units.py",
    "dump-data": "npm run dump-constants && npm run dump-units",
    "prebuild": "npm run dump-data",
    "predev": "npm run dump-data",
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint ."
  }
}
```

Use Edit tool to add these script entries to `web/package.json`.

- [x] **Step 6: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/scripts/ web/src/data/ web/package.json
git commit -m "feat: add constants/units dump scripts + JSON data"
```

---

### Task 4: Create Vite Plugin for Equations Markdown → JSON

**Files:**
- Create: `web/vite-plugin-equations.ts`

- [x] **Step 1: Install gray-matter for YAML frontmatter parsing**

Run: `cd web && npm install gray-matter`
Run: `cd web && npm install -D @types/node`

- [x] **Step 2: Write the Vite plugin**

```typescript
// web/vite-plugin-equations.ts
import { Plugin } from 'vite';
import matter from 'gray-matter';
import { readdirSync, readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const EQUATIONS_DIR = 'equations';
const OUTPUT_FILE = 'src/data/equations.json';

export function equationsPlugin(): Plugin {
  return {
    name: 'vite-plugin-equations',
    buildStart() {
      const { readdirSync, readFileSync, writeFileSync, mkdirSync } = require('fs') as typeof import('fs');
      const { join } = require('path') as typeof import('path');

      const equationsDir = join(process.cwd(), EQUATIONS_DIR);

      let files: string[];
      try {
        files = readdirSync(equationsDir).filter(f => f.endsWith('.md'));
      } catch {
        console.warn('No equations directory found, skipping');
        return;
      }

      const equations = files.map((file: string) => {
        const raw = readFileSync(join(equationsDir, file), 'utf8');
        const { data, content } = matter(raw);
        return {
          slug: file.replace(/\.md$/, ''),
          title: data.title || file,
          category: data.category || 'Uncategorized',
          tags: data.tags || [],
          params: data.params || [],
          expressions: data.expressions || [],
          body: content.trim() || undefined,
        };
      });

      const outDir = join(process.cwd(), dirname(OUTPUT_FILE));
      mkdirSync(outDir, { recursive: true });
      writeFileSync(join(process.cwd(), OUTPUT_FILE), JSON.stringify(equations, null, 2));
      console.log(`Built ${equations.length} equation templates → ${OUTPUT_FILE}`);
    },
  };
}
```

- [x] **Step 3: Wire plugin into vite.config.ts**

Read `web/vite.config.ts` and replace with:

```typescript
// web/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { equationsPlugin } from './vite-plugin-equations';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    equationsPlugin(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        maximumFileSizeToCacheInBytes: 40 * 1024 * 1024, // Pyodide WASM ~30MB
        globPatterns: ['**/*.{js,css,html,wasm,json,data,png,svg,woff2}'],
      },
      manifest: {
        name: 'AstroCalculator',
        short_name: 'AstroCalc',
        description: 'Calculator for Astronomers and Physicists',
        theme_color: '#1a1a2e',
        icons: [],
      },
    }),
  ],
  base: '/astrocalculator/',
});
```

- [x] **Step 4: Verify TypeScript compilation**

Run: `cd web && npx tsc --noEmit`
Expected: No errors

- [x] **Step 5: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/vite-plugin-equations.ts web/vite.config.ts web/package.json web/package-lock.json
git commit -m "feat: add Vite plugin for equations markdown → JSON"
```

---

### Task 5: Create Example Equation Markdown Files

**Files:**
- Create: `web/equations/escape-velocity.md`
- Create: `web/equations/schwarzschild-radius.md`
- Create: `web/equations/kepler-third-law.md`
- Create: `web/equations/eddington-luminosity.md`

- [x] **Step 1: Write escape-velocity.md**

```markdown
---
title: Escape Velocity
category: Mechanics
tags: [velocity, gravity, compact objects]
params:
  - symbol: M
    default: "1.4 M_sun"
    description: Mass of the object
  - symbol: R
    default: "10 km"
    description: Radius
expressions:
  - name: "Escape velocity"
    expression: "sqrt(2 G M / R) in km/s"
    latex: "v_{\\rm esc} = \\sqrt{\\frac{2GM}{R}}"
  - name: "Circular velocity"
    expression: "sqrt(G M / R) in km/s"
    latex: "v_{\\rm circ} = \\sqrt{\\frac{GM}{R}}"
    description: "Circular orbital velocity, 1/√2 times escape velocity"
---

The escape velocity is the minimum speed needed for an object to escape
the gravitational influence of a massive body.
```

- [x] **Step 2: Write schwarzschild-radius.md**

```markdown
---
title: Schwarzschild Radius
category: General Relativity
tags: [black hole, gravity, radius]
params:
  - symbol: M
    default: "1 M_sun"
    description: Mass of the object
expressions:
  - name: "Schwarzschild radius"
    expression: "2 G M / c^2 in km"
    latex: "r_s = \\frac{2GM}{c^2}"
  - name: "Schwarzschild density"
    expression: "3 c^6 / (32 pi G^3 M^2)"
    latex: "\\rho_s = \\frac{3c^6}{32\\pi G^3 M^2}"
    description: "Average density within the event horizon"
---

The Schwarzschild radius defines the event horizon of a non-rotating black hole.
```

- [x] **Step 3: Write kepler-third-law.md**

```markdown
---
title: Kepler's Third Law
category: Orbital Mechanics
tags: [orbit, period, binary]
params:
  - symbol: M
    default: "1 M_sun"
    description: Total mass of the system
  - symbol: a
    default: "1 au"
    description: Semi-major axis
expressions:
  - name: "Orbital period"
    expression: "sqrt(4 pi^2 a^3 / (G M)) in yr"
    latex: "P = \\sqrt{\\frac{4\\pi^2 a^3}{GM}}"
  - name: "Orbital separation from period"
    expression: "(G M P^2 / (4 pi^2))^(1/3) in au"
    latex: "a = \\left(\\frac{GMP^2}{4\\pi^2}\\right)^{1/3}"
    description: "Given period P, compute semi-major axis"
---

Kepler's Third Law relates orbital period to semi-major axis for two-body systems.
```

- [x] **Step 4: Write eddington-luminosity.md**

```markdown
---
title: Eddington Luminosity
category: Astrophysics
tags: [accretion, luminosity, limit]
params:
  - symbol: M
    default: "1.4 M_sun"
    description: Mass of the accreting object
expressions:
  - name: "Eddington luminosity"
    expression: "4 pi G M c m_p / sigma_T in erg/s"
    latex: "L_{\\rm Edd} = \\frac{4\\pi G M c m_p}{\\sigma_T}"
  - name: "Eddington accretion rate"
    expression: "4 pi G M m_p / (0.1 sigma_T c)"
    latex: "\\dot{M}_{\\rm Edd} = \\frac{4\\pi G M m_p}{0.1\\sigma_T c}"
    description: "Assuming 10% radiative efficiency"
---

The Eddington luminosity is the maximum luminosity a star can have
while maintaining hydrostatic equilibrium.
```

- [x] **Step 5: Verify equations.json generation**

Run: `cd web && npm run dev` (or trigger a Vite build to check the plugin runs)
Expected: In terminal output: `Built 4 equation templates → src/data/equations.json`

- [x] **Step 6: Verify equations.json content**

Run: `cd web && node -e "const eq = JSON.parse(require('fs').readFileSync('src/data/equations.json','utf8')); console.log(eq.length, 'equations'); eq.forEach(e => console.log(' -', e.title, ':', e.expressions.length, 'expressions'))"`
Expected: `4 equations` with their expression counts

- [x] **Step 7: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/equations/ web/src/data/equations.json
git commit -m "feat: add example equation templates"
```

---

### Task 6: Adapt calculator.py for Pyodide Web Worker

**Files:**
- Create: `web/src/engine/calculator.py`

- [x] **Step 1: Write calculator.py**

Copy the existing `AstroCalculator` class from `calc/__init__.py` and adapt it for Pyodide. Remove `prompt_toolkit`/`rich` dependencies, remove `USER_DATA_DIR`/`HISTORY_DIR`/`CACHE_FILE`, remove lazy imports (Pyodide provides astropy/sympy/numpy directly).

```python
# web/src/engine/calculator.py
"""AstroCalculator engine for Pyodide web worker."""

from math import pi, inf, log, log10, log2
import json

# Configuration
DIGITS = 10
IS_SCI = 0
F_FMT = f'{{:.{DIGITS-1}e}}' if IS_SCI else f'{{:#.{DIGITS}g}}'

# In Pyodide, these are available as globals after micropip.install
from astropy import units as u
from astropy import constants
import numpy as np
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication,
    convert_xor,
)

transformations = (convert_xor,) + standard_transformations + (implicit_multiplication,)


def simple_eval(expr, namespace):
    """Fast evaluation for simple mathematical expressions."""
    expr = expr.strip()
    safe_dict = {
        '__builtins__': {},
        'pi': pi, 'inf': inf,
        'log': log, 'log10': log10, 'log2': log2,
    }
    safe_dict.update(namespace)

    # Try direct eval for simple expressions
    try:
        if all(c in '0123456789+-*/().eE pinflogcossinqrt^**' for c in expr.replace(' ', '')):
            python_expr = expr.replace('^', '**')
            result = eval(python_expr, safe_dict)
            return python_expr, result
    except:
        pass

    # Fall back to sympy
    inp_expr = parse_expr(expr, transformations=transformations, evaluate=False)
    inp_expr_str = str(inp_expr)
    result = eval(inp_expr_str, globals(), namespace)
    return inp_expr_str, result


class AstroCalculator:
    """Calculator for astronomical and physical calculations."""
    user_units = ['deg', 'Ang', 'mpcc', 'm2', 'm3', 'cm2', 'cm3', 's2', 'pc2', 'pc3', 'arcsec2', 'Msun']

    def __init__(self):
        self.local_namespace = {}
        self._initialize_constants()
        self._initialize_units()

    def _initialize_constants(self):
        con_list = [
            'G', 'N_A', 'R', 'Ryd', 'a0', 'alpha', 'atm', 'b_wien', 'c', 'g0',
            'h', 'hbar', 'k_B', 'm_e', 'm_n', 'm_p', 'e', 'eps0', 'mu0', 'muB',
            'sigma_T', 'sigma_sb', 'GM_earth', 'GM_jup', 'GM_sun',
            'L_bol0', 'L_sun', 'M_earth', 'M_jup', 'M_sun', 'R_earth', 'R_jup',
            'R_sun', 'au', 'kpc', 'pc'
        ]
        con_list.sort(key=lambda y: y.lower())

        for con in con_list:
            try:
                self.local_namespace[con] = getattr(constants, con)
            except AttributeError:
                pass

        for func_name in ['sin', 'arcsin', 'cos', 'arccos', 'tan', 'arctan',
                          'sinh', 'arctanh', 'cosh', 'arccosh', 'arcsinh',
                          'tanh', 'arctanh', 'sqrt', 'exp']:
            self.local_namespace[func_name] = getattr(np, func_name)

        self.local_namespace['pi'] = pi
        self.local_namespace['inf'] = inf
        self.local_namespace['log'] = log
        self.local_namespace['log10'] = log10
        self.local_namespace['log2'] = log2

    def _initialize_units(self):
        more_units = {
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
        unit_skip = ['au', 'pc', 'M_sun']

        for key in more_units:
            for unit_name in more_units[key]:
                if unit_name not in unit_skip + self.user_units:
                    try:
                        self.local_namespace[unit_name] = getattr(u, unit_name)
                    except AttributeError:
                        pass

        self._define_derived_units()

    def _define_derived_units(self):
        e = self.local_namespace['e']
        m_p = self.local_namespace['m_p']
        M_sun = self.local_namespace['M_sun']
        sigma_sb = self.local_namespace['sigma_sb']
        c = self.local_namespace['c']
        m = u.m
        cm = u.cm
        nm = u.nm
        s = u.s
        pc = self.local_namespace['pc']
        arcsec = u.arcsec
        g = u.g

        self.local_namespace['esu'] = e.esu
        self.local_namespace['Ang'] = u.def_unit('Ang', 0.1 * nm)
        self.local_namespace['mpcc'] = u.def_unit('mpcc', m_p / cm**3)
        self.local_namespace['Msun'] = M_sun
        self.local_namespace['m2'] = m**2
        self.local_namespace['m3'] = m**3
        self.local_namespace['cm2'] = cm**2
        self.local_namespace['cm3'] = cm**3
        self.local_namespace['s2'] = s**2
        self.local_namespace['pc2'] = pc**2
        self.local_namespace['pc3'] = pc**3
        self.local_namespace['degrees'] = pi / 180
        self.local_namespace['arcsec2'] = arcsec**2
        self.local_namespace['Gauss'] = g**(1/2) * cm**(-1/2) * s**(-1)
        self.local_namespace['a_rad'] = 4. * sigma_sb / c

    def parse_and_eval(self, expr):
        try:
            return simple_eval(expr, self.local_namespace)
        except Exception as e:
            raise ValueError(str(e))

    def calculate(self, inp, delimiter=','):
        if not inp.strip():
            return None

        inp = inp.strip()

        # Check for 'in unit' clause
        target_unit = None
        if ' in ' in inp:
            parts = inp.split(' in ')
            if len(parts) == 2:
                inp = parts[0].strip()
                target_unit = parts[1].strip()

        exp_to_eval = None
        lines = inp.split(delimiter)
        n_line = len(lines)

        for count, line in enumerate(lines):
            line = line.strip()
            if count == n_line - 1:
                exp_to_eval = line.split('=')[0].strip()

            if not line or '=' not in line:
                continue

            items = line.split('=')
            if len(items) > 2:
                raise ValueError('Multiple equal signs found')

            var, value = items
            var = var.strip()
            if ' ' in var:
                raise ValueError('Variable should not have space in it')

            _, result = self.parse_and_eval(value)
            self.local_namespace[var] = result

        parsed_expr, raw_result = self.parse_and_eval(exp_to_eval)

        from astropy.units.quantity import Quantity
        from astropy.units.core import CompositeUnit

        si_result = None
        cgs_result = None

        if isinstance(raw_result, (int, float)):
            si_result = raw_result if isinstance(raw_result, int) else F_FMT.format(raw_result)
            cgs_result = si_result
        else:
            if isinstance(raw_result.si, Quantity):
                si_result = F_FMT.format(raw_result.si)
            else:
                si_result = str(raw_result.si)

            try:
                if isinstance(raw_result.cgs, CompositeUnit):
                    cgs_result = str(raw_result.cgs)
                else:
                    cgs_result = F_FMT.format(raw_result.cgs)
            except:
                cgs_result = str(raw_result.cgs) if raw_result.cgs else "N/A"

        converted = None
        if target_unit and raw_result is not None:
            try:
                if not isinstance(raw_result, (int, float)):
                    if target_unit in self.user_units:
                        cv = raw_result.to(self.local_namespace[target_unit])
                    else:
                        cv = raw_result.to(target_unit)
                    if isinstance(cv, int):
                        converted = str(cv)
                    elif isinstance(cv, float):
                        converted = F_FMT.format(cv)
                    else:
                        converted = f"{F_FMT.format(cv.value)} {cv._unit}"
            except:
                converted = f"Error converting to {target_unit}"

        return {
            "parsed": str(parsed_expr),
            "si": str(si_result),
            "cgs": str(cgs_result),
            "converted": converted,
            "targetUnit": target_unit,
        }


# Module-level singleton
_calc = None


def get_calculator():
    global _calc
    if _calc is None:
        _calc = AstroCalculator()
    return _calc


def evaluate(expression):
    calc = get_calculator()
    result = calc.calculate(expression)
    if result is None:
        return {"parsed": "", "si": "", "cgs": ""}
    return result


def convert_quantity(quantity_obj, unit):
    calc = get_calculator()
    # Re-evaluate the quantity string to get a quantity object
    _, qty = calc.parse_and_eval(quantity_obj)
    return calc.convert(qty, unit)
```

- [x] **Step 2: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/src/engine/calculator.py
git commit -m "feat: add Pyodide-adapted calculator engine"
```

---

### Task 7: Create Web Worker for Pyodide

**Files:**
- Create: `web/public/pyodide-worker.js`

**Note:** The worker must be a plain `.js` file in `public/` (not a bundled TypeScript module) because it uses `importScripts` to load Pyodide, which only works in classic web workers.

- [x] **Step 1: Write the plain JS web worker**

```javascript
// web/public/pyodide-worker.js
// Classic web worker — must be plain JS (not module) for importScripts to work

let pyodideReady = false;
let evaluateFn = null;

const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.25.1/full/';

async function initPyodide() {
  importScripts(PYODIDE_URL + 'pyodide.js');

  const pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
  await pyodide.loadPackage(['numpy', 'astropy', 'sympy']);

  // Fetch calculator.py from public/
  const resp = await fetch(new URL('calculator.py', self.location.href));
  const calcCode = await resp.text();
  await pyodide.runPythonAsync(calcCode);

  evaluateFn = pyodide.runPython(`
from calculator import evaluate as _evaluate
def evaluate_wrapper(expr):
    import json
    result = _evaluate(expr)
    return json.dumps(result)
evaluate_wrapper
  `);

  pyodideReady = true;
  self.postMessage({ type: 'ready' });
}

self.onmessage = async function(e) {
  var data = e.data;
  var id = data.id;
  var type = data.type;
  var payload = data.payload;

  if (type === 'init') {
    try {
      await initPyodide();
    } catch (err) {
      self.postMessage({ id: id, type: 'error', payload: String(err) });
    }
    return;
  }

  if (!pyodideReady) {
    self.postMessage({ id: id, type: 'error', payload: 'Engine not ready' });
    return;
  }

  if (type === 'evaluate') {
    try {
      var jsonStr = evaluateFn(payload);
      var result = JSON.parse(jsonStr);
      self.postMessage({ id: id, type: 'result', payload: result });
    } catch (err) {
      self.postMessage({ id: id, type: 'error', payload: String(err) });
    }
  }
};
```

- [x] **Step 2: Copy calculator.py to public/ for the worker to fetch**

The `vite.config.ts` needs to copy `calculator.py` to the `public/` dir at dev time so the worker can fetch it. Add a `vite-plugin-static-copy` or use a simple approach:

Add to `web/package.json` scripts:

```json
"copy-calc": "cp src/engine/calculator.py public/calculator.py"
```

Update `predev` and `prebuild` to include `copy-calc`:
```json
"predev": "npm run dump-data && npm run copy-calc",
"prebuild": "npm run dump-data && npm run copy-calc"
```

Or alternatively, use the vite config to alias the path. Simpler: use `vite-plugin-static-copy`.

For simplicity, manually copy and add to scripts:

Run: `cd web && cp src/engine/calculator.py public/calculator.py`

Edit `web/package.json` to add `"copy-calc"` script and update `predev`/`prebuild`.

- [x] **Step 3: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/public/pyodide-worker.js web/public/calculator.py web/package.json
git commit -m "feat: add Pyodide web worker (classic, in public/)"
```

---

### Task 8: Create useCalculator Hook and PyodideProvider

**Files:**
- Create: `web/src/hooks/useCalculator.ts`

- [x] **Step 1: Write useCalculator hook**

```typescript
// web/src/hooks/useCalculator.ts
import { createContext, useContext, useState, useEffect, useRef, useCallback, ReactNode } from 'react';
import type { CalculatorResult } from '../types';

interface CalculatorState {
  ready: boolean;
  loading: boolean;
  error: string | null;
  evaluate: (expression: string) => Promise<CalculatorResult>;
}

const CalculatorContext = createContext<CalculatorState>({
  ready: false,
  loading: true,
  error: null,
  evaluate: async () => ({ parsed: '', si: '', cgs: '' }),
});

export function PyodideProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const workerRef = useRef<Worker | null>(null);
  const pendingRef = useRef<Map<number, (r: CalculatorResult) => void>>(new Map());
  const nextIdRef = useRef(1);

  useEffect(() => {
    // Classic worker from public/ — needed for importScripts support in Pyodide
    // import.meta.env.BASE_URL handles base path in both dev (/) and prod (/astrocalculator/)
    const worker = new Worker(import.meta.env.BASE_URL + 'pyodide-worker.js');
    workerRef.current = worker;

    worker.onmessage = (e) => {
      const { id, type, payload } = e.data;
      if (type === 'ready') {
        setReady(true);
        setLoading(false);
      } else if (type === 'result') {
        const resolve = pendingRef.current.get(id);
        if (resolve) {
          pendingRef.current.delete(id);
          resolve(payload);
        }
      } else if (type === 'error') {
        setError(payload);
        setLoading(false);
        // Reject pending promise if there's one waiting
        const resolve = pendingRef.current.get(id);
        if (resolve) {
          pendingRef.current.delete(id);
          resolve({ parsed: '', si: payload, cgs: '' });
        }
      }
    };

    worker.onerror = (err) => {
      setError(err.message);
      setLoading(false);
    };

    worker.postMessage({ type: 'init' });

    return () => {
      worker.terminate();
    };
  }, []);

  const evaluate = useCallback((expression: string): Promise<CalculatorResult> => {
    return new Promise((resolve) => {
      const worker = workerRef.current;
      if (!worker || !ready) {
        resolve({ parsed: '', si: 'Engine not ready', cgs: '' });
        return;
      }
      const id = nextIdRef.current++;
      pendingRef.current.set(id, resolve);
      worker.postMessage({ id, type: 'evaluate', payload: expression });
    });
  }, [ready]);

  return (
    <CalculatorContext.Provider value={{ ready, loading, error, evaluate }}>
      {children}
    </CalculatorContext.Provider>
  );
}

export function useCalculator() {
  return useContext(CalculatorContext);
}
```

- [x] **Step 2: Verify TypeScript compilation**

Run: `cd web && npx tsc --noEmit`
Expected: No errors

- [x] **Step 3: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/src/hooks/useCalculator.ts
git commit -m "feat: add useCalculator hook with PyodideProvider"
```

---

### Task 9: Create App Shell, Header, and StudioLayout

**Files:**
- Create: `web/src/components/Header.tsx`
- Create: `web/src/components/StudioLayout.tsx`
- Modify: `web/src/App.tsx`
- Modify: `web/src/App.css`
- Modify: `web/src/index.css`

- [x] **Step 1: Write global CSS reset and variables**

Replace `web/src/index.css`:

```css
/* web/src/index.css */
:root {
  --sidebar-width: 320px;
  --color-bg: #f8fafc;
  --color-surface: #ffffff;
  --color-border: #e2e8f0;
  --color-text: #1a202c;
  --color-text-muted: #718096;
  --color-accent: #3182ce;
  --color-accent-light: #ebf8ff;
  --color-success: #38a169;
  --color-error: #e53e3e;
  --color-si: #ebf8ff;
  --color-cgs: #fffbeb;
  --color-parsed: #f0fdf4;
  --radius: 6px;
  --shadow: 0 1px 3px rgba(0,0,0,0.08);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #root {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  color: var(--color-text);
  background: var(--color-bg);
}
```

- [x] **Step 2: Write Header component**

```typescript
// web/src/components/Header.tsx
import { useCalculator } from '../hooks/useCalculator';

export default function Header() {
  const { ready, loading } = useCalculator();

  return (
    <header style={{
      height: 40,
      display: 'flex',
      alignItems: 'center',
      padding: '0 16px',
      background: 'var(--color-surface)',
      borderBottom: '1px solid var(--color-border)',
      gap: 12,
    }}>
      <h1 style={{ fontSize: 16, fontWeight: 700 }}>AstroCalculator</h1>
      <span style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>
        {loading ? 'Loading engine...' : ready ? 'Ready' : 'Error'}
      </span>
      {loading && <div className="spinner" style={{
        width: 12, height: 12, border: '2px solid #e0e0e0',
        borderTopColor: 'var(--color-accent)', borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />}
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </header>
  );
}
```

- [x] **Step 3: Write StudioLayout component**

```typescript
// web/src/components/StudioLayout.tsx
import { useState, ReactNode } from 'react';
import Sidebar from './Sidebar';
import type { SidebarTab } from '../types';

interface StudioLayoutProps {
  editor: ReactNode;
  results: ReactNode;
  onConstantClick: (symbol: string) => void;
  onEquationAdd: (params: { symbol: string; default: string }[], expression: string) => void;
  onHistoryClick: (input: string) => void;
  onSearchFocus: () => void;
  searchBarRef: React.RefObject<HTMLInputElement | null>;
  editorRef: React.RefObject<HTMLTextAreaElement | null>;
}

export default function StudioLayout({
  editor, results, onConstantClick, onEquationAdd,
  onHistoryClick, onSearchFocus, searchBarRef, editorRef,
}: StudioLayoutProps) {
  const [activeTab, setActiveTab] = useState<SidebarTab>('constants');
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div style={{
      display: 'flex',
      height: 'calc(100% - 40px)',
    }}>
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onConstantClick={onConstantClick}
        onEquationAdd={onEquationAdd}
        onHistoryClick={onHistoryClick}
        searchBarRef={searchBarRef}
      />
      <main style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        padding: 16,
        gap: 12,
        minWidth: 0,
      }}>
        {editor}
        {results}
      </main>
    </div>
  );
}
```

- [x] **Step 4: Write App.tsx**

```typescript
// web/src/App.tsx
import { useRef, useCallback } from 'react';
import { PyodideProvider } from './hooks/useCalculator';
import Header from './components/Header';
import StudioLayout from './components/StudioLayout';
import ExpressionEditor from './components/ExpressionEditor';
import ResultDisplay from './components/ResultDisplay';

export default function App() {
  return (
    <PyodideProvider>
      <AppContent />
    </PyodideProvider>
  );
}

function AppContent() {
  const searchBarRef = useRef<HTMLInputElement>(null);
  const editorRef = useRef<HTMLTextAreaElement>(null);

  const handleConstantClick = useCallback((symbol: string) => {
    const ta = editorRef.current;
    if (ta) {
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      ta.value = ta.value.slice(0, start) + symbol + ta.value.slice(end);
      ta.focus();
      ta.setSelectionRange(start + symbol.length, start + symbol.length);
    }
  }, []);

  const handleEquationAdd = useCallback((
    params: { symbol: string; default: string }[],
    expression: string
  ) => {
    const ta = editorRef.current;
    if (ta) {
      const assignments = params.map(p => `${p.symbol} = ${p.default}`).join('\n');
      const text = assignments + '\n' + expression;
      // If editor is empty, replace; otherwise append
      if (ta.value.trim()) {
        ta.value = ta.value + '\n' + text;
      } else {
        ta.value = text;
      }
      ta.focus();
    }
  }, []);

  const handleHistoryClick = useCallback((input: string) => {
    const ta = editorRef.current;
    if (ta) {
      ta.value = input;
      ta.focus();
    }
  }, []);

  const handleSearchFocus = useCallback(() => {
    searchBarRef.current?.focus();
  }, []);

  return (
    <>
      <Header />
      <StudioLayout
        editor={<ExpressionEditor editorRef={editorRef} />}
        results={<ResultDisplay />}
        onConstantClick={handleConstantClick}
        onEquationAdd={handleEquationAdd}
        onHistoryClick={handleHistoryClick}
        onSearchFocus={handleSearchFocus}
        searchBarRef={searchBarRef}
        editorRef={editorRef}
      />
    </>
  );
}
```

- [x] **Step 5: Verify TypeScript compilation**

Run: `cd web && npx tsc --noEmit`
Expected: No errors (warnings for missing components are OK — they're created in subsequent tasks)

- [x] **Step 6: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/src/components/Header.tsx web/src/components/StudioLayout.tsx web/src/App.tsx web/src/index.css web/src/App.css
git commit -m "feat: add App shell, Header, and StudioLayout"
```

---

### Task 10: Create Sidebar Component

**Files:**
- Create: `web/src/components/Sidebar.tsx`

- [x] **Step 1: Write Sidebar component**

```typescript
// web/src/components/Sidebar.tsx
import type { SidebarTab } from '../types';
import SearchBar from './SearchBar';
import ConstantsTable from './ConstantsTable';
import UnitsTable from './UnitsTable';
import EquationTemplates from './EquationTemplates';
import HistoryPanel from './HistoryPanel';

interface SidebarProps {
  activeTab: SidebarTab;
  onTabChange: (tab: SidebarTab) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onConstantClick: (symbol: string) => void;
  onEquationAdd: (params: { symbol: string; default: string }[], expression: string) => void;
  onHistoryClick: (input: string) => void;
  searchBarRef: React.RefObject<HTMLInputElement | null>;
}

const TABS: { key: SidebarTab; label: string }[] = [
  { key: 'constants', label: 'Constants' },
  { key: 'units', label: 'Units' },
  { key: 'equations', label: 'Equations' },
  { key: 'history', label: 'History' },
];

export default function Sidebar({
  activeTab, onTabChange, searchQuery, onSearchChange,
  onConstantClick, onEquationAdd, onHistoryClick, searchBarRef,
}: SidebarProps) {
  return (
    <aside style={{
      width: 'var(--sidebar-width)',
      borderRight: '1px solid var(--color-border)',
      background: 'var(--color-surface)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
    }}>
      <div style={{ padding: '8px 12px' }}>
        <SearchBar
          value={searchQuery}
          onChange={onSearchChange}
          inputRef={searchBarRef}
        />
      </div>

      {/* Tabs */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--color-border)',
        padding: '0 12px',
      }}>
        {TABS.map(tab => (
          <button
            key={tab.key}
            onClick={() => onTabChange(tab.key)}
            style={{
              padding: '6px 10px',
              border: 'none',
              background: 'none',
              borderBottom: activeTab === tab.key ? '2px solid var(--color-accent)' : '2px solid transparent',
              color: activeTab === tab.key ? 'var(--color-accent)' : 'var(--color-text-muted)',
              fontWeight: activeTab === tab.key ? 600 : 400,
              cursor: 'pointer',
              fontSize: 12,
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        {activeTab === 'constants' && (
          <ConstantsTable query={searchQuery} onClick={onConstantClick} />
        )}
        {activeTab === 'units' && (
          <UnitsTable query={searchQuery} onClick={onConstantClick} />
        )}
        {activeTab === 'equations' && (
          <EquationTemplates query={searchQuery} onAdd={onEquationAdd} />
        )}
        {activeTab === 'history' && (
          <HistoryPanel onClick={onHistoryClick} />
        )}
      </div>
    </aside>
  );
}
```

- [x] **Step 2: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/src/components/Sidebar.tsx
git commit -m "feat: add Sidebar with tab navigation"
```

---

### Task 11: Create SearchBar Component

**Files:**
- Create: `web/src/components/SearchBar.tsx`

- [x] **Step 1: Write SearchBar component**

```typescript
// web/src/components/SearchBar.tsx

interface SearchBarProps {
  value: string;
  onChange: (q: string) => void;
  inputRef: React.RefObject<HTMLInputElement | null>;
}

export default function SearchBar({ value, onChange, inputRef }: SearchBarProps) {
  return (
    <input
      ref={inputRef}
      type="text"
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder="Search (G, Planck, energy...)"
      style={{
        width: '100%',
        padding: '6px 10px',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius)',
        fontSize: 13,
        outline: 'none',
      }}
      onFocus={e => e.target.style.borderColor = 'var(--color-accent)'}
      onBlur={e => e.target.style.borderColor = 'var(--color-border)'}
    />
  );
}
```

- [x] **Step 2: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/src/components/SearchBar.tsx
git commit -m "feat: add SearchBar component"
```

---

### Task 12: Create ConstantsTable and UnitsTable Components

**Files:**
- Create: `web/src/components/ConstantsTable.tsx`
- Create: `web/src/components/UnitsTable.tsx`

- [x] **Step 1: Write ConstantsTable component**

```typescript
// web/src/components/ConstantsTable.tsx
import { useMemo } from 'react';
import type { ConstantEntry } from '../types';
import constantsData from '../data/constants.json';

const constants: ConstantEntry[] = constantsData as ConstantEntry[];

interface ConstantsTableProps {
  query: string;
  onClick: (symbol: string) => void;
}

export default function ConstantsTable({ query, onClick }: ConstantsTableProps) {
  const filtered = useMemo(() => {
    if (!query.trim()) return constants;
    const q = query.toLowerCase();
    return constants.filter(c =>
      c.symbol.toLowerCase().includes(q) ||
      c.name.toLowerCase().includes(q)
    );
  }, [query]);

  return (
    <div style={{ height: '100%', overflowY: 'auto', fontSize: 12 }}>
      <div style={{
        display: 'flex',
        padding: '6px 12px',
        borderBottom: '1px solid var(--color-border)',
        fontWeight: 600,
        color: 'var(--color-text-muted)',
        position: 'sticky', top: 0, background: 'var(--color-surface)',
      }}>
        <span style={{ flex: 1 }}>Symbol</span>
        <span style={{ flex: 2 }}>Name</span>
        <span style={{ flex: 1.5, textAlign: 'right' }}>Value</span>
        <span style={{ flex: 1, textAlign: 'right' }}>Unit</span>
      </div>
      {filtered.map(c => (
        <div
          key={c.symbol}
          onClick={() => onClick(c.symbol)}
          style={{
            display: 'flex',
            padding: '5px 12px',
            borderBottom: '1px solid #f5f5f5',
            cursor: 'pointer',
          }}
          onMouseEnter={e => (e.currentTarget.style.background = 'var(--color-accent-light)')}
          onMouseLeave={e => (e.currentTarget.style.background = '')}
        >
          <span style={{ flex: 1, fontWeight: 600, fontFamily: 'monospace' }}>{c.symbol}</span>
          <span style={{ flex: 2, color: 'var(--color-text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.name}</span>
          <span style={{ flex: 1.5, textAlign: 'right', fontFamily: 'monospace', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.value.toExponential(3)}</span>
          <span style={{ flex: 1, textAlign: 'right', color: 'var(--color-text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.unit}</span>
        </div>
      ))}
    </div>
  );
}
```

- [x] **Step 2: Write UnitsTable component**

```typescript
// web/src/components/UnitsTable.tsx
import { useMemo } from 'react';
import type { UnitEntry } from '../types';
import unitsData from '../data/units.json';

const units: UnitEntry[] = unitsData as UnitEntry[];

interface UnitsTableProps {
  query: string;
  onClick: (name: string) => void;
}

export default function UnitsTable({ query, onClick }: UnitsTableProps) {
  const grouped = useMemo(() => {
    const q = query.toLowerCase().trim();
    const filtered = q
      ? units.filter(u => u.name.toLowerCase().includes(q) || u.category.toLowerCase().includes(q))
      : units;
    const map = new Map<string, UnitEntry[]>();
    for (const u of filtered) {
      const list = map.get(u.category) || [];
      list.push(u);
      map.set(u.category, list);
    }
    return map;
  }, [query]);

  return (
    <div style={{ height: '100%', overflowY: 'auto', fontSize: 12 }}>
      {Array.from(grouped.entries()).map(([category, entries]) => (
        <div key={category}>
          <div style={{
            padding: '6px 12px',
            fontWeight: 600,
            color: 'var(--color-text-muted)',
            background: '#f8fafc',
            position: 'sticky', top: 0,
            borderBottom: '1px solid var(--color-border)',
          }}>
            {category}
          </div>
          {entries.map(u => (
            <div
              key={u.name}
              onClick={() => onClick(u.name)}
              style={{
                padding: '5px 12px',
                borderBottom: '1px solid #f5f5f5',
                cursor: 'pointer',
                fontFamily: 'monospace',
              }}
              onMouseEnter={e => (e.currentTarget.style.background = 'var(--color-accent-light)')}
              onMouseLeave={e => (e.currentTarget.style.background = '')}
            >
              {u.name}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
```

- [x] **Step 3: Verify TypeScript compilation (JSON imports need resolveJsonModule)**

Ensure `web/tsconfig.json` has `"resolveJsonModule": true` in compilerOptions.

Read `web/tsconfig.json`, use Edit to add `"resolveJsonModule": true` if missing.

Run: `cd web && npx tsc --noEmit`
Expected: No errors

- [x] **Step 4: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/src/components/ConstantsTable.tsx web/src/components/UnitsTable.tsx web/tsconfig.json
git commit -m "feat: add ConstantsTable and UnitsTable components"
```

---

### Task 13: Create EquationTemplates Component

**Files:**
- Create: `web/src/components/EquationTemplates.tsx`

- [x] **Step 1: Write EquationTemplates component**

```typescript
// web/src/components/EquationTemplates.tsx
import { useMemo } from 'react';
import katex from 'katex';
import type { Equation } from '../types';
import equationsData from '../data/equations.json';

const equations: Equation[] = equationsData as Equation[];

interface EquationTemplatesProps {
  query: string;
  onAdd: (params: { symbol: string; default: string }[], expression: string) => void;
}

function renderLatex(latex: string): string {
  try {
    return katex.renderToString(latex, { throwOnError: false, displayMode: true });
  } catch {
    return latex;
  }
}

export default function EquationTemplates({ query, onAdd }: EquationTemplatesProps) {
  const filtered = useMemo(() => {
    if (!query.trim()) return equations;
    const q = query.toLowerCase();
    return equations.filter(eq =>
      eq.title.toLowerCase().includes(q) ||
      eq.tags.some(t => t.toLowerCase().includes(q)) ||
      eq.category.toLowerCase().includes(q) ||
      eq.params.some(p => p.symbol.toLowerCase().includes(q)) ||
      eq.expressions.some(ex => ex.name.toLowerCase().includes(q))
    );
  }, [query]);

  return (
    <div style={{ height: '100%', overflowY: 'auto', fontSize: 12 }}>
      {filtered.map(eq => (
        <div
          key={eq.slug}
          style={{ padding: '10px 12px', borderBottom: '1px solid var(--color-border)' }}
        >
          <div style={{ fontWeight: 600, marginBottom: 2 }}>{eq.title}</div>
          <div style={{ color: 'var(--color-text-muted)', fontSize: 11, marginBottom: 8 }}>
            {eq.category} · {eq.params.map(p => p.symbol).join(', ')}
          </div>

          {eq.expressions.map((ex, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                padding: '6px 0',
                borderTop: i > 0 ? '1px solid #f0f0f0' : 'none',
              }}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ color: 'var(--color-text-muted)', fontSize: 11, marginBottom: 2 }}>
                  {ex.name}
                </div>
                {ex.latex ? (
                  <div
                    style={{ fontSize: 12 }}
                    dangerouslySetInnerHTML={{ __html: renderLatex(ex.latex) }}
                  />
                ) : (
                  <code style={{ fontSize: 11, color: '#555' }}>{ex.expression}</code>
                )}
                {ex.description && (
                  <div style={{ fontSize: 10, color: 'var(--color-text-muted)', marginTop: 2 }}>
                    {ex.description}
                  </div>
                )}
              </div>
              <button
                onClick={() => onAdd(eq.params, ex.expression)}
                style={{
                  marginLeft: 8,
                  padding: '2px 10px',
                  fontSize: 11,
                  background: 'var(--color-accent)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 'var(--radius)',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                }}
              >
                Add
              </button>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
```

- [x] **Step 2: Verify TypeScript compilation**

Run: `cd web && npx tsc --noEmit`
Expected: No errors

- [x] **Step 3: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/src/components/EquationTemplates.tsx
git commit -m "feat: add EquationTemplates component with KaTeX rendering"
```

---

### Task 14: Create ExpressionEditor Component

**Files:**
- Create: `web/src/components/ExpressionEditor.tsx`

- [x] **Step 1: Write ExpressionEditor component**

```typescript
// web/src/components/ExpressionEditor.tsx
import { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import constantsData from '../data/constants.json';
import unitsData from '../data/units.json';
import type { ConstantEntry, UnitEntry } from '../types';

const constants: ConstantEntry[] = constantsData as ConstantEntry[];
const units: UnitEntry[] = unitsData as UnitEntry[];

interface ExpressionEditorProps {
  editorRef: React.RefObject<HTMLTextAreaElement | null>;
}

export default function ExpressionEditor({ editorRef }: ExpressionEditorProps) {
  const [value, setValue] = useState('');
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [suggestions, setSuggestions] = useState<{ text: string; type: 'constant' | 'unit' }[]>([]);
  const [selectedIdx, setSelectedIdx] = useState(0);

  const allItems = useMemo(() => [
    ...constants.map(c => ({ text: c.symbol, type: 'constant' as const })),
    ...units.map(u => ({ text: u.name, type: 'unit' as const })),
  ], []);

  const handleInput = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setValue(newValue);

    // Get current word being typed
    const cursorPos = e.target.selectionStart;
    const textBeforeCursor = newValue.slice(0, cursorPos);
    const lastWordMatch = textBeforeCursor.match(/[\w_]+$/);

    if (lastWordMatch) {
      const word = lastWordMatch[0].toLowerCase();
      const matches = allItems.filter(item =>
        item.text.toLowerCase().includes(word)
      ).slice(0, 8);
      if (matches.length > 0) {
        setSuggestions(matches);
        setShowAutocomplete(true);
        setSelectedIdx(0);
        return;
      }
    }
    setShowAutocomplete(false);
  }, [allItems]);

  const insertSuggestion = useCallback((text: string) => {
    const ta = editorRef.current;
    if (!ta) return;
    const cursorPos = ta.selectionStart;
    const textBeforeCursor = ta.value.slice(0, cursorPos);
    const lastWordMatch = textBeforeCursor.match(/[\w_]+$/);
    if (lastWordMatch) {
      const before = ta.value.slice(0, cursorPos - lastWordMatch[0].length);
      const after = ta.value.slice(cursorPos);
      const newValue = before + text + after;
      setValue(newValue);
      // Need setTimeout for React state to flush before setting cursor
      setTimeout(() => {
        ta.value = before + text + after;
        ta.selectionStart = ta.selectionEnd = before.length + text.length;
        ta.focus();
      }, 0);
    }
    setShowAutocomplete(false);
  }, [editorRef]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      // Trigger evaluate — handled by parent via custom event
      window.dispatchEvent(new CustomEvent('evaluate', { detail: value }));
      return;
    }

    if (showAutocomplete) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIdx(prev => (prev + 1) % suggestions.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIdx(prev => (prev - 1 + suggestions.length) % suggestions.length);
      } else if (e.key === 'Enter' || e.key === 'Tab') {
        e.preventDefault();
        insertSuggestion(suggestions[selectedIdx].text);
      } else if (e.key === 'Escape') {
        setShowAutocomplete(false);
      }
    }
  }, [showAutocomplete, suggestions, selectedIdx, insertSuggestion, value]);

  // Listen for Cmd+J to focus
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'j') {
        e.preventDefault();
        editorRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [editorRef]);

  const lines = value.split('\n').length;

  return (
    <div style={{ position: 'relative', flex: 1, display: 'flex', flexDirection: 'column' }}>
      <div style={{
        display: 'flex',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius)',
        background: 'var(--color-surface)',
        flex: 1,
      }}>
        {/* Line numbers */}
        <div style={{
          padding: '8px 0',
          background: '#f8fafc',
          borderRight: '1px solid var(--color-border)',
          fontFamily: 'monospace',
          fontSize: 13,
          color: 'var(--color-text-muted)',
          textAlign: 'right',
          minWidth: 36,
          userSelect: 'none',
        }}>
          {Array.from({ length: Math.max(lines, 1) }, (_, i) => (
            <div key={i} style={{ padding: '0 8px', lineHeight: '1.5' }}>{i + 1}</div>
          ))}
        </div>

        <textarea
          ref={editorRef}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={`Enter expressions...\ne.g. M = 1.4 M_sun\nR = 10 km\nsqrt(2 G M / R) in km/s`}
          spellCheck={false}
          style={{
            flex: 1,
            border: 'none',
            outline: 'none',
            resize: 'none',
            padding: '8px 10px',
            fontFamily: 'monospace',
            fontSize: 13,
            lineHeight: 1.5,
            background: 'transparent',
          }}
        />
      </div>

      {/* Autocomplete dropdown */}
      {showAutocomplete && suggestions.length > 0 && (
        <div style={{
          position: 'absolute',
          bottom: 'calc(100% + 4px)',
          left: 36,
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius)',
          boxShadow: 'var(--shadow)',
          zIndex: 10,
          minWidth: 200,
        }}>
          {suggestions.map((s, i) => (
            <div
              key={s.text}
              onClick={() => insertSuggestion(s.text)}
              style={{
                padding: '4px 10px',
                cursor: 'pointer',
                background: i === selectedIdx ? 'var(--color-accent-light)' : undefined,
                fontSize: 12,
                fontFamily: 'monospace',
                display: 'flex',
                justifyContent: 'space-between',
              }}
            >
              <span>{s.text}</span>
              <span style={{ color: 'var(--color-text-muted)', fontSize: 10 }}>{s.type}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

- [x] **Step 2: Verify TypeScript compilation**

Run: `cd web && npx tsc --noEmit`
Expected: No errors

- [x] **Step 3: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/src/components/ExpressionEditor.tsx
git commit -m "feat: add ExpressionEditor with autocomplete and keyboard shortcuts"
```

---

### Task 15: Create ResultDisplay Component

**Files:**
- Create: `web/src/components/ResultDisplay.tsx`

- [x] **Step 1: Write ResultDisplay component**

```typescript
// web/src/components/ResultDisplay.tsx
import { useState, useEffect, useCallback } from 'react';
import { useCalculator } from '../hooks/useCalculator';
import type { CalculatorResult } from '../types';

export default function ResultDisplay() {
  const { evaluate, ready } = useCalculator();
  const [result, setResult] = useState<CalculatorResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [evaluating, setEvaluating] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail as string;
      if (!detail.trim()) return;
      setEvaluating(true);
      setError(null);
      evaluate(detail).then(res => {
        setResult(res);
        setEvaluating(false);
      }).catch(err => {
        setError(String(err));
        setEvaluating(false);
      });
    };
    window.addEventListener('evaluate', handler);
    return () => window.removeEventListener('evaluate', handler);
  }, [evaluate]);

  const copyText = useCallback((text: string) => {
    navigator.clipboard.writeText(text).catch(() => {});
  }, []);

  if (!result && !error && !evaluating) {
    return (
      <div style={{ color: 'var(--color-text-muted)', fontSize: 13, textAlign: 'center', padding: 20 }}>
        {ready
          ? 'Cmd+Enter to evaluate'
          : 'Loading scientific engine...'}
      </div>
    );
  }

  if (evaluating) {
    return <div style={{ color: 'var(--color-text-muted)', fontSize: 13, textAlign: 'center', padding: 20 }}>Evaluating...</div>;
  }

  if (error) {
    return (
      <div style={{ background: '#fff5f5', padding: 12, borderRadius: 'var(--radius)', color: 'var(--color-error)', fontSize: 13 }}>
        {error}
      </div>
    );
  }

  if (!result) return null;

  const cards = [
    { label: 'PARSED', value: result.parsed, color: 'var(--color-parsed)' },
    { label: 'RESULT (SI)', value: result.si, color: 'var(--color-si)' },
    { label: 'RESULT (CGS)', value: result.cgs, color: 'var(--color-cgs)' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ display: 'flex', gap: 8 }}>
        {cards.map(card => (
          <div key={card.label} style={{
            flex: 1,
            background: card.color,
            padding: '10px 12px',
            borderRadius: 'var(--radius)',
            position: 'relative',
          }}>
            <div style={{ fontSize: 10, color: 'var(--color-text-muted)', marginBottom: 2 }}>
              {card.label}
            </div>
            <div style={{ fontFamily: 'monospace', fontSize: 13, wordBreak: 'break-all' }}>
              {card.value}
            </div>
            <button
              onClick={() => copyText(card.value)}
              title="Copy"
              style={{
                position: 'absolute',
                top: 4,
                right: 4,
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                fontSize: 12,
                color: 'var(--color-text-muted)',
                padding: '2px 4px',
              }}
            >
              Copy
            </button>
          </div>
        ))}
      </div>

      {result.converted && (
        <div style={{
          background: '#faf5ff',
          padding: '10px 12px',
          borderRadius: 'var(--radius)',
          position: 'relative',
        }}>
          <div style={{ fontSize: 10, color: 'var(--color-text-muted)', marginBottom: 2 }}>
            IN {result.targetUnit?.toUpperCase() || 'CONVERTED'}
          </div>
          <div style={{ fontFamily: 'monospace', fontSize: 13 }}>{result.converted}</div>
          <button
            onClick={() => copyText(result.converted!)}
            title="Copy"
            style={{
              position: 'absolute', top: 4, right: 4,
              background: 'transparent', border: 'none',
              cursor: 'pointer', fontSize: 12,
              color: 'var(--color-text-muted)', padding: '2px 4px',
            }}
          >
            Copy
          </button>
        </div>
      )}
    </div>
  );
}
```

- [x] **Step 2: Verify TypeScript compilation**

Run: `cd web && npx tsc --noEmit`
Expected: No errors

- [x] **Step 3: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/src/components/ResultDisplay.tsx
git commit -m "feat: add ResultDisplay with copy buttons"
```

---

### Task 16: Create HistoryPanel Component

**Files:**
- Create: `web/src/components/HistoryPanel.tsx`

- [x] **Step 1: Write HistoryPanel component**

```typescript
// web/src/components/HistoryPanel.tsx
import { useState, useEffect, useCallback } from 'react';
import type { HistoryEntry } from '../types';

const HISTORY_KEY = 'astrocalculator-history';
const MAX_HISTORY = 100;

interface HistoryPanelProps {
  onClick: (input: string) => void;
}

export default function HistoryPanel({ onClick }: HistoryPanelProps) {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);

  // Load history from localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem(HISTORY_KEY);
      if (raw) {
        setEntries(JSON.parse(raw));
      }
    } catch {}
  }, []);

  // Listen for new evaluations to add to history
  useEffect(() => {
    const handler = (e: Event) => {
      const input = (e as CustomEvent).detail as string;
      if (!input.trim()) return;
      setEntries(prev => {
        const newEntry: HistoryEntry = {
          id: Date.now(),
          input,
          result: { parsed: '', si: '', cgs: '' },
          timestamp: Date.now(),
        };
        const updated = [newEntry, ...prev].slice(0, MAX_HISTORY);
        try {
          localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
        } catch {}
        return updated;
      });
    };
    window.addEventListener('evaluate', handler);
    return () => window.removeEventListener('evaluate', handler);
  }, []);

  const clearHistory = useCallback(() => {
    setEntries([]);
    localStorage.removeItem(HISTORY_KEY);
  }, []);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ flex: 1, overflowY: 'auto', fontSize: 12 }}>
        {entries.length === 0 ? (
          <div style={{ color: 'var(--color-text-muted)', padding: 16, textAlign: 'center' }}>
            No history yet
          </div>
        ) : (
          entries.map(entry => (
            <div
              key={entry.id}
              onClick={() => onClick(entry.input)}
              style={{
                padding: '8px 12px',
                borderBottom: '1px solid #f0f0f0',
                cursor: 'pointer',
                fontFamily: 'monospace',
                fontSize: 12,
              }}
              onMouseEnter={e => (e.currentTarget.style.background = 'var(--color-accent-light)')}
              onMouseLeave={e => (e.currentTarget.style.background = '')}
            >
              <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{entry.input}</div>
              <div style={{ color: 'var(--color-text-muted)', fontSize: 10, marginTop: 2 }}>
                {new Date(entry.timestamp).toLocaleString()}
              </div>
            </div>
          ))
        )}
      </div>
      {entries.length > 0 && (
        <button
          onClick={clearHistory}
          style={{
            margin: 8,
            padding: '4px 0',
            background: 'none',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius)',
            cursor: 'pointer',
            fontSize: 12,
            color: 'var(--color-text-muted)',
          }}
        >
          Clear history
        </button>
      )}
    </div>
  );
}
```

- [x] **Step 2: Verify TypeScript compilation**

Run: `cd web && npx tsc --noEmit`
Expected: No errors

- [x] **Step 3: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/src/components/HistoryPanel.tsx
git commit -m "feat: add HistoryPanel with localStorage persistence"
```

---

### Task 17: Wire Keyboard Shortcuts and Final Integration

**Files:**
- Modify: `web/src/App.tsx`

- [x] **Step 1: Update App.tsx with Cmd+K shortcut and evaluation integration**

Read `web/src/App.tsx` and replace with:

```typescript
// web/src/App.tsx
import { useRef, useCallback, useEffect } from 'react';
import { PyodideProvider } from './hooks/useCalculator';
import Header from './components/Header';
import StudioLayout from './components/StudioLayout';
import ExpressionEditor from './components/ExpressionEditor';
import ResultDisplay from './components/ResultDisplay';

export default function App() {
  return (
    <PyodideProvider>
      <AppContent />
    </PyodideProvider>
  );
}

function AppContent() {
  const searchBarRef = useRef<HTMLInputElement>(null);
  const editorRef = useRef<HTMLTextAreaElement>(null);

  // Cmd+K → focus search bar
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        searchBarRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const handleConstantClick = useCallback((symbol: string) => {
    const ta = editorRef.current;
    if (ta) {
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      ta.value = ta.value.slice(0, start) + symbol + ta.value.slice(end);
      ta.focus();
      ta.setSelectionRange(start + symbol.length, start + symbol.length);
      // Trigger React re-render for ExpressionEditor
      ta.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }, []);

  const handleEquationAdd = useCallback((
    params: { symbol: string; default: string }[],
    expression: string
  ) => {
    const ta = editorRef.current;
    if (ta) {
      const assignments = params.map(p => `${p.symbol} = ${p.default}`).join('\n');
      const text = assignments + '\n' + expression;
      if (ta.value.trim()) {
        ta.value = ta.value + '\n' + text;
      } else {
        ta.value = text;
      }
      ta.focus();
      ta.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }, []);

  const handleHistoryClick = useCallback((input: string) => {
    const ta = editorRef.current;
    if (ta) {
      ta.value = input;
      ta.focus();
      ta.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }, []);

  const handleSearchFocus = useCallback(() => {
    searchBarRef.current?.focus();
  }, []);

  return (
    <>
      <Header />
      <StudioLayout
        editor={<ExpressionEditor editorRef={editorRef} />}
        results={<ResultDisplay />}
        onConstantClick={handleConstantClick}
        onEquationAdd={handleEquationAdd}
        onHistoryClick={handleHistoryClick}
        onSearchFocus={handleSearchFocus}
        searchBarRef={searchBarRef}
        editorRef={editorRef}
      />
    </>
  );
}
```

- [x] **Step 2: Update main.tsx to remove Vite default content**

Read `web/src/main.tsx` and ensure it renders App:

```typescript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- [x] **Step 3: Verify TypeScript compilation**

Run: `cd web && npx tsc --noEmit`
Expected: No errors

- [x] **Step 4: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add web/src/App.tsx web/src/main.tsx
git commit -m "feat: wire keyboard shortcuts and final integration"
```

---

### Task 18: Test the App Locally

- [x] **Step 1: Start dev server**

Run: `cd web && npm run dev`
Expected: Dev server starts on http://localhost:5173

- [x] **Step 2: Check loading state**
Open http://localhost:5173 in browser.
Expected: "Loading engine..." spinner in header. Sidebar shows constants/units tables from JSON. Search works instantly.

- [x] **Step 3: Wait for Pyodide ready**
After ~5-8s, the spinner should disappear and the header shows "Ready".

- [x] **Step 4: Test a simple expression**
Type `m_e c^2 in MeV` in the editor, press Cmd+Enter.
Expected: Result cards show parsed expression, SI value (~8.1871e-14 J), CGS value, and converted 0.5110 MeV.

- [x] **Step 5: Test click-to-insert**
Click on "G" in the constants table.
Expected: "G" is inserted at cursor in the editor.

- [x] **Step 6: Test equation template**
Switch to Equations tab, click "Add" on Escape velocity.
Expected: Expression editor populates with `M = 1.4 M_sun\nR = 10 km\nsqrt(2 G M / R) in km/s`.

- [x] **Step 7: Test autocomplete**
Type `m_` in the editor.
Expected: Autocomplete dropdown shows `m_e`, `m_p`, `m_n`.

- [x] **Step 8: Test history**
After evaluating, switch to History tab.
Expected: Shows the expression just evaluated. Click it to reload.

- [x] **Step 9: Test keyboard shortcuts**
Press Cmd+K to focus search bar. Press Cmd+J to focus editor.

- [x] **Step 10: Commit any fixes**

```bash
cd /Users/u1149259/git/astrocalculator
git add -A web/
git commit -m "fix: issues found during manual testing"
```

---

### Task 19: Create GitHub Actions Deployment Workflow

**Files:**
- Create: `.github/workflows/deploy.yml`

- [x] **Step 1: Write deployment workflow**

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: web

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: web/package-lock.json

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Python deps
        run: pip install astropy numpy sympy

      - name: Install Node deps
        run: npm ci

      - name: Dump constants & units
        run: npm run dump-data

      - name: Build
        run: npm run build

      - uses: actions/configure-pages@v4

      - uses: actions/upload-pages-artifact@v3
        with:
          path: web/dist

      - uses: actions/deploy-pages@v4
        id: deployment

      - name: Output URL
        run: echo "Deployed to ${{ steps.deployment.outputs.page_url }}"
```

- [x] **Step 2: Commit**

```bash
cd /Users/u1149259/git/astrocalculator
git add .github/workflows/deploy.yml
git commit -m "feat: add GitHub Actions deployment to GitHub Pages"
```
