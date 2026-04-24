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
    expression: "P = sqrt(4 pi^2 a^3 / (G M)), P in yr"
    latex: "P = \\sqrt{\\frac{4\\pi^2 a^3}{GM}}"
  - name: "Orbital separation from period"
    expression: "P = sqrt(4 pi^2 a^3 / (G M)),\n d = (G M P^2 / (4 pi^2))^(1/3), d in au"
    latex: "a = \\left(\\frac{GMP^2}{4\\pi^2}\\right)^{1/3}"
    description: "Given period P, compute semi-major axis"
---

Kepler's Third Law relates orbital period to semi-major axis for two-body systems.
