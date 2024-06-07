from flask import render_template, flash
from app import app, config
from utils import ensure_sections
import configparser

@app.route('/drinks')
def drinks():
    ensure_sections()
    try:
        drinks = [
            {
                'name': key,
                'category': value.split(', ')[2] if len(value.split(', ')) > 2 else 'Other',
                'price': float(value.split(', ')[0].replace('€', '').replace(',', '.')),
                'amount': value.split(', ')[1] if len(value.split(', ')) > 1 else 'N/A'
            }
            for key, value in config.items('DRINKS')
        ]

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
