import bpy # type: ignore
from math import sqrt

from blender_modules.utils import object_is_armature, object_is_pose_bone



def get_pose_bone_global_position(armature, pose_bone):

    if not object_is_armature(armature) or not object_is_pose_bone(pose_bone):
        return None
    
    # inverter global para local
    vector = (armature.matrix_world @ pose_bone.matrix).to_translation()
    return vector[0], vector[2], vector[1]


def get_pose_bone_global_head_position(armature, pose_bone):

    if not object_is_armature(armature) or not object_is_pose_bone(pose_bone):
        return None
        
    # inverter global para local
    vector = armature.matrix_world @ pose_bone.head
    return vector[0], vector[2], vector[1]


def get_pose_bone_global_tail_position(armature, pose_bone):
    if not object_is_armature(armature) or not object_is_pose_bone(pose_bone):
        return None
    
    # inverter global para local
    vector = armature.matrix_world @ pose_bone.tail
    return vector[0], vector[2], vector[1]


def get_pose_bones_euclidean_distance(armature, bone1, bone2, bone_point="head"):
    """
    Obter distancia euclidiana entre dois ossos da armature em modo POSE (PoseBone).
    
    
    :arg armature: Objeto da armature
    :arg bone1: Objeto PoseBone 1
    :arg bone1: Objeto PoseBone 2
    :arg bone_point: Ponto utilizado do bone: head (DEFAULT) | tail | global
    
    :returns: float (sucess) | None (Fail)
    """

    if not object_is_armature(armature) or not object_is_pose_bone(bone1) or not object_is_pose_bone(bone2):
        return None
    
    if bone_point == "head":
        p_bone1 = get_pose_bone_global_head_position(armature, bone1) 
        p_bone2 = get_pose_bone_global_head_position(armature, bone2)

    elif bone_point == "tail":
        p_bone1 = get_pose_bone_global_tail_position(armature, bone1) 
        p_bone2 = get_pose_bone_global_tail_position(armature, bone2)

    elif bone_point == "global":
        p_bone1 = get_pose_bone_global_position(armature, bone1) 
        p_bone2 = get_pose_bone_global_position(armature, bone2)

    else:
        return None

    d_x = p_bone1[0] - p_bone2[0]
    d_y = p_bone1[1] - p_bone2[1]
    d_z = p_bone1[2] - p_bone2[2]

    return sqrt((d_x**2) + (d_y**2) + (d_z**2))

