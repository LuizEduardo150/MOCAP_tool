from python_utils.utils import file_name_check_extension



def write_basic_file(output_path, file_name) -> bool:
    txt_struct = "" \
    "# Para o preenchimento, lembre de usar a orientação do personagem\n" \
    "# Ou seja, a sua esquerda é a direita do personagem e vice verça,\n" \
    "# pois ele deve estar de frente para a câmera.\n" \
    "\n" \
    "# braço Esquerdo\n" \
    "(11, 13) : \n" \
    "\n"\
    "# braço Direito\n" \
    "(12, 14) : \n" \
    "\n" \
    "# Antebraço esquerdo \n" \
    "(13, 15) : \n" \
    "\n" \
    "# Antebraço direito\n" \
    "(14, 16) : \n" \
    "\n" \
    "# Mão esquerda\n" \
    "(15, 17) : \n" \
    "\n" \
    "# Mão direita\n" \
    "(16, 18) : \n" \
    "\n" \
    "# Parte superior da perna esquerda\n" \
    "(23, 25) : \n" \
    "\n" \
    "# Parte superior da perna direita\n" \
    "(24, 26) : \n"\
    "\n" \
    "# Parte inferior da perna esquerda\n" \
    "(25, 27) : \n" \
    "\n" \
    "# Parte inferior da perna direita\n" \
    "(26, 28) : \n" \
    "\n" \
    "# Pé esquerdo\n" \
    "(27, 31) : \n" \
    "\n" \
    "# Pé direito\n" \
    "(28, 32) : \n" \
    "\n" \
    "# Cabeça\n" \
    "(9, 1) : \n" \
    "\n\n" \
    "# Os demais parâmetros são para ossos não rastreados pelo Media Pipe\n\n" \
    "# Osso principal da armature (Controla rotação global)\n" \
    "(0) : \n" \
    "\n" \
    "# Ossos que constituem a coluna: Coloque os nomes separados por vírgula,\n" \
    "# do osso mais alto para o mais baixo.\n" \
    "(c) : \n" \
    "\n\n" \
    "# Armature\n" \
    "(a) : \n"


    file = None
    file_name = file_name_check_extension(file_name, "txt")

    try:
        file = open(f"{output_path}/{file_name}", "w")            
    except:
        return False

    file.writelines(txt_struct)
    print(f'\nArquivo "{file_name}" salvo na pasta: "{output_path}"')

    file.close()
    return True



def write_step_by_step_file(output_path, file_name):
    file = None
    file_name = file_name_check_extension(file_name, "txt")

    txt_struct = "" \
    "# Para o preenchimento, lembre de usar a orientação do personagem\n" \
    "# Ou seja, a sua esquerda é a direita do personagem e vice verça,\n" \
    "# pois ele deve estar de frente para a câmera.\n" \
    "\n" \
    
    try:
        file = open(f"{output_path}/{file_name}", "w")            
    except:
        return False
    
    print("\nPreencha os campos com os nomes dos ossos no blender.\n\n", txt_struct)
    
    name = input("Braço Esquerdo: ")
    txt_struct += f"# braço Esquerdo\n(11, 13) : {name}\n\n" \
    
    name = input("Braço direito: ")
    txt_struct += f"# braço Direito\n(12, 14) : {name}\n\n" \

    name = input("Antebraço esquerdo: ")
    txt_struct += f"# Antebraço esquerdo \n(13, 15) : {name}\n\n" \

    name = input("Antebraço direito: ")
    txt_struct += f"# Antebraço direito\n(14, 16) : {name}\n\n" \

    name = input("Mão esquerda: ")
    txt_struct += f"# Mão esquerda\n(15, 17) : {name}\n\n" \

    name = input("Mão direita: ")
    txt_struct += f"# Mão direita\n(16, 18) : {name}\n\n" \

    name = input("Parte superior da perna esqueda: ")
    txt_struct += f"# Parte superior da perna esquerda\n(23, 25) : {name}\n\n" \
    
    name = input("Parte superior da perna direita: ")
    txt_struct += f"# Parte superior da perna direita\n(24, 26) : {name}\n\n"\

    name = input("Parte inferior da perna esquerda: ")
    txt_struct += f"# Parte inferior da perna esquerda\n(25, 27) : {name}\n\n" \
    
    name = input("Parte inferior da perna direita: ")
    txt_struct += f"# Parte inferior da perna direita\n(26, 28) : {name}\n\n" \

    name = input("Pé esquerdo: ")
    txt_struct += f"# Pé esquerdo\n(27, 31) : {name}\n\n" \
    
    name = input("Pé direito: ")
    txt_struct += f"# Pé direito\n(28, 32) : {name}\n"

    name = input("Cabeça: ")
    txt_struct += f"# Cabeça\n(9, 1) : {name}\n" \

    name = input("Osso principal da armature (Controla rotação global): ")
    txt_struct += "\n\n# Os demais parâmetros são para ossos não rastreados pelo Media Pipe\n\n" \
                  "# Osso principal da armature (Controla rotação global)\n" \
                  f"(0) : {name}\n\n"
    
    name = input("\nOssos que constituem a coluna: Coloque os nomes separados por vírgula, ordenados\n" \
                 "do osso mais alto para o mais baixo.\nNome(s) do(s) osso(s): ")
    txt_struct += "# Ossos que constituem a coluna: Coloque os nomes separados por vírgula,\n" \
                  "# do osso mais alto para o mais baixo.\n" \
                  f"(c) : {name}\n"

    name = input('\nNome do objeto "Armature" no blender: ')
    txt_struct += f"\n\n# Armature\n(a) : {name}\n\n"

    file.writelines(txt_struct)
    print(f'\nArquivo "{file_name}" salvo na pasta: "{output_path}"')
    file.close()
    
    return True



def get_bone_map_from_file(file_path) -> dict | None:
    file = None
    file_path = file_name_check_extension(file_path, "txt")

    try:
        file = open(file_path, "r")
    except:
        return None
    
    bone_map = dict()

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

        key_str = line_content[0].rstrip().lstrip()
        content = line_content[1].rstrip().lstrip()

        key_parts = key_str.replace("(", "").replace(")", "").split(",")
        
        if len(key_parts) == 2:
            key_first_part = int(key_parts[0])
            key_second_part = int(key_parts[1])
            
            bone_map[(key_first_part, key_second_part)] = content
        
        elif len(key_parts) == 1 and key_parts[0] == '0': # main
            bone_map[(0)] = content
        
        elif len(key_parts) == 1 and key_parts[0] == "a": # armature
            bone_map[(key_parts[0])] = content
        
        elif len(key_parts) == 1 and key_parts[0] == "c": # coluna
            if content.find(",") != -1:
                content = content.split(",")
            
            if type(content) is list and len(content) > 0:
                for i in range(len(content)):
                    content[i] = content[i].rstrip().lstrip()

            bone_map[(key_parts[0])] = content
        
    
    file.close()
    return bone_map
