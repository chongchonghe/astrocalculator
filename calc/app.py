from flask import Flask, render_template, request
from calc import execute_calculation

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def calculate():
    if request.method == 'POST':
        inp = request.form['calculation']
        # Assume execute_calculation returns a tuple (parsed_input, result_si, result_cgs)
        parsed_input, result_si, result_cgs = execute_calculation(inp)
        return render_template('index.html', parsed_input=parsed_input, result_si=result_si, result_cgs=result_cgs, calculation=inp)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)  # Updated host and port
