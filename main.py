from threading import Thread, Event
from os import listdir

import cv2
import numpy as np

from python_utils.utils import cast_int, get_progress_bar
from python_utils.program_config import program_check
from python_utils.bone_map_storage import write_basic_file, write_step_by_step_file

from capture.video_methods import get_av_video_container
from capture.image_methods import rotate_image, resize_by_scale

from pose.media_pipe_pose import MPPoseProcessor
from pose.storage import FramePoseWriter, FramePoseReader
from pose.utils_cv2 import draw_landmarks_on_image
from pose.calculations import body_is_aligned_t_pose, body_aligned


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
            print(f"\r{new_progress_bar}", end="")

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


def dev_process_image():
    files = listdir(input_path)
        
    if len(files) == 0:
        print(f"\nX >> Não há arquivos salvos na pasta: {input_path}")
        return
    
    list_input_files(files)
    file = choose_input_file(files)
    
    if file is None:
        return
    
    img = cv2.imread(f"{input_path}/{file}")
    
    if img is None:
        print("\nXXX  Falha inesperada ou arquivo não suportado  XXX")
        return
            
    file_name = "image_" + input("\n> Escolha o nome do arquivo a ser gerado: ")
    pose_writer = FramePoseWriter(output_path, file_name)

    if not pose_writer.is_ready():
        print(f'\nXXX  Impossível gerar arquivo de saída "{output_path}/{file_name}"  XXX')
        return
    
    processor = MPPoseProcessor(trained_model)
    shape_recorded = False
    
    h, w, _ = img.shape

    if h > 1080 or w > 1920:
        prop1 = 1080/h
        prop2 = 1920/w
        prop = prop1-0.1 if prop1 < prop2 else prop2-0.1
        img = resize_by_scale(img, prop)
        h, w, _ = img.shape

    if not shape_recorded:
        pose_writer.write_shape_of_video(h, w)
        shape_recorded = True

    # __ Rastrear esqueleto
    processor.process_image(img)
    if len(processor.pose_info_result) != 33: # sem registros
        return

    #  __ Armazenar rastreamento
    if processor.pose_info_result is not None and len(processor.pose_info_result) > 0:
        pose_writer.write_landmarks(processor.get_pose_info_list())
    
    img = draw_landmarks_on_image(img, processor.get_pose_info_list())

    cv2.imshow("res", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    processor.close_landmarker()
    pose_writer.close_file_descriptor()

    print(f'"{file_name}" salvo na pasta do programa: files/output')


def dev_show_pose_from_image():
    file_name = input("Nome do arquivo de registros: ")
    
    reader = FramePoseReader(output_path, file_name)

    if not reader.is_ready():
        print("\nXXX Arquivo não encontrado XXX")
        return

    reader.load_data_from_file()
    height, width = reader.get_record_image_shape()
    
    for pose_list in reader.records_list:
        
        image = np.ones((height, width, 3), dtype=np.uint8)
        image = draw_landmarks_on_image(image, pose_list, [11, 13, 21, 15, 19, 17, 23, 25, 27, 29, 31, 1, 2, 3, 7, 9])
    
    cv2.imshow('process result', image)
    cv2.waitKey(0)        
    cv2.destroyAllWindows()
    reader.close_file_descriptor()



def map_bones_menu():
    
    def get_help():
        print(
            "\n\nO mapeamento dos ossos é a parte responsável em identificar os ossos\n" \
            "da armature no Blender que correspondem aos pontos rastreados do corpo pelo\n" \
            "Media Pipe.\n\n", \
            "Essa etapa é crucial para conseguir utilizar os dados processados pelo Media\n" \
            "Pipe no Blender para gerar a animação.\n\n", \
            "Neste menu existem duas opções:\n" \
            "  1- gerar o arquivo de configuração simples para ser preenchido manualmente\n",\
            "     em um editor de texto.\n" \
            "  2- opção do programa com passo a passo para gerar o arquivo completo.\n\n",\

            "Os arquivos de configuração são de formato textual e seguem a seguinte estrutura:\n" \
            "  * Linhas começadas com # indicam comentário, e não serão lidas.\n" \
            "  * Linhas começadas por uma tupla com dois números inteiros, seguida de : (Dois pontos)\n"\
            "     e por fim, o nome do osso no blender. Por exemplo:\n", \
            "     (11, 13) : Braço.L\n" \
            '  * Linhas com apenas um caractere entre () "parenteses": Ossos não rastreados pelo Media\n' \
            '     Pipe, mas que são importantes para a animação.\n'
        )
    
    bm_opt = ""
    while bm_opt != "0" and bm_opt.lower() != 'q':
        
        bm_opt = input(
            "\n\n------------------ Map bones -------------------" \
            "\n| (1) Criar estrutura em arquivo simples (irei edita-lo)" \
            "\n| (2) Gerar arquivo de mapeamento com passo a passo" \
            "\n| (3) Manual sobre mapeamentos dos ossos " \
            "\n| (0) Sair do menu atual" \
            "\n--------------------------------------------------" \
            "\n >> Sua escolha: "
        )

        if bm_opt == '1':
            file_name = input("Escolha o nome do arquivo a ser gerado.\nNome:")
            if not write_basic_file(output_path, file_name):
                print('Falha ao criar arquivo, verifique o diretório de "outputs" do programa.')

        elif bm_opt == '2':
            file_name = input("Escolha o nome do arquivo a ser gerado.\nNome:")
            if not write_step_by_step_file(output_path, file_name):
                print('Falha ao criar arquivo, verifique o diretório de "outputs" do programa.')

        elif bm_opt == '3':
            get_help()

        else:
            if bm_opt != "0" and bm_opt.lower() != 'q':
                input("\nXXX Opção inválida XXX")


#*********************************************************
#                           MAIN
#*********************************************************

# __ conferir estrutura de diretorios do programa
check_ret = program_check()
if check_ret is None:
    exit(1)

trained_model, input_path, output_path, incremental_method, emphasis_pose = check_ret
progress_thread = Thread(target=progress_tread_function)
thr_event = Event()
end_program = False
progress_bar_tot = None
progress_bar_value = 0
progress_bar = ""
main_opt = ""

# __ Testar instancia do media pipe
if not MPPoseProcessor.test_existing_model(trained_model):
    print('\nxxxXXX É necessário primeiro informar em "config.txt" o modelo treinado de reconhecimento de corpo em vídeo (arquivo.task) XXXxxx\n')
    exit(0)

# __ Iniciar loop principal do programa
progress_thread.start()
while main_opt != "0" and main_opt.lower() != 'q':

    main_opt = input(
        "\n\n-------------- MOCAP TOOL -------------------" \
        "\n| (1) Iniciar processamento de vídeo" \
        "\n| (2) Exibir captura sem gerar registro" \
        "\n| (3) Exibir poses registradas em arquivo binário" \
        "\n| (4) Prepara arquivo de mapeamento de ossos"
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
            continue
        
        # __ Arquivo foi escolhido
        container, stream = get_av_video_container(f"{input_path}/{file}")
        if container is None:
            print("\nXXX  Falha inesperada ou arquivo não suportado  XXX")
            continue
        
        if stream.frames <= 5: # Pouca quantidade de frames pode ser uma foto (0) ou video muito curto.
            print("\nXXX  Quantidade insuficiente de frames  XXX")
            continue
        
        file_name = input("\n> Escolha o nome do arquivo a ser gerado: ")
        pose_writer = FramePoseWriter(output_path, file_name)

        if not pose_writer.is_ready():
            print(f'\nXXX  Impossível gerar arquivo de saída "{output_path}/{file_name}"  XXX')
            continue
        
        # __ Video e descritores abertos
        processor = MPPoseProcessor(trained_model)
        shape_recorded = False
        body_size_cert = 0.0

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

            if incremental_method is None:
                frame_timestamp_ms = float(frame.pts * frame.time_base * 1000)
            else:
                frame_timestamp_ms += incremental_method

            if rotation is not None: 
                img = rotate_image(img, rotation)

            h, w, _ = img.shape

            if h > 1080 or w > 1920:
                prop1 = 1080/h
                prop2 = 1920/w
                prop = prop1-0.1 if prop1 < prop2 else prop2-0.1
                img = resize_by_scale(img, prop)
                h, w, _ = img.shape

            if not shape_recorded:
                pose_writer.write_shape_of_video(h, w)
                shape_recorded = True

            # __ Rastrear esqueleto
            processor.process_frame(img, frame_timestamp_ms)
            if len(processor.pose_info_result) != 33: # sem registros
                continue

            #  __ Armazenar rastreamento
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
        processor.close_landmarker()
        pose_writer.close_file_descriptor()

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
        frame_timestamp_ms = 0

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
                if incremental_method is None:
                    frame_timestamp_ms = float(frame.pts * frame.time_base * 1000)
                else:
                    frame_timestamp_ms += incremental_method
                
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
        height, width = reader.get_record_image_shape()
        
        if len(reader.records_list) <= 2:
            print("\nXXX Arquivo contem quantidade insuficiente de registros XXX")
            reader.close_file_descriptor()
            continue

        for pose_list in reader.records_list:
            if emphasis_pose is None:
                pose = False
            elif emphasis_pose == "align":
                pose, _ = body_aligned(pose_list)    
            elif emphasis_pose == "tpose":
                pose, _ = body_is_aligned_t_pose(pose_list, 20)
    
            if pose:
                image = np.full((height, width, 3), (0, 150, 0), dtype=np.uint8)
            else:
                image = np.ones((height, width, 3), dtype=np.uint8)
            
            image = draw_landmarks_on_image(image, pose_list, [11, 13, 21, 15, 19, 17, 23, 25, 27, 29, 31, 1, 2, 3, 7, 9])

            cv2.imshow('view bin', image)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        reader.close_file_descriptor()


    elif main_opt == "4":
        map_bones_menu()


    # __ Funcao escondida para uso na fase de desenvolvimento
    elif main_opt == "-7":
        
        dev_opt = ""
        while dev_opt != '0' and dev_opt.lower() != 'q':
            dev_opt = input(
                "\n\n---------- [DEV: DEBUG Options] --------------" \
                "\n| (1) Processamento em imagem" \
                "\n| (2) Exibir poses registradas em arquivo binário" \
                "\n| (0) Sair do DEV Menu " \
                "\n------------------------------------------------" \
                "\n >> Sua escolha: "
            )

            if dev_opt == "1" :
                dev_process_image()

            elif dev_opt == "2" :
                dev_show_pose_from_image()

            else:
                if dev_opt != '0' and dev_opt.lower() != "q":
                    input("\nXXX Opção inválida XXX")


    else:
        if main_opt != "0" and main_opt.lower() != 'q':
            input("\nXXX Opção inválida XXX")


# Finalizar Recursos
if not thr_event.is_set():
    thr_event.set()

end_program = True
