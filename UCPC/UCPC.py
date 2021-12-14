import threading
from time import sleep
import cv2
import numpy as np
from numpy.lib.function_base import average
from scipy.ndimage import center_of_mass, gaussian_filter
from subscriber import Subscriber
from controler import Controler
from store_coor import StoreCoor

bt = True
cam = 1

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
        lb = np.array([3, 150, 30])
        ub = np.array([20, 255, 120])
    return cv2.inRange(X,lb,ub)

def center_of_mass_area(mask):
    try:
        kernel = np.ones((5,5), np.uint8)  
        img_dilation = cv2.dilate(mask, kernel, iterations=1)  
        img_erosion = cv2.erode(img_dilation, kernel, iterations=1)  
        contours, hierarchy = cv2.findContours(img_erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        sorted_contours= sorted(contours, key=cv2.contourArea, reverse= True)
        largest_item= sorted_contours[0]
        M = cv2.moments(largest_item)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return (cY, cX)
    except:
        return (0,0)

def angulo(p1, p2):
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
        

def bt_receive(sub):
    while True:
        sub.bt_receive()
        sleep(0.2)


fps = 10
fps_cam = 5
cont = Controler(1/fps)  
port = "/dev/cu.IRB-G01-SPPDev"
#port = "/dev/cu.iPhonedeIgnacio-Wireles"

store_coor = StoreCoor()
if bt:
    clase = Subscriber(store_coor, port)
else:
    clase = Subscriber(store_coor)
    
state = np.array([0.0, 0.0, 0.0])
error_actual = np.array([0.0, 0.0])

cap = cv2.VideoCapture(cam)
cap.set(cv2.CAP_PROP_FPS, fps_cam) 
screen_to_real = 0.42
clase.bt_send(f"KAR{10}${0.0001}${0}$")

bt_thread = threading.Thread(target = manage_bt, args = [clase], daemon = True)
bt_thread.start()

bt_rec_thread = threading.Thread(target = bt_receive, args = [clase], daemon = True)
bt_rec_thread.start()

i=90
while(1):
    i += 1
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
    # green_mask[int(x1)-l:int(x1)+l,int(y1)-l:int(y1)+l] = 0
    
    # Brown mask
    brown_mask = mask_hsv(hsv, "brown")
    # brown_mask = gaussian_filter(brown_mask, 2)
    x2, y2 = center_of_mass_area(brown_mask)
    if np.isnan(x2) or np.isnan(y2):
        x2, y2 = (0,0)

    a = angulo((x1,y1), (x2,y2))
    state[:] = np.array([y1/2, x1/2, a])

    # Actualizamos constantes
    cont.kp_a, cont.ki_a, cont.kd_a = clase.angular_constants
    cont.kp_l, cont.ki_l, cont.kd_l = clase.linear_constants

    # Mandamos señal de control
    if clase.auto:
        cont.ref = np.array(store_coor.ref_d)
        u0, u1 = cont.control(state)
        clase.bt_msg = f"REF{u0}${u1}$"
        clase.bt_signal = True


    # Dibujamos 
    circle_pos = 2*store_coor.ref_d[0], 2*store_coor.ref_d[1]
    cv2.line(frame, circle_pos, (int(y1),int(x1)), (255, 255, 255),3) # Linea al goal
    cv2.line(frame, (int(y2),int(x2)), (int(y1),int(x1)), (0, 0, 0),8) # Linea Robot
    cv2.circle(frame, circle_pos, 10,(135,229, 255), -1) # Goal
    cv2.circle(frame, (int(y1),int(x1)), 10,(0,150, 20), -1) # Green Circle
    cv2.circle(frame, (int(y2),int(x2)), 10,(0,50, 100), -1)  # Brown Circle

    # Actualizamos frame actual y diccionario
    error = cont.error
    clase.current_frame = frame
    clase.mqtt_dict['error_lineal']=cont.error[0]
    clase.mqtt_dict['error_angular']=cont.error[1]
    clase.mqtt_dict['ref']=store_coor.ref_d
    clase.mqtt_dict['x']=state[0]
    clase.mqtt_dict['y']=state[1]
    clase.mqtt_dict['theta']=state[2]

    if (cv2.waitKey(1) & 0xFF == ord('q')):
        break

cap.release()
cv2.destroyAllWindows()