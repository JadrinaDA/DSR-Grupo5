import numpy as np
from numpy.core.shape_base import _block_format_index
#from scipy.integrate import odeint
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from functools import partial  # https://docs.python.org/3.6/library/functools.html
                               # required to pass additional parameters to solve_ivp


from modelo import *

class MobileBasePID():
    def __init__(self, mobile_base, reference, kp_l=0, kd_l=0, ki_l=0, kp_a=0, kd_a=0, ki_a=0, error=np.array([0.0, 0.0]), past_error=np.array([0.0, 0.0]), ac_error=np.array([0.0, 0.0])):
        self.kp_l = kp_l
        self.kd_l = kd_l
        self.ki_l = ki_l
        self.kp_a = kp_a
        self.kd_a = kd_a
        self.ki_a = ki_a
        self.error = error
        self.past_error = past_error
        self.ac_error = ac_error
        self.mobile_base = mobile_base
        self.reference = reference

    def set_linear_constants(self, kp, kd, ki):
        self.kp_l = kp
        self.kd_l = kd
        self.ki_l = ki

    def set_angular_constants(self, kp, kd, ki):
        self.kp_a = kp
        self.kd_a = kd
        self.ki_a = ki

    def update_error(self):
        self.past_error = self.error

        state = self.mobile_base.GetSensor()
        ref = self.reference
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
        
        self.error = np.array([d,a])

        self.ac_error += self.error
        return self.error
    
    def update(self):
        self.update_error()

        u_0 = self.kp_l*self.error[0] - self.kp_a*self.error[1] - self.kd_a*(self.error[1]-self.past_error[1])/self.mobile_base._Ts
        u_1 = self.kp_l*self.error[0] + self.kp_a*self.error[1] + self.kd_a*(self.error[1]-self.past_error[1])/self.mobile_base._Ts
        self.mobile_base.SetActuator([u_0,u_1])



def PID(botin, error_actual, error_previo, kp_lineal, kd_lineal, ki_lineal, kp_angular, kd_angular, ki_angular):
    u_0 = kp_lineal*error_actual[0] - kp_angular*error_actual[1] - kd_angular*(error_actual[1]-error_previo[1])/botin._Ts
    u_1 = kp_lineal*error_actual[0] + kp_angular*error_actual[1] + kd_angular*(error_actual[1]-error_previo[1])/botin._Ts
    botin.SetActuator([u_0,u_1])

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

# auto = False

# state = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
# ref = np.array([0.5, 0.0])
# u = np.array([0.0, 0.0])

# kp_lineal = 0.01
# ki_lineal = 0.0
# kd_lineal = 0.0
# kp_angular = 1.0
# ki_angular = 0.0
# kd_angular = 0.0

# error_actual = np.array([0.0, 0.0])
# error_previo = np.array([0.0, 0.0])
# error_acumulado =  np.array([0.0, 0.0])

# datos_tiempo = open("tiempo.txt","w")                 # archivo para guardar el tiempo
# datos_referencias = open("referencias.txt","w")       # archivo para guardar las referencias
# datos_estados = open("estados.txt","w")               # archivo para guardar las variables manipuladas
# datos_errores = open("errores.txt","w")               # archivo parta guardar los errores

# botin = BaseMovil()
# botin.SetState(state)


# while(1):
#     datos_tiempo.write(str(botin._t)+"\n")
#     datos_referencias.write(str(ref[0]) + " " + str(ref[1]) + "\n")
#     datos_estados.write(str(state[0])+ " " + str(state[1]) + "\n")
#     datos_errores.write(str(error_actual[0])+ " " + str(error_actual[1]) + "\n")

#     error_previo[:] = error_actual[:]
#     # error_actual[:] = ref - state[0:2]
#     error_actual[:] = error(ref, state)
#     error_acumulado[:] = error_acumulado[:] + error_actual[:]
#     PID()
#     botin.SetActuator(u)
#     botin.UpdateState()
#     state = botin.GetSensor()
#     update_display(state, ref)
