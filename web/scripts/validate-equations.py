#!/usr/bin/env python3
"""Validate all equation templates against the calculator engine.

Mirrors the web worker's evaluate() flow:
  1. Build input: params (var = default) + expression lines
  2. Join lines with ', ' (the worker's delimiter)
  3. Feed to AstroCalculator.calculate()
"""
import json
import os
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from calc import AstroCalculator


def validate_one(calc, params, expression: str) -> None:
    """Evaluate a single expression with its params. Raises on error."""
    # Build input exactly as the web worker's evaluate() does:
    #   lines = [line.strip().rstrip(',;') for line in expression.split('\n')]
    #   expression = ', '.join(lines)
    param_lines = [f"{p['symbol']} = {p['default'].strip()}" for p in params]
    expr_lines = [
        line.strip().rstrip(',;')
        for line in expression.split('\n')
        if line.strip()
    ]
    full_input = ', '.join(param_lines + expr_lines)
    calc.calculate(full_input)


def main():
    equations_path = os.path.join(
        os.path.dirname(__file__), '..', 'src', 'data', 'equations.json'
    )
    with open(equations_path) as f:
        equations = json.load(f)

    failed = 0
    passed = 0

    for eq in equations:
        for expr in eq['expressions']:
            label = f"{eq['slug']}: {expr['name']}"
            calc = AstroCalculator(use_cache=False)
            try:
                validate_one(calc, eq['params'], expr['expression'])
                passed += 1
                print(f"  OK  {label}")
            except Exception as e:
                failed += 1
                msg = traceback.format_exception_only(e)[-1].strip()
                print(f"  FAIL  {label}  —  {msg}")

    print(f"\n{'='*50}")
    print(f"{passed} passed, {failed} failed (of {passed + failed} total)")
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()
