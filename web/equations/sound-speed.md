---
title: Sound Speed
category: gas dynamics
tags: [sound speed, temperature, gas]
params:
  - symbol: T
    default: "10 K"
    description: Gas temperature
  - symbol: mu
    default: "1.4"
    description: Mean particle weight (mu = 0.5 for ionized gas)
  - symbol: gamma_ad
    default: "1"
    description: Adiabatic index (1 for isothermal, 5/3 for adiabatic)
expressions:
  - name: "Sound speed"
    expression: "c_s = sqrt(gamma_ad * k_B * T / (mu * m_p)); c_s in km/s"
    latex: "c_s = \\sqrt{\\frac{\\gamma kT}{\\mu m_{\\rm H}}}"
  - name: "Isothermal sound speed (gamma=1)"
    expression: "c_s = 0.29 * sqrt(T / 10 / mu); c_s in km/s"
    latex: "c_s \\approx 0.29 \\, \\left(\\frac{T/10\\,{\\rm K}}{\\mu}\\right)^{1/2} \\, {\\rm km/s}"
---

The sound speed sets the characteristic velocity of pressure waves in a gas. In astrophysics, the isothermal sound speed is most commonly used for cold molecular gas.
