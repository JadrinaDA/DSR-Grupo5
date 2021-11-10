import numpy as np
import matplotlib.pyplot as plt

t = np.loadtxt("tiempo.txt")
referencias = np.loadtxt("referencias.txt")
estados = np.loadtxt("estados.txt")
errores = np.loadtxt("errores.txt")

print(np.shape(t))
print(np.shape(referencias))
print(np.shape(estados))
print(np.shape(errores))


x = estados[:,0]
x_ref = referencias[:,0]
y = estados[:,1]
y_ref = referencias[:,1]
error_distancia = errores[:,0]
error_angulo = errores[:,1]

fig1, axs1 = plt.subplots(2,1)
axs1[0].plot(t,x,t,x_ref)
axs1[1].plot(t,y,t,y_ref)
axs1[0].set_xlabel('time')
axs1[1].set_xlabel('time')
axs1[0].set_ylabel('x(t)')
axs1[1].set_ylabel('y(t)')
axs1[0].grid(True)
axs1[1].grid(True)

fig3, axs2 = plt.subplots(2,1)
axs2[0].plot(t,error_distancia)
axs2[1].plot(t,error_angulo)
axs2[0].set_xlabel('time')
axs2[1].set_xlabel('time')
axs2[0].set_ylabel('error distancia')
axs2[1].set_ylabel('error angulo')
axs2[0].grid(True)
axs2[1].grid(True)

plt.show()