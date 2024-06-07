from flask import render_template, request, redirect, url_for, flash, session
from app import app, config, CONFIG_FILE
from utils import ensure_sections, parse_dj_details, allowed_file, save_password
import configparser

@app.route('/config', methods=['GET', 'POST'])
def config_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    ensure_sections()
    editable_sections = ['DJ SCHEDULE', 'DRINKS', 'HOME', 'LOCATION', 'ADMIN']

    if request.method == 'POST':
        try:
            handle_post_request(request, editable_sections)
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
            flash('Configuration updated successfully.')
        except Exception as e:
            flash(f"Error processing request: {e}")
        return redirect(url_for('config_page'))

    context = load_context()
    return render_template('config.html', **context)


def handle_post_request(request, editable_sections):
    action = request.form.get('action')
    if action == 'save':
        save_configurations(request, editable_sections)
    elif action == 'delete':
        delete_configuration(request, editable_sections)
    elif action == 'add-dj':
        add_dj(request)
    elif action == 'add-drink':
        add_drink(request)
    elif action == 'clear':
        clear_configurations()


def save_configurations(request, editable_sections):
    for section in editable_sections:
        if section == 'DJ SCHEDULE':
            update_dj_schedule(request, section)
        elif section == 'DRINKS':
            update_drinks(request, section)
        elif section == 'HOME':
            update_home(request)
        elif section == 'LOCATION':
            update_location(request)
        elif section == 'ADMIN':
            update_admin_password(request)


def update_dj_schedule(request, section):
    djs_to_update = {}
    for key, value in request.form.items():
        if key.startswith(f'{section}-') and '-' in key[len(f'{section}-'):]:
            dj_name, field = key[len(f'{section}-'):].rsplit('-', 1)
            if dj_name not in djs_to_update:
                djs_to_update[dj_name] = parse_dj_details(config.get(section, dj_name).split(', '))
            djs_to_update[dj_name][field] = value
    for dj_name, details in djs_to_update.items():
        config.set(section, dj_name, ', '.join(details.values()))


def update_drinks(request, section):
    drinks_to_update = {}
    for key, value in request.form.items():
        if key.startswith('DRINKS-') and '-' in key[len('DRINKS-'):]:
            drink_name, field = key[len('DRINKS-'):].rsplit('-', 1)
            if drink_name not in drinks_to_update:
                drinks_to_update[drink_name] = config.get(section, drink_name).split(', ')
            if field == 'price':
                drinks_to_update[drink_name][0] = value
            elif field == 'amount':
                if len(drinks_to_update[drink_name]) > 1:
                    drinks_to_update[drink_name][1] = value
                else:
                    drinks_to_update[drink_name].append(value)
    for drink_name, details in drinks_to_update.items():
        config.set(section, drink_name, ', '.join(details))


def update_home(request):
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


def update_location(request):
    location_link = request.form.get('location-link', '')
    config.set('LOCATION', 'link', location_link)


def update_admin_password(request):
    new_password = request.form.get('admin-password', '')
    if new_password:
        save_password(new_password)
        flash('Admin password updated successfully.')


def delete_configuration(request, editable_sections):
    section, key = request.form['delete'].split('-')
    if section in editable_sections:
        config.remove_option(section, key)


def add_dj(request):
    new_dj_name = request.form.get('new-dj-name', '')
    new_dj_time = request.form.get('new-dj-time', '')
    new_dj_genre = request.form.get('new-dj-genre', '')
    new_dj_soundcloud = request.form.get('new-dj-soundcloud', '')
    new_dj_instagram = request.form.get('new-dj-instagram', '')
    dj_details = ', '.join(filter(None, [new_dj_time, new_dj_genre, new_dj_soundcloud, new_dj_instagram]))
    config.set('DJ SCHEDULE', new_dj_name, dj_details)


def add_drink(request):
    new_drink_name = request.form.get('new-drink-name', '')
    new_drink_price = request.form.get('new-drink-price', '')
    new_drink_amount = request.form.get('new-drink-amount', '')
    drink_details = ', '.join(filter(None, [new_drink_price, new_drink_amount]))
    config.set('DRINKS', new_drink_name, drink_details)


def clear_configurations():
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


def load_context():
    dj_config = load_section_config('DJ SCHEDULE', parse_dj_details)
    drinks_config = load_section_config('DRINKS', lambda x: x.split(', '))
    home_text = load_option('HOME', 'text', 'Welcome to our event!')
    home_image = load_option('HOME', 'image', 'event.png')
    location_link = load_option('LOCATION', 'link', '')
    sections = config.sections()
    return {
        'dj_config': dj_config,
        'drinks_config': drinks_config,
        'sections': sections,
        'home_text': home_text,
        'home_image': home_image,
        'location_link': location_link
    }


def load_section_config(section, parse_function):
    try:
        return {key: parse_function(value.split(', ')) for key, value in config.items(section)}
    except configparser.NoSectionError:
        return {}
    except Exception as e:
        flash(f"Error loading {section}: {e}")
        return {}


def load_option(section, option, default):
    try:
        return config.get(section, option)
    except configparser.NoOptionError:
        return default
    except Exception as e:
        flash(f"Error loading {section} {option}: {e}")
        return default
