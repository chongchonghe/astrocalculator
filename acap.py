#!/usr/bin/env python
""" acap.py
ACAP, an Awesome Calculator for Astronomers and Physicists.
Author: Chong-Chong He (che1234@umd.edu)
Date: 2020-06-20

A calculator written in python with GUI.
"""

from math import *
from numpy import sqrt
from astropy import units as U
from astropy import constants as C
from astropy.constants import *
# from astropy.cosmology import WMAP9

#========================================================================
# The following variables can be changed by the user
SCALE = 1.3      # Recommended: 1.3 on 1080p, 1.0 on a retina display.
USE_ENTER = True    # True or False. Use <Enter> to calculate instead of 'Calculate' button
DIGITS = 4       # number of significant digits in scientific notations
#========================================================================

# load astropy constants
Units = {
    'Length': ['m', 'cm', 'mm', 'um', 'nm', 'Angstrom', 'km', 'au', 'AU', 'pc', 'kpc', 'Mpc', 'lyr',],
    'Mass': ['kg', 'g', 'M_sun', 'Msun'],
    'Density': ['mpcc'],
    'Time': ['s', 'yr', 'Myr', 'Gyr',],
    'Energy': ['J', 'erg', 'eV', 'keV', 'MeV', 'GeV'],
    'Power': ['W'],
    'Pressure': ['Pa', 'bar', 'mbar'],
    'Frequency': ['Hz', 'kHz', 'MHz', 'GHz',],
    'Temperature': ['K',],
    'Angular size': ['deg', 'arcmin', 'arcsec', 'arcsec2'],
    'Astronomy': ['Lsun', 'Jy', 'mJy', 'MJy'],
    'Composite': ['m2', 'm3', 'cm2', 'cm3', 's2', 'pc2', 'pc3']
    }
UNITS_USER = ['Msun', 'Ang', 'mpcc', 'm2', 'm3', 'cm2', 'cm3', 's2', 'pc2',
              'pc3', 'deg', 'arcsec', 'arcsec2']
_unit_skip = ['au', 'pc', 'M_sun']  # defined as constants instead of units
# Extra
for _key in Units.keys():
    for _unit in Units[_key]:
        if _unit not in _unit_skip + UNITS_USER:
            locals()[_unit] = eval("U.{}".format(_unit))

# User defined units
# Ang = 0.1 * nm
esu = e.esu
Ang = U.def_unit('Ang', 0.1 * nm)
# mpcc = m_p / cm**3
mpcc = U.def_unit('mpcc', m_p / cm**3)
Msun = M_sun
m2 = m**2
m3 = m**3
cm2 = cm**2
cm3 = cm**3
s2 = s**2
pc2 = pc**2
pc3 = pc**3
deg = pi / 180.
arcmin = deg / 60.
arcsec = deg / 60.**2
arcsec2 = arcsec**2

# Cosmology
# H0 = WMAP9.H0

# from sympy.printing.str import StrPrinter
# class CustomStrPrinter(StrPrinter):
#     def _print_Float(self, expr):
#         return '{:.3e}'.format(expr)

IS_SCI = 0

def main():

    # transformations = standard_transformations +\
    #     (restrict_e_notation_precision,) +\
    #     (implicit_multiplication,) +\
    #     (convert_xor,)
    transformations = standard_transformations +\
        (implicit_multiplication,) +\
        (convert_xor,)

    win = tk.Tk()
    win.tk.call('tk', 'scaling', SCALE)
    win.title("ACAP")
    win.geometry('{:d}x{:d}'.format(int(600.0*SCALE), int(660.0*SCALE)))

    # Documentation
    doc = \
        "Welcome to ACAP, an Awesome Calculator for Astronomers and Physicists!\n"\
        "Author: Chong-Chong He (che1234@umd.edu)\n"\
        "\n"\
        "Type in the expression you want to evaluate in the box below and "\
        "{}. ".format("press <Enter>" if USE_ENTER else "click 'Calculate'") +\
        "The box in the bottom left corner can be used to express the output in any units.\n"\
        "\n"\
        "Example input: \n"\
        "    4 pc\n"\
        "    sqrt(G M_sun / au)\n"\
        "    m_p c^2 / k_B\n"\
        "    esu^2 / (0.1 nm)^2 (esu is the electron charge in ESU system)\n"\
        "\n"
    doc += "\n".join(C.__doc__.splitlines()[13:]) + "\n"
    doc += "\n"
    doc += "The following units are available:\n\n"
    for _key in Units.keys():
        doc += "{:s} | {}\n".format(_key.rjust(12), ", ".join(Units[_key]))
    doc += "\n"
    doc += "Command math operations are available. For instance, sin, cos, exp, ! (factorial), ^ (power), sqrt\n"
    doc += "\n"
    doc += "More units are available for the user-defined unit."
    # print('\n\nHere')
    # doc = doc.splitlines()[13:]
    # doc = "\n".join(doc)

    scrollbar = tk.Scrollbar(win)
    scrollbar.pack(side='right', fill='y')
    # text_doc = tk.Text(win, height=16, font=font.Font(family='TkFixedFont'))
    text_doc = tk.Text(win, height=18/SCALE, bd=10, font="-size {:d}".format(int(12*SCALE)))
    text_doc.pack(fill='x', padx=5, pady=5, ipadx=5, ipady=5)
    text_doc.insert(tk.END, doc)
    text_doc.config(state=tk.DISABLED)
    text_doc.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=text_doc.yview)

    # input1
    if USE_ENTER:
        input1 = tk.Entry(win, font="-size {:d}".format(int(16*SCALE)), justify='center')
    else:
        input1 = tk.Text(win, height=3, font="-size 16")
        input1.pack(fill='x', padx=5)

    # error message
    # row0 = tk.Label(win, text="", anchor='center', )
    row0 = tk.Label(win, text="Outputs:", anchor='w', justify='left', font="-size {:d}".format(int(12*SCALE)))

    # four rows for output

    fontbig = "-size {:d}".format(int(16*SCALE))
    fontnormal = "-size {:d}".format(int(12*SCALE))
    out_justify = 'center'

    row_cgs = tk.Frame(win)
    lab_cgs = tk.Label(row_cgs, width=10, text='CGS', anchor='e', font=fontnormal)
    out_cgs = tk.Label(row_cgs, anchor='w', padx=20, font=fontbig)

    row_si = tk.Frame(win)
    lab_si = tk.Label(row_si, width=10, text='SI', anchor='e',
                      justify='center', font=fontnormal)
    out_si = tk.Label(row_si, anchor='w', padx=20, font=fontbig)

    row_user = tk.Frame(win)
    ent_user = tk.Entry(row_user, width=10, justify='center', font=fontnormal)
    out_user = tk.Label(row_user, anchor='w', padx=20, font=fontbig)

    def evaluate_user(event):
        unit = ent_user.get()
        if unit == '':
            out_user.config(text="", fg='black')
            return
        f_fmt = '{{:.{}e}}'.format(DIGITS-1) if IS_SCI else '{}'
        if type(Ret) is int:
            out_user.config(text=Ret, fg='black')
        # elif type(Ret) in [float, np.float, np.float64]:
        elif type(Ret) is float:
            out_user.config(text=f_fmt.format(Ret), fg='black')
        else:
            try:
                if unit in UNITS_USER:
                    ret_loc = Ret.to(eval(unit))
                else:
                    ret_loc = Ret.to(unit)
                if type(ret_loc) is int:
                    out_user.config(text=ret_loc, fg='black')
                elif type(ret_loc) is float:
                    out_user.config(text=f_fmt.format(ret_loc), fg='black')
                else:
                    out_user.config(text=f_fmt.format(ret_loc.value) + " " +
                                    str(ret_loc._unit), fg='black')
            except UnitConversionError as uce:
                out_user.config(text=uce, fg='red')
            except ValueError as _e:
                out_user.config(text=_e, fg='red')

    # define the calculate function
    def calculate(event=None):
        if USE_ENTER:
            inp = input1.get()
            if inp == "":
                out_cgs.config(text="")
                print("Output (cgs):", "")
                out_si.config(text="")
                out_user.config(text="")
                return
        else:
            if input1.compare("end-1c", "==", "1.0"):
                out_cgs.config(text="")
                print("Output (cgs):", "")
                out_si.config(text="")
                out_user.config(text="")
                return
            inp = input1.get(1.0, tk.END)

        # parse input
        print("Input:", inp)
        with evaluate(False):
            inp_expr = parse_expr(inp, transformations=transformations, evaluate=False)
            inp = str(inp_expr)
        input_parse.config(text=inp)
        # print("Input-paresed:", CustomStrPrinter().doprint(inp_expr))

        # get the results
        global Ret
        error_msg = None
        try:
            Ret = eval(inp)
        except NameError as _ne:
            error_msg = "Error: " + str(_ne)
            # row0.config(text=, fg='red')
            # return
        except SyntaxError as _se:
            error_msg = "Error: " + str(_se)
            # row0.config(text="Error: " + str(_se), fg='red')
            # return
        except Exception as _e:
            error_msg = "Unexpected error: " + str(_e)
            # row0.config(text="Unexpected error: " + str(_e), fg='red')
            # return
        if error_msg is not None:
            out_cgs.config(text="")
            print("Output (cgs):", "")
            out_si.config(text="")
            row0.config(text=textwrap.fill(error_msg, 80), fg='red')
            return

        # Display results
        f_fmt = '{{:.{}e}}'.format(DIGITS-1) if IS_SCI else '{}'
        row0.config(text='Outputs:', fg='black')
        if type(Ret) is int:
            out_cgs.config(text=Ret)
            print("Output (cgs):", Ret)
            out_si.config(text=Ret)
        # elif type(Ret) in [float, np.float, np.float64]:
        elif type(Ret) is float:
        # if type(Ret) in [float, int]:
            # out1.config(text=str(Ret))
            out_cgs.config(text=f_fmt.format(Ret))
            print("Output (cgs):", f_fmt.format(Ret))
            out_si.config(text=f_fmt.format(Ret))
        else:                       # is astropy stuff
            # SI
            if type(Ret.si) is Quantity:
                out_si.config(text=f_fmt.format(Ret.si))
            # if type(Ret.si) is CompositeUnit:
            #     # TODO: sci here. Seems impossible to work
            #     out_si.config(text=Ret.si)
            else:
                # out_si.config(text=f_fmt.format(Ret.si.value) + ' ' + str(Ret.si._unit))
                out_si.config(text=Ret.si)
            # CGS
            try:
                if type(Ret.cgs) is CompositeUnit:
                    # TODO: sci here. Seems impossible to work
                    out_cgs.config(text=Ret.cgs)
                    print("Output (cgs):", Ret.cgs)
                else:
                    # out1.config(text="{} {}".format(Ret.value, Ret._unit))
                    _text = f_fmt.format(Ret.cgs.value) + ' ' + str(Ret.cgs._unit)
                    out_cgs.config(text=_text)
                    print("Output (cgs):", _text)
                # out_cgs.config(text=str(Ret.cgs))
            except Exception as _e:
                row0.config(text=textwrap.fill(str(_e), 80), fg='red')
        evaluate_user(None)

    def sci_switch():
        global IS_SCI
        IS_SCI = sci.get()
        calculate()

    if USE_ENTER:
        input1.bind("<Return>", calculate)
        input1.pack(fill='x', padx=5, pady=5, ipady=16)

    # calculate button
    sci = tk.IntVar()
    row_cal = tk.Frame(win)
    row_cal.pack(fill='x', padx=5, pady=5)
    if not USE_ENTER:
        tk.Button(row_cal, text="Calculate", command=calculate).pack(side='top')
    tk.Checkbutton(row_cal, text='Scientific', variable=sci,
                   onvalue=1, font="-size {:d}".format(int(12*SCALE)), offvalue=0,
                   command=sci_switch).pack(side='right')

    input_fm = tk.Frame(win)
    input_lab = tk.Label(input_fm, width=14, text='Python input:',
                         anchor='w', font="-size {:d}".format(int(12*SCALE)))
    input_parse = tk.Label(input_fm, justify='center', anchor='w',
                           font="-size {:d}".format(int(12*SCALE)))
    input_fm.pack(fill='x', padx=5, pady=5)
    input_lab.pack(side='left')
    input_parse.pack(side='right', expand=1, fill='x')

    # display parsed input

    # pack error message
    row0.pack(fill='both', padx=5, pady=6)

    # pack the four rows

    row_cgs.pack(fill='x', padx=5, pady=5)
    lab_cgs.pack(side='left')
    out_cgs.pack(side='right', expand=1, fill='x')

    row_si.pack(fill='x', padx=5, pady=5)
    lab_si.pack(side='left')
    out_si.pack(side='right', expand=1, fill='x')

    row_user.pack(fill='x', padx=5, pady=5)
    ent_user.bind("<Return>", evaluate_user)
    ent_user.pack(side='left', ipady=4)
    out_user.pack(side='right', expand=1, fill='x')

    win.mainloop()


if __name__ == "__main__":

    from astropy.units.core import UnitConversionError, CompositeUnit
    from astropy.units.quantity import Quantity
    import tkinter as tk
    # from tkinter.filedialog import askdirectory
    import textwrap
    from sympy import evaluate
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, \
        implicit_multiplication, convert_xor

    # try:
    #     main()
    # except Exception as uncaught:
    #     print(uncaught)
    main()
