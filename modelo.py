import numpy as np
from scipy.integrate import solve_ivp
from functools import partial

class BaseMovil:

    def __init__(self, name='botin'):
        self.name = name
        self._x = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        # self._x_min
        # self._x_max
        self._t = 0.0
        self._u = np.array([0.0, 0.0])
        self._u_max = np.array([1.0, 1.0])
        self._Ts = 0.01
        self._step_size = self._Ts
        self._t0 = 0.
        self._tf = self._t0 + self._step_size
        self._Nsamples = 10+1
        self._tX = np.linspace(self._t0, self._tf, self._Nsamples)

        # model parameters
        self._m = 2.0
        self._r = 0.04
        self._l = 0.2
        self._w = 0.1
        self._c = 1.0
        self._b = 1.0
        self._j = self._m*(self._l**2 + self._w**2)/12

    def SetState(self, x):
        self._x = x

    def SetSimulationTime(self, T):
        self._Ts = T
        self._step_size = self._Ts
        self._t0 = 0.
        self._tf = self._t0 + self._step_size
    
    def SetActuator(self, u):
        for k in range(len(u)):
            if np.abs(u[k]) > self._u_max[k]:    # Apply actuator saturations
                u[k] = self._u_max[k]*np.sign(u[k])
        self._u = u
    
    def _modelo_base_movil(self, t, x, u):
        xdot = np.array([self._x[3]*np.cos(self._x[2]), self._x[3]*np.sin(self._x[2]), self._x[4], ((self._u[0]+self._u[1])/self._r-self._c*self._x[3])/self._m, (self._w*(self._u[0]-self._u[1])/(2*self._r)-self._b*self._x[4])/self._j])
        return xdot
    
    def UpdateState(self):
    
        #print('Updating crane state')
        # t, x = step_model(model, t0, x0, u, step_size)
    
        # odeint - Perform integration using Fortran's LSODA (Adams & BDF methods)
        # This function has been deprecated.  It is slower and the integration methods
        # cannot handle ODEs with noise, producing diverging results.
        #x = odeint(lambda x, t, *args : model(t, x, *args), x0, tX, args=(u, sigma_v))   
        #t = tfinal
        #return t, x.T
    
        # solve_ivp
        x0 = self._x
        x = solve_ivp(partial(self._modelo_base_movil, u=self._u), (self._t0,self._tf), x0, method='BDF') #, teval=self._tX)
        #return x.t, x.y
        self._x = ((x.y).T)[-1,:]
        self._t = self._t + self._Ts
        
        # Check state bounds
        '''
        for k in range(len(self._x)):
            self._x[k] = self._x_min[k] if (self._x[k] < self._x_min[k]) else self._x[k]
            self._x[k] = self._x_max[k] if (self._x[k] > self._x_max[k]) else self._x[k]
        '''

    def GetSensor(self):
        return self._x