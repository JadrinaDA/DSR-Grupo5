import numpy as np
#from scipy.integrate import odeint
from scipy.integrate import solve_ivp
from functools import partial  # https://docs.python.org/3.6/library/functools.html
                               # required to pass additional parameters to solve_ivp
from flask import Flask 
from flask_socketio import SocketIO, send

from modelo import *
import threading


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app, cors_allowed_origins='*')

@socketio.on('update')
def handleMessage(msg):
    # print("Enviando Mensaje")
    state = botin.GetSensor()
    state_dict = {
        'x': state[0], 
        'y': state[1],
        'theta': state[2]
    }
    send(state_dict, broadcast=True)

def run_simulation():
    # print("Corriendo Sim")
    while(1):
        botin.UpdateState()

def run():
    socketio.run(app)


XMAX = 640
YMAX = 480
ppm = 50                                                    # conversion entre pixeles y metros del sistema
screen = None

state = np.array([0.0, 0.0, 0.0, 0.0, 0.0])

u = np.array([0.0, 0.0])

kp = 0.0
ki = 0.0
kd = 0.0

botin = BaseMovil()
botin.SetActuator([1.0, 0.5])

simulation = threading.Thread(target=run_simulation)

simulation.start()


if __name__ == '__main__':
    socketio.run(app)
