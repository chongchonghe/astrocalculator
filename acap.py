#!/usr/bin/env python
""" acap
ACAP, an Awesome Calculator for Astronomers and Physicists.
Author: Chong-Chong He (che1234@umd.edu)
Date: 2020-06-20

A calculator written in python with GUI.
"""

from math import *
from astropy import units as U
from astropy import constants as C
from astropy.constants import *

#========================================================================
# The following variables can be changed by the user
USE_ENTER = 1    # Use <Enter> to calculate instead of 'Calculate' button
DIGITS = 4       # number of significant digits in scientific notations
#========================================================================

# load astropy constants
Units = {
    'Length': ['m', 'cm', 'mm', 'um', 'nm', 'Ang', 'km', 'au', 'pc', 'Mpc', 'lyr',],
    'Mass': ['kg', 'g', 'M_sun'],
    'Density': ['mpcc'],
    'Time': ['s', 'yr', 'Myr', 'Gyr',],
    'Energy': ['J', 'erg', 'eV', 'MeV', 'GeV'],
    'Frequency': ['Hz', 'MHz', 'GHz',],
    'Temperature': ['K',],
    }
_unit_extra = ['Ang', 'mpcc']
_unit_skip = ['au', 'pc', 'M_sun']
# Extra
for _key in Units.keys():
    for _unit in Units[_key]:
        if _unit in _unit_extra or _unit in _unit_skip:
            continue
        locals()[_unit] = eval("U.{}".format(_unit))
Ang = 0.1 * nm
mpcc = m_p / cm**3

IS_SCI = 0

# from sympy.printing.str import StrPrinter
# class CustomStrPrinter(StrPrinter):
#     def _print_Float(self, expr):         
#         return '{:.3e}'.format(expr)

def main():

    transformations = standard_transformations + (implicit_multiplication,) + (convert_xor,)

    win = tk.Tk()
    win.title("ACAP")
    win.geometry('600x660')

    # Documentation
    doc = \
        "Welcome to ACAP, an Awesome Calculator for Astronomers and Physicists!\n"\
        "Author: Chong-Chong He (che1234@umd.edu)\n"\
        "\n"\
        "Type in the expression you want to evaluate in the box blow and "\
        "{}. ".format("press <Enter>" if USE_ENTER else "click 'Calculate'") +\
        "The box in the bottom left corner can be used to express the output in any units.\n"\
        "\n"\
        "Example input: \n"\
        "    4 pc\n"\
        "    (G M_sun / au)^.5\n"\
        "    m_p c^2 / k_B\n"\
        "    e.esu^2 / (0.1 nm)^2\n"\
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
    text_doc = tk.Text(win, height=18, bd=10)
    text_doc.pack(fill='x', padx=5, pady=5, ipadx=5, ipady=5)
    text_doc.insert(tk.END, doc)
    text_doc.config(state=tk.DISABLED)
    text_doc.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=text_doc.yview)

    # top text
    # text_top_text = "Type in the expression you want to evaluate and " \
    #     "{}.\n".format("press <Enter>" if USE_ENTER else "click 'Calculate'") + \
    #     "e.g. 4 * pc, (G * M_sun / au)^.5, m_p * c^2 / k_B, e.esu^2 / (0.1 * nm)^2"
    # text_top = tk.Label(win,
    #                     text=text_top_text,
    #                     anchor='w',
    #                     justify='left')
    # text_top.pack(fill='both', padx=5, pady=6)

    # input1
    if USE_ENTER:
        input1 = tk.Entry(win, font="-size 16", justify='center')
    else:
        input1 = tk.Text(win, height=3, font="-size 16")
        input1.pack(fill='x', padx=5)

    # error message
    # row0 = tk.Label(win, text="", anchor='center', )
    row0 = tk.Label(win, text="Outputs:", anchor='w', justify='left')

    # four rows for output

    # row1 = tk.Frame(win)
    # lab1 = tk.Label(row1, width=10, text='Raw', anchor='center')
    # out1 = tk.Label(row1, text='alkdjfl adlkf aslkdfjalksdjflaksdjf lasdjf l', anchor='w')

    out_justify = 'center'

    row_cgs = tk.Frame(win)
    lab_cgs = tk.Label(row_cgs, width=10, text='CGS', anchor='e', ) #font="-size 16")
    out_cgs = tk.Label(row_cgs, anchor='w', padx=20, font="-size 16", justify=out_justify)

    row_si = tk.Frame(win)
    lab_si = tk.Label(row_si, width=10, text='SI', anchor='e', justify='center', ) #font="-size 16")
    out_si = tk.Label(row_si, anchor='w', padx=20, font="-size 16", justify='center')

    row_user = tk.Frame(win)
    ent_user = tk.Entry(row_user, width=10, justify='center') #font="-size 16")
    out_user = tk.Label(row_user, anchor='w', padx=20, font="-size 16", justify=out_justify)

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
        # print("Input:", inp, end='\t')
        # print(type(inp))
        print("Input:", inp)
        # inp = inp.replace('^', '**')
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
    tk.Checkbutton(row_cal, text='Scientific', variable=sci, onvalue=1,
                offvalue=0, command=sci_switch).pack(side='right')

    input_fm = tk.Frame(win)
    input_lab = tk.Label(input_fm, width=12, text='Python input:', anchor='w')
    input_parse = tk.Label(input_fm, justify='center', anchor='w')
    input_fm.pack(fill='x', padx=5, pady=5)
    input_lab.pack(side='left')
    input_parse.pack(side='right', expand=1, fill='x')

    # display parsed input

    # pack error message
    # row0.pack(pady=8, )
    row0.pack(fill='both', padx=5, pady=6)

    # pack the four rows

    # row1.pack(fill='x', padx=5, pady=5)
    # lab1.pack(side='left')
    # out1.pack(side='right', expand=1, fill='x')

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

    main()
