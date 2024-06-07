from flask import Flask
from flask_bcrypt import Bcrypt
import os
import configparser
from collections import OrderedDict

# Initialize Flask and Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configurations
UPLOAD_FOLDER = 'static'
CONFIG_FILE = 'config.ini'
PASSWORD_FILE = 'password.txt'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size
app.secret_key = 'supersecretkey'

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize ConfigParser
class PreservingConfigParser(configparser.ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.optionxform = str  # Preserve the case of keys

    def items(self, section, raw=False, vars=None):
        d = OrderedDict(super().items(section, raw=raw, vars=vars))
        return d.items()

config = PreservingConfigParser()
config.read(CONFIG_FILE)

# Import views and other components
import views.home_view
import views.schedule_view
import views.location_view
import views.drinks_view
import views.auth_view
import views.config_view
import views.uploaded_file_view  # Ensure this is imported
from utils import *

if not os.path.exists(PASSWORD_FILE):
    save_password('admin')  # Set a default password if none exists
