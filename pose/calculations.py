from math import sqrt, acos, degrees, cos, radians, atan2


"""
Modulo python contendo todas as funcoes de calculo que serao usados
sobre os valores retornados pelo media pipe pose.
"""

def convert_mp_world_data_to_blender_format(frames:list):
    """
    Tornar o eixo Y do MP_Pose com mesmo sistema do blender,
    fazendo deslocamento dos valores se preciso.

    MP_Pose Y Zero: meio do corpo (perto do umbigo)
    Blender Y Zero: Depende de onde construiram o modelo, mas geralmente nos pés
    """

    if frames is None or len(frames) == 0:
        return None

    # __ (inverter sinais do Y) e (obter menor valor de Y em cada frame)
    for pose_list in frames:
        min = None

        for pose in pose_list:
            pose.y_world *= -1

            if min is None or pose.y_world < min:
                min = pose.y_world

        # __ fazer o deslocamento dos numeros do eixo Y
        # __ converter Y para Z    
        for pose in pose_list:
            if min < 0:
                pose.y_world = pose.y_world + (min * -1)
            else:
                pose.y_world = pose.y_world + min

            y_aux = pose.y_world
            pose.y_world = pose.z_world
            pose.z_world = y_aux


def get_correct_bone_index_sequence(pose_list, index1, index2):
    """
    Funcao para garantir que todos os vetores tenham a mesma direcao
    sendo a escolhida: esquerda para direita. Util para calculo de
    angulos diretores
    
    :returns: None (Caso de erro) | int, int
    """

    if pose_list is None or len(pose_list) != 33 or index1 > 32 or index2 > 32:
        return None, None
    
    if pose_list[index2].x_world > pose_list[index1].x_world:
        return index1, index2
    else:
        return index2, index1



def get_body_part_horizontal_rotation(pose_list, index1, index2):
    """
    Calcular a rotação horizontal (XZ) de uma parte do corpo formada
    por dois pontos do resultado do MediaPipe.
    
    OBS: ->NAO<- usar valores de index corrigidos por 'get_correct_bone_index_sequence'
    OBS2: Usar os valores da esquerda para direita (Do maior para o menor)
    """
    
    if pose_list is None or len(pose_list) != 33 or index1 > 32 or index2 > 32:
        return None
     
    d_x = pose_list[index2].x_world - pose_list[index1].x_world
    d_y = pose_list[11].y_world - pose_list[12].y_world

    return degrees(atan2(d_y, d_x))


def euclidean_distance_3d(pose_list, bone_index_1:int, bone_index_2:int, ignore_z=False):
    if pose_list is None or len(pose_list) == 0 or \
        bone_index_1 >= len(pose_list) or bone_index_2 >= len(pose_list):
        
        return None
    
    d_x = pose_list[bone_index_2].x_world - pose_list[bone_index_1].x_world
    d_y = pose_list[bone_index_2].y_world - pose_list[bone_index_1].y_world
    
    if not ignore_z:
        d_z = pose_list[bone_index_2].z_world - pose_list[bone_index_1].z_world
    else:
        d_z = 0

    return sqrt((d_x**2) + (d_y**2) + (d_z**2))


def direct_angle_x_3d(pose_list, bone_index_1, bone_index_2, ignore_z=False):
    if pose_list is None or len(pose_list) == 0 or \
        bone_index_1 >= len(pose_list) or bone_index_2 >= len(pose_list):
        
        return None
    
    IvI = euclidean_distance_3d(pose_list, bone_index_1, bone_index_2, ignore_z)
    d_x = pose_list[bone_index_2].x_world - pose_list[bone_index_1].x_world
    
    return degrees( acos ( (d_x / IvI) ) )

    

def direct_angle_y_3d(pose_list, bone_index_1, bone_index_2):
    if pose_list is None or len(pose_list) == 0 or \
        bone_index_1 >= len(pose_list) or bone_index_2 >= len(pose_list):
        
        return None
    
    IvI = euclidean_distance_3d(pose_list, bone_index_1, bone_index_2)
    
    d_y = pose_list[bone_index_2].y_world - pose_list[bone_index_1].y_world
    angle = acos ( (d_y / IvI) )

    return degrees(angle)


def direct_angle_z_3d(pose_list, bone_index_1, bone_index_2):
    if pose_list is None or len(pose_list) == 0 or \
        bone_index_1 >= len(pose_list) or bone_index_2 >= len(pose_list):
        
        return None
    
    IvI = euclidean_distance_3d(pose_list, bone_index_1, bone_index_2)
    
    d_z = pose_list[bone_index_2].z_world - pose_list[bone_index_1].z_world
    angle = acos ( (d_z / IvI) )

    return degrees(angle)


def check_directs_angles(x, y, z):
    """
    Funcao apenas para fase de desenvolvimento onde o
    resultado deve ser 1 ou muito proximo de 1.
    """
    
    x = radians(x)
    y = radians(y)
    z = radians(z)
    value = cos(x)**2 + cos(y)**2 + cos(z)**2
    
    return value


def body_aligned(pose_list, max_distance_btwn_pivots=6.0):
    """
    Verificar se um corpo rastrado pelo MediaPipe esta alinhado com a camera
    OBS: ->NAO<- usar valores de index corrigidos por 'get_correct_bone_index_sequence'
    OBS2: Não destingue corpo de frente ou de costas, apenas o alinhamento com a camera
    
    :returns: Boolean (corpo alinhado), float (certeza do modelo ao resultado)
    """

    r_shoulder = get_body_part_horizontal_rotation(pose_list, 12, 11)
    r_waist = get_body_part_horizontal_rotation(pose_list, 24, 23)

    certainty1 = (pose_list[12].get_combined_certainty() * 0.5) + (pose_list[11].get_combined_certainty() * 0.5)
    certainty2 = (pose_list[24].get_combined_certainty() * 0.5) + (pose_list[23].get_combined_certainty() * 0.5)
    certainty = (certainty1 * 0.5) + (certainty2 * 0.5)

    if (-max_distance_btwn_pivots <= r_shoulder <= max_distance_btwn_pivots) and \
       (-max_distance_btwn_pivots <= r_waist <= max_distance_btwn_pivots):
        return True, certainty
    
    else:
        return False, certainty


def body_is_aligned_t_pose(pose_list, maximum_deviation=5.0):
    """
    Verifica se um corpo está reto diante da câmera e em pose em T
    analiza a certeza do modelo sobre o resultado do rastreamento.

    :returns: None,None (Caso de erro) | boolen, float (esta em t pose, grau de certeza)
    """

    if pose_list is None or len(pose_list) == 0:
        return None, None
    
    align, cert = body_aligned(pose_list)

    if not align or cert < 0.8:
        return False, cert
    
    # __ obter os indices dos ossos ordenadamente
    b1_L_arm, b2_L_arm = get_correct_bone_index_sequence(pose_list, 11, 13)
    b1_L_forearm, b2_L_forearm = get_correct_bone_index_sequence(pose_list, 13, 15)
    b1_R_arm, b2_R_arm = get_correct_bone_index_sequence(pose_list, 14, 12)
    b1_R_forearm, b2_R_forearm = get_correct_bone_index_sequence(pose_list, 16, 14)


    rot_L_arm = direct_angle_x_3d(pose_list, b1_L_arm, b2_L_arm, True)
    cert1 = pose_list[b1_L_arm].get_combined_certainty()
    cert2 = pose_list[b2_L_arm].get_combined_certainty()
    cert_L_arm = (cert1 * 0.5) + (cert2 * 0.5)

    rot_L_forearm = direct_angle_x_3d(pose_list, b1_L_forearm, b2_L_forearm, True)
    cert1 = pose_list[b1_L_forearm].get_combined_certainty()
    cert2 = pose_list[b2_L_forearm].get_combined_certainty()
    cert_L_forearm = (cert1 * 0.5) + (cert2 * 0.5)

    rot_R_arm = direct_angle_x_3d(pose_list, b1_R_arm, b2_R_arm, True)
    cert1 = pose_list[b1_R_arm].get_combined_certainty()
    cert2 = pose_list[b2_R_arm].get_combined_certainty()
    cert_R_arm = (cert1 * 0.5) + (cert2 * 0.5)

    rot_R_forearm = direct_angle_x_3d(pose_list, b1_R_forearm, b2_R_forearm, True)
    cert1 = pose_list[b1_R_forearm].get_combined_certainty()
    cert2 = pose_list[b2_R_forearm].get_combined_certainty()
    cert_R_forearm = (cert1 * 0.5) + (cert2 * 0.5)    

    cert = (cert_L_arm * 0.25) + (cert_L_forearm * 0.25) + (cert_R_arm * 0.25) + (cert_R_forearm * 0.25)

    if (0-maximum_deviation <= rot_L_arm     <= 0+maximum_deviation) and \
       (0-maximum_deviation <= rot_L_forearm <= 0+maximum_deviation) and \
       (0-maximum_deviation <= rot_R_arm     <= 0+maximum_deviation) and \
       (0-maximum_deviation <= rot_R_forearm <= 0+maximum_deviation):
        
        return True, cert

    else:
        return False, cert


def euclidean_distance_for_hight(pose_list, ignore_z=False):
    if pose_list is None or len(pose_list) == 0:
        return 0.0
    
    # Criando um ponto ficticio no meio do corpo e na altura dos pes
    x = pose_list[23].x_world - pose_list[24].x_world
    y = pose_list[29].y_world
    z = pose_list[23].z_world

    d_x = x - pose_list[0].x_world
    d_y = y - pose_list[0].y_world
    d_z = 0 if ignore_z else z - pose_list[0].z_world
    
    return sqrt((d_x**2) + (d_y**2) + (d_z**2))


def get_body_shape(pose_list, t_pose_max_deviation=5.0, ignore_z = True):
    """
    Obter a altura e largura do corpo. Caso corpo estiver em posicao T,
    o calculo da largura sera de uma mao a outra, caso contrario, sera a
    largura do ombro.
        
    :returns: None | float, float, boolean, float (height, width, body_in_T_pose, certainty)
    """
    
    if pose_list is None or len(pose_list) != 33:
        return None, None, None, None
    
    tpose, cert = body_is_aligned_t_pose(pose_list, t_pose_max_deviation)
    if tpose:
        w = euclidean_distance_3d(pose_list, 16, 15, ignore_z) # maoR -> maoL         
        h = euclidean_distance_for_hight(pose_list)
        
    else:
        w = euclidean_distance_3d(pose_list, 12, 11, ignore_z)
        h = euclidean_distance_for_hight(pose_list, ignore_z)

    return h, w, tpose, cert

