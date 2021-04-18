#!/Users/chongchonghe/anaconda3/envs/flask/bin/python

import sys
from flask import Flask, render_template, request
from wtforms import Form, FloatField, validators, StringField, TextAreaField
from calculate import calculate, EvalError

class InputForm(Form):
    I = TextAreaField(
        label="Input:\n", default="",
        validators=[validators.InputRequired()],
    )

try:
    template_name = sys.argv[1]
except IndexError:
    template_name = 'view0'

app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET'])
def index():
    form = InputForm(request.form)
    expr = None
    ret_raw = None
    ret_si = None
    ret_cgs = None
    error = None
    # if request.method == 'POST' and form.validate():
    if form.validate():
        # result = compute(form.A.data, form.b.data, form.w.data, form.T.data)
        # result = form.A.data + form.b.data + form.w.data + form.T.data
        try:
            # result = eval(form.I.data)
            expr, ret_raw, ret_si, ret_cgs = calculate(form.I.data)
        except EvalError as _e:
            error = "Error: " + str(_e)
        except Exception as _e:
            error = "Uncaught error: " + str(_e)

    return render_template(template_name + '.html',
                           form=form, ret_cgs=ret_cgs, ret_si=ret_si, 
                           error=error)

if __name__ == '__main__':
    app.run()
    # app.run(host="127.0.0.1", port=8080, debug=True)
