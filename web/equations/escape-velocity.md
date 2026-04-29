---
title: Escape Velocity
category: mechanics
tags: [velocity]
params:
  - symbol: M
    default: "1 M_sun"
    description: Mass of the object
  - symbol: R
    default: "1 R_sun"
    description: Radius
expressions:
  - name: "Escape velocity"
    expression: "v_esc = sqrt(2 * G * M / R); v_esc in km/s"
    latex: "v_{\\rm esc} = \\sqrt{\\frac{2GM}{R}}"
  - name: "Circular velocity"
    expression: "v_circ = sqrt(G * M / R); v_circ in km/s"
    latex: "v_{\\rm circ} = \\sqrt{\\frac{GM}{R}}"
    description: "Circular orbital velocity, 1/√2 times escape velocity"
---

The escape velocity is the minimum speed needed for an object to escape
the gravitational influence of a massive body.
