from threading import Thread, Event
from os import listdir

import cv2
import numpy as np

from python_utils.utils import cast_int, get_progress_bar
from python_utils.program_config import program_check

from capture.video_methods import get_av_video_container
from capture.image_methods import rotate_image, resize_by_scale

from pose.media_pipe_pose import MPPoseProcessor
from pose.storage import FramePoseWriter, FramePoseReader
from pose.utils_cv2 import draw_landmarks_on_image


"""
Modulo contendo o programa principal para processamento de videos e imagens
em sua vercao por linha de comando
"""


def progress_tread_function():
    global progress_bar

    while True:
        thr_event.wait()
        if end_program:
            break

        new_progress_bar = get_progress_bar(progress_bar_tot, progress_bar_value)
        if new_progress_bar != progress_bar:
            progress_bar = new_progress_bar
            print(new_progress_bar)


        thr_event.clear()


def choose_input_file(files:list):
    while True:
        index = input("\n>> indice do arquivo (q para cancelar) : ")
        if index.lower() == "q":
            return None
        
        index = cast_int(index)

        if index is None:
            print("\nX >> Opção inválida\n")
        
        elif 0 <= index < len(files):
            return files[index]
            
        else:
            print("\nX >> Índice forda dos limites\n")


def list_input_files(files:list):
    print("\n============== Input Files ================")
    for i, file in enumerate(files):
        print(f"({i}) - {file}")


#*********************************************************
#                           MAIN
#*********************************************************

# __ conferir estrutura de diretorios do programa
ret = program_check()
if ret is None:
    exit(1)

trained_model, input_path, output_path = ret # TODO usar os outros retornos!

progress_thread = Thread(target=progress_tread_function)
thr_event = Event()
end_program = False
progress_bar_tot = 15 # TODO Converfir necessidade de ter valor inicial
progress_bar_value = 0
progress_bar = ""
main_opt = ""

# __ Testar instancia do media pipe
if not MPPoseProcessor.test_existing_model(trained_model):
    print('\nxxxXXX É necessário primeiro informar em "config.txt" o modelo treinado de reconhecimento de corpo em vídeo (arquivo.task) XXXxxx\n')
    exit(0)

# __ Iniciar loop principal do programa
progress_thread.start()
while main_opt != "0":

    main_opt = input(
        "\n\n-------------- MOCAP EZ TOOL -------------------" \
        "\n| (1) Iniciar processamento de vídeo" \
        "\n| (2) Exibir captura sem gerar registro" \
        "\n| (3) Exibir poses registradas em arquivo binário" \
        "\n| (0) Sair do programa" \
        "\n------------------------------------------------" \
        "\n >> Sua escolha: "
    )

    # MENU: Iniciar processamento de vídeo
    if main_opt == "1":
        files = listdir(input_path)
        
        if len(files) == 0:
            print(f"\nX >> Não há arquivos salvos na pasta: {input_path}")
            continue
        
        list_input_files(files)
        file = choose_input_file(files)
        
        if file is None:
            print("* Nada a ser feito.")
            continue
        
        # __ Arquivo foi escolhido
        file_name = input("\n> Escolha o nome do arquivo a ser gerado: ")
        pose_writer = FramePoseWriter(output_path, file_name)
        processor = MPPoseProcessor(trained_model)

        container, stream = get_av_video_container(f"{input_path}/{file}")
        
        if container is None or not pose_writer.is_ready():
            print("\nXXX  Falha inesperada ou arquivo não suportado  XXX")
            continue
        
        if stream.frames == 0: # quantidade de frame = 0 pode ser uma foto.
            continue
        
        # __ Arquivos abertos
        shape_recorded = False
        fps = float(stream.average_rate)
        duration_sec = float(stream.duration * stream.time_base) if stream.duration else 0
        progress_bar_value = 0
        progress_bar_tot = stream.frames
        frame_timestamp_ms = 0
        print(f"\n{file}\nQtd Frames: {stream.frames}  |   Duração: {duration_sec:.2f}")

        rotation = input("\nSerá preciso aplicar rotação nos frames ?\n(S/Any): ").lower()
        exibition = input("Exibir frame e resultado do processamento ? \n(S/Any): ").lower()
        rotation = 90 if rotation == "s" else None
        
        # Rodar vídeo
        for frame in container.decode(video=0):
            img = frame.to_ndarray(format="bgr24")
            
            if not shape_recorded:
                h, w, _ = img.shape
                pose_writer.write_shape_of_video(h, w)
                shape_recorded = True

            if rotation is not None: 
                img = rotate_image(img, rotation)
            
            frame_timestamp_ms += float(frame.pts * frame.time_base * 1000)

            # __ Rastrear esqueleto
            processor.process_frame(img, frame_timestamp_ms)
            
            if processor.pose_info_result is not None and len(processor.pose_info_result) > 0:
                pose_writer.write_landmarks(processor.get_pose_info_list())
            
            # Sinalizar thread de exibicao de progresso
            progress_bar_value += 1
            thr_event.set()
            
            if exibition == 's':
                img = draw_landmarks_on_image(img, processor.get_pose_info_list())
                cv2.imshow("Video", img)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cv2.destroyAllWindows()
        container.close()
        pose_writer.close_file_descriptor()
        processor.close_landmarker()
        print(f'"{file_name}" salvo na pasta do programa: files/output')


    # MENU: Exibir captura sem gerar registro
    elif main_opt == "2":
        files = listdir(input_path)
        
        if len(files) == 0:
            print(f"\nX >> Não há arquivos salvos na pasta: {input_path}")
            continue
            
        list_input_files(files)
        file = choose_input_file(files)

        if file is None:
            print("* Nada a ser feito.")
            continue
        
        container, stream = get_av_video_container(f"{input_path}/{file}")

        if container is None:
            print("\nX > Falha inesperada")
            continue

        fps = float(stream.average_rate)
        frame_count = stream.frames
        duration_sec = float(stream.duration * stream.time_base) if stream.duration else 0
        print(f"\nQtd Frames: {frame_count}\nFPS: {fps}\nDuração: {duration_sec:.2f}\nresolucao:{stream.width}x{stream.height}")

        rotation = input("\nSerá preciso aplicar rotação nos frames ?\n(S/Any): ").lower()
        process = input("\nDeseja visualizar a captura dos ossos ?\n(S/Any): ").lower()
        
        rotation = 90 if rotation == "s" else None
        process = True if process == "s" else False
        delay = int(1000 / fps)
        processor = MPPoseProcessor(trained_model)

        for frame in container.decode(video=0):
            img = frame.to_ndarray(format="bgr24")

            if rotation is not None: 
                img = rotate_image(img, rotation)
            
            h, w, _ = img.shape

            if h > 1080 or w > 1920:
                prop1 = 1080/h
                prop2 = 1920/w
                prop = prop1-0.1 if prop1 < prop2 else prop2-0.1
                
                img = resize_by_scale(img, prop)

            if process:
                frame_timestamp_ms = float(frame.pts * frame.time_base * 1000)
                processor.process_frame(img, frame_timestamp_ms)
                img = draw_landmarks_on_image(img, processor.get_pose_info_list())

            cv2.imshow("Video", img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        processor.close_landmarker()
        container.close()


    # MENU : Exibir poses registradas em arquivo binário
    elif main_opt == '3':
        
        file_name = input("Nome do arquivo de registros: ")
        reader = FramePoseReader(output_path, file_name)

        if not reader.is_ready():
            print("\nXXX Arquivo não encontrado XXX")
            continue

        reader.load_data_from_file()
        hight, width = reader.get_record_image_shape()
        
        for pose_list in reader.records_list:

            image = np.ones((hight, width, 3), dtype=np.uint8)
            image = draw_landmarks_on_image(image, pose_list, [11, 13, 21, 15, 19, 17, 23, 25, 27, 29, 31, 1, 2, 3, 7, 9])

            cv2.imshow('view bin', image)
        
            if cv2.waitKey(15) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        reader.close_file_descriptor()

    else:
        if main_opt != "0":
            input("\nXXX Opção inválida XXX")


# Finalizar Recursos
if not thr_event.is_set():
    thr_event.set()

end_program = True
