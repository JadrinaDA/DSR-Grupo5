import threading
import cv2
import numpy as np
from numpy.lib.function_base import average
from scipy.ndimage import center_of_mass
from subscriber import Subscriber
from controler import Controler
from store_coor import StoreCoor
# import Filtro as filter

'''
conversion de colores

green = np.uint8([[[0,255,0 ]]])
hsv_green = cv.cvtColor(green,cv.COLOR_BGR2HSV)
print( hsv_green )
'''

def mask_hsv(X,color):
    lb = np.array([0, 0, 0])
    ub = np.array([179, 255, 255])
    if (color=="red")or(color=="rojo"):
        lb = np.array([0, 50, 50])
        ub = np.array([0, 255, 255])
    elif (color=="green")or(color=="verde"):
        lb = np.array([33, 80, 70])
        ub = np.array([90, 255, 255])
    elif (color=="blue")or(color=="azul"):
        lb = np.array([110, 50, 70])
        ub = np.array([130, 255, 255])
    elif (color=="brown")or(color=="cafe"):
        lb = np.array([10, 100, 20])
        ub = np.array([15, 255, 255])
    return cv2.inRange(X,lb,ub)

def angulo(p1, p2):
    # a = np.arctan2(p2[1]-p1[1], p2[0]-p1[0]) + np.pi/2
    a = np.arctan2(p2[1]-p1[1], p2[0]-p1[0])
    while a>np.pi:
        a-= 2*np.pi
    while a<-np.pi:
        a+= 2*np.pi
    return a

def manage_bt(sub):
    while True:
        if sub.bt_signal:
            sub.bt_send(sub.bt_msg)
            sub.bt_signal = False

fps = 10
cont = Controler(1/fps)  
port = "/dev/cu.IRB-G01-SPPDev"
#port = "/dev/cu.iPhonedeIgnacio-Wireles"

store_coor = StoreCoor()
# clase = Subscriber(store_coor, port)
clase = Subscriber(store_coor, port)
    
state = np.array([0.0, 0.0, 0.0])
error_actual = np.array([0.0, 0.0])

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FPS, fps)
screen_to_real = 0.42
clase.bt_send(f"KSA{10}${0.1}${0}$")

bt_thread = threading.Thread(target = manage_bt, args = [clase], daemon = True)
bt_thread.start()

while(1):
    ret, frame = cap.read()
    # frame = filter.FiltroTarea2(frame, 0.8,20,25)
    s = np.shape(frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    l = 5
    
    # Green mask
    green_mask = mask_hsv(hsv, "green")
    x1, y1 = center_of_mass(green_mask)
    if np.isnan(x1) or np.isnan(y1):
        x1, y1 = (0,0)
    green_mask[int(x1)-l:int(x1)+l,int(y1)-l:int(y1)+l] = 0
    
    # Brown mask
    brown_mask = mask_hsv(hsv, "brown")
    x2, y2 = center_of_mass(brown_mask)
    if np.isnan(x2) or np.isnan(y2):
        x2, y2 = (0,0)
    brown_mask[int(x2)-l:int(x2)+l,int(y2)-l:int(y2)+l] = 0

    a = angulo((x1,y1), (x2,y2))
    # print(f"Angulo: {a*180/ np.pi}")
    
    # dist = int(((store_coor.ref[0] -y1)*2 + (store_coor.ref[1] -x1)2)*(0.5) * screen_to_real)
    # font = cv2.FONT_HERSHEY_SIMPLEX
    # cv2.putText(frame,'Dist:' + str(dist),(10,450), font, 2,(255,255,255),2,cv2.LINE_AA)

    # state[:] = np.array([y1-640/2, 480/2-x1, a])
    state[:] = np.array([y1/2, x1/2, a])
    # print(f"Angulo: {a*180/np.pi}")
    # print(f"({state[0]}, {state[1]}), angulo: {state[2]*180/np.pi} Ref: {store_coor.ref_d}")
    # error_actual[:] = error(store_coor.ref_d, state)
    # clase.bt_msg = f"ERA{error_actual[1]}$"
    # cont.UpdateError(error_actual)
    # print(f"Error actual: {error_actual[1] * 180/np.pi}")
    # print(f"Referencia: {store_coor.ref_d}")

    # Actualizamos constantes
    cont.kp_a, cont.ki_a, cont.kd_a = clase.angular_constants
    cont.kp_l, cont.ki_l, cont.kd_l = clase.linear_constants


    # Mandamos señal de control
    # print(clase.auto)
    if clase.auto:
        cont.ref = np.array(store_coor.ref_d)
        u0, u1 = cont.control(state)
        clase.bt_msg = f"REF{u0}${u1}$"
        clase.bt_signal = True
        # print(clase.bt_msg)


    #dist = int(((store_coor.ref[0] -y1)**2 + (store_coor.ref[1] -x1)**2)**(0.5) * screen_to_real)
    # font = cv2.FONT_HERSHEY_SIMPLEX
    #cv2.putText(frame,'Dist:' + str(dist),(10,450), font, 2,(255,255,255),2,cv2.LINE_AA)

    # Dibujamos 
    circle_pos = 2*store_coor.ref_d[0], 2*store_coor.ref_d[1]
    cv2.circle(frame, circle_pos, 10,(0,0, 255), -1)
    cv2.line(frame, circle_pos, (int(y1),int(x1)), (255, 0, 0),5)
    # cv2.imshow('frame', frame)

    # Mostramos segmentaciones
    cv2.imshow('brown', brown_mask)
    cv2.imshow('green', green_mask)

    # Actualizamos frame actual y diccionario
    error = cont.error
    clase.current_frame = frame
    clase.mqtt_dict['error_lineal']=cont.error[0]
    clase.mqtt_dict['error_angular']=cont.error[1]
    #print(cont.error[1]*180/np.pi)
    #print(cont.error[1]*180/np.pi)
    # clase.mqtt_dict['u0']=u0
    # clase.mqtt_dict['u1']=u1
    clase.mqtt_dict['ref']=store_coor.ref_d
    clase.mqtt_dict['x']=state[0]
    clase.mqtt_dict['y']=state[1]
    clase.mqtt_dict['theta']=state[2]

    if (cv2.waitKey(1) & 0xFF == ord('q')):
        break

cap.release()
cv2.destroyAllWindows()