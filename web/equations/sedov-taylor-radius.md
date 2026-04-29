---
title: Sedov-Taylor Blast Wave
category: star
tags: [supernova, blast wave, SN remnant]
params:
  - symbol: E
    default: "1e51 erg"
    description: Explosion energy
  - symbol: n
    default: "1 cm^-3"
    description: Ambient hydrogen number density
  - symbol: t
    default: "1000 yr"
    description: Time since explosion
  - symbol: mu
    default: "1.4"
    description: Mean molecular weight
expressions:
  - name: "Shock radius"
    expression: "r_sh = (E * t^2 / (mu * m_p * n))^(1/5); r_sh in pc"
    latex: "r_{\\rm sh}(t) = \\xi_0 \\left(\\frac{Et^2}{\\rho_1}\\right)^{1/5}"
  - name: "Shock velocity"
    expression: "U_sh = (2/5) * (E / (mu * m_p * n))^(1/5) * t^(-3/5); U_sh in km/s"
    latex: "U_{\\rm sh} = \\frac{2}{5} \\left(\\frac{E}{\\rho_1}\\right)^{1/5} t^{-3/5}"
---

The Sedov-Taylor phase describes the adiabatic expansion of a strong blast wave, such as a supernova remnant, before radiative losses become significant. The shock conserves energy during this self-similar phase.
