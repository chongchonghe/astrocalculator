# ACAP: an Awesome Calculator for Astronomers and Physicists

## About

ACAP, an Awesome Calculator for Astronomers and Physicists.  
Author: Chong-Chong He (che1234@umd.edu)  
Date: 2020-06-20

This is a calculator designed for astronomers and physicists,
programmed in Python with GUI.

<img src="./demo-fast.gif" width="500">

## How to run?

No installation required. Simply download and run the python script `acap.py`. 
Or, make it as an executable and move it to your PATH so that
you can start this program in your terminal with `acap`. e.g.,

```
mv acap.py ~/local/bin/acap
chmod +x ~/local/bin/acap
```

Or, better clone this repo and make a symbolic link of acap.py to your `local/bin` so that you can get the most update-to-date version 
```
chmod +x acap.py
cd /usr/local/bin
ln -s /path/to/acap.py acap
```

The following python modules are required: tkinter, sympy, and
astropy. `tkinter` is available on most Unix platforms as well as on
Windows systems. You can install the other two modules via `pip
install sympy astropy`.

## Example inputs

- sin(2.3) * 5!
- h
- m_e c^2  (then input MeV as user-defined unit)
- m_e c^2 / h  
- (G M_sun / au)^.5 (define output units as km/s)
- e.esu^2 / (0.1 nm)^2

## TODO

- Add latex preview
- Add logo ([[https://www.c-sharpcorner.com/blogs/create-application-title-and-icon-in-python-gui][ref1]] and [[https://stackoverflow.com/questions/22618156/how-to-replace-the-python-logo-in-a-tkinter-based-python-gui-app][ref2]])

## References

- https://www.lidavidm.me/blog/posts/2013-09-15-implicit-parsing-in-sympy.html
- https://docs.astropy.org/en/stable/units/
- https://docs.astropy.org/en/stable/constants/
- https://stackoverflow.com/questions/62507535/python-suppress-expansion-of-exponential-notation-in-parse-expr-sympy, answer from metatoaster

