import configparser
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.debug = config.getboolean('FLASK', 'debug', fallback=True)

def ensure_sections():
    sections = ['DJ SCHEDULE', 'DRINKS', 'HOME']
    for section in sections:
        if section not in config.sections():
            config.add_section(section)
    if 'text' not in config['HOME']:
        config.set('HOME', 'text', 'Welcome to our event!')
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

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

@app.route('/')
def home():
    ensure_sections()
    try:
        config_text = config.get('HOME', 'text')
    except configparser.NoOptionError:
        config_text = "Welcome to our event!"
    return render_template('home.html', config_text=config_text)

@app.route('/schedule')
def schedule():
    ensure_sections()
    try:
        djs = {key: parse_dj_details(value.split(', ')) for key, value in config.items('DJ SCHEDULE')}
    except configparser.NoSectionError:
        djs = {}
    now = datetime.now().time()
    current_dj = next((dj for dj, details in djs.items() if datetime.strptime(details['time'], '%H:%M').time() <= now), None)
    progress = len([dj for dj, details in djs.items() if datetime.strptime(details['time'], '%H:%M').time() <= now]) / len(djs) if djs else 0
    return render_template('schedule.html', djs=djs, current_dj=current_dj, progress=progress)

@app.route('/location')
def location():
    return render_template('location.html')

@app.route('/drinks')
def drinks():
    ensure_sections()
    try:
        drinks = {key: value.split(', ') for key, value in config.items('DRINKS')}
    except configparser.NoSectionError:
        drinks = {}
    return render_template('drinks.html', drinks=drinks)

@app.route('/config', methods=['GET', 'POST'])
def config_page():
    ensure_sections()
    editable_sections = ['DJ SCHEDULE', 'DRINKS']  # Define the sections that can be edited
    if request.method == 'POST':
        if 'save' in request.form:
            for section in editable_sections:  # Only iterate over editable sections
                if section == 'DJ SCHEDULE':
                    djs_to_update = {}
                    for key, value in request.form.items():
                        if key.startswith(f'{section}-') and '-' in key[len(f'{section}-'):]:
                            dj_name, field = key[len(f'{section}-'):].rsplit('-', 1)
                            if dj_name not in djs_to_update:
                                djs_to_update[dj_name] = parse_dj_details(config.get(section, dj_name).split(', '))
                            djs_to_update[dj_name][field] = value
                    for dj_name, details in djs_to_update.items():
                        config.set(section, dj_name, ', '.join([details['time'], details['genre'], details['soundcloud'], details['instagram']]))
                elif section == 'DRINKS':
                    drinks_to_update = {}
                    for key, value in request.form.items():
                        if key.startswith('DRINKS-') and '-' in key[len('DRINKS-'):]:
                            drink_name, field = key[len('DRINKS-'):].rsplit('-', 1)
                            if drink_name not in drinks_to_update:
                                drinks_to_update[drink_name] = config.get(section, drink_name).split(', ')
                            drinks_to_update[drink_name] = list(drinks_to_update[drink_name])
                            if field == 'price':
                                drinks_to_update[drink_name][0] = value
                            elif field == 'amount':
                                if len(drinks_to_update[drink_name]) > 1:
                                    drinks_to_update[drink_name][1] = value
                                else:
                                    drinks_to_update[drink_name].append(value)
                    for drink_name, details in drinks_to_update.items():
                        config.set(section, drink_name, ', '.join(details))
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        elif 'delete' in request.form:
            section, key = request.form['delete'].split('-')
            if section in editable_sections:  # Only allow deleting from editable sections
                config.remove_option(section, key)
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
        elif 'add-dj' in request.form:
            new_dj_name = request.form.get('new-dj-name', '')
            new_dj_time = request.form.get('new-dj-time', '')
            new_dj_genre = request.form.get('new-dj-genre', '')
            new_dj_soundcloud = request.form.get('new-dj-soundcloud', '')
            new_dj_instagram = request.form.get('new-dj-instagram', '')
            dj_details = ', '.join(filter(None, [new_dj_time, new_dj_genre, new_dj_soundcloud, new_dj_instagram]))
            config.set('DJ SCHEDULE', new_dj_name, dj_details)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        elif 'add-drink' in request.form:
            new_drink_name = request.form.get('new-drink-name', '')
            new_drink_price = request.form.get('new-drink-price', '')
            new_drink_amount = request.form.get('new-drink-amount', '')
            drink_details = ', '.join(filter(None, [new_drink_price, new_drink_amount]))
            config.set('DRINKS', new_drink_name, drink_details)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        elif 'clear' in request.form:
            config.clear()
            config.add_section('FLASK')
            config.set('FLASK', 'debug', 'True')
            config.add_section('DJ SCHEDULE')
            config.add_section('DRINKS')
            config.add_section('HOME')
            config.set('HOME', 'text', 'Welcome to our event!')
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        return redirect(url_for('config_page'))
    else:
        # handle GET request here
        # Fetch current config and pass it to your template
        try:
            dj_config = {key: parse_dj_details(value.split(', ')) for key, value in config.items('DJ SCHEDULE')}
            drinks_config = {key: value.split(', ') for key, value in config.items('DRINKS')}
        except configparser.NoSectionError:
            dj_config = {}
            drinks_config = {}
        sections = config.sections()  # Fetch the sections from the config
        return render_template('config.html', dj_config=dj_config, drinks_config=drinks_config, sections=sections)

if __name__ == "__main__":
    app.run()
