from flask import render_template, flash
from app import app, config
from utils import ensure_sections

@app.route('/location')
def location():
    ensure_sections()
    try:
        location_link = config.get('LOCATION', 'link', fallback="")
    except configparser.NoOptionError:
        location_link = ""
    except Exception as e:
        flash(f"Error loading location link: {e}")
        location_link = ""
    return render_template('location.html', location_link=location_link)
