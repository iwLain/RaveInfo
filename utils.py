import os
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import configparser
from collections import OrderedDict
from app import app, config, PASSWORD_FILE, CONFIG_FILE

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
bcrypt = Bcrypt(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_password(password):
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    with open(PASSWORD_FILE, 'w') as f:
        f.write(hashed)

def check_password(password):
    try:
        with open(PASSWORD_FILE, 'r') as f:
            hashed = f.read()
        return bcrypt.check_password_hash(hashed, password)
    except FileNotFoundError:
        return False

def parse_dj_details(details):
    parsed = {'time': '', 'genre': '', 'soundcloud': '', 'instagram': ''}
    if len(details) > 0:
        parsed['time'] = details[0]
    if len(details) > 1:
        parsed['genre'] = details[1]
    if len(details) > 2:
        parsed['soundcloud'] = details[2]
    if len(details) > 3:
        parsed['instagram'] = details[3]
    return parsed

def ensure_sections():
    sections = ['FLASK', 'DJ SCHEDULE', 'DRINKS', 'HOME', 'LOCATION', 'TICKETS', 'ADMIN']
    for section in sections:
        if section not in config.sections():
            config.add_section(section)
    if 'text' not in config['HOME']:
        config.set('HOME', 'text', 'Welcome to our event!')
    if 'image' not in config['HOME']:
        config.set('HOME', 'image', 'event.png')
    if 'link' not in config['LOCATION']:
        config.set('LOCATION', 'link', '')
    if 'link' not in config['TICKETS']:
        config.set('TICKETS', 'link', 'https://example.com/tickets')
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def ensure_default_password():
    if not os.path.exists(PASSWORD_FILE):
        save_password('rave24')
