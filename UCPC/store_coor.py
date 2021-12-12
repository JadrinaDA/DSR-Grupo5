class StoreCoor:
    def __init__(self, XMAX=640, YMAX=480):
        self.ref_d = (170, 170) # Seteamos como referencia inicial
        self.ref_m = (0,0)
        self.XMAX = XMAX
        self.YMAX = YMAX
        self.error_angular = 0

    def click_event(self, x, y):
        self.ref_d = (x,y)
        self.ref_m = (x-int(self.XMAX/2), int(self.YMAX/2)-y)