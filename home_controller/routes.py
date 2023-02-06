'''
Flask routes for the watering_controller
'''

from flask import render_template # pylint: disable=import-error
from home_controller import app

# --- ROUTES ---
@app.route('/')
@app.route('/index')
def homepage():
    '''
    Homepage page
    '''
    return render_template('index.html')

from .watering_controller import routes as watering_controller_routes
from .water_flow_sensor import routes as water_flow_sensor_routes
