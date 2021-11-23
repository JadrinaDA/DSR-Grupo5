from flask import Flask, render_template, request, jsonify, session
from flask_session import Session

import numpy as np
from flask_socketio import SocketIO, send
from engineio.payload import Payload

from werkzeug.exceptions import abort


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

from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user(id_user):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM usuarios WHERE id = ?',
                        (id_user,)).fetchone()
    conn.close()
    if user is None:
        abort(404)
    return user

def get_changes(user, form):
    new = {}
    for x in form.keys():
        print(x)
        if x == "major":
            if form[x] == "robotica":
                new['robotica'] = 1
            else:
                new['robotica'] = 0
        elif form[x]:
            new[x] = form[x]
        else:
            new[x] = user[x]
    return new
       
def send_message(message):
    client.connect('broker.mqttdashboard.com', 1883, 60)
    client.publish('DSR5/1', message)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


Payload.max_decode_packets = 500
socketio = SocketIO(app, cors_allowed_origins='*')
simulation_list = []


ref = np.array([0.0, 0.0])

client = mqtt.Client()
#client.connect('broker.mqttdashboard.com', 1883, 60)


kp_l = 0.0 # 0.01
ki_l = 0.0
kd_l = 0.0
kp_a = 0.0 # 1.0
ki_a = 0.0
kd_a = 0.0

horas = ["8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00","17:00","18:00"]

@app.route("/")
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()
    return render_template("inicio/pagina_inicio.html", users = users)

@app.route("/main")
def main():
    id_user = session["user_id"]
    usuario = get_user(id_user)
    full_date = datetime.now().strftime("%d/%m/%Y %H").split(" ")
    hoy = full_date[0]
    if hoy[0] == "0":
        hoy = hoy[1:]
    ahora = full_date[1] +":00"
    conn = get_db_connection()
    tiene_hora  = conn.execute('SELECT * FROM reservas WHERE id_user = ? AND fecha = ? AND hora = ?', (id_user, hoy, ahora,)).fetchone()
    week = conn.execute('SELECT * FROM reservas WHERE id_user = ?',
                        (id_user,)).fetchall()
    print(tiene_hora)
    if week:
        week = week[0:3]
    conn.close()
    return render_template("pagina_principal/info_lab.html", now = tiene_hora, week = week)

@app.route("/login", methods = ['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        mail = request.form['email']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE mail = ?',
                        (mail,)).fetchone()
        conn.close()
        if user is None:
            error = 'Correo no registrado'
        else:
            if user['password'] == request.form["password"]:
                session['user_id'] = user["id"]
                return redirect("/main")
            else:
                error = 'Contraseña incorrecta'
    return render_template("login/index.html", error = error)

@app.route("/exp")
def exper():
    conn = get_db_connection()
    exp = conn.execute('SELECT * FROM experiencias WHERE id = ?',
                        (1,)).fetchone()
    conn.close()
    return render_template("pagina_exp/exp.html", exp = exp)

@app.route("/reg", methods=('GET', 'POST'))
def reg():
    if request.method == 'POST':
        uni = request.form['inst']
        if (uni == "UC" and request.form['carrera'] == "ing"):
            is_robot = int((request.form['major'] == 'robotica'))
        else:
            is_robot = 0
        conn = get_db_connection()
        conn.execute("INSERT INTO usuarios (name, lastname, mail, password, tipo, inst, carrera, robotica) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (request.form['name'], request.form['lastname'], request.form['email'],
             request.form['psw'], request.form['cargo'], uni, request.form["carrera"], is_robot))
        conn.commit()
        user = conn.execute('SELECT * FROM usuarios WHERE mail = ?',
                        (request.form['email'],)).fetchone()
        conn.close()
        session['user_id'] = user["id"]
        return redirect(url_for('main'))

    return render_template("registro/main.html")

@app.route("/res", methods =('GET', 'POST'))
def res():
    user_id = session["user_id"]
    full_date = datetime.now().strftime("%d/%m/%Y %H:%M").split(" ")
    hoy = full_date[0]
    if hoy[0] == "0":
        hoy = hoy[1:]
        

    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('INSERT INTO reservas (id_user, id_exp, fecha, hora) VALUES (?, ?, ?, ?)',
         (user_id, request.form['id_exp'], request.form['dia'], request.form['hora']))
        conn.commit()
        conn.close()
        return redirect(url_for('exps'))

    conn = get_db_connection()
    taken = conn.execute('SELECT hora FROM reservas WHERE fecha = ?', (hoy, )).fetchall()
    conn.close()
    available = horas
    for hora in taken:
        available.remove(hora["hora"])
    return render_template("reserva_horas/reserva.html", ava = available)


@app.route("/cuenta", methods=('GET', 'POST'))
def perfil():
    user = get_user(session["user_id"])

    if request.method == 'POST':
        new = get_changes(user, request.form)
        conn = get_db_connection()
        conn.execute('UPDATE usuarios SET name = ?, lastname = ?, mail = ?,'
         ' tipo = ?, inst = ?, carrera = ?, robotica = ? WHERE mail = ?',
         (new['name'], new['lastname'], new['mail'], new['tipo'], new['inst'], new['carrera'], new['robotica'], user['mail']))
        conn.commit()
        conn.close()
        return redirect(url_for('main'))

    return render_template("perfil/datos_personales.html", user = user)

@app.route("/sim")
def sim():
    return render_template("Simulacion/simulacion_base_movil.html")

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

@app.route("/cuenta/exp")
def exps():
    user_id = session["user_id"]
    conn = get_db_connection()
    reservas = conn.execute('SELECT * FROM reservas WHERE id_user = ?',
                        (user_id,)).fetchall()
    nomexp = ['Robot PID']
    conn.close()
    return render_template("perfil/historial_experiencias.html", reservas = reservas, nombres_exp = nomexp)

@app.route("/cuenta/del", methods =('POST', ))
def delete():
    id_user = session.get("user_id")
    conn = get_db_connection()
    conn.execute('DELETE FROM usuarios WHERE id = ?', (id_user,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route("/exp_con", methods =('GET', ))
def exp_con():
    id_user = session.get("user_id")
    usuario = get_user(id_user)
    full_date = datetime.now().strftime("%d/%m/%Y %H").split(" ")
    hoy = full_date[0]
    if hoy[0] == "0":
        hoy = hoy[1:]
    ahora = full_date[1] +":00"
    conn = get_db_connection()
    tiene_hora  = conn.execute('SELECT * FROM reservas WHERE id_user = ? AND fecha = ? AND hora = ?', (id_user, hoy, ahora,)).fetchone()
    conn.close()
    if tiene_hora:
        return redirect(url_for('index'))
    else: 
        flash("No tienes reservada esta hora, reserva una aquí.")
        return redirect(url_for('res'))



@app.route("/salir", methods =('POST',))
def salir():
    session['user_id'] = None
    return redirect(url_for('index'))


@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")
        

if __name__ == '__main__':
    app.run(debug=True)


