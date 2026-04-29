---
title: Alfvén Velocity
category: mhd
tags: [magnetic field, Alfven wave, MHD]
params:
  - symbol: B
    default: "1e-5 Gauss"
    description: Magnetic field strength
  - symbol: n
    default: "100 cm^-3"
    description: Hydrogen number density
  - symbol: mu
    default: "1.4"
    description: Mean molecular weight
  - symbol: L
    default: "1 pc"
    description: Length scale (for crossing time)
expressions:
  - name: "Alfvén velocity"
    expression: "v_A = B / sqrt(4 * pi * mu * m_p * n); v_A in km/s"
    latex: "v_{\\rm A} = \\frac{B_0}{\\sqrt{4\\pi\\rho_0}}"
---

The Alfvén velocity is the characteristic speed of magnetohydrodynamic waves propagating along magnetic field lines. The Alfvén crossing time gives the timescale for magnetic communication across a region of size L.
