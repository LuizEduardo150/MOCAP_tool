import bpy # type: ignore
from math import sqrt, degrees, acos

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


def blender_direct_angle_x_3d(armature, pose_bone, ignore_z=False):
    if not object_is_armature(armature) or not object_is_pose_bone(pose_bone):
        return None
    
    head = get_pose_bone_global_head_position(armature, pose_bone)
    tail = get_pose_bone_global_tail_position(armature, pose_bone)

    IvI = blender_euclidean_distance_3d(armature, pose_bone, ignore_z)
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

