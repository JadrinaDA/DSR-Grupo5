import numpy as np
from numpy.core.shape_base import _block_format_index
#from scipy.integrate import odeint
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from functools import partial  # https://docs.python.org/3.6/library/functools.html
                               # required to pass additional parameters to solve_ivp
import threading
import ctypes # For Thread exception

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

        u_0 = self.kp_l*self.error[0] - self.kp_a*self.error[1] + 0 - self.kd_a*(self.error[1]-self.past_error[1])/self.mobile_base._Ts
        u_1 = self.kp_l*self.error[0] + self.kp_a*self.error[1] + 0 + self.kd_a*(self.error[1]-self.past_error[1])/self.mobile_base._Ts
        # def PID():
        #     u[0] = kp_lineal*error_actual[0] - kp_angular*error_actual[1] + ki_lineal*error_acumulado[0]*botin._Ts - ki_angular*error_acumulado[1]*botin._Ts + kd_lineal*(error_actual[0]-error_previo[0])/botin._Ts - kd_angular*(error_actual[1]-error_previo[1])/botin._Ts
        #     u[1] = kp_lineal*error_actual[0] + kp_angular*error_actual[1] + ki_lineal*error_acumulado[0]*botin._Ts + ki_angular*error_acumulado[1]*botin._Ts + kd_lineal*(error_actual[0]-error_previo[0])/botin._Ts + kd_angular*(error_actual[1]-error_previo[1])/botin._Ts

        self.mobile_base.SetActuator([u_0,u_1])

    def set_reference(self, x, y):
        self.reference = np.array([x, y])
        print(f"Nueva referencia: ({x},{y})")

class Simulacion(threading.Thread):
    def __init__(self,robot, controler):
        super().__init__()
        self.robot = robot
        self.controler = controler
        self.loop = True

    def run(self):
        print("Corriendo Sim")
        self.robot.SetState([0,0,0,0,0])
        while(self.loop):
            self.controler.update()
            self.robot.UpdateState()

    def stop(self):
        self.loop = False
