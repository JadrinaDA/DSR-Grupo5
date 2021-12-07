import numpy as np
import matplotlib.pyplot as plt
import cv2
from   scipy.fftpack     import fft2,ifft2,fftshift,ifftshift
from   scipy.ndimage     import gaussian_filter
from   scipy.signal      import fftconvolve

def imshow(X):
    s = np.shape(X)
    print(s)
    if len(s)>2:
        Y = X[:,:,[2,1,0]]
        plt.imshow(Y)
    else:
        plt.imshow(X,cmap='gray')
    plt.show()

def FiltroTarea(X,p1,p2,p3):
    s = np.shape(X)
    Y = np.zeros(s)
    mask = np.ones(s)

    m = np.max(np.abs(X))*p1

    for k1 in range(p2,s[0]-p2):
        for k2 in range(p2,s[1]-p2):
            if np.abs(X[k1,k2])>m:
                mask[k1-p2:k1+p2,k2-p2:k2+p2] = 0
    mask[int(s[0]/2)-p3:int(s[0]/2)+p3,int(s[1]/2)-p3:int(s[1]/2)+p3] = 1
    # imshow(mask)
    Y = mask*X
    return Y


def FiltroTarea2(X,p1,p2,p3):
    X_fft = fft2(X)

    X_fft = fftshift(X_fft)

    s = np.shape(X)
    Y_fft = np.zeros(s)
    mask = np.ones(s)

    X_fft_log = np.log(1+np.abs(X_fft))

    m = np.max(np.abs(X_fft_log))*p1

    for k1 in range(p2,s[0]-p2):
        for k2 in range(p2,s[1]-p2):
            if np.abs(X_fft_log[k1,k2])>m:
                mask[k1-p2:k1+p2,k2-p2:k2+p2] = 0
    mask[int(s[0]/2)-p3:int(s[0]/2)+p3,int(s[1]/2)-p3:int(s[1]/2)+p3] = 1
    
    # imshow(mask)

    Y_fft = mask*X_fft

    Y = np.abs(ifft2(Y_fft))
    return Y

img = cv2.imread('J1.png',0)

# img_fft = fft2(img)

# img_fft = fftshift(img_fft)

filtrada = FiltroTarea2(img,0.8,20,25)

# filtrada = np.abs(ifft2(filtrada_fft))

imshow(filtrada)