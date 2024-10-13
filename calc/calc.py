#!/usr/bin/env python
""" calculator.py
A Calculator for Astronomers and Physicists.
Author: Chong-Chong He (che1234@umd.edu)
Date: 2020-06-20
"""

import sys
from math import pi, inf, log, log10, log2
from numpy import sin, arcsin, cos, arccos, tan, arctan, sinh, arctanh, cosh, arccosh, arcsinh, cosh, arccosh, tanh, arctanh, sqrt, exp, float64
import readline
from sympy import evaluate
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication, convert_xor
from astropy import units as U
from astropy import constants
from astropy.units.core import UnitConversionError, CompositeUnit
from astropy.units.quantity import Quantity
import logging
import textwrap

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
more_units = {
    'Length': ['m', 'cm', 'mm', 'um', 'nm', 'Angstrom', 'km', 'au', 'AU', 'pc', 'kpc', 'Mpc', 'lyr',],
    'Mass': ['kg', 'g', 'M_sun', 'Msun'],
    'Density': ['mpcc'],
    'Time': ['s', 'yr', 'Myr', 'Gyr',],
    'Energy': ['J', 'erg', 'eV', 'keV', 'MeV', 'GeV'],
    'Power': ['W'],
    'Pressure': ['Pa', 'bar', 'mbar'],
    'Frequency': ['Hz', 'kHz', 'MHz', 'GHz',],
    'Temperature': ['K',],
    'Angular size': ['deg', 'radian', 'arcmin', 'arcsec', 'arcsec2', 'sr'],
    'Astronomy': ['Lsun', 'Jy', 'mJy', 'MJy'],
    'Composite': ['m2', 'm3', 'cm2', 'cm3', 's2', 'pc2', 'pc3']
    }
# The following units are not avaiable in astropy.units and I have to define them myself
user_units = ['deg', 'Ang', 'mpcc', 'm2', 'm3', 'cm2', 'cm3', 's2', 'pc2', 'pc3', 'arcsec2', 'Msun']
# The following units are already defined as physical constants
_unit_skip = ['au', 'pc', 'M_sun']
# Define units that are not already defined in astropy.units
for _key in more_units.keys():
    for _unit in more_units[_key]:
        if _unit not in _unit_skip + user_units:
            locals()[_unit] = eval("U.{}".format(_unit))

# Function to define derived units globally
def define_derived_units():
    global esu, Ang, mpcc, Msun, m2, m3, cm2, cm3, s2, pc2, pc3, degree, arcsec2, Gauss
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
    degree = pi / 180
    arcsec2 = arcsec**2
    Gauss = g**(1/2) * cm**(-1/2) * s**(-1)

# Call the function to define derived units
define_derived_units()

# Define transformations
TRANSFORMATIONS = (convert_xor,) + standard_transformations + (implicit_multiplication,)

# Define format strings
IS_SCI = 0
F_FMT = '{{:.{}e}}'.format(DIGITS-1) if IS_SCI else "{{:#.{}g}}".format(DIGITS)


class EvalError(Exception):
    """Error in variable assignment"""
    pass


class UnitConversionError(Exception):
    """Error in variable assignment"""
    pass


def parse_and_eval(expr, local_vars_={}):
    """
    Return:
        parsed_input, output

    Raise:
        EvalError
    """

    inp_expr = expr
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
        return 1, inp_expr, str(error_msg)

    logging.debug("here #810")
    # get the results
    try:
        ret = eval(inp_expr)
    except Exception as _e:
        return 1, inp_expr, str(_e)

    return 0, inp_expr, ret


def calculate(inp, delimiter=','):
    """
    Return:
        err, parsed_expr, ret_raw, ret_si, ret_cgs
    """

    if inp == "":
        return 0, '', '', '', ''

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
            err, parsed_expr, ret = parse_and_eval(value, local_vars)
            local_vars[var] = ret

    # eval the last line
    logging.debug("here #250")
    err, parsed_expr, Ret = parse_and_eval(inp, local_vars)
    if err == 1:
        return 1, parsed_expr, Ret, '', ''

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
    return 0, parsed_expr, Ret, ret, ret2


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


def readline_input(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)
   finally:
      readline.set_startup_hook()


def parse_input(inp):
    inp = inp.replace('\n', ', ')
    inp = inp.replace(';', ',')
    return inp


def execute_calculation(inp, units=None):
    inp_parsed = parse_input(inp)
    err, expr, ret_raw, ret_si, ret_cgs = calculate(inp_parsed)
    if err == 1:
        return expr, ret_raw, '', ''
    result_user_units = 'none'
    if units is not None:
        userunit = units.strip()
        if userunit in ['degree', 'arcmin', 'arcsec']:
            try:
                result_user_units = convert(ret_raw, userunit)
            except Exception as _e:
                try:
                    result_user_units = convert(ret_raw * radian, userunit)
                except Exception as _e:
                    result_user_units = "Error: " + str(_e)
        else:
            try:
                result_user_units = convert(ret_raw, userunit)
            except Exception as _e:
                result_user_units = "Error: " + str(_e)
    return expr, ret_si, ret_cgs, result_user_units


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
            expr, ret_raw, ret_si, ret_cgs = calculate(inp)
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


if __name__ == '__main__':
    _withcolor = not "-nc" in sys.argv[1:]
    # main(withcolor=_withcolor)

    units = None
    expr = sys.argv[1]
    if len(sys.argv) > 2:
        units = sys.argv[2]
    parsed_input, result_si, result_cgs, result_user_units = execute_calculation(expr, units)
    print(parsed_input)
    print(result_si)
    print(result_cgs)
    print(result_user_units)
