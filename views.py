from flask import render_template, request, redirect, url_for, send_from_directory, flash, session
from app import app, config
from utils import *
import pytz
from datetime import datetime

import home_view
import schedule_view
import location_view
import drinks_view
import auth_view
import config_view
