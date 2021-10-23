import numpy as np
#from scipy.integrate import odeint
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from functools import partial  # https://docs.python.org/3.6/library/functools.html
                               # required to pass additional parameters to solve_ivp
import pygame
from pygame.locals import *

from modelo import *

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

# --- Graphics Variables ---
XMAX = 640
YMAX = 480
ppm = 200                                                    # conversion entre pixeles y metros del sistema
screen = None

def PID():
    u[0] = kp_lineal*error_actual[0] - kp_angular*error_actual[1] - kd_angular*(error_actual[1]-error_previo[1])/botin._Ts
    u[1] = kp_lineal*error_actual[0] + kp_angular*error_actual[1] + kd_angular*(error_actual[1]-error_previo[1])/botin._Ts

def init_display():
    global XMAX, YMAX, screen
    
    # Initialize PyGame and setup a PyGame display
    pygame.init()
    # pygame.display.set_mode()
    screen = pygame.display.set_mode((XMAX,YMAX))
    pygame.display.set_caption('base movil')
    pygame.key.set_repeat(1,50)     # Works with essentially no delay.
    #pygame.key.set_repeat(0,50)    # Doesn't work because when the delay
                                    # is set to zero, key.set_repeat is
                                    # returned to the default, disabled
                                    # state.

def update_display(state, ref):
    global XMAX, YMAX

    x1 = XMAX/2 + int(state[0]*ppm)
    y1 = YMAX/2 - int(state[1]*ppm)
    x2 = XMAX/2 + int((state[0] + np.cos(state[2])*0.2)*ppm)
    y2 = YMAX/2 - int((state[1] + np.sin(state[2])*0.2)*ppm)
    x3 = XMAX/2 + int(ref[0]*ppm)
    y3 = YMAX/2 - int(ref[1]*ppm)
    pygame.draw.rect(screen, (0,0,0), (0,0,XMAX,YMAX), 0)
    pygame.draw.circle(screen, (255,0,0), (x1,y1), 0.2*ppm, 0)
    pygame.draw.line(screen, (0,0,255), (x1,y1), (x2,y2), 5)
    pygame.draw.circle(screen, (0,255,0), (x3,y3), 10, 0)

    pygame.display.flip()

def handle_keyboard():
    global XMAX, YMAX
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # pygame.QUITis sent when the user clicks the window's "X" button, or when the system 'asks' for the process to quit
                                       # http://stackoverflow.com/questions/10080715/pygame-event-event-type-pygame-quit-confusion
            datos_tiempo.close()
            datos_referencias.close()
            datos_estados.close()
            datos_errores.close()
            pygame.quit(); #sys.exit() if sys is imported
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            datos_tiempo.close()
            datos_referencias.close()
            datos_estados.close()
            datos_errores.close()
            pygame.quit(); #sys.exit() if sys is imported
        if event.type == MOUSEBUTTONDOWN:                                               # si seguimiento es falso un click define la referencia
            if event.button==1:
                ref_display = np.array(list(pygame.mouse.get_pos()))
                ref[0] = (ref_display[0] - XMAX/2)/ppm
                ref[1] = -(ref_display[1] - YMAX/2)/ppm

        if event.type == pygame.KEYDOWN:    # http://www.pygame.org/docs/ref/key.html   # si auto es false se modifica la señal de control con las flechas
            if event.key == pygame.K_UP:
                if (not auto):
                    u[0] += 0.00001
            if event.key == pygame.K_DOWN:
                if (not auto):
                    u[0] -= 0.00001
            if event.key == pygame.K_RIGHT:
                if (not auto):
                    u[1] += 0.00001
            if event.key == pygame.K_LEFT:
                if (not auto):
                    u[1] -= 0.00001
        '''
        if event.type == pygame.KEYUP:                                                  # se cambian los modos con 'A' y 'T'
            if event.key == pygame.K_a:
                auto = not auto
        '''

def error(ref, state):
    d = np.linalg.norm(ref-state[0:2])
    a = state[2]-np.pi/2+np.arctan2(ref[0]-state[0],ref[1]-state[1])
    '''
    if (a<-np.pi)and(a>-3*np.pi/2):
        a+= 2*np.pi
    '''
    
    while a>np.pi:
        a-= 2*np.pi
    while a<-np.pi:
        a+= 2*np.pi
    
    return np.array([d,a])

def graficar(tiempo, referencia, estado):
    plt.plot(tiempo,referencia,estado)

auto = False

state = np.array([0.0, 0.0, 0.0, 0.0, 0.0])

ref = np.array([0.5, 0.0])

u = np.array([0.0, 0.0])

kp_lineal = 0.01
ki_lineal = 0.0
kd_lineal = 0.0
kp_angular = 1.0
ki_angular = 0.0
kd_angular = 0.0

error_actual = np.array([0.0, 0.0])
error_previo = np.array([0.0, 0.0])
error_acumulado =  np.array([0.0, 0.0])

datos_tiempo = open("tiempo.txt","w")                 # archivo para guardar el tiempo
datos_referencias = open("referencias.txt","w")       # archivo para guardar las referencias
datos_estados = open("estados.txt","w")               # archivo para guardar las variables manipuladas
datos_errores = open("errores.txt","w")               # archivo parta guardar los errores

botin = BaseMovil()
botin.SetState(state)

init_display()

while(1):
    datos_tiempo.write(str(botin._t)+"\n")
    datos_referencias.write(str(ref[0]) + " " + str(ref[1]) + "\n")
    datos_estados.write(str(state[0])+ " " + str(state[1]) + "\n")
    datos_errores.write(str(error_actual[0])+ " " + str(error_actual[1]) + "\n")

    handle_keyboard()
    error_previo[:] = error_actual[:]
    # error_actual[:] = ref - state[0:2]
    error_actual[:] = error(ref, state)
    error_acumulado[:] = error_acumulado[:] + error_actual[:]
    PID()
    botin.SetActuator(u)
    botin.UpdateState()
    state = botin.GetSensor()
    update_display(state, ref)
