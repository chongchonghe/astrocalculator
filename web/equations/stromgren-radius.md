---
title: Strömgren Radius
category: star
tags: [HII region, ionization, recombination]
params:
  - symbol: Q0
    default: "1e49 s^-1"
    description: Ionizing photon emission rate
  - symbol: n
    default: "100 cm^-3"
    description: Hydrogen number density
  - symbol: T
    default: "10000 K"
    description: Electron temperature
  - symbol: alpha_B
    default: "2.6e-13 cm^3/s"
    description: Case B recombination coefficient (~2.6e-13 at 10^4 K)
expressions:
  - name: "Strömgren radius"
    expression: "R_S = (3 * Q0 / (4 * pi * n^2 * alpha_B))^(1/3); R_S in pc"
    latex: "R_{\\rm S} = \\left(\\frac{3Q_0}{4\\pi n_0^2 \\alpha_B}\\right)^{1/3}"
---

The Strömgren radius is the size of the ionized region (H II region) around a young, massive star, set by the balance between photoionization and radiative recombination. alpha_B(T) is the Case B recombination coefficient.
