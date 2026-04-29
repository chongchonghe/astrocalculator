---
title: Eddington Luminosity
category: Astrophysics
tags: [accretion, luminosity, limit]
params:
  - symbol: M
    default: "1e6 M_sun"
    description: Mass of the accreting object
expressions:
  - name: "Eddington luminosity"
    expression: "Ledd = 4 pi G M c m_p / sigma_T, \n Ledd in erg/s"
    latex: "L_{\\rm Edd} = \\frac{4\\pi G M c m_p}{\\sigma_T}"
  - name: "Eddington accretion rate"
    expression: "Aedd = 4 pi G M m_p / (0.1 sigma_T c)"
    latex: "\\dot{M}_{\\rm Edd} = \\frac{4\\pi G M m_p}{0.1\\sigma_T c}"
    description: "Assuming 10% radiative efficiency"
---

The Eddington luminosity is the maximum luminosity a star can have
while maintaining hydrostatic equilibrium.
