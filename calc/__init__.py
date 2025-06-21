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
from datetime import datetime
from math import pi, inf, log, log10, log2
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import readline
from sympy import evaluate
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication,
    convert_xor,
)
from astropy import units as u
from astropy import constants
from astropy.units.core import UnitConversionError, CompositeUnit
from astropy.units.quantity import Quantity

# Configuration constants
DIGITS = 10          # number of significant digits in the scientific notation
REQUIRE_UNDERSCORE = False
IS_SCI = 0
F_FMT = f'{{:.{DIGITS-1}e}}' if IS_SCI else f'{{:#.{DIGITS}g}}'

# Define transformations for sympy parsing
TRANSFORMATIONS = (convert_xor,) + standard_transformations + (implicit_multiplication,)

# Directory for saved history
USER_DATA_DIR = os.path.expanduser("~/.cache/astrocalculator")
HISTORY_DIR = os.path.join(USER_DATA_DIR, "history")

# Ensure directories exist
os.makedirs(HISTORY_DIR, exist_ok=True)


class EvalError(Exception):
    """Exception raised when there's an error in variable evaluation."""
    pass


class AstroCalculator:
    """Calculator for astronomical and physical calculations with unit support."""

    # Units not available in astropy.units that require custom definitions
    user_units = ['deg', 'Ang', 'mpcc', 'm2', 'm3', 'cm2', 'cm3', 's2', 'pc2', 'pc3', 'arcsec2', 'Msun']

    def __init__(self):
        """Initialize the calculator with constants and units."""
        self.local_namespace = {}
        self._initialize_constants()
        self._initialize_units()

    def _initialize_constants(self):
        """Initialize physical constants from astropy."""
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
            # Parse the expression using sympy
            inp_expr = parse_expr(expr, transformations=TRANSFORMATIONS, evaluate=False)
            inp_expr_str = str(inp_expr)

            # Evaluate the parsed expression with our namespace
            result = eval(inp_expr_str, globals(), self.local_namespace)
            return inp_expr_str, result

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

        if isinstance(raw_result, (int, float, np.float64)):
            # Handle numeric results without units
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
                    # unit = getattr(u, unit_name)
                    # converted = quant.to(unit)

                    converted = quant.to(unit_name)

                if isinstance(converted, int):
                    return converted
                elif isinstance(converted, float):
                    return F_FMT.format(converted)
                else:
                    return f"{F_FMT.format(converted.value)} {converted._unit}"

            except (AttributeError, UnitConversionError) as e:
                raise UnitConversionError(str(e))


def readline_input(prompt: str, prefill: str = '') -> str:
    """Get input with readline support for history and prefill.

    Args:
        prompt: Prompt string to display
        prefill: Text to prefill in the input line

    Returns:
        User input string
    """
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
    calculator = AstroCalculator()
    inp_parsed = parse_input(inp)
    expr, ret_raw, ret_si, ret_cgs, target_unit = calculator.calculate(inp_parsed)
    output = f"Parsed input = {expr}\nResult (SI)  = {ret_si}\nResult (cgs) = {ret_cgs}"

    # If a target unit was specified, convert the result
    if target_unit and ret_raw is not None:
        try:
            converted = calculator.convert(ret_raw, target_unit)
            if converted is not None:
                output += f"\nConverted to {target_unit} = {converted}"
        except UnitConversionError as e:
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

    calculator = AstroCalculator()
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
            except UnitConversionError as e:
                print(c_error + "Error: " + str(e) + c_end)
            except ValueError as e:
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
                except UnitConversionError as e:
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
    """Main function to run the calculator.

    Args:
        withcolor: Whether to use colored output
    """

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

    calculator = AstroCalculator()
    inputs = input.strip().split('\n')
    # print(inputs)
    for inp in inputs[:-1]:
        calculator.calculate(inp)
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
            except UnitConversionError as e:
                print(c_error + f"Error converting to {target_unit}: {str(e)}" + c_end)
        else:
            print(f"{expr} = {ret_cgs}")


if __name__ == '__main__':

    # _withcolor = "-nc" not in sys.argv[1:]

    if len(sys.argv) == 1:
        main_interactive()
    else:
        main_non_interactive()
