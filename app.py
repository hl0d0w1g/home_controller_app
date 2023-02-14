'''
Watering controller app
'''
import sys

from home_controller import app, socketio

sys.path.insert(0, './home_controller/watering_controller')
sys.path.insert(0, './home_controller/water_flow_sensor')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
