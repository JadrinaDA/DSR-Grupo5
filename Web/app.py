from flask import Flask, render_template, request, jsonify

import numpy as np
from flask_socketio import SocketIO, send
from engineio.payload import Payload

from modelo import *
from simulacion2 import *

import threading


app = Flask(__name__)
Payload.max_decode_packets = 500
socketio = SocketIO(app, cors_allowed_origins='*')

ref = np.array([100.0, 100.0])

kp_l = 0.01
ki_l = 0.0
kd_l = 0.0
kp_a = 1.0
ki_a = 0.0
kd_a = 0.0

botin = BaseMovil()
cont = MobileBasePID(botin, ref, kp_l, kd_l, ki_l, kp_a, kd_a, ki_a)

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
            cont.update()
            botin.UpdateState()

    # botin.SetActuator([1.0, 0.5])
    
    simulation = threading.Thread(target=run_simulation)
    simulation.start()
    return render_template("Simulacion/simulacion_base_movil.html")

@app.route("/setGoal/<x>/<y>")
def set_goal(x,y):
    if request.method == 'GET':
        x = float(x)
        y = float(y)
        cont.set_reference(x,y)
        message = f'Goal set in ({x},{y})'
        return jsonify(message)  # serialize and use JSON headers
    # POST request
    if request.method == 'POST':
        print(request.get_json())  # parse as JSON
        return 'Sucesss', 200
    

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