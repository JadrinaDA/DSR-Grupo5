from flask import Flask, render_template, request, jsonify

import numpy as np
from flask_socketio import SocketIO, send
from engineio.payload import Payload

from modelo import BaseMovil
from simulacion2 import MobileBasePID, Simulacion

import threading

import sqlite3
from flask import Flask, render_template, url_for, flash, redirect, Response

import paho.mqtt.client as mqtt

import base64
import cv2 as cv

import threading

lock = threading.Lock()
frame = np.ones((80, 120, 3), np.uint8)

MQTT_BROKER = 'broker.mqttdashboard.com'
MQTT_RECEIVE = "DSR5/CAM"

def show_camera():
    global frame
    while True:
        print(frame)
        #cv.imshow("Stream", frame)
        # if cv.waitKey(1) & 0xFF == ord('q'):
        #     break

# The callback for when the client receives a CONNACK response from the server.
def cam_on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_RECEIVE)


# The callback for when a PUBLISH message is received from the server.
def cam_on_message(client, userdata, msg):
    global frame
    # Decoding the message
    img = base64.b64decode(msg.payload)
    # converting into numpy array from buffer
    npimg = np.frombuffer(img, dtype=np.uint8)
    # Decode to Original Frame
    frame = cv.imdecode(npimg, 1)

def generate():
    # grab global references to the output frame and lock variables
	global frame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if frame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv.imencode(".jpg", frame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global frame
    # Decoding the message
    img = base64.b64decode(msg.payload)
    # converting into numpy array from buffer
    npimg = np.frombuffer(img, dtype=np.uint8)
    # Decode to Original Frame
    frame = cv.imdecode(npimg, 1)
    print(frame)

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


@app.route('/experiencia_base_movil')
def speed_index():
    return render_template('experiencia_base_movil/index.html')

@app.route('/experiencia_base_movil', methods=['post', 'get'])
def experiencia_base_movil():
    m1_speed = request.args.get('m1')
    m2_speed = request.args.get('m2')
    send_message(f"{m1_speed}{m2_speed}000")
    return render_template('experiencia_base_movil/index.html')

@app.route('/camera', methods=['post', 'get'])
def camera():
    # Abrir pantalla de stream
    send_message('CAM')

    client = mqtt.Client()
    client.on_connect = cam_on_connect
    client.on_message = cam_on_message

    client.connect(MQTT_BROKER)

    # Starting thread which will receive the frames
    client.loop_start()
    # t = threading.Thread(target=show_camera)
    # t.start()
    return render_template('experiencia_base_movil/index.html')

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


@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")
        

if __name__ == '__main__':
    app.run(debug=True)


