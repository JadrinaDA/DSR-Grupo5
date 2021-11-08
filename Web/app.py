from flask import Flask, render_template, request, jsonify

import numpy as np
from flask_socketio import SocketIO, send
from engineio.payload import Payload

from modelo import BaseMovil
from simulacion2 import MobileBasePID, Simulacion

import threading

import sqlite3
from flask import Flask, render_template, url_for, flash, redirect

import paho.mqtt.client as mqtt
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def send_message(message):
    client.connect('broker.mqttdashboard.com', 1883, 60)
    client.publish('DSR5/1', message)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
Payload.max_decode_packets = 500
socketio = SocketIO(app, cors_allowed_origins='*')
simulation_list = []


ref = np.array([0.0, 0.0])

client = mqtt.Client()
client.connect('broker.mqttdashboard.com', 1883, 60)


kp_l = 0.0 # 0.01
ki_l = 0.0
kd_l = 0.0
kp_a = 0.0 # 1.0
ki_a = 0.0
kd_a = 0.0

botin = BaseMovil()
cont = MobileBasePID(botin, ref, kp_l, kd_l, ki_l, kp_a, kd_a, ki_a)

@app.route("/")
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()
    return render_template("inicio/pagina_inicio.html", users = users)

@app.route("/main")
def main():
    return render_template("pagina_principal/info_lab.html")

@app.route("/login")
def login():
    return render_template("login/index.html")

@app.route("/exp")
def exper():
    return render_template("pagina_exp/exp.html")

@app.route("/reg", methods=('GET', 'POST'))
def reg():
    if request.method == 'POST':
        is_robot = 0 #int((request.form['major'] == 'rob'))
        name = request.form['name'] + " " + request.form['last_name'] 
        conn = get_db_connection()
        conn.execute("INSERT INTO usuarios (name, mail, password, tipo, robotica) VALUES (?, ?, ?, ?, ?)",
            (name, request.form['email'],
             request.form['psw'], 'alumno', is_robot))
        conn.commit()
        conn.close()
        return redirect(url_for('main'))

    return render_template("registro/main.html")

@app.route("/res")
def res():
    return render_template("reserva_horas/reserva.html")

@app.route("/cuenta")
def perfil():
    return render_template("perfil/datos_personales.html")

@app.route("/sim")
def sim():
    print("entre a sim run")
    
    global simulation_list
    if simulation_list != []:
        print(f"simulation_list: {simulation_list}")
        simulation_list[0].stop()
    simulation = Simulacion(botin, cont)
    simulation.start()
    print("Sigo paralelo al thread")
    simulation_list.append(simulation)
    return render_template("Simulacion/simulacion_base_movil.html")

@app.route('/set_constants/<kp_l>/<kd_l>/<ki_l>/<kp_a>/<kd_a>/<ki_a>')
def set_constants(kp_l,kd_l,ki_l,kp_a,kd_a,ki_a):
    if request.method == 'GET':
        kp_l=float(kp_l)
        kd_l=float(kd_l)
        ki_l=float(ki_l)
        cont.set_linear_constants(kp_l,kd_l,ki_l)
        kp_a=float(kp_a)
        kd_a=float(kd_a)
        ki_a=float(ki_a)
        cont.set_angular_constants(kp_a,kd_a,ki_a)
        print(f"Constantes recibidas: {kp_l}, {kd_l}, {ki_l}")
        message = f'Constants set in ({kp_l},{kd_l}, {ki_l})'
        return jsonify(message)  # serialize and use JSON headers
    # POST request
    if request.method == 'POST':
        print(request.get_json())  # parse as JSON
        return 'Sucesss', 200
    

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


@app.route('/speed-index')
def speed_index():
    return render_template('speed/index.html')

@app.route('/speed', methods=['post', 'get'])
def speed():
    m1_speed = request.args.get('m1')
    m2_speed = request.args.get('m2')
    send_message(f"{m1_speed}{m2_speed}000")
    return render_template('speed/speed.html')

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

@app.route("/cuenta/exp")
def exps():
    return render_template("perfil/historial_experiencias.html")

if __name__ == '__main__':
    app.run(debug=True)


