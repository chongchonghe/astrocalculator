---
title: Jeans Mass and Jeans Length
category: star
tags: [instability, collapse, star formation]
params:
  - symbol: T
    default: "10 K"
    description: Gas temperature
  - symbol: n
    default: "1000 cm^-3"
    description: Hydrogen number density
  - symbol: mu
    default: "1.4"
    description: Mean molecular weight
expressions:
  - name: "Jeans length"
    expression: "c_s = sqrt(k_B * T / (mu * m_p))\n lambda_J = c_s * sqrt(pi / (G * mu * m_p * n)); lambda_J in pc"
    latex: "\\lambda_{\\rm J} = c_{\\rm s} \\sqrt{\\frac{\\pi}{G\\bar\\rho}}"
  - name: "Jeans mass"
    expression: "c_s = sqrt(k_B * T / (mu * m_p))\n lambda_J = c_s * sqrt(pi / (G * mu * m_p * n))\n M_J = (4/3) * pi * (lambda_J / 2)^3 * mu * m_p * n; M_J in M_sun"
    latex: "M_{\\rm J} = \\frac{4\\pi}{3} \\left(\\frac{\\lambda_{\\rm J}}{2}\\right)^3 \\bar\\rho"
  - name: "Bonnor-Ebert mass"
    expression: "M_BE = 1.182 * sqrt(k_B * T / (mu * m_p))^3 / (G^3 * mu * m_p * n)^(1/2); M_BE in M_sun"
    latex: "M_{\\rm BE} = 1.182 \\frac{c_s^3}{(G^3 \\rho)^{1/2}} = 0.41 M_{\\rm J}"
    description: "Maximum stable mass for a pressure-confined isothermal sphere"
---

The Jeans length and Jeans mass define the scale above which a self-gravitating gas cloud becomes unstable to gravitational collapse. The Bonnor-Ebert mass is the equivalent for a pressure-confined isothermal sphere.
