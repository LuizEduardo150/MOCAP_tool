import bpy # type: ignore

from mathutils import Vector, Quaternion # type: ignore

from math import sqrt, degrees, acos

from blender_modules.utils import object_is_armature, object_is_pose_bone, object_is_a_3x3_matrix



def get_pose_bone_global_position(armature, pose_bone):

    if not object_is_armature(armature) or not object_is_pose_bone(pose_bone):
        return None
    
    return (armature.matrix_world @ pose_bone.matrix).to_translation()    


def get_pose_bone_global_head_position(armature, pose_bone):

    if not object_is_armature(armature) or not object_is_pose_bone(pose_bone):
        return None
        
    return armature.matrix_world @ pose_bone.head    


def get_pose_bone_global_tail_position(armature, pose_bone):
    if not object_is_armature(armature) or not object_is_pose_bone(pose_bone):
        return None
    
    return armature.matrix_world @ pose_bone.tail


def get_pose_bone_vector(armature, pose_bone) -> Vector:
    """
        Constroi o vetor que representa a direção do osso no blender, da cabeca até a cauda do poseBone
    """

    if not object_is_armature(armature) or not object_is_pose_bone(pose_bone):
        return None

    head = get_pose_bone_global_head_position(armature, pose_bone)
    tail = get_pose_bone_global_tail_position(armature, pose_bone)
    
    return tail - head


def get_bone_global_to_local_reference_list(pose_bone):
    """
        Obter a posição das componentes do vetor de osso em pose Mode, para ajustar a orientação
        global para local.
        
        OBS: Os valores retornados representam a posicao das componentes x, y, z seguidos de um inteiro
        -1 ou 1, para indicar sentido trocado ou não.
        
        :Returns sucess: lista com 3 tuplas: (index, sinal)
        :Returns fail: None
    """

    if not object_is_pose_bone(pose_bone):
        return None
    
    check_matrix = pose_bone.matrix.to_3x3()
    
    x_line = round(check_matrix[0][0]), round(check_matrix[0][1]), round(check_matrix[0][2])
    y_line = round(check_matrix[1][0]), round(check_matrix[1][1]), round(check_matrix[1][2])
    z_line = round(check_matrix[2][0]), round(check_matrix[2][1]), round(check_matrix[2][2])


    for index_x, global_x_signal in enumerate(x_line):
        if global_x_signal != 0:
            break
    
    for index_y, global_y_signal in enumerate(y_line):
        if global_y_signal != 0:
            break
    
    for index_z, global_z_signal in enumerate(z_line):
        if global_z_signal != 0:
            break

    return [(index_x, global_x_signal), (index_y, global_y_signal), (index_z, global_z_signal)]


def convert_vector_to_local_reference(original_vector: Vector, global_to_local_map: list):

    if original_vector is None or len(original_vector) != 3 or global_to_local_map is None or len(global_to_local_map) != 3:
        return None

    global_x_component = Vector((0, 0, 0))
    global_y_component = Vector((0, 0, 0))
    global_z_component = Vector((0, 0, 0))

    # deslocar valor de X
    global_x_component[global_to_local_map[0][0]] = original_vector[0] * global_to_local_map[0][1]
    
    # deslocar valor de y
    global_y_component[global_to_local_map[1][0]] = original_vector[1] * global_to_local_map[1][1]

    # deslocar valor de z
    global_z_component[global_to_local_map[2][0]] = original_vector[2] * global_to_local_map[2][1]


    return global_x_component + global_y_component + global_z_component




def get_pose_bone_local_y_axis_basic_direction(transform_matrix):
    """
    Obter a direção de apontamento simples dos eixo Y local, com base no eixo global do blender
    
    OBS: Não obtem medida precisa de apontamento, apenas valores de 0 a 1, para indicar o quão
    está apontando para um eixo global ou não.
    
    :returns fail: (None, None, None)
    :returns sucess: (int, int, int)
    """

    if not object_is_a_3x3_matrix(transform_matrix):
        return None, None, None
    
    x = round(transform_matrix.col[1][0])
    y = round(transform_matrix.col[1][1])
    z = round(transform_matrix.col[1][2])

    return x, y, z



def get_pose_bone_local_x_axis_basic_direction(transform_matrix):
    """
    Obter a direção de apontamento simples dos eixo X local, com base no eixo global do blender
    
    OBS: Não obtem medida precisa de apontamento, apenas valores de 0 a 1, para indicar o quão
    está apontando para um eixo global ou não.
    
    :returns fail: (None, None, None)
    :returns sucess: (int, int, int)
    """

    if not object_is_a_3x3_matrix(transform_matrix):
        return None, None, None
    
    x = round(transform_matrix.col[0][0])
    y = round(transform_matrix.col[0][1])
    z = round(transform_matrix.col[0][2])

    return x, y, z



def get_pose_bone_local_z_axis_basic_direction(transform_matrix):
    """
    Obter a direção de apontamento simples dos eixo Z local, com base no eixo global do blender
    
    OBS: Não obtem medida precisa de apontamento, apenas valores de 0 a 1, para indicar o quão
    está apontando para um eixo global ou não.
    
    :returns fail: (None, None, None)
    :returns sucess: (int, int, int)
    """

    if not object_is_a_3x3_matrix(transform_matrix):
        return None, None, None
    
    x = round(transform_matrix.col[2][0])
    y = round(transform_matrix.col[2][1])
    z = round(transform_matrix.col[2][2])

    return x, y, z


def blender_euclidean_distance_3d(armature, pose_bone, ignore_z=False):
    """
    Comprimento de um osso
    """
    if not object_is_armature(armature) or not object_is_pose_bone(pose_bone):
        return None
    
    head = get_pose_bone_global_head_position(armature, pose_bone)
    tail = get_pose_bone_global_tail_position(armature, pose_bone)
    
    d_x = tail[0] - head[0]
    d_y = tail[1] - head[1]

    if not ignore_z:
        d_z = tail[2] - head[2]
    else:
        d_z = 0

    return sqrt((d_x**2) + (d_y**2) + (d_z**2))



def blender_direct_angle_x_3d(armature, pose_bone, ignore_z=False, same_vector_orientation=True):
    if not object_is_armature(armature) or not object_is_pose_bone(pose_bone):
        return None
    
    head = get_pose_bone_global_head_position(armature, pose_bone)
    tail = get_pose_bone_global_tail_position(armature, pose_bone)

    IvI = blender_euclidean_distance_3d(armature, pose_bone, ignore_z)
    
    if same_vector_orientation:
        if tail[0] > head[0]:
            d_x = tail[0] - head[0]
        else:
            d_x = head[0] - tail[0]

    else:
        d_x = tail[0] - head[0]

    return degrees( acos ( (d_x / IvI) ) )



def blender_direct_angle_y_3d(armature, pose_bone, ignore_z=False):
    if not object_is_armature(armature) or not object_is_pose_bone(pose_bone):
        return None
    
    head = get_pose_bone_global_head_position(armature, pose_bone)
    tail = get_pose_bone_global_tail_position(armature, pose_bone)

    IvI = blender_euclidean_distance_3d(armature, pose_bone, ignore_z)
    d_y = tail[1] - head[1]

    return degrees( acos ( (d_y / IvI) ) )
