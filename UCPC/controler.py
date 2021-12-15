import numpy as np

class Controler():
    def __init__(self, dt, kp_l=0, kd_l=0, ki_l=0, kp_a=0, kd_a=0, ki_a=0):
        self._ref = np.array([0.0, 0.0])
        self.past_ref = np.array([0.0, 0.0])
        self.dt = dt
        self.kp_l = kp_l
        self.kd_l = kd_l
        self.ki_l = ki_l
        self.kp_a = kp_a
        self.kd_a = kd_a
        self.ki_a = ki_a
        self.u_0 = 0
        self.u_1 = 0
        self.constante_tuning_angular = 6.6
        self.constante_tuning_lineal = 10 
        self.error = [0.0, 0.0]
        self.past_error = [0.0, 0.0]
        self.ac_error = [0.0, 0.0]

        self.last_errors = [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
    
    def UpdateError(self, current_error):
        self.last_errors[0:3] = self.last_errors[1:4]
        self.last_errors[3] = current_error

        self.past_error = self.error
        self.ac_error[0] += current_error[0]
        self.ac_error[1] += current_error[1]

        self.error = current_error

    def control(self, state):
        self.calculate_error(state)
        #av_error = self.average_error()
        av_error = self.error
        # print(f"kpa: {self.kp_a}")
        #print(f"av_error_0: {av_error[0]}")s
        #u_0 = self.kp_l*av_error[0]   
        self.kp_l = self.constante_tuning_lineal*self.kp_l
        self.kd_l = self.constante_tuning_lineal*self.kd_l
        self.ki_l = self.constante_tuning_lineal*self.ki_l
        
        self.kp_a = self.constante_tuning_angular*self.kp_a
        self.kd_a = self.constante_tuning_angular*self.kd_a
        self.ki_a = self.constante_tuning_angular*self.ki_a
        
        self.u_0 = self.kp_l*av_error[0] - self.kp_a*av_error[1] + self.ki_l*self.ac_error[0]*self.dt - self.ki_a*self.ac_error[1]*self.dt + self.kd_l*(av_error[0]-self.past_error[0])/self.dt - self.kd_a*(av_error[1]-self.past_error[1])/self.dt
        self.u_1 = self.kp_l*av_error[0] + self.kp_a*av_error[1] + self.ki_l*self.ac_error[0]*self.dt + self.ki_a*self.ac_error[1]*self.dt + self.kd_l*(av_error[0]-self.past_error[0])/self.dt + self.kd_a*(av_error[1]-self.past_error[1])/self.dt
        #u_1 = 0.0
        # print(f"acumulado 0: {self.ac_error[0]}")
        # print(f"pasado 0: {self.past_error[0]}")
        return (-self.u_0,self.u_1) 
    
    def average_error(self):
        res = list()
        for j in range(2):
            tmp = 0
            for i in range(4):
                tmp = tmp + self.last_errors[i][j]
            res.append(tmp/4)
        return res

    def calculate_error(self, state):
        a = np.arctan2(self.ref[0]-state[0], self.ref[1]-state[1]) + np.pi - state[2]
        d = np.linalg.norm(self.ref-state[0:2]) * np.cos(a)
        # a = state[2]-np.pi/2+np.arctan2(ref[0]-state[0],ref[1]-state[1])
        '''
        if (a<-np.pi)and(a>-3*np.pi/2):
            a+= 2*np.pi
        '''

        while a>np.pi:
            a-= 2*np.pi
        while a<-np.pi:
            a+= 2*np.pi
        
        e = np.array([d,a])
        self.UpdateError(e)
        return e

    @property
    def ref(self):
        return self._ref

    @ref.setter    
    def ref(self, new_ref):
        if not (self.past_ref == new_ref).all():
            self.ac_error = np.array([0.0, 0.0])
            self.past_ref = self.ref
            self._ref = new_ref


