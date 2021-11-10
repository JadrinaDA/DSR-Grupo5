import numpy as np
import cv2
import time
import serial

# cv2.namedWindow('frame')

msgOn = "100002003;" # Mensaje que queremos enviar
# El Ambos mensajes que estan en formato Sring deben ser transformados en un arreglo de bytes mediante la funcion .encode
msgOnEncode = str.encode(msgOn) 

# seria.Serial nos permite abrir el puerto COM deseado	
ser = serial.Serial("/dev/cu.G01-DevB", baudrate = 38400, timeout = 1)
# Cuando se abre el puerto serial con el Arduino, este siempre se reinicia por lo que hay que esperar a que inicie para enviar los mensajes
time.sleep(5)

while(True):
	# .write nos permite enviar el arreglo de bytes correspondientes a los mensajes
	ser.write(msgOnEncode);
	time.sleep(1)
	ser.write(msgOnEncode);
	time.sleep(1)
	print("Mensaje enviado")
	
	# Terminamos el codigo con la tecla ESC
	if cv2.waitKey(10) & 0xFF == 27:
		break
	
# Cerramos el puerto serial abierto una vez terminado el codigo
ser.close()
# cv2.destroyAllWindows()	
