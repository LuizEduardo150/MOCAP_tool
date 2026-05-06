import cv2
from threading import Lock, Thread


"""
imshow e waitKey não é thread‑safe,
Resumindo Impossível usar métodos de entrada e saída do opencv em 
threads a não ser a principal. Por isso utilizamos a classe CameraThread
personalizada
"""
class CameraThread:
    def __init__(self, index):
        #cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)   # Windows
        #cap = cv2.VideoCapture(0, cv2.CAP_V4L2)    # Linux
        #cam1.set(cv2.CAP_PROP_FRAME_WIDTH, 110)
        #cam1.set(cv2.CAP_PROP_FRAME_HEIGHT, 110)

        # vc pode TENTAR limitar pelo opencv
        # cam1.set(cv2.CAP_PROP_FPS, 10) # n funciona para todas as cmâmeras
        # print(cam1.get(cv2.CAP_PROP_FPS)) # verifica se respeitou
        
        self.cap = cv2.VideoCapture(index)
        self.frame = None
        self.running = False
        self.lock = Lock() # todo ver se precisa mesmo

    def start(self):
        self.running = True
        self.thread = Thread(target=self._update)
        self.thread.start()

    def _update(self):
        while self.running:
            
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def read(self):
        with self.lock:
            return self.frame

    def stop(self):
        self.running = False
        self.thread.join() # todo ver se precisa mesmo
        self.cap.release()


def get_all_cameras(max_devices=10):
    """
    OpenCV LogLevels: 
    0 = SILENT   → nada
    1 = ERROR    → só erros
    2 = WARNING  → erros + warnings
    3 = INFO     → padrão (recomendado)
    4 = DEBUG    → extremamente verboso
    """
    cv2.setLogLevel(0) # desabilitando mensagem de log do opencv

    webcams = []
    for i in range(max_devices):
        
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            webcams.append(i)
            cap.release()
    
    cv2.setLogLevel(3) # habilitando logs do opencv novamente
    return webcams


