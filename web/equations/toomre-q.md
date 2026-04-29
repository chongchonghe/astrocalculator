---
title: Toomre Q Parameter
category: galaxy
tags: [stability, disk, Toomre]
params:
  - symbol: Omega
    default: "30 km/s/kpc"
    description: Angular frequency
  - symbol: c_s
    default: "10 km/s"
    description: Velocity dispersion (sound speed)
  - symbol: Sigma
    default: "100 M_sun/pc^2"
    description: Surface density
expressions:
  - name: "Toomre Q (Keplerian)"
    expression: "Q = Omega * c_s / (pi * G * Sigma)"
    latex: "Q = \\frac{\\Omega c_s}{\\pi G \\Sigma}"
  - name: "Toomre Q (flat rotation)"
    expression: "Q = sqrt(2) * Omega * c_s / (pi * G * Sigma)"
    latex: "Q = \\frac{\\sqrt{2} \\Omega c_s}{\\pi G \\Sigma}"
  - name: "Toomre Q (rigid rotation)"
    expression: "Q = 2 * Omega * c_s / (pi * G * Sigma)"
    latex: "Q = \\frac{2 \\Omega c_s}{\\pi G \\Sigma}"
---

The Toomre Q parameter measures the stability of a rotating disk against gravitational collapse. The disk is unstable when Q < 1. The expression depends on the rotation curve: Keplerian, flat, or rigid.
