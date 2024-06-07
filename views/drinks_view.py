from flask import render_template, flash
from app import app, config
from utils import ensure_sections

@app.route('/drinks')
def drinks():
    ensure_sections()
    try:
        drinks = {key: value.split(', ') for key, value in config.items('DRINKS')}
    except configparser.NoSectionError:
        drinks = {}
    except Exception as e:
        flash(f"Error loading drinks: {e}")
        drinks = {}
    return render_template('drinks.html', drinks=drinks)
