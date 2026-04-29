---
title: Free-Fall Time
category: star
tags: [timescale, collapse, star formation]
params:
  - symbol: n
    default: "1000 cm^-3"
    description: Hydrogen number density
  - symbol: mu
    default: "1.4"
    description: Mean molecular weight
expressions:
  - name: "Free-fall time"
    expression: "t_ff = sqrt(3 * pi / (32 * G * mu * m_p * n)); t_ff in Myr"
    latex: "t_{\\rm ff} = \\sqrt{\\frac{3\\pi}{32G\\rho}}"
---

The free-fall time is the characteristic timescale for a pressureless, self-gravitating cloud to collapse under its own gravity. It sets the fundamental timescale for star formation.
