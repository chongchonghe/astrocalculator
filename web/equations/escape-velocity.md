---
title: Escape Velocity
category: Mechanics
tags: [velocity, gravity, compact objects]
params:
  - symbol: M
    default: "1.4 M_sun"
    description: Mass of the object
  - symbol: R
    default: "10 km"
    description: Radius
expressions:
  - name: "Escape velocity"
    expression: "v = sqrt(2 G M / R)\n v in km/s"
    latex: "v_{\\rm esc} = \\sqrt{\\frac{2GM}{R}}"
  - name: "Circular velocity"
    expression: "sqrt(G M / R) in km/s"
    latex: "v_{\\rm circ} = \\sqrt{\\frac{GM}{R}}"
    description: "Circular orbital velocity, 1/√2 times escape velocity"
---

The escape velocity is the minimum speed needed for an object to escape
the gravitational influence of a massive body.
