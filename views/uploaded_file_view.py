from flask import send_from_directory, flash, redirect, url_for
from app import app

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        flash('File not found.')
        return redirect(url_for('home'))
