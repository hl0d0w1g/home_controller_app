"""
Home app web routes
"""

from flask import render_template # pylint: disable=import-error
from home_controller import app

# --- ROUTES ---
@app.route('/')
@app.route('/index')
def homepage():
    '''
    Homepage template
    '''
    return render_template('index.html')

from .watering_controller import routes as watering_controller_routes
from .water_intake import routes as water_intake_routes
