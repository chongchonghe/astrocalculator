---
title: Kelvin-Helmholtz Timescale
category: star
tags: [timescale, contraction, pre-main-sequence]
params:
  - symbol: M
    default: "1 M_sun"
    description: Mass of the star
  - symbol: R
    default: "1 R_sun"
    description: Radius of the star
  - symbol: L
    default: "1 L_sun"
    description: Luminosity of the star
expressions:
  - name: "KH timescale"
    expression: "tau = G * M^2 / (R * L); tau in Myr"
    latex: "\\tau_{\\rm KH} \\approx \\frac{GM^2}{RL}"
---

The Kelvin-Helmholtz (thermal) timescale is the time for a star to radiate its gravitational binding energy at its current luminosity. It governs the contraction of protostars and pre-main-sequence stars.
