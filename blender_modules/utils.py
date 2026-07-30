import bpy # type: ignore

from mathutils import Matrix # type: ignore



def object_is_bpy_type(obj):
    
    if obj is None:
        return False
    
    return isinstance( obj, bpy.types.bpy_struct )


def object_is_armature(obj) -> bool:

    if not object_is_bpy_type(obj):
        return False

    try:
        if obj.type == "ARMATURE":
            return True
        
        else:
            return False
    
    except:
        return False


def object_is_pose_bone(obj):
    
    if not object_is_bpy_type(obj):
        return False

    return isinstance(obj, bpy.types.PoseBone)


def object_is_a_3x3_matrix(obj):
    if obj is None or not type(obj) is Matrix or len(obj) != 3:
        return False
    else:
        return True



def find_any_armature() -> str | None:
    """
    Retorna o nome da primeira armature encontrada no arquivo, se existir.
    """
    for obj in bpy.data.objects:
        if object_is_armature(obj):
            return obj.name
    return None


def get_all_pose_bones_name_list_from_armature(armature):
    if not object_is_armature(armature):
        return None

    bone_names = []

    for bone in armature.pose.bones:
        bone_names.append(bone.name)

    return bone_names


def object_ready_for_keyframe_animation(obj):
    if not object_is_bpy_type(obj):
        return False
    
    if obj.id_data.animation_data is None:
        return False

    else:
        if obj.id_data.animation_data.action is None:
            return False
        else:
            return True



def anim_data_and_action_check_create(obj):
    if not object_is_bpy_type(obj):
        return False
    
    if obj.id_data.animation_data is None:
        obj.animation_data_create()

    if obj.id_data.animation_data.action is None:
        obj.id_data.animation_data.action = bpy.data.actions.new(name="MocapAction")

    return True



def transform_all_pose_bones_to_quaternion_rotation(armature):
    if not object_is_bpy_type(armature) or not object_is_armature(armature):
        return False
    
    for bone in armature.pose.bones:
        bone.rotation_mode = 'QUATERNION'

    return True



def reset_armature_pose(armature):
    if not object_is_armature(armature):
        return False

    for bone_ in armature.pose.bones:
        bone_.rotation_quaternion = (1.0, 0, 0, 0)

    bpy.context.view_layer.update()
    return True