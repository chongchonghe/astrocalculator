# Writing an equation file

Each equation lives in its own `.md` file under `web/equations/`. The file has YAML frontmatter and a short markdown body.

## Frontmatter

| Field | Required | Description |
|---|---|---|
| `title` | yes | Display name of the equation |
| `category` | yes | Lowercase, from `categories.txt` |
| `tags` | yes | YAML list of search keywords |
| `params` | yes | Input variables (see below) |
| `expressions` | yes | Computable forms (see below) |

The file ends with a 1–2 sentence description after the closing `---`.

## Params

Each param has three fields:

```yaml
- symbol: n
  default: "1000 cm^-3"
  description: Hydrogen number density
```

- **symbol** — the variable name used in expressions. Single-word, no spaces.
- **default** — a sensible default value with its unit (e.g. `"10 K"`, `"1 M_sun"`, `"1 au"`).
- **description** — short human-readable explanation.

Use only symbols defined in the `params` list within expressions. The calculator provides known constants (`G`, `c`, `m_p`, `k_B`, `pi`, `sigma_T`, etc.) and unit suffixes (`M_sun`, `R_sun`, `L_sun`, `au`, `pc`, `kpc`, `Myr`, `Gyr`, etc.).

## Expressions

Each entry in `expressions` has these fields:

```yaml
- name: "Jeans length"
  expression: "c_s = sqrt(k_B * T / (mu * m_p))\n lambda_J = c_s * sqrt(pi / (G * mu * m_p * n))\n lambda_J in pc"
  latex: "\\lambda_{\\rm J} = c_{\\rm s} \\sqrt{\\frac{\\pi}{G\\bar\\rho}}"
```

- **name** — short label shown in the UI.
- **expression** — the computable form. Rules below.
- **latex** — LaTeX for display (use `\\` for backslashes in YAML).
- **description** (optional) — extra context shown under the expression.

### Expression syntax

1. **Use only defined symbols** — every variable must appear in `params`, plus the built-in constants (`G`, `c`, `m_p`, `k_B`, `pi`, `sigma_T`, etc.).

2. **Always write the fundamental form** — do not bake in numerical constants. The calculator has all physical constants and unit conversion built in, so write `G * M / c_s^2` not `1.3e15 * M / c_s^2`.

3. **Assign the result to a variable** — always on the final line:
   ```
   var = expression
   var in unit
   ```

4. **Unit conversion on the final line** — append `\n var in unit`:
   ```
   v_esc = sqrt(2 * G * M / R)\n v_esc in km/s
   ```

5. **Intermediate computations** — use `\n` to separate steps. Intermediate assignments don't need `in unit`:
   ```
   c_s = sqrt(k_B * T / (mu * m_p))\n lambda_J = c_s * sqrt(pi / (G * mu * m_p * n))\n lambda_J in pc
   ```

6. **No `;` separators** — the engine processes the `in unit` clause on the last line only. Separate statements with `\n`.

7. **Dimensionless results** — if the result has no units (e.g. Toomre Q), no `in unit` line is needed:
   ```
   Qtoomre = Omega * c_s / (pi * G * Sigma)
   ```

## Example

See `jeans-mass.md` for a complete example with multi-line intermediate computations and multiple related expressions.
