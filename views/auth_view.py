from flask import render_template, request, redirect, url_for, flash, session
from app import app
from utils import check_password

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if check_password(password):
            session['logged_in'] = True
            return redirect(url_for('config_page'))
        else:
            flash('Invalid password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('login'))
