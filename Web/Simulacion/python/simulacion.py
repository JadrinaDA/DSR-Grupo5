import numpy as np
#from scipy.integrate import odeint
from scipy.integrate import solve_ivp
from functools import partial  # https://docs.python.org/3.6/library/functools.html
                               # required to pass additional parameters to solve_ivp
import pygame

from modelo import *

# --- Graphics Variables ---
XMAX = 640
YMAX = 480
ppm = 50                                                    # conversion entre pixeles y metros del sistema
screen = None

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

def draw_base_movil(state):
    x1 = 320 + int(state[0])
    y1 = 240 - int(state[1])
    x2 = 320 + int(state[0] + np.cos(state[2])*ppm)
    y2 = 240 - int(state[1] + np.sin(state[2])*ppm)
    pygame.draw.rect(screen, (0,0,0), (0,0,XMAX,YMAX), 0)
    pygame.draw.circle(screen, (255,0,0), (x1,y1), ppm, 0)
    pygame.draw.line(screen, (0,0,255), (x1,y1), (x2,y2), 5)

    pygame.display.flip()

def handle_keyboard():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # pygame.QUITis sent when the user clicks the window's "X" button, or when the system 'asks' for the process to quit
                                       # http://stackoverflow.com/questions/10080715/pygame-event-event-type-pygame-quit-confusion
            pygame.quit(); #sys.exit() if sys is imported
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit(); #sys.exit() if sys is imported
        '''
        if event.type == MOUSEBUTTONDOWN:                                               # si seguimiento es falso un click define la referencia
        if event.type == pygame.KEYDOWN:    # http://www.pygame.org/docs/ref/key.html   # si auto es false se modifica la señal de control con las flechas
            if event.key == pygame.K_UP:
                if (not auto):
            if event.key == pygame.K_DOWN:
                if (not auto):
            if event.key == pygame.K_RIGHT:
                if (not auto):
            if event.key == pygame.K_LEFT:
                if (not auto):
        if event.type == pygame.KEYUP:                                                  # se cambian los modos con 'A' y 'T'
            if event.key == pygame.K_a:
                auto = not auto
            '''





state = np.array([0.0, 0.0, 0.0, 0.0, 0.0])

u = np.array([0.0, 0.0])

kp = 0.0
ki = 0.0
kd = 0.0

botin = BaseMovil()
botin.SetState(state)

init_display()
botin.SetActuator([1, 0.0])

while(1):
    handle_keyboard()
    botin.UpdateState()
    state = botin.GetSensor()
    draw_base_movil(state)