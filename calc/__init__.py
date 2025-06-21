#!/usr/bin/env python
"""AstroCalculator - A Calculator for Astronomers and Physicists.

This module provides a command-line calculator with support for physical constants
and units from astropy. It allows users to perform calculations with physical
quantities, convert between units, and access various astronomical and physical constants.

Author: Chong-Chong He (chongchong.he@anu.edu.au)
Last updated: 2025-06-21
"""

from __future__ import annotations

import logging
import sys
import textwrap
import json
import os
import pickle
from datetime import datetime
from math import pi, inf, log, log10, log2
from typing import Any, Dict, List, Optional, Tuple, Union

# Configuration constants
DIGITS = 10          # number of significant digits in the scientific notation
REQUIRE_UNDERSCORE = False
IS_SCI = 0
F_FMT = f'{{:.{DIGITS-1}e}}' if IS_SCI else f'{{:#.{DIGITS}g}}'

# Directory for saved history and cache
USER_DATA_DIR = os.path.expanduser("~/.cache/astrocalculator")
HISTORY_DIR = os.path.join(USER_DATA_DIR, "history")
CACHE_FILE = os.path.join(USER_DATA_DIR, "calculator_cache.pkl")

# Ensure directories exist
os.makedirs(HISTORY_DIR, exist_ok=True)

# Global variables for lazy imports
_numpy = None
_astropy_units = None
_astropy_constants = None
_sympy_parser = None
_readline = None
_cached_calculator = None


def get_numpy():
    """Lazy import of numpy."""
    global _numpy
    if _numpy is None:
        import numpy as np
        _numpy = np
    return _numpy


def get_astropy_units():
    """Lazy import of astropy units."""
    global _astropy_units
    if _astropy_units is None:
        from astropy import units as u
        _astropy_units = u
    return _astropy_units


def get_astropy_constants():
    """Lazy import of astropy constants."""
    global _astropy_constants
    if _astropy_constants is None:
        from astropy import constants
        _astropy_constants = constants
    return _astropy_constants


def get_sympy_parser():
    """Lazy import of sympy parser."""
    global _sympy_parser
    if _sympy_parser is None:
        from sympy.parsing.sympy_parser import (
            parse_expr,
            standard_transformations,
            implicit_multiplication,
            convert_xor,
        )
        from sympy import evaluate
        
        transformations = (convert_xor,) + standard_transformations + (implicit_multiplication,)
        _sympy_parser = {
            'parse_expr': parse_expr,
            'transformations': transformations,
            'evaluate': evaluate
        }
    return _sympy_parser


def get_readline():
    """Lazy import of readline."""
    global _readline
    if _readline is None:
        import readline
        _readline = readline
    return _readline


class EvalError(Exception):
    """Exception raised when there's an error in variable evaluation."""
    pass


def simple_eval(expr: str, namespace: Dict[str, Any]) -> Tuple[str, Any]:
    """
    Fast evaluation for simple mathematical expressions without sympy.
    Falls back to sympy for complex expressions.
    """
    # Remove whitespace
    expr = expr.strip()
    
    # Check if it's a simple expression that Python can handle directly
    # This covers basic arithmetic, constants, and function calls
    try:
        # Create a safe evaluation environment
        safe_dict = {
            '__builtins__': {},
            'pi': pi,
            'inf': inf,
            'log': log,
            'log10': log10,
            'log2': log2,
        }
        safe_dict.update(namespace)
        
        # For simple expressions, try direct evaluation first
        if all(c in '0123456789+-*/().eE pinflogcossinqrt^**' for c in expr.replace(' ', '')):
            # Replace ^ with ** for Python compatibility
            python_expr = expr.replace('^', '**')
            result = eval(python_expr, safe_dict)
            return python_expr, result
    except:
        pass
    
    # Fall back to sympy for complex expressions
    sympy_parser = get_sympy_parser()
    inp_expr = sympy_parser['parse_expr'](expr, transformations=sympy_parser['transformations'], evaluate=False)
    inp_expr_str = str(inp_expr)
    result = eval(inp_expr_str, globals(), namespace)
    return inp_expr_str, result


class AstroCalculator:
    """Calculator for astronomical and physical calculations with unit support."""

    # Units not available in astropy.units that require custom definitions
    user_units = ['deg', 'Ang', 'mpcc', 'm2', 'm3', 'cm2', 'cm3', 's2', 'pc2', 'pc3', 'arcsec2', 'Msun']

    def __init__(self, use_cache: bool = True):
        """Initialize the calculator with constants and units."""
        self.local_namespace = {}
        self.use_cache = use_cache
        
        if use_cache:
            if self._load_from_cache():
                return
        
        self._initialize_constants()
        self._initialize_units()
        
        if use_cache:
            self._save_to_cache()

    def _load_from_cache(self) -> bool:
        """Load calculator state from cache if available."""
        try:
            if os.path.exists(CACHE_FILE):
                # Check if cache is recent (less than 1 day old)
                cache_age = datetime.now().timestamp() - os.path.getmtime(CACHE_FILE)
                if cache_age < 86400:  # 24 hours
                    with open(CACHE_FILE, 'rb') as f:
                        self.local_namespace = pickle.load(f)
                    return True
        except:
            pass
        return False

    def _save_to_cache(self):
        """Save calculator state to cache."""
        try:
            with open(CACHE_FILE, 'wb') as f:
                pickle.dump(self.local_namespace, f)
        except:
            pass

    def _initialize_constants(self):
        """Initialize physical constants from astropy."""
        constants = get_astropy_constants()
        
        # Define constants available in astropy.units
        con_list = [
            'G', 'N_A', 'R', 'Ryd', 'a0', 'alpha', 'atm', 'b_wien', 'c', 'g0',
            'h', 'hbar', 'k_B', 'm_e', 'm_n', 'm_p', 'e', 'eps0', 'mu0', 'muB',
            'sigma_T', 'sigma_sb', 'GM_earth', 'GM_jup', 'GM_sun',
            'L_bol0', 'L_sun', 'M_earth', 'M_jup', 'M_sun', 'R_earth', 'R_jup',
            'R_sun', 'au', 'kpc', 'pc'
        ]
        con_list.sort(key=lambda y: y.lower())

        # Load constants into the namespace
        fail_list = []
        for con in con_list:
            try:
                self.local_namespace[con] = getattr(constants, con)
            except AttributeError:
                fail_list.append(con)

        # Add math and numpy functions to namespace
        np = get_numpy()
        for func_name in ['sin', 'arcsin', 'cos', 'arccos', 'tan', 'arctan',
                          'sinh', 'arctanh', 'cosh', 'arccosh', 'arcsinh',
                          'tanh', 'arctanh', 'sqrt', 'exp']:
            self.local_namespace[func_name] = getattr(np, func_name)

        # Add math constants
        self.local_namespace['pi'] = pi
        self.local_namespace['inf'] = inf
        self.local_namespace['log'] = log
        self.local_namespace['log10'] = log10
        self.local_namespace['log2'] = log2

    def _initialize_units(self):
        """Initialize unit definitions from astropy and derived units."""
        u = get_astropy_units()
        
        # Define unit categories
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

        # Units already defined as physical constants
        unit_skip = ['au', 'pc', 'M_sun']

        # Add basic astropy units to namespace
        for key in more_units.keys():
            for unit_name in more_units[key]:
                if unit_name not in unit_skip + self.user_units:
                    try:
                        self.local_namespace[unit_name] = getattr(u, unit_name)
                    except AttributeError:
                        pass

        # Define derived units
        self._define_derived_units()

    def _define_derived_units(self):
        """Define derived units that are combinations of basic units."""
        u = get_astropy_units()
        
        # Access constants from the namespace
        e = self.local_namespace['e']
        m_p = self.local_namespace['m_p']
        M_sun = self.local_namespace['M_sun']
        sigma_sb = self.local_namespace['sigma_sb']
        c = self.local_namespace['c']

        # Access basic units
        m = u.m
        cm = u.cm
        nm = u.nm
        s = u.s
        pc = self.local_namespace['pc']
        arcsec = u.arcsec
        g = u.g

        # Define derived units
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

    def parse_and_eval(self, expr: str) -> Tuple[str, Any]:
        """Parse and evaluate a mathematical expression.

        Args:
            expr: Mathematical expression to evaluate

        Returns:
            Tuple containing (parsed_expression, result)

        Raises:
            EvalError: If there's an error in parsing or evaluating the expression
        """
        logging.debug(f"Evaluating expression: {expr}")

        try:
            return simple_eval(expr, self.local_namespace)
        except Exception as error_msg:
            raise EvalError(error_msg)

    def calculate(self, inp: str, delimiter: str = ',') -> Tuple[Optional[str], Optional[Any], Optional[str], Optional[str], Optional[str]]:
        """Calculate results from input string with support for multiple expressions.

        Args:
            inp: Input string containing expressions to evaluate
            delimiter: Delimiter for separating multiple expressions

        Returns:
            Tuple of (parsed_expression, raw_result, si_result, cgs_result, target_unit)
            where target_unit is the unit to convert to if 'in unit' is specified
        """
        if not inp.strip():
            return None, None, None, None, None

        # Remove trailing whitespace
        inp = inp.strip()

        # Check if there's an 'in unit' part at the end
        target_unit = None
        if ' in ' in inp:
            # Extract the target unit
            parts = inp.split(' in ')
            if len(parts) == 2:
                inp = parts[0].strip()
                target_unit = parts[1].strip()

        # Handle variable assignments. If a delimiter is found, all but the last line are variable assignments.
        exp_to_eval = None

        lines = inp.split(delimiter)
        n_line = len(lines)

        for count, line in enumerate(lines):
            line = line.strip()

            # if last line, set the first part (before =) as exp_to_eval
            if count == n_line - 1:
                exp_to_eval = line.split('=')[0].strip()

            if not line or '=' not in line:
                continue

            items = line.split('=')
            if len(items) > 2:
                raise EvalError('Multiple equal signs found in variable assignment')

            var, value = items
            var = var.strip()

            # Check variable name validity
            if REQUIRE_UNDERSCORE and var[0] != '_':
                raise EvalError("Assigned variable must begin with _ (underscore)")
            if ' ' in var:
                raise EvalError('Variable should not have space in it')

            # Evaluate and store in local namespace
            _, result = self.parse_and_eval(value)
            self.local_namespace[var] = result

        # Evaluate the final expression
        parsed_expr, raw_result = self.parse_and_eval(exp_to_eval)

        # Format results
        si_result = None
        cgs_result = None

        # Lazy import astropy.units for result formatting
        u = get_astropy_units()
        from astropy.units.quantity import Quantity
        from astropy.units.core import UnitConversionError, CompositeUnit

        if isinstance(raw_result, (int, float)):
            # Handle numeric results without units
            np = get_numpy()
            if not isinstance(raw_result, int):
                si_result = F_FMT.format(raw_result)
            else:
                si_result = raw_result
            cgs_result = si_result
        else:
            # Handle results with units
            if isinstance(raw_result.si, Quantity):
                si_result = F_FMT.format(raw_result.si)
            else:
                # Physical constants. Display full description.
                si_result = '\n' + str(raw_result.si)

            # CGS units
            try:
                if isinstance(raw_result.cgs, CompositeUnit):
                    cgs_result = raw_result.cgs
                else:
                    cgs_result = F_FMT.format(raw_result.cgs)
            except Exception as e:
                cgs_result = textwrap.fill(str(e), 80)

        return parsed_expr, raw_result, si_result, cgs_result, target_unit

    def convert(self, quant, unit_name: str) -> Optional[str]:
        """Convert a quantity to the specified unit.

        Args:
            quant: Quantity to convert
            unit_name: Target unit name

        Returns:
            Formatted string with the converted value
        """
        if not unit_name:
            return None

        # Lazy import for unit conversion
        from astropy.units.core import UnitConversionError
        np = get_numpy()

        if isinstance(quant, int):
            return quant
        elif isinstance(quant, (float, np.float64)):
            return F_FMT.format(quant)
        else:
            # Handle unit conversion for quantities
            try:
                # Check if it's a user-defined unit
                if unit_name in self.user_units:
                    converted = quant.to(self.local_namespace[unit_name])
                else:
                    # Try to get from astropy units
                    converted = quant.to(unit_name)

                if isinstance(converted, int):
                    return converted
                elif isinstance(converted, float):
                    return F_FMT.format(converted)
                else:
                    return f"{F_FMT.format(converted.value)} {converted._unit}"

            except (AttributeError, UnitConversionError) as e:
                raise UnitConversionError(str(e))


def get_cached_calculator():
    """Get a cached calculator instance for better performance."""
    global _cached_calculator
    if _cached_calculator is None:
        _cached_calculator = AstroCalculator(use_cache=True)
    return _cached_calculator


def readline_input(prompt: str, prefill: str = '') -> str:
    """Get input with readline support for history and prefill.

    Args:
        prompt: Prompt string to display
        prefill: Text to prefill in the input line

    Returns:
        User input string
    """
    readline = get_readline()
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def parse_input(inp: str) -> str:
    """Parse input string to standardize format.

    Args:
        inp: Raw input string

    Returns:
        Parsed input string
    """
    inp = inp.replace('\n', ', ')
    inp = inp.replace(';', ',')
    return inp


def execute_calculation(inp: str) -> None:
    """Execute a calculation and print results.

    Args:
        inp: Input string with calculation
    """
    calculator = get_cached_calculator()
    inp_parsed = parse_input(inp)
    expr, ret_raw, ret_si, ret_cgs, target_unit = calculator.calculate(inp_parsed)
    output = f"Parsed input = {expr}\nResult (SI)  = {ret_si}\nResult (cgs) = {ret_cgs}"

    # If a target unit was specified, convert the result
    if target_unit and ret_raw is not None:
        try:
            converted = calculator.convert(ret_raw, target_unit)
            if converted is not None:
                output += f"\nConverted to {target_unit} = {converted}"
        except Exception as e:
            from astropy.units.core import UnitConversionError
            if isinstance(e, UnitConversionError):
                output += f"\nError converting to {target_unit}: {str(e)}"

    print(output)


def save_session(history: List[str], session_name: Optional[str] = None) -> str:
    """
    Save the command history to a file.

    Args:
        history: List of command history
        session_name: Optional name for the history file

    Returns:
        Path to the saved history file
    """
    if not session_name:
        # Generate a timestamp-based name if none provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_name = f"history_{timestamp}"

    # Ensure .json extension
    if not session_name.endswith(".json"):
        session_name += ".json"

    # Full path to the history file
    history_path = os.path.join(HISTORY_DIR, session_name)

    # Prepare history data
    history_data = {
        "history": history,
        "timestamp": datetime.now().isoformat()
    }

    # Write to file
    with open(history_path, 'w') as f:
        json.dump(history_data, f, indent=2)

    return history_path


def list_history_files() -> List[str]:
    """
    List all saved history files.

    Returns:
        List of history file names
    """
    if not os.path.exists(HISTORY_DIR):
        return []

    # Get all JSON files in the history directory
    history_files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    return sorted(history_files)


def load_history(history_file: str) -> List[str]:
    """
    Load command history from a file.

    Args:
        history_file: Path to the history file

    Returns:
        List of command history entries
    """
    # If just the name was provided, construct the full path
    if not os.path.isabs(history_file):
        if not history_file.endswith(".json"):
            history_file += ".json"
        history_file = os.path.join(HISTORY_DIR, history_file)

    try:
        with open(history_file, 'r') as f:
            history_data = json.load(f)

        history = history_data.get("history", [])
        return history
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to load history: {str(e)}")


def main_interactive() -> None:
    """Main function to run the calculator.

    Args:
        withcolor: Whether to use colored output
    """
    print("""===============================================
A Calculator for Astrophysicists and Physicists
Author: Chong-Chong He (che1234@umd.edu)

Examples:
>>> m_p

>>> m_e c^2

>>> m_e c^2 in eV

>>> M = 1.4 M_sun, R = 10 km, sqrt(2 G M / R) in km/s

Special commands:
- save [name]  : Save command history
- history      : List all saved history files
- history [name] : Display commands from a specific history file
- help         : Show help
- q            : Quit

For available constants and units, check
https://github.com/chongchonghe/acap/blob/master/docs/constants.md
===============================================""")
    print()

    withcolor = True

    # Set up color codes if enabled
    if withcolor:
        c_diag = '\33[92m'
        c_error = '\033[91m'
        c_end = '\033[m'
    else:
        c_diag = ''
        c_error = ''
        c_end = ''

    calculator = AstroCalculator(use_cache=True)
    count = 0
    default = ''
    history: List[str] = []
    ret_raw = None

    while True:
        count += 1
        pre = c_diag + f"Input[{count}]: " + c_end + "\n"

        # Collect multiple lines until empty line
        input_lines: List[str] = []
        while True:
            if default == '':
                line = input(pre if not input_lines else "")
            else:
                line = readline_input(pre if not input_lines else "", default).strip()
                default = ''
            line = line.strip()

            # Handle empty line
            if not line:
                break

            # Remove trailing comma or semicolon
            line = line.rstrip(',;')
            input_lines.append(line)

            if line.startswith('in ') or line == 'q' or line.startswith('save ') or line.startswith('history'):
                break

        # Combine all lines with commas
        inp = ', '.join(input_lines)

        if not inp:
            continue
        if inp == 'q':
            return

        # Handle special commands
        if inp.startswith('save '):
            # Extract history name (if provided)
            parts = inp.split(' ', 1)
            history_name = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None

            try:
                # Save the history
                saved_path = save_session(history, history_name)
                print(f"History saved to {os.path.basename(saved_path)}")
            except Exception as e:
                print(c_error + f"Error saving history: {str(e)}" + c_end)

            print()
            continue

        elif inp.startswith('history'):
            parts = inp.split(' ', 1)

            # If a specific history file is provided, display its contents
            if len(parts) > 1 and parts[1].strip():
                history_name = parts[1].strip()
                try:
                    # Load history from the specified file
                    cmds = load_history(history_name)

                    if not cmds:
                        print(f"No commands found in history file '{history_name}'")
                    else:
                        print(f"Commands in '{history_name}':")
                        for cmd in cmds:
                            print(cmd)
                except Exception as e:
                    print(c_error + f"Error loading history: {str(e)}" + c_end)
            else:
                # List all saved history files
                history_files = list_history_files()

                if not history_files:
                    print("No saved history files found")
                else:
                    print("Saved history files:")
                    for i, h_file in enumerate(history_files, 1):
                        # Remove .json extension for display
                        display_name = h_file[:-5] if h_file.endswith(".json") else h_file
                        print(f"{i}. {display_name}")

            print()
            continue

        elif inp == 'help':
            print("""Commands:
- save [name]  : Save command history
- history      : List all saved history files
- history [name] : Display commands from a specific history file
- help         : Show this help
- q            : Quit calculator
- in [unit]    : Convert last result to specified unit
""")
            print()
            continue

        # Add to history for normal commands
        history.append(inp)
        print()

        # Handle unit conversion request (standalone)
        if len(inp) > 3 and inp[:3] == 'in ':
            if ret_raw is None:
                continue
            userunit = inp[3:].strip()
            try:
                converted = calculator.convert(ret_raw, userunit)
                if converted is not None:
                    print(converted)
            except Exception as e:
                from astropy.units.core import UnitConversionError
                if isinstance(e, UnitConversionError):
                    print(c_error + "Error: " + str(e) + c_end)
                else:
                    print(c_error + "Error: " + str(e) + c_end)
            print()
            continue

        # Handle calculation
        try:
            inp = inp.replace(';', ',')
            expr, ret_raw, ret_si, ret_cgs, target_unit = calculator.calculate(inp)
            print(c_diag + "Parsed input =" + c_end, end=' ')
            print(expr)
            print(c_diag + "Result (SI)  =" + c_end, end=' ')
            print(ret_si)
            print(c_diag + "Result (cgs) =" + c_end, end=' ')
            print(ret_cgs)

            # If a target unit was specified, display the conversion
            if target_unit and ret_raw is not None:
                try:
                    converted = calculator.convert(ret_raw, target_unit)
                    if converted is not None:
                        print(c_diag + f"In {target_unit} =" + c_end, end=' ')
                        print(converted)
                except Exception as e:
                    from astropy.units.core import UnitConversionError
                    if isinstance(e, UnitConversionError):
                        print(c_error + f"Error converting to {target_unit}: {str(e)}" + c_end)

            print()
        except EvalError as e:
            print(c_error + "Error: " + str(e) + c_end)
            print()
            continue
        except Exception as e:
            print(c_error + "Uncaught error: " + str(e) + c_end)
            print()
            continue


def main_non_interactive() -> None:
    """Main function to run the calculator in non-interactive mode."""

    withcolor = False
    input = sys.argv[1]

    # Set up color codes if enabled
    if withcolor:
        c_diag = '\33[92m'
        c_error = '\033[91m'
        c_end = '\033[m'
    else:
        c_diag = ''
        c_error = ''
        c_end = ''

    calculator = get_cached_calculator()
    inputs = input.strip().split('\n')

    n_inputs = len(inputs)
    if n_inputs == 1:
        input1 = inputs[0].replace(';', ',')
        firsts = ','.join(input1.split(',')[:-1])
        calculator.calculate(firsts)
        last_inputs = [input1.split(',')[-1]]
    else:
        # Process all but the last input (variable assignments)
        for inp in inputs[:-1]:
            calculator.calculate(inp)
        # Process the last input (the expression to evaluate)
        last_inputs = inputs[-1].replace(';', ',').split(',')

    for last_input in last_inputs:
        expr, ret_raw, _, ret_cgs, target_unit = calculator.calculate(last_input)
        # If a target unit was specified, display the conversion
        if target_unit and ret_raw is not None:
            try:
                converted = calculator.convert(ret_raw, target_unit)
                if converted is not None:
                    print(c_diag + f"{expr} =" + c_end, end=' ')
                    print(converted)
            except Exception as e:
                from astropy.units.core import UnitConversionError
                if isinstance(e, UnitConversionError):
                    print(c_error + f"Error converting to {target_unit}: {str(e)}" + c_end)
        else:
            print(f"{expr} = {ret_cgs}")


if __name__ == '__main__':

    if len(sys.argv) == 1:
        main_interactive()
    else:
        main_non_interactive()
