---
title: Bondi Accretion
category: star
tags: [accretion, black hole, Bondi]
params:
  - symbol: M
    default: "1 M_sun"
    description: Mass of the accretor
  - symbol: rho_inf
    default: "1e-24 g/cm^3"
    description: Ambient gas density
  - symbol: c_s
    default: "10 km/s"
    description: Sound speed of ambient gas
  - symbol: v_inf
    default: "0 km/s"
    description: Relative velocity (0 for pure Bondi)
expressions:
  - name: "Bondi radius"
    expression: "r_B = G * M / c_s^2; r_B in cm"
    latex: "r_{\\rm B} = \\frac{GM}{c_s^2}"
  - name: "Bondi accretion rate"
    expression: "Mdot = 4 * pi * G^2 * M^2 * rho_inf / c_s^3; Mdot in M_sun/yr"
    latex: "\\dot{M}_{\\rm B} = \\frac{4\\pi G^2 M^2 \\rho_{\\infty}}{c_s^3}"
  - name: "Bondi-Hoyle accretion rate"
    expression: "Mdot = 4 * pi * G^2 * M^2 * rho_inf / (c_s^2 + v_inf^2)^(3/2); Mdot in M_sun/yr"
    latex: "\\dot{M}_{\\rm BH} = \\frac{4\\pi G^2 M^2 \\rho_{\\infty}}{(c_\\infty^2 + v_\\infty^2)^{3/2}}"
    description: "Interpolation formula including relative motion"
---

Bondi accretion describes the spherical accretion of gas onto a compact object. The Bondi-Hoyle interpolation extends this to account for the relative motion between the object and the gas.
