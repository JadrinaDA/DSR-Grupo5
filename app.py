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
import time
import json
import parameters as p

lock = threading.Lock()
whos_there = "N"
frame = np.ones((160, 120, 3), np.uint8)
exp_data = dict()
ard_data = dict()
was_redic = False

MQTT_BROKER = 'broker.mqttdashboard.com'
MQTT_RECEIVE = "DSR5/CAM"
MQTT_CAM = "DSR5/CAM"
MQTT_DATA = "DSR5/DATA"
MQTT_ARD = "DSR5/ARD"
idx_img = 0

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
    client.subscribe([(MQTT_CAM,1) , (MQTT_DATA,1) , (MQTT_ARD, 1)])

# The callback for when a PUBLISH message is received from the server.
def cam_on_message(client, userdata, msg):
    global frame
    global exp_data
    global ard_data
    if msg.topic == MQTT_CAM:
        # idx = int.from_bytes(msg.payload[:2],"little")
        # Decoding the message
        img = base64.b64decode(msg.payload[2:])
        # converting into numpy array from buffer
        npimg = np.frombuffer(img, dtype=np.uint8)
        # Decode to Original Frame
        frame = cv.imdecode(npimg, 1)

    elif msg.topic == MQTT_DATA:
        exp_data = json.loads(msg.payload)
        # print(exp_data)

    elif msg.topic == MQTT_ARD:
        ard_data = json.loads(msg.payload)
        # print(ard_data)

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

def my_teach(id_prof, id_est):
    conn = get_db_connection()
    is_stud = conn.execute('SELECT * FROM estudiante_de WHERE id_est = ? AND id_prof = ?',
                        (id_est, id_prof)).fetchone()
    conn.close()
    if is_stud is None:
        return False
    return True

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
    publisher.connect('broker.mqttdashboard.com', 1883, 60)
    publisher.publish('DSR5/1', message)


app = Flask(__name__)
#CORS(app)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


Payload.max_decode_packets = 500
socketio = SocketIO(app, cors_allowed_origins='*', logger = True)
simulation_list = []

ref = np.array([0.0, 0.0])

publisher = mqtt.Client()
try:
    publisher.connect('broker.mqttdashboard.com', 1883, 60)
except:
    print("No se pudo conectar al MQTT")

cam_client = mqtt.Client()
cam_client.on_connect = cam_on_connect
cam_client.on_message = cam_on_message

cam_client.connect(MQTT_BROKER)

# Starting thread which will receive the frames
cam_client.loop_start()

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
    users = conn.execute('SELECT * FROM estudiante_de').fetchall()
    conn.close()
    print(my_teach(2,3))
    return render_template("inicio/pagina_inicio.html", users = None)

@app.route("/capture")
def capture():
    return render_template("capture.html")

@app.route("/main")
def main():
    if not session:
        return redirect(url_for('index'))
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
    coming_up = []
    if tiene_hora:
        global was_redic
        was_redic = True
    dia_h, mes_h, año_h = hoy.split("/")
    for res in week:
        dia_r, mes_r, año_r = res['fecha'].split("/")
        hora_r = int(res['hora'].split(":")[0])
        if ((dia_r >= dia_h) & (mes_r >= mes_h) & (año_r >= año_h)):
            if ((dia_r == dia_h) and (hora_r < int(full_date[1]))):
                continue
            coming_up.append(res)
    conn.close()
    return render_template("pagina_principal/info_lab.html", now = tiene_hora, week = coming_up)

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
                session['time_con'] = -1
                return redirect("/main")
            else:
                error = 'Contraseña incorrecta'
    return render_template("login/index.html", error = error)

@app.route("/exp")
def exper():
    if not session:
        return redirect(url_for('index'))
    if session['time_con'] != -1:
        hour_n, min_n, sec_n = datetime.now().strftime("%H:%M:%S").split(':')
        hour_c, min_c, sec_c = session['time_con'].split(':')
        if int(hour_n) > int(hour_c):
            session['time_con'] = -1
    global whos_there
    if whos_there != "N":
        whos_there = "N"
    conn = get_db_connection()
    exp = conn.execute('SELECT * FROM experiencias WHERE id = ?',
                        (1,)).fetchone()
    conn.close()
    return render_template("pagina_exp/exp.html", exp = exp)

@app.route("/reg", methods=('GET', 'POST'))
def reg():
    if request.method == 'POST':
        errors = []
        if request.form['psw'] != request.form['psw-repeat']:
            errors.append('Las contraseñas no coinciden.')
        if 'cargo' not in request.form.keys() or 'inst' not in request.form.keys():
            errors.append('Seleccione un cargo e institución.')
        elif 'inst' in request.form.keys() and 'cargo' in request.form.keys():
            if 'carrera' not in request.form.keys() and request.form['cargo'] == 'alumno' and request.form['inst'] == "UC":
                errors.append('Seleccione una carrera.')
            elif 'carrera' in request.form.keys():
                if 'major' not in request.form.keys() and request.form['inst'] == "UC" and request.form['carrera'] == "ing":
                  errors.append('Seleccione un major.')  
        if len(request.form['psw']) < 6:
            errors.append('Contraseña debe ser mínimo 6 caracteres.')
        conn = get_db_connection()
        user_old = conn.execute('SELECT * FROM usuarios WHERE mail = ?',
                        (request.form['email'],)).fetchone()
        if (('@' not in request.form['email']) or ('.cl' not in request.form['email']) & ('.com' not in request.form['email'])) :
            errors.append('Correo no es valido.')
        elif user_old != None:
            errors.append('Correo no es valido.')
        if len(errors) > 0:
            conn.close()
            return render_template("registro/main.html", errors = errors) 
        if (request.form['cargo'] == "profesor"):
            carrera = "profe"
        elif (request.form['cargo'] == "otro"):
            carrera = "otro"
        else:
            carrera = request.form['carrera']
        uni = request.form['inst']
        if (uni == "UC" and carrera == "ing"):
            is_robot = int((request.form['major'] == 'robotica'))
        elif (carrera == "profe" and 'es_robotica' in request.form.keys()):
            is_robot = 1
        else:
            is_robot = 0
        conn.execute("INSERT INTO usuarios (name, lastname, mail, password, tipo, inst, carrera, robotica) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (request.form['name'], request.form['lastname'], request.form['email'],
             request.form['psw'], request.form['cargo'], uni, carrera, is_robot))
        conn.commit()
        user = conn.execute('SELECT * FROM usuarios WHERE mail = ?',
                        (request.form['email'],)).fetchone()
        conn.close()
        session['user_id'] = user["id"]
        session['time_con'] = -1
        return redirect(url_for('main'))

    return render_template("registro/main.html")

@app.route("/res", methods =('GET', 'POST'))
def res():
    if not session:
        return redirect(url_for('index'))
    user_id = session["user_id"]
    full_date = datetime.now().strftime("%d/%m/%Y %H:%M").split(" ")
    hoy = full_date[0]
    if hoy[0] == "0":
        hoy = hoy[1:]
    dia_h, mes_h, año_h = hoy.split("/")

    conn = get_db_connection()
    taken = conn.execute('SELECT * FROM reservas').fetchall()
    users_res = conn.execute('SELECT * FROM reservas WHERE id_user = ?',
                        (user_id,)).fetchall()
    
    conn.close()

    user = get_user(user_id)
    if user['blacklist']:
        flash("Estas en lista negra, habla con tu profesor.")
        return redirect(url_for('main'))
    if user['tipo'] == 'profesor':
        is_teach = 1
    else:
        is_teach = 0
        
    if request.method == 'POST':

        this_week = 0
        this_month = 0
        
        dia_c, mes_c, año_c = request.form['dia'].split("/")
        for res in users_res:
            dia_r, mes_r, año_r = res['fecha'].split("/")
            if abs(int(dia_r) - int(dia_c)) < 7:
                this_week += 1
            if mes_r == mes_c:
                this_month += 1
        # Check limit 
        can_res = 1
        if user['tipo'] == "alumno":
            if user['robotica']:
                if this_week >= 3:
                    flash("Ya reservaste 3 horas esta semana.")
                    can_res = 0
            elif user['inst'] == "UC":
                if this_week >= 1:
                    flash("Ya reservaste una hora esta semana.")
                    can_res = 0
            else:
                if this_month >= 1:
                    flash("Ya reservaste una hora este mes.")
                    can_res = 0 
        if can_res:
            conn = get_db_connection()
            #Check if its reserved by teach
            update = conn.execute('SELECT * FROM reservas WHERE fecha = ? AND hora = ?',
                        (request.form['dia'], request.form['hora'])).fetchone()
            if update:
                if is_teach and request.form['is_enc']:
                    conn.execute('UPDATE reservas SET id_user = ?, taken = ?, id_enc = ? WHERE fecha = ? AND hora = ?', (user_id, 0, user_id, request.form['dia'], request.form['hora']))
                elif is_teach:
                    conn.execute('UPDATE reservas SET id_user = ?, taken = ?, id_enc = ? WHERE fecha = ? AND hora = ?', (user_id, 1, user_id, request.form['dia'], request.form['hora']))
                else:
                    conn.execute('UPDATE reservas SET id_user = ?, taken = ? WHERE fecha = ? AND hora = ?', (user_id, 1, request.form['dia'], request.form['hora']))
            elif request.form['is_enc']:
                conn.execute('INSERT INTO reservas (id_user, id_exp, fecha, hora, id_enc, taken) VALUES (?, ?, ?, ?, ?, ?)',
                 (user_id, request.form['id_exp'], request.form['dia'], request.form['hora'], user_id, 0))
            else:
                conn.execute('INSERT INTO reservas (id_user, id_exp, fecha, hora, id_enc) VALUES (?, ?, ?, ?, ?)',
                (user_id, request.form['id_exp'], request.form['dia'], request.form['hora'], user_id))
            conn.commit()
            conn.close()
            return redirect(url_for('exps'))

    available = ["8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00","17:00","18:00"]
    coming_up = []
    for res in taken:
        dia_r, mes_r, año_r = res['fecha'].split("/")
        if ((dia_r >= dia_h) & (mes_r >= mes_h) & (año_r >= año_h)):
            if is_teach and  user['robotica']:
                la_user = get_user(res['id_enc'])
                if (la_user['tipo'] == 'profesor' and la_user['robotica']):
                    coming_up.append(res)
            elif is_teach:
                if (my_teach(res['id_enc'], res['id_user']) or get_user(res['id_user'])['tipo'] == 'profesor'):
                    coming_up.append(res)
            else:
                if (res['taken'] or not my_teach(res['id_enc'], user_id)): 
                    coming_up.append(res)
        if ((dia_r == dia_h) & (mes_r == mes_h) & (año_r == año_h)):
            available.remove(res["hora"])
    coming_up_dic = ""
    for ress in coming_up:
        coming_up_dic += ress["fecha"] + "," + ress["hora"] + "*"
    coming_up_dic = coming_up_dic[:-1]

    return render_template("reserva_horas/reserva.html", ava = available, taken = coming_up_dic, is_teach = is_teach)

@app.route("/cuenta", methods=('GET', 'POST'))
def perfil():
    if not session:
        return redirect(url_for('index'))
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

@app.route("/sim", methods = ('GET', 'POST'))
def sim():
    if not session:
        return redirect(url_for('index'))
    return render_template("Simulacion/simulacion_base_movil.html")

@app.route('/experiencia_base_movil/s')
def speed_index():
    if not session:
        return redirect(url_for('index'))
    return render_template('experiencia_base_movil/index.html')

@app.route('/experiencia_base_movil/set_speed', methods=['post', 'get'])
def experiencia_base_movil():
    global was_redic
    if not session:
        return redirect(url_for('index'))
    if not was_redic:
        return redirect(url_for('main'))
    was_redic = True
    m1_speed = request.args.get('m1')
    m2_speed = request.args.get('m2')
    #send_message(f"{m1_speed}{m2_speed}000")
    print(session['time_con'])
    if session['time_con'] == -1:
        print("beep")
        session['time_con'] = datetime.now().strftime("%H:%M:%S");
    send_message(f"SPD{m1_speed}${m2_speed}$")
    return render_template('experiencia_base_movil/index.html', time_con = session['time_con'], wt = whos_there)

@app.route('/experiencia_base_movil/set_arduino_k', methods=['POST', 'GET'])
def constantes_arduino():
    if request.method == "POST":
        kp = request.args.get('kp')
        ki = request.args.get('ki')
        kd = request.args.get('kd')
        print(f"contantes recibidas: {kp}, {ki}, {kd}")
        send_message(f"KAR{kp}${kd}${ki}")
        return render_template('experiencia_base_movil/index.html')

# RECEPCION DE INFORMACION DE VARIABLES DE LA EXPERIENCIA
@app.route('/experiencia_base_movil/arduino_constants', methods=['POST', 'GET'])
def arduino_constants():
    if request.method == 'POST':
        print(request.get_json())
        data = request.get_json()
        kp = data['kp']
        ki = data['ki']
        kd = data['kd']
        send_message(f"KAR{kp}${kd}${ki}")

        return 'OK', 200

@app.route('/experiencia_base_movil/main_control_constants', methods=['POST', 'GET'])
def main_control_constants():
    if request.method == 'POST':
        print(request.get_json())
        data = request.get_json()

        kpl = data['kpl']
        kil = data['kil']
        kdl = data['kdl']
        
        kpa = data['kpa']
        kia = data['kia']
        kda = data['kda']
        # send_message(f"K{kpl}${kdl}${kil}${kpa}${kda}${kia}$")
        send_message(f"KSL{kpl}${kil}${kdl}")
        print("KSL enviado")
        time.sleep(1)
        send_message(f"KSA{kpa}${kia}${kda}")
        print("KSA enviado")
        print()

        return 'OK', 200

@app.route('/experiencia_base_movil/motor_speeds', methods=['POST', 'GET'])
def motor_speeds():
    if request.method == 'POST':
        print(request.get_json())
        data = request.get_json()
        m1_speed = data['m1']
        m2_speed = data['m2']
        send_message(f"SPD{m1_speed}${m2_speed}$")
        
        return 'OK', 200

@app.route('/experiencia_base_movil/open_camera', methods=['POST', 'GET'])
def open_camera():
    if request.method == 'POST':
        print(request.get_data)

        send_message('CAM')
        
        return 'OK', 200

@app.route('/experiencia_base_movil/exp_data', methods = ['GET'] )
def send_exp_data():
    global exp_data
    print(f"DATOS ENVIADOS: \n {exp_data}\n")
    return jsonify(exp_data)

@app.route('/experiencia_base_movil/ard_data', methods = ['GET'] )
def send_ard_data():
    global ard_data
    print(f"DATOS ENVIADOS: \n {ard_data}\n")
    return jsonify(ard_data)

@app.route('/experiencia_base_movil/set_constants', methods=['post', 'get'])
def set_exp_constants():
    kpl = request.args.get('kpl')
    kil = request.args.get('kil')
    kdl = request.args.get('kdl')
    
    kpa = request.args.get('kpa')
    kia = request.args.get('kia')
    kda = request.args.get('kda')
    # send_message(f"K{kpl}${kdl}${kil}${kpa}${kda}${kia}$")
    send_message(f"KSL{kpl}${kil}${kdl}")
    print("KSL enviado")
    time.sleep(1)
    send_message(f"KSA{kpa}${kia}${kda}")
    print("KSA enviado")
    print()
    return render_template('experiencia_base_movil/index.html')

@app.route("/setRef/<x>/<y>")
def set_ref(x,y):
    if request.method == 'GET':
        x = float(x)
        y = float(y)
        send_message(f'REF{x},{y}')
        message = f'Ref set in ({x},{y})'
        return jsonify(message)  # serialize and use JSON headers
    # POST request
    if request.method == 'POST':
        print(request.get_json())  # parse as JSON
        return 'Success', 200

@app.route('/camera', methods=['post', 'get'])
def camera():
    send_message('CAM')
    return render_template('experiencia_base_movil/index.html')

@app.route("/cuenta/exp")
def exps():
    if not session:
        return redirect(url_for('index'))
    user_id = session["user_id"]
    user = get_user(user_id)
    conn = get_db_connection()
    reservas = conn.execute('SELECT * FROM reservas WHERE id_user = ?',
                        (user_id,)).fetchall()
    nomexp = ['Robot PID']
    conn.close()
    full_date = datetime.now().strftime("%d/%m/%Y %H").split(" ")
    hoy = full_date[0]
    if hoy[0] == "0":
        hoy = hoy[1:]
    coming_up = []
    reservas_new = []
    dia_h, mes_h, año_h = hoy.split("/")
    for res in reservas:
        new_res = {"fecha": res['fecha'], "hora": res['hora'],"id_exp": res['id_exp']}
        enc = get_user(res['id_enc'])
        if enc['tipo'] == "profesor":
            new_res['enc'] = enc['name'] + " " + enc['lastname']
        else:
            new_res['enc'] = "Libre"
        dia_r, mes_r, año_r = res['fecha'].split("/")
        hora_r = int(res['hora'].split(":")[0])
        if ((dia_r >= dia_h) & (mes_r >= mes_h) & (año_r >= año_h)):
            if ((dia_r == dia_h) and (hora_r < int(full_date[1]))):
                continue
            coming_up.append(new_res)
        else:
            reservas_new.append(new_res)
    return render_template("perfil/historial_experiencias.html", reservas = reservas_new, nombres_exp = nomexp, reservas_cu = coming_up, user = user)

@app.route("/cuenta/est", methods = ('POST', 'GET'))
def estuds():
    #if not session:
    #   return redirect(url_for('index'))
    user_id = session["user_id"]
    conn = get_db_connection()
    if request.method == 'POST':
        act, id_est = request.form['sid'][0], int(request.form['sid'][1:])
        if act == "A":
            conn.execute("INSERT INTO estudiante_de (id_est, id_prof) VALUES (?, ?)", (id_est,user_id))
        elif act == "D":
            conn.execute("DELETE FROM estudiante_de WHERE id_est = ? AND id_prof = ?", (id_est,user_id))
        elif act == "U":
            conn.execute("UPDATE usuarios SET blacklist = ? WHERE id = ?", (0,id_est))
        else:
            conn.execute("UPDATE usuarios SET blacklist = ? WHERE id = ?", (1,id_est))
        conn.commit()
    estuds = conn.execute('SELECT * FROM usuarios WHERE tipo = ?',
                        ('alumno',)).fetchall()
    conn.close()
    mine = []
    not_mine = []
    for estud in estuds:
        if my_teach(user_id, estud['id']):
            mine.append(estud)
        else:
            not_mine.append(estud)
    return render_template("perfil/estudiantes.html", mine = mine, not_mine = not_mine)

@app.route("/cuenta/del", methods =('POST', ))
def delete():
    if not session:
        return redirect(url_for('index'))
    id_user = session.get("user_id")
    conn = get_db_connection()
    conn.execute('DELETE FROM usuarios WHERE id = ?', (id_user,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route("/exp_con", methods =('GET', ))
def exp_con():
    if not session:
        return redirect(url_for('index'))
    id_user = session.get("user_id")
    usuario = get_user(id_user)
    if usuario['blacklist']:
        flash("Estas en lista negra, habla con tu profesor.")
        return redirect(url_for('main'))
    full_date = datetime.now().strftime("%d/%m/%Y %H").split(" ")
    hoy = full_date[0]
    if hoy[0] == "0":
        hoy = hoy[1:]
    global was_redic
    ahora = full_date[1] +":00"
    conn = get_db_connection()
    hora_res  = conn.execute('SELECT * FROM reservas WHERE fecha = ? AND hora = ?', (hoy, ahora,)).fetchone()
    if hora_res != None:
        if hora_res['id_user'] == id_user:
            tiene_hora = 1
        else:
            tiene_hora = 0
        conn.close()
        if tiene_hora:
            was_redic = True
            return redirect(url_for('experiencia_base_movil'))
        else: 
            flash("No tienes reservada esta hora, reserva una aquí.")
            return redirect(url_for('res'))
    else:
        global whos_there
        answer = whos_there
        print(answer)
        rob = usuario['robotica']
        uc = (usuario['inst'] == 'UC')
        #If robotic, external or uc in there
        #If uc, external in there
        #If external, first come first serve
        if (answer == 'N') or ((answer == 'E' or answer == 'U') and rob) or (answer == 'E' and uc):
            if rob:
                whos_there = "R"
            elif uc:
                whos_there  = "U"
            else:
                whos_there = "E"
            was_redic = True
            return redirect(url_for('experiencia_base_movil'))
        else:
            flash("No tienes reservada esta hora, reserva una aquí.")
            return redirect(url_for('res'))

@app.route('/getwt', methods = ['GET'] )
def get_wt():
    global whos_there
    print(f"DATOS ENVIADOS: \n {whos_there}\n")
    return whos_there

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
    socketio.run(app)


