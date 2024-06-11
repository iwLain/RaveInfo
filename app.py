from flask import Flask
from flask_bcrypt import Bcrypt
import os
import configparser
from collections import OrderedDict

app = Flask(__name__)
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = 'static'
CONFIG_FILE = 'config.ini'
PASSWORD_FILE = 'password.txt'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'supersecretkey'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class PreservingConfigParser(configparser.ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.optionxform = str

    def items(self, section, raw=False, vars=None):
        d = OrderedDict(super().items(section, raw=raw, vars=vars))
        return d.items()

config = PreservingConfigParser()
config.read(CONFIG_FILE)

import views.home_view
import views.schedule_view
import views.location_view
import views.drinks_view
import views.auth_view
import views.config_view
import views.uploaded_file_view
from utils import *

ensure_default_password()
ensure_sections()

@app.context_processor
def inject_ticket_link():
    tickets_link = config.get('TICKETS', 'link', fallback='https://example.com/tickets')
    return dict(tickets_link=tickets_link)

if __name__ == '__main__':
    app.run(debug=True)
