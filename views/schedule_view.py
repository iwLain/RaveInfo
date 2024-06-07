from flask import render_template, flash
from app import app, config
import pytz
from datetime import datetime
from utils import ensure_sections, parse_dj_details

@app.route('/schedule')
def schedule():
    ensure_sections()
    try:
        djs = {key: parse_dj_details(value.split(', ')) for key, value in config.items('DJ SCHEDULE')}
    except configparser.NoSectionError:
        djs = {}
    except Exception as e:
        flash(f"Error loading DJ schedule: {e}")
        djs = {}

    try:
        berlin_tz = pytz.timezone('Europe/Berlin')
        now = datetime.now(berlin_tz).time()
        current_dj = None
        for dj, details in djs.items():
            dj_time = datetime.strptime(details['time'], '%H:%M').time()
            if dj_time <= now:
                current_dj = dj
        progress = len([dj for dj, details in djs.items() if datetime.strptime(details['time'], '%H:%M').time() <= now]) / len(djs) if djs else 0
    except Exception as e:
        flash(f"Error calculating current DJ: {e}")
        current_dj = None
        progress = 0

    return render_template('schedule.html', djs=djs, current_dj=current_dj, progress=progress)
