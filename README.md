# AstroCalculator, a Calculator for Astronomers and Physicists

## About

AstroCalculator is a calculator for astronomers and physicists written in Python.  
Author: ChongChong He (chongchong.he@anu.edu.au)

## Installation

You can install astrocalculator from [PyPI](https://pypi.org/project/realpython-reader/):

```sh
pip install astrocalculator
```

`astrocalculator` is supported on Python 3.6 and above.

## How to use

Start the program with `calc`. This will start a web server and open a browser window where you can type in your inputs. A input can be one of the following: 1) a single variable or constant like `k_B`, 2) an expression like `m_e c^2`, or 3) a list of variable assignments followed by a final expression to evaluate, e.g. `M = 1.4 M_sun, R = 10 km, sqrt(2 G M / R)`. 

Another way is to use it as a Python module in your script or interactively in iPython. Put the following in your code:

```python
from calc import *
```

Now you can use all the physical constants defined in `astrocalculator` as listed in [here](https://github.com/chongchonghe/acap/docs/constants.md). 

### Example inputs and outputs

```
Input[1]: m_p

Parsed input = m_p
Result (SI)  = 
  Name   = Proton mass
  Value  = 1.67262192369e-27
  Uncertainty  = 5.1e-37
  Unit  = kg
  Reference = CODATA 2018
Result (cgs) = 1.6726e-24 g

Input[2]: m_e c^2

Parsed input = c**2*m_e
Result (SI)  = 8.1871e-14 m N
Result (cgs) = 8.1871e-07 erg

User units: MeV

0.51100 MeV

Input[4]: M = 1.4 M_sun, R = 10 km, sqrt(2 G M / R)

Parsed input = sqrt(2*G*M*1/R)
Result (SI)  = 1.9277e+08 m / s
Result (cgs) = 1.9277e+10 cm / s

User units: km/s

1.9277e+05 km / s
```

## Todos

- [ ] Add latex preview

## References

- https://docs.astropy.org/en/stable/units/
- https://docs.astropy.org/en/stable/constants/
- https://www.lidavidm.me/blog/posts/2013-09-15-implicit-parsing-in-sympy.html
- https://stackoverflow.com/questions/62507535/python-suppress-expansion-of-exponential-notation-in-parse-expr-sympy
