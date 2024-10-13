import sys
import webbrowser
import threading
from flask import Flask, render_template, request
from .calc import execute_calculation  # Updated relative import

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    calculation = ''
    parsed_input = None
    result_si = None
    result_cgs = None
    result_user_units = None
    user_units = None

    if request.method == 'POST':
        calculation = request.form.get('calculation', '')
        user_units = request.form.get('user_units', None)  # Get user-defined units

        # Execute the calculation and get results
        parsed_input, result_si, result_cgs, result_user_units = execute_calculation(calculation, user_units)

    return render_template('index.html', calculation=calculation, parsed_input=parsed_input,
                           result_si=result_si, result_cgs=result_cgs, 
                           result_user_units=result_user_units, user_units=user_units)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

def start_server():
    threading.Timer(1.0, open_browser).start()
    app.run(debug=False, use_reloader=False)

if __name__ == '__main__':
    start_server()
