---
title: Dynamical Friction
category: dynamics
tags: [dynamical friction, black hole, orbit decay]
params:
  - symbol: M
    default: "1e8 M_sun"
    description: Mass of the orbiting object
  - symbol: n
    default: "1 cm^-3"
    description: Ambient number density
  - symbol: sigma
    default: "200 km/s"
    description: Velocity dispersion of background stars
  - symbol: r_i
    default: "5 kpc"
    description: Initial orbital radius
  - symbol: Coulomb_log
    default: "6"
    description: Coulomb logarithm (typically 3-20)
expressions:
  - name: "Deceleration (subsonic, v_M << sigma)"
    expression: "dv = 4 * sqrt(2*pi) / 3 * G^2 * M * m_p * n * sigma / sigma^3 * log(Coulomb_log); dv in cm/s^2"
    latex: "\\frac{dv_M}{dt} \\approx \\frac{4\\sqrt{2\\pi}}{3} \\frac{G^2 M \\rho}{\\sigma^2} \\ln \\Lambda"
    description: "Assuming the object moves at velocity sigma through the background"
  - name: "Deceleration (supersonic, v_M >> sigma)"
    expression: "dv = 4 * pi * G^2 * M * m_p * n / sigma^2 * log(Coulomb_log); dv in cm/s^2"
    latex: "\\frac{dv_M}{dt} \\approx \\frac{4\\pi G^2 M \\rho}{v_M^2} \\ln \\Lambda"
    description: "Assuming the object moves at velocity sigma >> velocity dispersion"
  - name: "Decay timescale (BH in galaxy core)"
    expression: "t_fric = 19 / Coulomb_log * (r_i / 5)^2 * sigma / 200 * (1e8 / M); t_fric in Gyr"
    latex: "t_{\\rm fric} \\approx \\frac{19 \\, {\\rm Gyr}}{\\ln \\Lambda} \\left(\\frac{r_i}{5\\,{\\rm kpc}}\\right)^2 \\frac{\\sigma}{200\\,{\\rm km/s}} \\left(\\frac{10^8 M_\\odot}{M}\\right)"
    description: "Timescale for a BH to decay to galaxy center in an isothermal sphere"
---

Dynamical friction is the drag force experienced by a massive object moving through a background of lighter particles. It governs the orbital decay of supermassive black holes and massive star clusters in galaxies.
