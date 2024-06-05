import configparser
from datetime import datetime
from flask import Flask, render_template

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.debug = config.getboolean('FLASK', 'Debug')

@app.route('/')
def home():
    config_text = config.get('HOME', 'Text')  # Replace 'HOME' and 'Text' with the actual section and option names
    return render_template('home.html')

@app.route('/schedule')
def schedule():
    djs = {key: value.split(', ') for key, value in config.items('DJ SCHEDULE')}
    now = datetime.now().time()
    current_dj = next((dj for dj, (time, genre, soundcloud, instagram) in djs.items() if datetime.strptime(time, '%I:%M %p').time() <= now), None)
    progress = len([dj for dj, (time, genre, soundcloud, instagram) in djs.items() if datetime.strptime(time, '%I:%M %p').time() <= now]) / len(djs)
    return render_template('schedule.html', djs=djs, current_dj=current_dj, progress=progress)

@app.route('/location')
def location():
    return render_template('location.html')

@app.route('/drinks')
def drinks():
    drinks = {key: value for key, value in config.items('DRINKS')}
    return render_template('drinks.html', drinks=drinks)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)