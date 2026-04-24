# AstroCalculator Web — Design Spec

**Date:** 2026-04-24
**Status:** Approved

## Overview

Rewrite AstroCalculator as a client-side web application hosted on GitHub Pages. The core calculation engine (Python + astropy + sympy) runs in the browser via Pyodide/WebAssembly. The frontend is a React + Vite single-page app with a Studio layout — a persistent sidebar for discoverability and a main panel for expression editing.

## Goals

1. **Input ergonomics** — proper multi-line text editing in a browser with keyboard shortcuts and autocomplete
2. **Discoverability** — always-visible, searchable constants and units tables
3. **Equation templates** — pre-built astrophysics equations with one-click insertion, defined as markdown files
4. **Preserve existing features** — same expression syntax, same astropy-based results, SI/CGS display, variable assignments, history
5. **Offline support** — local dev server for daily use, service worker for deployed PWA

## Architecture

### Component Tree

```
App
├── PyodideProvider          // React context — loads Pyodide in web worker, exposes useCalculator() hook
├── Header                   // App title, GitHub link
└── StudioLayout
    ├── Sidebar
    │   ├── SearchBar        // Global search: matches symbol + physical name
    │   ├── ConstantsTable   // Tab: constants with click-to-insert
    │   ├── UnitsTable       // Tab: units grouped by category
    │   ├── EquationTemplates// Tab: markdown-driven equations with "Add" button
    │   └── HistoryPanel     // Tab: past calculations from localStorage
    └── MainPanel
        ├── ExpressionEditor // Multi-line textarea with autocomplete
        └── ResultDisplay    // Parsed / SI / CGS / Converted cards
```

### Data Flow

1. **Build time:** scripts dump astropy constants + units to JSON (`src/data/`). A Vite plugin reads `equations/*.md` and generates `equations.json`. These JSON files are bundled as static assets.
2. **Load time:** PyodideProvider mounts a web worker that downloads Pyodide + sympy + astropy + numpy (~30MB WASM). While loading, the UI is functional — sidebar search and autocomplete work from the bundled JSON (no Pyodide needed).
3. **Evaluate:** User types expression → Cmd+Enter → `postMessage` to web worker → worker runs `AstroCalculator.calculate()` → result returned → displayed in result cards.
4. **Insert constant:** User clicks a row in ConstantsTable or selects from autocomplete → symbol inserted at cursor in editor.
5. **Insert equation template:** User clicks "Add" on an equation → params assigned as variable lines + expression inserted into editor.

### Pyodide Web Worker

- Pyodide loads once and stays alive for the session.
- The worker exposes: `evaluate(expression)` and `convert(quantity, unit)`.
- The main thread communicates via `postMessage` — non-blocking, UI stays responsive.
- If Pyodide hasn't finished loading, the editor is disabled with a "Loading scientific engine..." indicator.

## Sidebar Design

### SearchBar
- Single input at the top of the sidebar.
- Matches against **symbol** ("G") and **physical name** ("gravitational constant", "Planck").
- Filters all sidebar tabs simultaneously — typing "energy" shows matching constants, units (eV, MeV, GeV), and equation templates.
- Instant filtering against the bundled JSON (no Pyodide needed).

### Tabs
Four tabs below the search bar: **Constants | Units | Equations | History**

**ConstantsTable:**
- Columns: Symbol | Name | Value | Unit | Uncertainty
- Clicking a row inserts the symbol into the editor at cursor position.
- Filtered by SearchBar.

**UnitsTable:**
- Grouped by category: Length, Mass, Time, Energy, Power, Pressure, Frequency, Temperature, Angular size, Astronomy, Composite.
- Each row shows the unit name. Clicking inserts it into the editor.

**EquationTemplates:**
- Rendered from `equations/*.md` files at build time.
- Each file can contain multiple expressions.
- Each expression shows: grey name label → KaTeX-rendered equation (or monospace code fallback) → optional description → "Add" button.
- "Add" inserts the params as variable assignment lines followed by the expression.

**HistoryPanel:**
- Shows last N calculations from localStorage.
- Each entry: expression + result. Click to reload into editor. "Clear" button at bottom.

## Equations Folder

### Directory
```
equations/
├── escape-velocity.md
├── schwarzschild-radius.md
├── kepler-third-law.md
└── ...
```

### File Format
```yaml
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
  - name: "Free-fall timescale"
    expression: "1 / sqrt(G rho)"
    description: "No LaTeX — renders as code"
---

(Optional markdown body for documentation — not parsed for sidebar display)
```

### Rendering Rules
| Field | How it renders |
|---|---|
| `name` | Grey label above the equation |
| `latex` | Rendered as display math via KaTeX below the name |
| `expression` | Inserted into the editor on "Add" (not displayed in sidebar) |
| `description` | Optional helper text below the equation |
| *no latex* | Displays `expression` as monospace code string instead |

### Build-time Ingestion
A Vite plugin reads all `.md` files from `equations/`, parses YAML frontmatter, and generates a single `equations.json` manifest bundled into the app. Adding a new equation requires no code changes — just drop a new `.md` file.

## Main Panel Design

### ExpressionEditor
- Multi-line `<textarea>` with line numbers.
- Each line is a variable assignment or the final expression (same model as current CLI).
- **Autocomplete:** dropdown overlay triggered as the user types, showing matching constants, units, and functions from the bundled JSON. Selecting one inserts it at cursor.
- **Keyboard shortcuts:**
  - `Cmd+Enter` — evaluate expression
  - `Cmd+K` — focus search bar in sidebar
  - `Cmd+J` — focus editor

### ResultDisplay
Three cards displayed after evaluation:
- **Parsed** — the SymPy-parsed expression string
- **Result (SI)** — SI-unit value with a copy button
- **Result (CGS)** — CGS-unit value with a copy button
- If the expression contains `in <unit>`, a fourth card shows the converted value

## Constants & Units JSON

Build scripts (`scripts/dump-constants.py`, `scripts/dump-units.py`) use astropy to dump all supported constants and units into:

```json
[
  {"symbol": "G",  "name": "Gravitational constant", "value": 6.6743e-11, "unit": "m^3/(kg s^2)", "uncertainty": 1.5e-15, "ref": "CODATA 2018"},
  {"symbol": "c",  "name": "Speed of light", "value": 2.99792458e8, "unit": "m/s", "uncertainty": 0, "ref": "CODATA 2018"},
  ...
]
```

This JSON powers the sidebar tables, search, and autocomplete — all instant, no Pyodide needed. The Pyodide engine is only invoked on actual evaluation, which gives the authoritative numeric result.

## Offline & Local Use

Three modes, all supported:

| Mode | Command | Pyodide Load | Offline |
|---|---|---|---|
| **Local dev server** | `npm run dev` | ~1-2s (local disk) | Always |
| **Local production** | `npm run build` then serve `dist/` with any static server | ~1-2s (local disk) | Always |
| **GitHub Pages (first visit)** | Open URL | ~3-8s (CDN) | No (needs CDN) |
| **GitHub Pages (subsequent)** | Service worker cached | Instant (cache) | Yes |

For the deployed version, the Vite PWA plugin (`vite-plugin-pwa`) adds a service worker that caches all app assets and the Pyodide WASM. After the first visit, the app loads instantly and works fully offline.

## What's Preserved from the CLI

- Same expression syntax: implicit multiplication (`m_e c^2`), `^` for exponentiation, `in <unit>` for conversion
- Same `AstroCalculator` Python class — identical calculation results
- Variable assignments with comma/multi-line separation
- SI + CGS result display
- All 28+ astropy constants
- History (now via localStorage instead of disk)

## What's New

- Searchable constants/units tables always visible in sidebar
- Autocomplete for constants and units in the editor
- Equation templates with one-click insertion (markdown-driven)
- KaTeX-rendered equations
- Multi-line text editing with proper cursor control
- Keyboard shortcuts (Cmd+Enter, Cmd+K, Cmd+J)
- Copy buttons on results
- PWA offline support
- Accessible from any device (mobile/tablet via browser)

## Technology Stack

- **Frontend:** React 18+, TypeScript, Vite
- **Math rendering:** KaTeX
- **Python engine:** Pyodide (CPython 3.11 compiled to WASM) with sympy, astropy, numpy
- **Offline:** vite-plugin-pwa (service worker)
- **Deployment:** GitHub Pages via GitHub Actions

## File Structure

```
astrocalculator-web/
├── equations/                 # Markdown definition files
│   ├── escape-velocity.md
│   └── ...
├── scripts/
│   ├── dump-constants.py      # Generates src/data/constants.json
│   └── dump-units.py          # Generates src/data/units.json
├── src/
│   ├── data/                  # Build artifacts (bundled)
│   │   ├── constants.json
│   │   └── units.json
│   ├── engine/
│   │   ├── calculator.py      # Existing AstroCalculator class
│   │   └── worker.ts          # Web worker: loads Pyodide, runs calculator
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── StudioLayout.tsx
│   │   ├── Sidebar.tsx
│   │   ├── SearchBar.tsx
│   │   ├── ConstantsTable.tsx
│   │   ├── UnitsTable.tsx
│   │   ├── EquationTemplates.tsx
│   │   ├── HistoryPanel.tsx
│   │   ├── ExpressionEditor.tsx
│   │   └── ResultDisplay.tsx
│   ├── hooks/
│   │   └── useCalculator.ts   // React hook wrapping the web worker
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── tsconfig.json
└── vite.config.ts             // Includes markdown→JSON + PWA plugins
```
