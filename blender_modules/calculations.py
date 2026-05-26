import bpy # type: ignore

from blender_modules.utils import object_is_armature, object_is_pose_bone



def get_pose_bone_global_position(armature, pose_bone):

    if object_is_armature(armature) and not object_is_pose_bone(pose_bone):
        return None
    
    return (armature.matrix_world @ pose_bone.matrix).to_translation()


def get_pose_bone_global_head_position(armature, pose_bone):

    if object_is_armature(armature) and not object_is_pose_bone(pose_bone):
        return None
    
    return armature.matrix_world @ pose_bone.head


def get_pose_bone_global_tail_position(armature, pose_bone):
    if object_is_armature(armature) and not object_is_pose_bone(pose_bone):
        return None
    
    return armature.matrix_world @ pose_bone.tail