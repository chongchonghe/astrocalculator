# ACAP: an Awesome Calculator for Astronomers and Physicists

## About

ACAP, an Awesome Calculator for Astronomers and Physicists.  
Author: Chong-Chong He (che1234@umd.edu)  
Date: 2020-06-20

This is a calculator designed for astronomers and physicists,
programmed in Python with GUI.

<img src="https://user-images.githubusercontent.com/24463821/87982584-0295ae80-caa5-11ea-9319-2da2b9ef2ea9.gif" width="500">

## How to run?

Simply clone this repository and run the python program with `python
acap`.

Alternatively, to install ACAP as a software, clone this repository, cd
into it, and install it via pip:

```
git clone https://github.com/chongchonghe/acap.git
cd acap
pip install -e .
```

This will create an executable `acap` in your PATH. Anywhere in
your terminal you can do `acap` to start this program.

**The following python modules are required and will be installed
automatically:** tkinter, sympy, and astropy. `tkinter` is available
on most Unix platforms as well as on Windows systems. The other two
packages with be installed via pip.

## Example inputs

| Input              | Output                                                       |
| ------------------ | ------------------------------------------------------------ |
| sin(pi/2)          | 1.0                                                          |
| h                  | 6.62607015e-27 erg s (plus detailed descriptions of plank constant) |
| m_e c^2            | 8.187105776823886e-07 erg (0.5109989499961642 MeV)           |
| sqrt(G M_sun / au) | 2978469.182967693 cm / s (29.78 km/s)                        |
| 1 Mpc * 2 arcsec   | 2.991957413976559e+19 cm rad                                 |


## TODO

- [X] Add setup.py
- [ ] Add latex preview
- [ ] Add logo ([ref1](https://www.c-sharpcorner.com/blogs/create-application-title-and-icon-in-python-gui) and [ref2)](https://stackoverflow.com/questions/22618156/how-to-replace-the-python-logo-in-a-tkinter-based-python-gui-app)

## References

- https://www.lidavidm.me/blog/posts/2013-09-15-implicit-parsing-in-sympy.html
- https://docs.astropy.org/en/stable/units/
- https://docs.astropy.org/en/stable/constants/
- https://stackoverflow.com/questions/62507535/python-suppress-expansion-of-exponential-notation-in-parse-expr-sympy, answer from metatoaster

