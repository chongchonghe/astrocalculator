# web/src/engine/calculator.py
"""AstroCalculator engine for Pyodide web worker."""

from math import pi, inf, log, log10, log2
import json

# Configuration
DIGITS = 10
IS_SCI = 0
F_FMT = f'{{:.{DIGITS-1}e}}' if IS_SCI else f'{{:#.{DIGITS}g}}'

# In Pyodide, these are available as globals after micropip.install
from astropy import units as u
from astropy import constants
import numpy as np
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication,
)

transformations = standard_transformations + (implicit_multiplication,)


def simple_eval(expr, namespace):
    """Fast evaluation for simple mathematical expressions."""
    expr = expr.strip()
    safe_dict = {
        '__builtins__': {},
        'pi': pi, 'inf': inf,
        'log': log, 'log10': log10, 'log2': log2,
    }
    safe_dict.update(namespace)

    # Try direct eval for simple expressions
    try:
        if all(c in '0123456789+-*/().eE pinflogcossinqrt^**' for c in expr.replace(' ', '')):
            python_expr = expr.replace('^', '**')
            result = eval(python_expr, safe_dict)
            return python_expr, result
    except:
        pass

    # Fall back to sympy — preprocess ^ to ** since convert_xor was removed in sympy 1.13+
    sympy_expr = expr.replace('^', '**')
    inp_expr = parse_expr(sympy_expr, transformations=transformations, evaluate=False)
    inp_expr_str = str(inp_expr)
    result = eval(inp_expr_str, globals(), namespace)
    return inp_expr_str, result


class AstroCalculator:
    """Calculator for astronomical and physical calculations."""
    user_units = ['deg', 'Ang', 'mpcc', 'm2', 'm3', 'cm2', 'cm3', 's2', 'pc2', 'pc3', 'arcsec2', 'Msun']

    def __init__(self):
        self.local_namespace = {}
        self._initialize_constants()
        self._initialize_units()

    def _initialize_constants(self):
        con_list = [
            'G', 'N_A', 'R', 'Ryd', 'a0', 'alpha', 'atm', 'b_wien', 'c', 'g0',
            'h', 'hbar', 'k_B', 'm_e', 'm_n', 'm_p', 'e', 'eps0', 'mu0', 'muB',
            'sigma_T', 'sigma_sb', 'GM_earth', 'GM_jup', 'GM_sun',
            'L_bol0', 'L_sun', 'M_earth', 'M_jup', 'M_sun', 'R_earth', 'R_jup',
            'R_sun', 'au', 'kpc', 'pc'
        ]
        con_list.sort(key=lambda y: y.lower())

        for con in con_list:
            try:
                self.local_namespace[con] = getattr(constants, con)
            except AttributeError:
                pass

        for func_name in ['sin', 'arcsin', 'cos', 'arccos', 'tan', 'arctan',
                          'sinh', 'arctanh', 'cosh', 'arccosh', 'arcsinh',
                          'tanh', 'arctanh', 'sqrt', 'exp']:
            self.local_namespace[func_name] = getattr(np, func_name)

        self.local_namespace['pi'] = pi
        self.local_namespace['inf'] = inf
        self.local_namespace['log'] = log
        self.local_namespace['log10'] = log10
        self.local_namespace['log2'] = log2

    def _initialize_units(self):
        more_units = {
            'Length': ['m', 'cm', 'mm', 'um', 'nm', 'Angstrom', 'km', 'au', 'AU', 'pc', 'kpc', 'Mpc', 'lyr'],
            'Mass': ['kg', 'g', 'M_sun', 'Msun'],
            'Density': ['mpcc'],
            'Time': ['s', 'yr', 'Myr', 'Gyr'],
            'Energy': ['J', 'erg', 'eV', 'keV', 'MeV', 'GeV'],
            'Power': ['W'],
            'Pressure': ['Pa', 'bar', 'mbar'],
            'Frequency': ['Hz', 'kHz', 'MHz', 'GHz'],
            'Temperature': ['K'],
            'Angular size': ['deg', 'radian', 'arcmin', 'arcsec', 'arcsec2'],
            'Astronomy': ['Lsun', 'Jy', 'mJy', 'MJy'],
            'Composite': ['m2', 'm3', 'cm2', 'cm3', 's2', 'pc2', 'pc3']
        }
        unit_skip = ['au', 'pc', 'M_sun']

        for key in more_units:
            for unit_name in more_units[key]:
                if unit_name not in unit_skip + self.user_units:
                    try:
                        self.local_namespace[unit_name] = getattr(u, unit_name)
                    except AttributeError:
                        pass

        self._define_derived_units()

    def _define_derived_units(self):
        e = self.local_namespace['e']
        m_p = self.local_namespace['m_p']
        M_sun = self.local_namespace['M_sun']
        sigma_sb = self.local_namespace['sigma_sb']
        c = self.local_namespace['c']
        m = u.m
        cm = u.cm
        nm = u.nm
        s = u.s
        pc = self.local_namespace['pc']
        arcsec = u.arcsec
        g = u.g

        self.local_namespace['esu'] = e.esu
        self.local_namespace['Ang'] = u.def_unit('Ang', 0.1 * nm)
        self.local_namespace['mpcc'] = u.def_unit('mpcc', m_p / cm**3)
        self.local_namespace['Msun'] = M_sun
        self.local_namespace['m2'] = m**2
        self.local_namespace['m3'] = m**3
        self.local_namespace['cm2'] = cm**2
        self.local_namespace['cm3'] = cm**3
        self.local_namespace['s2'] = s**2
        self.local_namespace['pc2'] = pc**2
        self.local_namespace['pc3'] = pc**3
        self.local_namespace['degrees'] = pi / 180
        self.local_namespace['arcsec2'] = arcsec**2
        self.local_namespace['Gauss'] = g**(1/2) * cm**(-1/2) * s**(-1)
        self.local_namespace['a_rad'] = 4. * sigma_sb / c

    def parse_and_eval(self, expr):
        try:
            return simple_eval(expr, self.local_namespace)
        except Exception as e:
            raise ValueError(str(e))

    def calculate(self, inp, delimiter=','):
        if not inp.strip():
            return None

        inp = inp.strip()

        # Check for 'in unit' clause
        target_unit = None
        if ' in ' in inp:
            parts = inp.split(' in ')
            if len(parts) == 2:
                inp = parts[0].strip()
                target_unit = parts[1].strip()

        exp_to_eval = None
        lines = inp.split(delimiter)
        n_line = len(lines)

        for count, line in enumerate(lines):
            line = line.strip()
            if count == n_line - 1:
                exp_to_eval = line.split('=')[0].strip()

            if not line or '=' not in line:
                continue

            items = line.split('=')
            if len(items) > 2:
                raise ValueError('Multiple equal signs found')

            var, value = items
            var = var.strip()
            if ' ' in var:
                raise ValueError('Variable should not have space in it')

            _, result = self.parse_and_eval(value)
            self.local_namespace[var] = result

        parsed_expr, raw_result = self.parse_and_eval(exp_to_eval)

        from astropy.units.quantity import Quantity
        from astropy.units.core import CompositeUnit

        si_result = None
        cgs_result = None

        if isinstance(raw_result, (int, float)):
            si_result = raw_result if isinstance(raw_result, int) else F_FMT.format(raw_result)
            cgs_result = si_result
        else:
            if isinstance(raw_result.si, Quantity):
                si_result = F_FMT.format(raw_result.si)
            else:
                si_result = str(raw_result.si)

            try:
                if isinstance(raw_result.cgs, CompositeUnit):
                    cgs_result = str(raw_result.cgs)
                else:
                    cgs_result = F_FMT.format(raw_result.cgs)
            except:
                cgs_result = str(raw_result.cgs) if raw_result.cgs else "N/A"

        converted = None
        if target_unit and raw_result is not None:
            try:
                if not isinstance(raw_result, (int, float)):
                    if target_unit in self.user_units:
                        cv = raw_result.to(self.local_namespace[target_unit])
                    else:
                        cv = raw_result.to(target_unit)
                    if isinstance(cv, int):
                        converted = str(cv)
                    elif isinstance(cv, float):
                        converted = F_FMT.format(cv)
                    else:
                        converted = f"{F_FMT.format(cv.value)} {cv._unit}"
            except:
                converted = f"Error converting to {target_unit}"

        return {
            "parsed": str(parsed_expr),
            "si": str(si_result),
            "cgs": str(cgs_result),
            "converted": converted,
            "targetUnit": target_unit,
        }


# Module-level singleton
_calc = None


def get_calculator():
    global _calc
    if _calc is None:
        _calc = AstroCalculator()
    return _calc


def evaluate(expression):
    calc = get_calculator()
    # Normalize multi-line input: newlines → commas (same as original CLI)
    expression = expression.replace('\n', ', ')
    result = calc.calculate(expression)
    if result is None:
        return {"parsed": "", "si": "", "cgs": ""}
    return result


def convert_quantity(quantity_obj, unit):
    calc = get_calculator()
    _, qty = calc.parse_and_eval(quantity_obj)
    return calc.convert(qty, unit)
