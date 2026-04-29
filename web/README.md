# AstroCalculator Web

A client-side calculator for astronomers and physicists. Runs entirely in the browser — no server required. The Python engine (astropy, numpy, sympy) executes inside a Web Worker via [Pyodide](https://pyodide.org).

Live at: https://chongchonghe.github.io/astrocalculator/

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  React UI (main thread)                         │
│                                                 │
│  ExpressionEditor ──CustomEvent('evaluate')──▶  │
│  ResultDisplay    ◀── useCalculator hook ──▶    │
│  Sidebar (constants / units / equations / history) │
└──────────────────────┬──────────────────────────┘
                       │ postMessage
┌──────────────────────▼──────────────────────────┐
│  Web Worker (public/pyodide-worker.js)          │
│                                                 │
│  importScripts → Pyodide runtime               │
│  loadPackage([numpy, astropy, sympy])          │
│  fetch + exec calculator.py                    │
│  evaluate(expression) → JSON result            │
└─────────────────────────────────────────────────┘
```

**Why a classic Web Worker?** Pyodide loads via `importScripts`, which only works in classic (non-module) workers. The worker file lives in `public/` so it is served as a static asset, not bundled.

**Why a `CustomEvent`?** The editor and result display are siblings in the tree with no shared parent state. A window-level `evaluate` event decouples them without prop-drilling or a global store.

### Data flow

1. User types an expression and presses **Cmd+Enter** (or Ctrl+Enter).
2. `ExpressionEditor` fires `window.dispatchEvent(new CustomEvent('evaluate', { detail: expression }))`.
3. `ResultDisplay` listens for the event and calls `evaluate(expression)` from `useCalculator`.
4. `useCalculator` posts a message to the Web Worker with a unique `id`.
5. The worker calls `evaluate_wrapper(expr)` in Python, which runs `AstroCalculator.calculate()`.
6. The result JSON is posted back; `useCalculator` resolves the pending promise.
7. `ResultDisplay` renders the SI, CGS, and (optional) converted values.
8. `App` also listens for `evaluate` events to write history to `localStorage`.

### Build-time data generation

| Script | Output | Purpose |
|--------|--------|---------|
| `scripts/dump-constants.py` | `src/data/constants.json` | 36 astropy physical/astronomical constants |
| `scripts/dump-units.py` | `src/data/units.json` | ~60 units grouped by category |
| `vite-plugin-equations.ts` | `src/data/equations.json` | Compiled equation templates from `equations/*.md` |

All three run automatically before every `dev` or `build` via `predev`/`prebuild` npm hooks.

### Source layout

```
web/
├── equations/              # Equation template markdown files (add yours here)
├── scripts/
│   ├── dump-constants.py   # Generates src/data/constants.json
│   └── dump-units.py       # Generates src/data/units.json
├── src/
│   ├── components/
│   │   ├── Header.tsx          # Engine status indicator
│   │   ├── StudioLayout.tsx    # Sidebar + main panel split
│   │   ├── Sidebar.tsx         # Tab bar + tab content router
│   │   ├── SearchBar.tsx       # Search input wired to sidebar tabs
│   │   ├── ConstantsTable.tsx  # Filterable constants list
│   │   ├── UnitsTable.tsx      # Units grouped by category
│   │   ├── EquationTemplates.tsx  # KaTeX-rendered equation cards
│   │   ├── ExpressionEditor.tsx   # Multi-line editor with line numbers
│   │   ├── ResultDisplay.tsx   # SI / CGS / converted result cards
│   │   ├── HistoryPanel.tsx    # localStorage-backed evaluation history
│   │   └── DebugPanel.tsx      # Collapsible Pyodide init log
│   ├── data/               # Generated JSON (do not edit by hand)
│   ├── engine/
│   │   └── calculator.py   # AstroCalculator class (Pyodide-compatible)
│   ├── hooks/
│   │   └── useCalculator.tsx  # PyodideProvider + useCalculator hook
│   └── types/
│       └── index.ts        # Shared TypeScript interfaces
├── public/
│   ├── pyodide-worker.js   # Classic Web Worker — loads Pyodide
│   └── calculator.py       # Copied from src/engine/ at build time
├── vite-plugin-equations.ts  # Vite plugin: equations/*.md → equations.json
└── vite.config.ts
```

---

## Local development

**Prerequisites:** Node 20+, Python 3.10+ with a virtual environment at `../.venv` containing astropy, numpy, and sympy.

```bash
# From the repo root — set up the Python venv once
python3 -m venv .venv
.venv/bin/pip install astropy numpy sympy

# Start the dev server (dumps JSON data, then launches Vite)
cd web
npm install
npm run dev
```

Open http://localhost:5173/astrocalculator/. The page loads immediately; the scientific engine appears in the header as "Loading engine…" and becomes "Ready" after Pyodide and the packages finish loading (~5–15 s depending on your connection and cache).

### Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| **Cmd+Enter** / **Ctrl+Enter** | Evaluate expression |
| **Cmd+K** / **Ctrl+K** | Focus sidebar search |
| **Cmd+J** / **Ctrl+J** | Focus expression editor |

### Expression syntax

The editor accepts multi-line expressions. Lines containing `=` define variables; the last line (or the last `=`-free line) is evaluated.

```
M = 1.4 M_sun
R = 10 km
sqrt(2 G M / R) in km/s
```

- Use `in <unit>` at the end of the final expression to request a unit conversion.
- Separate multiple statements with newlines.
- Constants (`G`, `c`, `h`, `k_B`, `M_sun`, …) and units (`km`, `erg`, `au`, …) are pre-loaded.
- Math functions: `sqrt`, `sin`, `cos`, `exp`, `log`, `log10`, `pi`, `inf`.

### Production build

```bash
cd web
npm run build     # outputs to dist/
npm run preview   # serve dist/ locally
```

---

## Adding equation templates

Create a Markdown file in `web/equations/`. The YAML frontmatter defines the template; the body is optional descriptive text.

```markdown
---
title: Virial Temperature
category: Astrophysics
tags: [temperature, clusters, gas]
params:
  - symbol: M
    default: "1e14 M_sun"
    description: Cluster mass
  - symbol: R
    default: "1 Mpc"
    description: Cluster radius
expressions:
  - name: "Virial temperature"
    expression: "mu m_p G M / (2 k_B R) in keV"
    latex: "T_{\\rm vir} = \\frac{\\mu m_p G M}{2 k_B R}"
    description: "Mean molecular weight μ ≈ 0.6 for fully ionized solar plasma"
---

The virial temperature is the characteristic temperature of gas in hydrostatic
equilibrium within a gravitational potential well.
```

**Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `title` | yes | Display name |
| `category` | yes | Groups the card in search results |
| `tags` | no | Extra search keywords |
| `params` | yes | Variables injected into the editor; `default` must be a valid expression |
| `expressions[].name` | yes | Short label for the expression |
| `expressions[].expression` | yes | The expression pasted into the editor |
| `expressions[].latex` | no | KaTeX source rendered in the card |
| `expressions[].description` | no | One-line note shown under the equation |

The Vite plugin picks up the new file automatically on the next `npm run dev` or `npm run build`.

---

## Deployment to GitHub Pages

The repo ships a GitHub Actions workflow (`.github/workflows/deploy.yml`) that builds and deploys automatically on every push to `main`. You only need to enable GitHub Pages once in your repository settings.

### One-time setup

1. Push the repo to GitHub (e.g. `github.com/chongchonghe/astrocalculator`).
2. Go to **Settings → Pages** in your repository.
3. Under **Source**, select **GitHub Actions**.
4. Save. No branch or folder selection is needed — the workflow handles everything.

That's it. The next push to `main` (or a manual trigger from **Actions → Deploy to GitHub Pages → Run workflow**) will build and publish the site.

### What the workflow does

1. Checks out the repo.
2. Installs Python 3.11 and `pip install astropy numpy sympy`.
3. Installs Node 20 dependencies with `npm ci`.
4. Runs `npm run dump-data` — regenerates `constants.json` and `units.json` from astropy.
5. Copies `src/engine/calculator.py` to `public/` so the Web Worker can fetch it.
6. Runs `npm run build` — TypeScript compilation + Vite bundle + equations plugin.
7. Uploads `web/dist/` as a Pages artifact and deploys it.

The deployed URL follows the pattern `https://<username>.github.io/<repo>/`. The app is pre-configured for this: `vite.config.ts` sets `base: '/astrocalculator/'` and the Web Worker is loaded via `import.meta.env.BASE_URL` so all asset paths resolve correctly.

### Deploying a fork

If you fork the repo under a different username or rename it, update the `base` in `vite.config.ts`:

```ts
export default defineConfig({
  base: '/<your-repo-name>/',
  // ...
});
```

Then enable Pages under **Settings → Pages → Source → GitHub Actions** in your fork.

---

## Contributing

### Adding a constant or unit

Constants come from astropy's `constants` module. To expose a new one, add its name to `con_list` in both `scripts/dump-constants.py` and `src/engine/calculator.py` (`_initialize_constants`). Units follow the same pattern via `scripts/dump-units.py` and `_initialize_units`.

### Modifying the calculator engine

`src/engine/calculator.py` is the single source of truth. It runs in two contexts:

- **Locally** via `.venv/bin/python` (for the dump scripts).
- **In-browser** inside the Pyodide Web Worker.

Avoid any imports that Pyodide does not provide. The packages available to the worker are: `numpy`, `astropy`, `sympy`, and the Python standard library. Do not use `prompt_toolkit`, `rich`, or anything that touches the filesystem or terminal.

After editing `calculator.py`, run:

```bash
cd web && npm run copy-calc   # sync to public/
npm run dev                   # restart dev server to pick up changes
```

### Modifying the Web Worker

`public/pyodide-worker.js` must remain a **classic** (non-module) script — it cannot use ES module syntax or Vite's bundler. Keep it dependency-free; all logic belongs in `calculator.py`.

### Code style

- TypeScript strict mode is enabled; avoid `any`.
- Inline styles are used throughout (no CSS framework dependency); follow the existing CSS variable convention (`--color-*`, `--radius`, etc.) defined in `src/index.css`.
- No test suite currently exists. Manual smoke-testing against the expression examples in this README is the baseline before opening a PR.
