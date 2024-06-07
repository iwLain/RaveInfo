from flask import render_template, flash
from app import app, config
from utils import ensure_sections

@app.route('/')
def home():
    ensure_sections()
    try:
        config_text = config.get('HOME', 'text')
    except configparser.NoOptionError:
        config_text = "Welcome to our event!"
    try:
        image_path = config.get('HOME', 'image')
    except configparser.NoOptionError:
        image_path = "event.png"
    except Exception as e:
        flash(f"Error loading image: {e}")
        image_path = "event.png"
    return render_template('home.html', config_text=config_text, image_path=image_path)
