from flask import Flask, render_template

import numpy as np
from flask_socketio import SocketIO, send
from engineio.payload import Payload

from modelo import *
from simulacion2 import *

import threading


app = Flask(__name__)
Payload.max_decode_packets = 500
socketio = SocketIO(app, cors_allowed_origins='*')

botin = BaseMovil()


@app.route("/")
def index():
    return render_template("inicio/pagina_inicio.html")

@app.route("/main")
def main():
    return render_template("pagina_principal/info_lab.html")

@app.route("/login")
def login():
    return render_template("login/index.html")

@app.route("/exp")
def exper():
    return render_template("pagina_exp/exp.html")

@app.route("/reg")
def reg():
    return render_template("registro/main.html")

@app.route("/res")
def res():
    return render_template("reserva_horas/reserva.html")

@app.route("/sim")
def sim():
    return render_template("Simulacion/simulacion_base_movil.html")

@app.route("/cuenta")
def perfil():
    return render_template("perfil/datos_personales.html")

@app.route("/sim/run")
def sim_run():
    def run_simulation():
        print("Corriendo Sim")
        botin.SetState([0,0,0,0,0])
        while(1):
            state = botin.GetSensor()
            error_previo[:] = error_actual[:]
            error_actual[:] = error(ref, state)
            error_acumulado[:] = error_acumulado[:] + error_actual[:]
            PID(botin, error_actual, error_previo, kp_lineal, kd_lineal, ki_lineal, kp_angular, kd_angular, ki_angular)
            botin.UpdateState()

    ref = np.array([100.0, 100.0])

    kp_lineal = 0.01
    ki_lineal = 0.0
    kd_lineal = 0.0
    kp_angular = 1.0
    ki_angular = 0.0
    kd_angular = 0.0

    # Errores
    error_actual = np.array([0.0, 0.0])
    error_previo = np.array([0.0, 0.0])
    error_acumulado =  np.array([0.0, 0.0])

    botin.SetActuator([1.0, 0.5])
    simulation = threading.Thread(target=run_simulation)
    simulation.start()
    return render_template("Simulacion/simulacion_base_movil.html")

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

if __name__ == '__main__':
    app.run(debug=True)