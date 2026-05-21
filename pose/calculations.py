from math import sqrt, acos, degrees, cos, radians, atan2


"""
Modulo python contendo todas as funcoes de calculo que serao usados
sobre os valores retornados pelo media pipe pose.
"""


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
    """
    
    if pose_list is None or len(pose_list) != 33 or index1 > 32 or index2 > 32:
        return None
     
    d_x = pose_list[index2].x_world - pose_list[index1].x_world
    d_z = pose_list[index2].z_world - pose_list[index1].z_world

    return degrees(atan2(d_z, d_x))


def euclidean_distance_3d(pose_list, bone_index_1:int, bone_index_2:int, ignore_z=False):
    if pose_list is None or len(pose_list) < 0 or \
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
    #print(f">> 1: {bone_index_1} 2:{bone_index_2}")
    if pose_list is None or len(pose_list) < 0 or \
        bone_index_1 >= len(pose_list) or bone_index_2 >= len(pose_list):
        
        return None
    
    IvI = euclidean_distance_3d(pose_list, bone_index_1, bone_index_2, ignore_z)
    d_x = pose_list[bone_index_2].x_world - pose_list[bone_index_1].x_world
    
    return degrees( acos ( (d_x / IvI) ) )

    

def direct_angle_y_3d(pose_list, bone_index_1, bone_index_2):
    if pose_list is None or len(pose_list) < 0 or \
        bone_index_1 >= len(pose_list) or bone_index_2 >= len(pose_list):
        
        return None
    
    IvI = euclidean_distance_3d(pose_list, bone_index_1, bone_index_2)
    
    d_y = pose_list[bone_index_2].y_world - pose_list[bone_index_1].y_world
    angle = acos ( (d_y / IvI) )

    return degrees(angle)


def direct_angle_z_3d(pose_list, bone_index_1, bone_index_2):
    if pose_list is None or len(pose_list) < 0 or \
        bone_index_1 >= len(pose_list) or bone_index_2 >= len(pose_list):
        
        return None
    
    IvI = euclidean_distance_3d(pose_list, bone_index_1, bone_index_2)
    
    d_z = pose_list[bone_index_2].z_world - pose_list[bone_index_1].z_world
    angle = acos ( (d_z / IvI) )

    return degrees(angle)


def check_directs_angles(x, y, z):
    x = radians(x)
    y = radians(y)
    z = radians(z)
    value = cos(x)**2 + cos(y)**2 + cos(z)**2
    
    return value


def body_in_front_view(pose_list, max_distance_btwn_pivots=5.0):
    """
    Verificar se um corpo rastrado pelo MediaPipe esta de frente para a camera
    OBS: ->NAO<- usar valores de index corrigidos por 'get_correct_bone_index_sequence'
    """

    rot_z = direct_angle_z_3d(pose_list, 12, 11)
    
    if 90+max_distance_btwn_pivots >= rot_z >= 90-max_distance_btwn_pivots:
        return True

    r_shoulder = get_body_part_horizontal_rotation(pose_list, 12, 11)
    r_waist = get_body_part_horizontal_rotation(pose_list, 24, 23)
    r_ears = get_body_part_horizontal_rotation(pose_list, 8, 7)
    r_mouth = get_body_part_horizontal_rotation(pose_list, 10, 9)

    if (0-max_distance_btwn_pivots <= r_shoulder <= 0+max_distance_btwn_pivots) and \
       (0-max_distance_btwn_pivots <= r_waist <= 0+max_distance_btwn_pivots) and \
       (0-max_distance_btwn_pivots <= r_ears <= 0+max_distance_btwn_pivots) and \
       (0-max_distance_btwn_pivots <= r_mouth <= 0+max_distance_btwn_pivots):
        return True
    else:
        return False


def body_is_in_front_t_pose(pose_list, maximum_deviation=5.0):
    if pose_list is None or len(pose_list) < 0:
        return None
    
    if not body_in_front_view(pose_list):
        return False
    
    b1_L_arm, b2_L_arm = get_correct_bone_index_sequence(pose_list, 11, 13)
    b1_L_forearm, b2_L_forearm = get_correct_bone_index_sequence(pose_list, 13, 15)
    b1_R_arm, b2_R_arm = get_correct_bone_index_sequence(pose_list, 14, 12)
    b1_R_forearm, b2_R_forearm = get_correct_bone_index_sequence(pose_list, 16, 14)

    rot_L_arm = direct_angle_x_3d(pose_list, b1_L_arm, b2_L_arm, True)
    rot_L_forearm = direct_angle_x_3d(pose_list, b1_L_forearm, b2_L_forearm, True)
    rot_R_arm = direct_angle_x_3d(pose_list, b1_R_arm, b2_R_arm, True)
    rot_R_forearm = direct_angle_x_3d(pose_list, b1_R_forearm, b2_R_forearm, True)

    if (0-maximum_deviation <= rot_L_arm     <= 0+maximum_deviation) and \
       (0-maximum_deviation <= rot_L_forearm <= 0+maximum_deviation) and \
       (0-maximum_deviation <= rot_R_arm     <= 0+maximum_deviation) and \
       (0-maximum_deviation <= rot_R_forearm <= 0+maximum_deviation):
        
        return True

    else:
        return False
    




"""
def direct_angle_x_2d(x1, x2, y1, y2):
    dx = x2 - x1
    dy = y2 - y1
    
    print("2d_X: ", degrees(atan2( dy, dx )))


def direct_angle_y_2d(x1, x2, y1, y2):
    dx = x2 - x1
    dy = y2 - y1
    
    degrees(atan2( dx, dy ))
"""


