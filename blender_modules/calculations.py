import bpy # type: ignore
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


def search_for_forward_direction(arm, map_bones:dict):
    
    if not object_is_armature(arm) or map_bones is None or len(map_bones) == 0:
        return None

    for key in map_bones.keys():
        if key == (27, 29) or key == (28, 30):
            bone = arm.pose.bones.get(map_bones[key])
            vector = get_pose_bone_local_y_axis_basic_direction(bone.matrix.to_3x3())
            
            if vector[0] != 0: # X
                if vector[0] > 0:
                    return "x+"
                else:
                    return "x-"
            
            elif vector[1] != 0: # Y
                if vector[1] > 0:
                    return "y+"
                else:
                    return "y-"

            elif vector[2] != 0: # Z
                if vector[2] > 0:
                    return "z+"
                else:
                    return "z-"

    return None



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