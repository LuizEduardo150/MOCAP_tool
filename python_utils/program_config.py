from os import listdir, mkdir
from os import path as os_path

from python_utils.utils import cast_int



def program_check():
    """
    checar: Pastas de arquivos de entrada e saida e configrar modelo de treinamento

    :Returns: None or (trained_model, input, output, incremental_method, emphasis_pose)
    """

    dir = listdir("./")
    
    #__ Conferir Pasta de Arquivos de entrada e saida

    if "files" in dir:
        files_dir = listdir("./files")

        if not "input" in files_dir:
            print('>> Pasta "input" não existia e foi criada na pasta "files".')
            mkdir("./files/input")

        if not "output" in files_dir:
            print('>> Pasta "output" não existia e foi criada na pasta "files".')
            mkdir("./files/output")

    else:
        mkdir("./files")
        mkdir("./files/input")
        mkdir("./files/output")

        print('>> Pasta "files" não existia foi criada na raiz do programa.')
        print('>> Pasta "input" não existia foi criada na raiz do programa.')
        print('>> Pasta "output" não existia foi criada na raiz do programa.')


    # __ Ler arquivo de configuracao

    if "config.txt" in dir:
        return read_config_file()
    

    # __ Criar arquivo de configuracao

    else:
        text = "# Informe o nome do arquivo de treinamento do modelo (.task) que será usado para a detecção do corpo em vídeo.\n" \
            "# Caso o arquivo esteja no do diretório raiz do programa, basta informar o nome do arquivo,\n" \
            "# caso contrário, coloque o caminho completo até o arquivo. \n\n" \
            "trained_model:\n\n" \
            "# Iforme o diretorio onde deseja que o programa registre \n" \
            "# os resultados. Se ficar em branco, será utilizado a\n" \
            '# pasta padrão do programa "files/output" \n\n' \
            "output:\n\n" \
            "# Iforme o diretorio onde deseja que o programa leia os arquivos \n" \
            "# de entrada. Se ficar em branco, será utilizado a \n" \
            '# pasta padrão do programa "files/input"\n' \
            "input:\n\n" \
            "# ____________________________________________________________________\n\n" \
            "# XX Seção crítica, mexa apenas se tiver certeza! XX\n\n" \
            "# Defina o valor incremental que será usado para identificar cada frame do vídeo para o rastreador\n" \
            '# Esse valor é usado em processamento de vídeos apenas e pode ser usado para suavisar "jitter"\n'\
            "# valores menores resultaram em uma suavização maior do movimento porém pode ignorar movimentos\n"\
            '# Valores maiores captam todos movimentos mas é mais sujeito a "jitter"\n' \
            "# Valores maiores que 10 não apresentam muita diferença.\n" \
            '# Valor vazio ou menor ou igual a zero será ignorado por tanto usando o metodo padrão (frame Timestamp)\n\n'\
            'video_process_incremental_value:\n\n'\
            "# ____________________________________________________________________\n\n" \
            "# Seção menos critica apenas para fins de debug para desenvolvimento:\n\n" \
            "# Informe se deseja marcar na visualização de vídeo, quando for exibido alguma\n" \
            "# posição conhecida, como pose em T (Braços erguidos na horiozntal e coluna reta)\n" \
            "# ou corpo alinhado com a câmera\n" \
            '# use "None" ou vazio: para não destacar poses\n' \
            '# use "tpose"        : para destacar pose em T\n' \
            '# use "align"        : para destacar corpo alinhado com a câmera\n\n' \
            "emphasis_pose: None\n\n\n"\
            "# ____________________________________________________________________\n\n"\
            "# Seção para configuração do programa injector.bin\n"\
            "# responsável por injetar o script python dentro de um projeto blender\n"\
            "# todos os campos a seguir devem ser preenchidos com diretório absoluto\n\n"\
            "# executável do blender:\n"\
            "blender_exec:\n\n"\
            "# projeto blender:\n"\
            "blender_project:"
        

        file = open("./config.txt", "w")
        file.writelines(text)
        file.close()
        print(">> Arquivo de configuração criado. Informe o modelo de treinamento nele antes de executar o programa novamente.")

    return None



def read_config_file():
    
    file = open("./config.txt", "r")

    trained_model = None
    output = None
    input = None
    incremental_method = None
    emphasis_pose = None

    while True:
        line = file.readline()
        
        if line is None or line == "":
            break
        
        line = line.lstrip().rstrip()

        if len(line) == 0 or line[0] == "#": # ignorando comentarios e linhas brancas
            continue
    
        line_content = line.split(':')
        
        if len(line_content) != 2:
            continue

        title = line_content[0].rstrip().lstrip()
        content = line_content[1].rstrip().lstrip()

        if title == "trained_model":
            if len(content) > 2:
                trained_model = content
        
        elif title == "output":
            if len(content) > 2:
                output = content

        elif title == "input":
            if len(content) > 2:
                input = content

        elif title == "video_process_incremental_value":
            if len(content) > 0:
                value = cast_int(content)
                
                if value is not None and value > 0:                    
                    incremental_method = value

        elif title == "emphasis_pose":
            if len(content) > 2:
                if content == "tpose":
                    emphasis_pose = "tpose"
                    
                elif content == "align":
                    emphasis_pose = "align"
                    
        else:
            continue
    
    file.close()

    if trained_model is None:
        print("xxxXXX  É obrigatório informar o modelo de treinamento (.task) no arquivo do configurações do programa! XXXxxx")
        return None

    elif not os_path.exists(trained_model):
        print("xxxXXX  Impossível alcançar o modelo de treinamento (.task) informado ou arquivo inexistente. XXXxxx")
        return None
    
    if input is None or not os_path.isdir(input):
        input = "./files/input"

    if output is None or not os_path.isdir(output):
        output = "./files/output"


    return trained_model, input, output, incremental_method, emphasis_pose
    