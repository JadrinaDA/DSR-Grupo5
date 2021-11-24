import cv2
import numpy as np
from scipy.ndimage import center_of_mass

'''
conversion de colores

green = np.uint8([[[0,255,0 ]]])
hsv_green = cv.cvtColor(green,cv.COLOR_BGR2HSV)
print( hsv_green )
'''


def mask_rgb(X,color):
    return 0

def mask_hsv(X,color):
    lb = np.array([0, 0, 0])
    ub = np.array([179, 255, 255])
    if (color=="red")or(color=="rojo"):
        lb = np.array([0, 50, 50])
        ub = np.array([0, 255, 255])
    elif (color=="green")or(color=="verde"):
        lb = np.array([33, 80, 100])
        ub = np.array([102, 255, 255])
    elif (color=="blue")or(color=="azul"):
        lb = np.array([110, 50, 50])
        ub = np.array([130, 255, 255])
    elif (color=="brown")or(color=="cafe"):
        lb = np.array([10, 100, 100])
        ub = np.array([20, 255, 255])
    return cv2.inRange(X,lb,ub)


def filtro(X):
    s =  np.shape(X)
    Y = np.zeros(s)

    l = 5
    t = 0.9

    for k1 in range(l,s[0]-l):
        for k2 in range(l,s[1]-l):
            if (np.sum(X[k1-l:k1+l,k2-l:k2+l])>=4*l**2*t*255):
                Y[k1,k2] = 1
    return Y

def centro(M):
    x = 0
    return 0

def angulo(p1, p2):
    a = np.arctan2(p2[1]-p1[1], p2[0]-p1[0]) + np.pi/2
    return a

class StoreCoor:
    def __init__(self):
        self.ref = (-1,-1)

    def click_event(self, event, x, y, flags, params):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.ref = (x, y)


def run_cv(store_coor):
    cap = cv2.VideoCapture(1)
    screen_to_real = 0.42
    while(1):
        ret, frame = cap.read()
        s = np.shape(frame)


        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        l = 5
        
        # green mask
        green_mask = mask_hsv(hsv, "green")
        x1, y1 = center_of_mass(green_mask)
        if x1 and y1:
            green_mask[int(x1)-l:int(x1)+l,int(y1)-l:int(y1)+l] = 0
        
        # brown mask
        brown_mask = mask_hsv(hsv, "brown")
        x2, y2 = center_of_mass(brown_mask)
        if x2 and y2:
            brown_mask[int(x2)-l:int(x2)+l,int(y2)-l:int(y2)+l] = 0
        
        a = angulo((x1,y1), (x2,y2))
        
        print(a*180/np.pi)
        dist = int(((store_coor.ref[0] -y1)**2 + (store_coor.ref[1] -x1)**2)**(0.5) * screen_to_real)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame,'Dist:' + str(dist),(10,450), font, 2,(255,255,255),2,cv2.LINE_AA)


        cv2.circle(frame, store_coor.ref, 10,(0,0, 255), -1)
        cv2.line(frame, store_coor.ref, (int(y1),int(x1)), (255, 0, 0),5)
        cv2.imshow('frame', frame)
        cv2.setMouseCallback('frame', store_coor.click_event)

        cv2.imshow('green', green_mask)
        cv2.imshow('brown', brown_mask)

        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break


    cap.release()
    cv2.destroyAllWindows()