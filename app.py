import numpy as np
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import pickle
import pandas as pd
from functools import wraps

app = Flask(__name__)

app.secret_key = "2FABF43CA4C11CA916817BB689461"

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
def home():
    if 'logged_in' in session:
        return redirect(url_for('welcome'))
    else:
        return redirect(url_for('login'))

@app.route('/index')
@login_required
def welcome():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'test' or request.form['password'] != 'test':
            error = 'Invalid credentials. Please try again.'
        else:
            session['logged_in'] = True
            # flash('You were just logged in!')
            return redirect(url_for('welcome'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('login'))

@app.route('/predict',methods=['POST', 'GET'])
def predict():
    if request.method=='POST':
        result = request.form

        pkl_file = open('cat', 'rb')
        index_dict = pickle.load(pkl_file)
        new_vector = np.zeros(len(index_dict))

        try:
            new_vector[index_dict['age']] = result['age']
        except:
            pass
        try:
            new_vector[index_dict['sex_' + str(result['sex'])]] = 1
        except:
            pass
        try:
            new_vector[index_dict['bmi']] = result['bmi']
        except:
            pass
        try:
            new_vector[index_dict['children']] = result['children']
        except:
            pass
        try:
            new_vector[index_dict['smoker_' + str(result['smoker'])]] = 1
        except:
            pass
        try:
            new_vector[index_dict['region_' + str(result['region'])]] = 1
        except:
            pass

        model = pickle.load(open('random_forst_model_1.pkl', 'rb'))
        prediction = model.predict(new_vector.reshape(1, -1))

    return render_template('index.html',pred='Expected Bill will be ${:.2f}'.format(prediction[0]))

@app.route('/predict_api',methods=['POST'])
def predict_api():
    data = request.get_json(force=True)
    data_unseen = pd.DataFrame([data])
    prediction = predict_model(model, data=data_unseen)
    output = prediction.Label[0]
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)