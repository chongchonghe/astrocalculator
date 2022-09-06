#!/usr/bin/env python
""" calculator.py
A Calculator for Astronomers and Physicists.
Author: Chong-Chong He (che1234@umd.edu)
Date: 2020-06-20
"""

import sys
from math import pi, inf, log, log10, log2
# from math import pi, inf, log
import numpy as np
from numpy import sin, arcsin, cos, arccos, tan, arctan, sinh, arctanh, \
        cosh, arccosh, arcsinh, cosh, arccosh, tanh, arctanh, sqrt, exp, \
        float64
import readline
try:
    from sympy import evaluate
except ImportError:
    raise SystemExit("Please install sympy by running:\n"
                     "python -m pip install sympy==1.6.1")
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, \
        implicit_multiplication, convert_xor
try:
    from astropy import units as U
except ImportError:
    raise SystemExit("Please install astropy by running:\n"
                     "python -m pip install astropy")
# from astropy.constants import *
from astropy import constants
from astropy.units.core import UnitConversionError, CompositeUnit
from astropy.units.quantity import Quantity
from datetime import datetime
# from astropy.cosmology import WMAP9
import logging
import textwrap

# print('test')

# logging.basicConfig(level=logging.DEBUG)

DIGITS = 10          # number of significant digits in the scientific notation
REQUIRE_UNDERSCORE = False

# Define constants that are avialable in astropy.units
conList = ['G', 'N_A', 'R', 'Ryd', 'a0', 'alpha', 'atm', 'b_wien', 'c', 'g0',
           'h', 'hbar', 'k_B', 'm_e', 'm_n', 'm_p', 'e', 'eps0', 'mu0', 'muB',
           'sigma_T', 'sigma_sb', 'u', 'GM_earth', 'GM_jup', 'GM_sun',
           'L_bol0', 'L_sun', 'M_earth', 'M_jup', 'M_sun', 'R_earth', 'R_jup',
           'R_sun', 'au', 'kpc', 'pc']
conList.sort(key=lambda y: y.lower())

# Some EM constants is unable to load because different cgs system
# has different values. They are included in failList.
failList = []
for con in conList:
    try:
        locals()[con] = getattr(constants, con)
    except:
        failList.append(con)

# Define more units/derived constants
all_units = {
    'Length': ['m', 'cm', 'mm', 'um', 'nm', 'Angstrom', 'km', 'au', 'AU',
               'pc', 'kpc', 'Mpc', 'lyr',],
    'Mass': ['kg', 'g', 'M_sun', 'Msun'],
    'Density': ['mpcc'],
    'Time': ['s', 'yr', 'Myr', 'Gyr',],
    'Energy': ['J', 'erg', 'eV', 'keV', 'MeV', 'GeV'],
    'Power': ['W'],
    'Pressure': ['Pa', 'bar', 'mbar'],
    'Frequency': ['Hz', 'kHz', 'MHz', 'GHz',],
    'Temperature': ['K',],
    'Angular size': ['deg', 'radian', 'arcmin', 'arcsec', 'arcsec2'],
    'Astronomy': ['Lsun', 'Jy', 'mJy', 'MJy'],
    'Composite': ['m2', 'm3', 'cm2', 'cm3', 's2', 'pc2', 'pc3']
    }
# The following units are not avaiable in astropy.units and I will define
# them by hand
user_units = ['deg', 'Ang', 'mpcc', 'm2', 'm3', 'cm2', 'cm3', 's2', 'pc2',
              'pc3', 'arcsec2', 'Msun']
# The following units are already defined as physical constants
_unit_skip = ['au', 'pc', 'M_sun']
for _key in all_units.keys():
    for _unit in all_units[_key]:
        if _unit not in _unit_skip + user_units:
            locals()[_unit] = eval("U.{}".format(_unit))
# define some derived units by hand
esu = e.esu
Ang = U.def_unit('Ang', 0.1 * nm)
mpcc = U.def_unit('mpcc', m_p / cm**3)
Msun = M_sun
m2 = m**2
m3 = m**3
cm2 = cm**2
cm3 = cm**3
s2 = s**2
pc2 = pc**2
pc3 = pc**3
# degree = pi / 180. * radian
degrees = pi / 180
# deg = degrees    # Error: SympifyError: <function deg at 0x7fe6d9403af0>
arcsec2 = arcsec**2
Gauss = g**(1/2) * cm**(-1/2) * s**(-1)

# TRANSFORMATIONS = standard_transformations +\
#     (implicit_multiplication,) +\
#     (convert_xor,)
TRANSFORMATIONS = (convert_xor,) + standard_transformations +\
    (implicit_multiplication,)

IS_SCI = 0
F_FMT = '{{:.{}e}}'.format(DIGITS-1) if IS_SCI else "{{:#.{}g}}".format(DIGITS)

class EvalError(Exception):
    """Error in variable assignment"""
    pass

class UnitConversionError(Exception):
    """Error in variable assignment"""
    pass

# user-defined functions
def logten(x):
    return np.log10(x)

def parse_and_eval(expr, local_vars_={}):
    """
    Return:
        parsed_input, output

    Raise:
        EvalError
    """

    logging.debug("here #800")
    for item in local_vars_:
        locals()[item] = local_vars_[item]
    try:
        # with evaluate(False):     # TODO: confirm this is okay. I remove this
        # line in order to fix an error: ValueError: Abs(22*1) is not an integer
        logging.debug("expr = {}".format(expr))
        inp_expr = parse_expr(expr, transformations=TRANSFORMATIONS,
                              evaluate=False)
        logging.debug("inp_expr = {}".format(inp_expr))
        inp_expr = str(inp_expr)
        # logging.info(repr("Parsed inp = {}".format(inp_expr)))
    except Exception as error_msg:
        logging.debug("here #801")
        raise EvalError(error_msg)

    logging.debug("here #810")
    # get the results
    try:
        ret = eval(inp_expr)
    except Exception as _e:
        raise EvalError(_e)

    return inp_expr, ret

def calculate(inp, delimiter='\n'):

    if inp == "":
        return None, None

    # removing tracing '\n'
    inp = inp.strip()

    # eval all but the last line
    local_vars = {}
    logging.debug("here #200")
    if delimiter in inp:
        lines = inp.split(delimiter)  # this ensures a list
        n_line = len(lines)
        logging.info('Lines:')
        logging.debug("here #201")
        for count, line in enumerate(lines):
            logging.info(repr(line))
            if count >= n_line - 1:  # last line
                inp = line
                break
            # remove spaces
            logging.debug("here #202")
            line = line.strip()
            items = line.split('=')
            if len(items) > 2:
                raise EvalError('Multiple equal signs found in variable assignment')
            if len(items) == 1:
                continue
            var, value = items
            var = var.strip()
            logging.debug("here #203")
            if REQUIRE_UNDERSCORE and var[0] != '_':
                raise EvalError("Assigned variable must begin with _ (underscore")
            if ' ' in var:
                raise EvalError('Variable should not have space in it')
            parsed_expr, ret = parse_and_eval(value, local_vars)
            local_vars[var] = ret

    # eval the last line
    logging.debug("here #250")
    parsed_expr, Ret = parse_and_eval(inp, local_vars)
    ret = None                  # in SI unit
    ret2 = None                 # in cgs unit

    # Display results
    # F_FMT = '{{:.{}e}}'.format(DIGITS-1) if IS_SCI else '{}'
    logging.debug("here #300")
    # F_FMT = '{{:.{}e}}'.format(DIGITS-1) if IS_SCI else "{{:.{}g}}".format(DIGITS)
    if type(Ret) in [int, float, float64]: # has no units
        logging.debug("here #400")
        if type(Ret) is not int:
            ret = F_FMT.format(Ret)
        else:
            ret = Ret
        ret2 = ret
    else: # has units
        # SI units
        if type(Ret.si) is Quantity:
            ret = F_FMT.format(Ret.si)
        else:
            # Physical constants. Display full description.
            ret = '\n' + str(Ret.si)
        # CGS units
        try:
            if type(Ret.cgs) is CompositeUnit:
                logging.debug("here #410")
                ret2 = Ret.cgs
            else:
                logging.debug("here #415")
                ret2 = F_FMT.format(Ret.cgs)
        except Exception as _e:
            ret2 = textwrap.fill(str(_e), 80)
        # user units
        # if userunit != "":
        #     if unit in user_units:
        #         ret_loc = ret.to(eval(userunit))
        #     else:
        #         ret_loc = ret.to(userunit)
    return parsed_expr, Ret, ret, ret2

def convert(quant, userunit):
    """ Convert quant to specified unit """

    if userunit == '':
        return
    # F_FMT = '{{:.{}e}}'.format(DIGITS-1) if IS_SCI else "{{:.{}g}}".format(DIGITS+1)
    if type(quant) is int:
        return quant
    elif type(quant) in [float, float64]:
        return F_FMT.format(quant)
    else:
        if userunit in user_units:
            ret_loc = quant.to(eval(userunit))
        else:
            ret_loc = quant.to(userunit)
        if type(ret_loc) is int:
            return ret_loc.format(quant)
        elif type(ret_loc) is float:
            return F_FMT.format(ret_loc)
        else:
            return F_FMT.format(ret_loc.value) + " " + str(ret_loc._unit)
        # except UnitConversionError as _e:
        #     UnitConversionError(_e)
        # except ValueError as _e:
        #     UnitConversionError(_e)

def readline_input(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)
   finally:
      readline.set_startup_hook()

def main(withcolor=True):
    print("""===============================================
A Calculator for Astrophysicists and Physicists
Author: Chong-Chong He (che1234@umd.edu)

Examples:
>>> m_p

>>> m_e c^2
>>>
>>> in eV

>>> M = 1.4 M_sun, R = 10 km, sqrt(2 G M / R)
>>>
>>> in km/s

For avaiable constants and units, check
https://github.com/chongchonghe/acap/blob/master/docs/constants.md
===============================================""")
    print()
    if withcolor:
        c_diag = '\33[92m'
        c_error = '\033[91m'
        c_end = '\033[m'
    else:
        c_diag = ''
        c_error = ''
        c_end = ''
    count = 0
    default = ''
    history = []
    ret_raw = None
    while True:
        count += 1
        # inp = input("Input: ")
        # print(c_diag + "=============================================")
        # print(c_diag + f"Input[{count}]:" + c_end, end=' ')
        # # multiple line
        # sentinel = ''
        # inp = '\n'.join(iter(input, sentinel))
        # inp = inp.replace(';', '\n')
        # single line
        pre = c_diag + f"Input[{count}]: " + c_end + "\n"
        if default == '':
            inp = input(pre)
        else:
            inp = readline_input(pre, default).strip()
        default = ''
        history.append(inp)
        print()
        if inp == "":
            continue
        if inp == 'q':
            return
        if inp[0] == '!':
            if len(inp) == 1:
                idx = count - 1
            else:
                try:
                    idx = int(inp.split('!')[1])
                except ValueError:
                    print()
                    continue
            default = history[idx - 1]
            print()
            continue
        if len(inp) > 3:
            if inp[:3] == 'in ':  # do unit conversion of previous result
                if ret_raw is None:
                    # previous return is None, skip
                    continue
                userunit = inp[3:].strip()
                try:
                    tmp = convert(ret_raw, userunit)
                    if tmp is not None:
                        print(tmp)
                except UnitConversionError as _e:
                    print(c_error + "Error: " + str(_e) + c_end)
                except ValueError as _e:
                    print(c_error + "Error: " + str(_e) + c_end)
                print()
                continue
        try:
            inp = inp.replace(';', ',')
            expr, ret_raw, ret_si, ret_cgs = calculate(inp, ',')
            print(c_diag + "Parsed input =" + c_end, end=' ')
            print(expr)
            # print()
            print(c_diag + "Result (SI)  =" + c_end, end=' ')
            print(ret_si)
            # print()
            print(c_diag + "Result (cgs) =" + c_end, end=' ')
            print(ret_cgs)
            print()
        except EvalError as _e:
            print(c_error + "Error: " + str(_e) + c_end)
            print()
            continue
        except Exception as _e:
            print(c_error + "Uncaught error: " + str(_e) + c_end)
            print()
            continue
        # # print()
        # userunit = input(c_diag + "In unit (press enter to skip): " + c_end)
        # try:
        #     tmp = convert(ret_raw, userunit)
        #     if tmp is not None:
        #         print(tmp)
        # except UnitConversionError as _e:
        #     print(c_error + "Error:" + str(_e) + c_end)
        # print()


if __name__ == '__main__':
    _withcolor = not "-nc" in sys.argv[1:]
    main(withcolor=_withcolor)
