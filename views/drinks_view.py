from flask import render_template, flash
from app import app, config
from utils import ensure_sections
import configparser
import re

@app.route('/drinks')
def drinks():
    ensure_sections()
    try:
        drinks = []
        for key, value in config.items('DRINKS'):
            print(f"Key: {key}, Value: {value}")  # Debug print
            if isinstance(value, str):
                details = re.findall(r'([^,]+)', value)
                print(f"Details: {details}")  # Debug print
                if len(details) >= 2:
                    drinks.append({
                        'name': key,
                        'category': details[2].strip() if len(details) > 2 else 'Other',
                        'price': float(details[0].replace('€', '').replace(',', '.').strip()),
                        'amount': details[1].strip() if len(details) > 1 else 'N/A'
                    })
                else:
                    print(f"Not enough details for {key}: {details}")  # Debug print

        # Sort drinks by category first and then by price within each category
        drinks.sort(key=lambda x: (x['category'], x['price']))

        # Group drinks by category
        categories = {}
        for drink in drinks:
            if drink['category'] not in categories:
                categories[drink['category']] = []
            categories[drink['category']].append(drink)
    except configparser.NoSectionError:
        categories = {}
    except Exception as e:
        flash(f"Error loading drinks: {e}")
        categories = {}
    return render_template('drinks.html', categories=categories)
