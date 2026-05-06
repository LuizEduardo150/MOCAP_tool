import av
import cv2


def get_av_video_container(video_path:str):
    """
        Retorna objeto para reproducao de video em loop.
        Args:
            video_path: caminho no diretorio para o video
        Returns:
            (video container, stream contendo dados do video)
            ou (None, None) em caso de erro.
    """
    try:
        container = av.open(video_path)
        return container, container.streams.video[0]

    except FileNotFoundError:
        return None, None

    
def create_video(file_name:str, camera_index:int, use_poselandmarks=False):
    from pose.media_pipe_pose import MPPoseProcessor, draw_landmarks_on_image
    
    if len(file_name) == 0:
        return
    
    if use_poselandmarks:
        pose_processor = MPPoseProcessor()
    
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        raise RuntimeError("Erro ao abrir a câmera")

    # Propriedades do vídeo
    fps = 30.0
    largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    altura = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Codec e arquivo de saída
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # ou 'MJPG', 'mp4v'
    out = cv2.VideoWriter(f'./out_in_files/{file_name}.avi', fourcc, fps, (largura, altura))

    if not out.isOpened():
        raise RuntimeError("VideoWriter NÃO abriu. Codec não suportado.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Grava o frame no vídeo
        out.write(frame)

        # Exibir os pontos rastreados pelo mediapipe
        if use_poselandmarks:
            result = pose_processor.process_image(frame)
            img_dr = draw_landmarks_on_image(frame, result, True)
            cv2.imshow('esqueleton', img_dr)

        cv2.imshow('Camera', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    # Libera recursos
    if use_poselandmarks:
        pose_processor.close_landmarker()
        
    cap.release()
    out.release()
    cv2.destroyAllWindows()



def rodar_video_cv():
    "!!! Problema no LINUX !!!! "
    cap = cv2.VideoCapture("./corpo2.avi")
    fps = cap.get(cv2.CAP_PROP_FPS)

    delay = int(1000 / fps) if fps > 0 else 30

    if not cap.isOpened():
        raise RuntimeError("Não foi possível abrir o vídeo")

    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("ERRO ")
            break  # fim do vídeo

        cv2.imshow('Video', frame)

        # controla a velocidade (tecla q para sair)
        
        if cv2.waitKey(delay) & 0xFF == ord('q'):
            print("ja foi")
            break

        cap.release()
        cv2.destroyAllWindows()


def rodar_video_av(source_file:str):
    container = av.open(source_file)

    stream = container.streams.video[0]

    fps = float(stream.average_rate)
    frame_count = stream.frames
    duration_sec = float(stream.duration * stream.time_base) if stream.duration else 0

    print(f"Qtd Frames: {frame_count}\nFPS: {fps}\nDuração: {duration_sec:.2f}\nresolucao:{stream.width}x{stream.height}")

    delay = int(1000 / fps)
    for frame in container.decode(video=0):
        img = frame.to_ndarray(format="bgr24")
        cv2.imshow("Video", img)
        
        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()



def rodar_camera_livre():
    """
    Funcao de teste para observar a camera
    """

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Erro ao abrir a câmera")

    # Propriedades do vídeo
    fps = 30.0
    cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame is not None:
            cv2.resizeWindow("Camera", 1080, 720)
            cv2.imshow('Camera', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    # Libera recursos
    cap.release()
    cv2.destroyAllWindows()
    