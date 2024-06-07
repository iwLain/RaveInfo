from flask import render_template, request, redirect, url_for, flash, session
from app import app, config
from utils import ensure_sections, parse_dj_details, allowed_file, save_password

@app.route('/config', methods=['GET', 'POST'])
def config_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    ensure_sections()
    editable_sections = ['DJ SCHEDULE', 'DRINKS', 'HOME', 'LOCATION', 'ADMIN']  # Include 'ADMIN' in editable sections
    if request.method == 'POST':
        if 'save' in request.form:
            try:
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
                    elif section == 'HOME':
                        home_text = request.form.get('home-text', 'Welcome to our event!')
                        config.set('HOME', 'text', home_text)
                        if 'home-image' in request.files:
                            file = request.files['home-image']
                            if file and allowed_file(file.filename):
                                filename = secure_filename(file.filename)
                                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                                config.set('HOME', 'image', filename)
                                flash('Image successfully uploaded and displayed below')
                            else:
                                flash('Allowed image types are - png, jpg, jpeg, gif')
                    elif section == 'LOCATION':
                        location_link = request.form.get('location-link', '')
                        config.set('LOCATION', 'link', location_link)
                    elif section == 'ADMIN':
                        new_password = request.form.get('admin-password', '')
                        if new_password:
                            save_password(new_password)
                            flash('Admin password updated successfully.')
                with open(CONFIG_FILE, 'w') as configfile:
                    config.write(configfile)
            except Exception as e:
                flash(f"Error saving configuration: {e}")
        elif 'delete' in request.form:
            try:
                section, key = request.form['delete'].split('-')
                if section in editable_sections:  # Only allow deleting from editable sections
                    config.remove_option(section, key)
                    with open(CONFIG_FILE, 'w') as configfile:
                        config.write(configfile)
            except Exception as e:
                flash(f"Error deleting item: {e}")
        elif 'add-dj' in request.form:
            try:
                new_dj_name = request.form.get('new-dj-name', '')
                new_dj_time = request.form.get('new-dj-time', '')
                new_dj_genre = request.form.get('new-dj-genre', '')
                new_dj_soundcloud = request.form.get('new-dj-soundcloud', '')
                new_dj_instagram = request.form.get('new-dj-instagram', '')
                dj_details = ', '.join(filter(None, [new_dj_time, new_dj_genre, new_dj_soundcloud, new_dj_instagram]))
                config.set('DJ SCHEDULE', new_dj_name, dj_details)
                with open(CONFIG_FILE, 'w') as configfile:
                    config.write(configfile)
            except Exception as e:
                flash(f"Error adding DJ: {e}")
        elif 'add-drink' in request.form:
            try:
                new_drink_name = request.form.get('new-drink-name', '')
                new_drink_price = request.form.get('new-drink-price', '')
                new_drink_amount = request.form.get('new-drink-amount', '')
                drink_details = ', '.join(filter(None, [new_drink_price, new_drink_amount]))
                config.set('DRINKS', new_drink_name, drink_details)
                with open(CONFIG_FILE, 'w') as configfile:
                    config.write(configfile)
            except Exception as e:
                flash(f"Error adding drink: {e}")
        elif 'clear' in request.form:
            try:
                config.clear()
                config.add_section('FLASK')
                config.set('FLASK', 'debug', 'True')
                config.add_section('DJ SCHEDULE')
                config.add_section('DRINKS')
                config.add_section('HOME')
                config.set('HOME', 'text', 'Welcome to our event!')
                config.set('HOME', 'image', 'event.png')
                config.add_section('LOCATION')
                config.set('LOCATION', 'link', '')
                with open(CONFIG_FILE, 'w') as configfile:
                    config.write(configfile)
            except Exception as e:
                flash(f"Error clearing configuration: {e}")
        return redirect(url_for('config_page'))
    else:
        try:
            dj_config = {key: parse_dj_details(value.split(', ')) for key, value in config.items('DJ SCHEDULE')}
        except configparser.NoSectionError:
            dj_config = {}
        except Exception as e:
            flash(f"Error loading DJ schedule: {e}")
            dj_config = {}

        try:
            drinks_config = {key: value.split(', ') for key, value in config.items('DRINKS')}
        except configparser.NoSectionError:
            drinks_config = {}
        except Exception as e:
            flash(f"Error loading drinks: {e}")
            drinks_config = {}

        try:
            home_text = config.get('HOME', 'text')
        except configparser.NoOptionError:
            home_text = 'Welcome to our event!'
        except Exception as e:
            flash(f"Error loading home text: {e}")
            home_text = 'Welcome to our event!'

        try:
            home_image = config.get('HOME', 'image', fallback="event.png")
        except Exception as e:
            flash(f"Error loading home image: {e}")
            home_image = "event.png"

        try:
            location_link = config.get('LOCATION', 'link', fallback="")
        except Exception as e:
            flash(f"Error loading location link: {e}")
            location_link = ""

        sections = config.sections()  # Fetch the sections from the config
        return render_template('config.html', dj_config=dj_config, drinks_config=drinks_config, sections=sections, home_text=home_text, home_image=home_image, location_link=location_link)
