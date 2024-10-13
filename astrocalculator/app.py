import sys
import webbrowser
import threading
from flask import Flask, render_template, request
from .calc import execute_calculation  # Updated relative import
import gunicorn.app.base
from multiprocessing import cpu_count

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

class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.application = app
        self.options = options or {}
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def start_server():
    options = {
        'bind': '%s:%s' % ('127.0.0.1', '5000'),
        'workers': 1,
    }
    threading.Timer(1.0, open_browser).start()
    StandaloneApplication(app, options).run()

if __name__ == '__main__':
    start_server()
