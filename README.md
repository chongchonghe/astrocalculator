# ACAP: an Awesome Calculator for Astronomers and Physicists

## About

ACAP, an Awesome Calculator for Astronomers and Physicists.  
Author: Chong-Chong He (che1234@umd.edu)

This is a calculator designed for astronomers and physicists,
programmed in Python with GUI.

<img src="https://user-images.githubusercontent.com/24463821/87982584-0295ae80-caa5-11ea-9319-2da2b9ef2ea9.gif" width="500">

## How to install and upgrade?

To try it out, simply download this repository and run the python script with `python acap`.

Alternatively, to **install ACAP** as a software, clone this repository, cd into it, and install it via pip:

```
# clone acap
git clone https://github.com/chongchonghe/acap.git

# cd into it
cd acap

# install (alternatively, run 'make')
pip install -e .
```

This will create an executable `acap` in your PATH, which is linked to the git repository. Now type `acap` in your terminal to start this program. `acap` also works as a Python package. You can do `from acap import *` and all physical constants like `M_sun` and `k_B` are available. 

**To upgrade** to the latest version, `git pull` in the code directory to pull
the latest version and your ACAP is automatically upgraded.

The following python modules are required and will be installed
automatically: tkinter, sympy, and astropy. `tkinter` is available
on most Unix platforms as well as on Windows systems. The other two
packages with be installed via pip.

## New features

- Enabled multi-line input. Check the last example in the "Example inputs and outputs" section.

## Example inputs and outputs

- `h`

  CGS: `6.62607e-27 erg s`  
  SI:
  ```
    Name   = Planck constant
    Value  = 6.62607015e-34
    Uncertainty  = 0.0
    Unit  = J s
    Reference = CODATA 2018
  ```

- `m_e c^2`

  CGS: `8.18711e-07 erg`  
  SI: `8.18711e-14 s W`  
  MeV: `0.5109989 MeV`

- `1 Mpc * 2 arcsec/radian`

  CGS: `2.99196e+19 cm`  
  SI: `2.99196e+17 m`  
  pc: `9.696274 pc`

- `sqrt(G M_sun / au)`

  CGS: `2.97847e+06 cm / s`  
  SI: `29784.7 m / s`  
  km/s: `29.78469 km / s`

- 
```python
rho = 100 mpcc
tff = sqrt(1 / (G rho))
cs = 10 km/s
tff * cs
```

  CGS: `2.99294e+20 cm`  
  SI: `2.99294e+18 m`  
  pc: `96.99463 pc`

## Configurations

Configuration is possible via changing variables at the beginning of the Python
script. Currently the configurable parameters are:

| Parameter | Default | Description                                                                                |
| --------- | ------- | ------------------------------------------------------------                               |
| SCALE     | 1.1     | Scaling of the window size. Recommended: >=1.2 on a 1080p screen, 1.0 on a retina display. |
| PRINT_LOG | True    | Toggle printing inputs and outputs to `~/.acap_history`. Will always print on terminal.    |
| DIGITS    | 4       | Number of significant digits in the scientific notation.                                   |
| HEIGHT    | 520     | Height of the window (in pixels)                                                                                        |

## TODO

- [X] Enable si mode: display SI and USER_UNIT. 
- [ ] parse keyword 'in' at the last line and automatically change User Unit.
- [ ] Add more units: N (Newton), 
- [X] Enable variable assignment
- [X] Add setup.py
- [X] Make the outputs copyable
- [ ] Add latex preview
- [ ] Add logo ([ref1](https://www.c-sharpcorner.com/blogs/create-application-title-and-icon-in-python-gui) and [ref2)](https://stackoverflow.com/questions/22618156/how-to-replace-the-python-logo-in-a-tkinter-based-python-gui-app)

## References

- https://www.lidavidm.me/blog/posts/2013-09-15-implicit-parsing-in-sympy.html
- https://docs.astropy.org/en/stable/units/
- https://docs.astropy.org/en/stable/constants/
- https://stackoverflow.com/questions/62507535/python-suppress-expansion-of-exponential-notation-in-parse-expr-sympy, answer from metatoaster

