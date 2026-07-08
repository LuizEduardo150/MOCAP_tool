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



def get_object_location_keyframes(obj):
    
    if not object_is_bpy_type(obj) or not object_ready_for_keyframe_animation(obj):
            return None
    
    if object_is_pose_bone(obj):    
        obj: bpy.types.PoseBone = obj

        action : bpy.types.Action = obj.id_data.animation_data.action
        data_path = f'pose.bones["{obj.name}"].location'
        fcurve = action.fcurve_ensure_for_datablock(obj.id_data, data_path, index=0)

    else:
        obj: bpy.types.Object = obj

        action : bpy.types.Action = obj.animation_data.action
        fcurve = action.fcurve_ensure_for_datablock(obj, "location", index=0)
    
    # Acessar keyframes pelo fcurve
    frames = []
    for k in fcurve.keyframe_points:
        frames.append(k.co.x)
    
    return frames



def get_object_rotation_keyframes(obj):
    
    if not object_is_bpy_type(obj) or not object_ready_for_keyframe_animation(obj):
        return None
    
    if object_is_pose_bone(obj):
        obj: bpy.types.PoseBone = obj
        
        action : bpy.types.Action = obj.id_data.animation_data.action
        data_path = f'pose.bones["{obj.name}"].rotation_euler'
        fcurve = action.fcurve_ensure_for_datablock(obj.id_data, data_path, index=0)
        
    else:
        obj: bpy.types.Object = obj
        
        action : bpy.types.Action = obj.animation_data.action
        fcurve = action.fcurve_ensure_for_datablock(obj, "rotation_euler", index=0)

    # Acessar keyframes pelo fcurve 
    frames = []
    for k in fcurve.keyframe_points:
        frames.append(k.co.x)
    
    return frames


def remove_all_pose_bones_location_keyframes(armature):

    if not object_is_bpy_type(armature) or not object_is_armature(armature):
        return False

    for bone in armature.pose.bones:
        key_list = get_object_location_keyframes(bone)

        if key_list is not None and len(key_list) > 0:
            
            for key_time in key_list:
                bone.keyframe_delete(
                    data_path="location",
                    frame=key_time
                )

    return True


def remove_all_pose_bones_rotation_keyframes(armature):
    if not object_is_bpy_type(armature) or not object_is_armature(armature):
        return False

    for bone in armature.pose.bones:
        key_list = get_object_rotation_keyframes(bone)

        if key_list is not None and len(key_list) > 0:
            
            for key_time in key_list:
                bone.keyframe_delete(
                    data_path="rotation_euler",
                    frame=key_time
                )

    return True


def remove_all_pose_bones_keyframes(armature):
    if not object_is_bpy_type(armature) or not object_is_armature(armature):
        return False
    
    ret1 = remove_all_pose_bones_location_keyframes(armature)
    ret2 = remove_all_pose_bones_rotation_keyframes(armature)
    
    return ret1 and ret2


def transform_all_pose_bones_to_eulerian_rotation(armature):
    if not object_is_bpy_type(armature) or not object_is_armature(armature):
        return False
    
    for bone in armature.pose.bones:
        bone.rotation_mode = 'XYZ'

    return True



def get_object_last_location_keyframe(obj):
    
    if not object_is_bpy_type(obj) or not object_ready_for_keyframe_animation(obj):
        return None

    if object_is_pose_bone(obj):
        obj: bpy.types.PoseBone = obj
        
        action : bpy.types.Action = obj.id_data.animation_data.action
        data_path = f'pose.bones["{obj.name}"].location'
        fcurve = action.fcurve_ensure_for_datablock(obj.id_data, data_path, index=0)

    else:
        obj: bpy.types.Object = obj
        
        action : bpy.types.Action = obj.animation_data.action
        fcurve = action.fcurve_ensure_for_datablock(obj, "location", index=0)
    
    if len(fcurve.keyframe_points) == 0:
        return -1

    return fcurve.keyframe_points[-1].co.x


def get_object_last_rotation_keyframe(obj):
    
    if not object_is_bpy_type(obj) or not object_ready_for_keyframe_animation(obj):
        return None

    if object_is_pose_bone(obj):
        obj: bpy.types.PoseBone = obj
        
        action : bpy.types.Action = obj.id_data.animation_data.action
        data_path = f'pose.bones["{obj.name}"].rotation_euler'
        fcurve = action.fcurve_ensure_for_datablock(obj.id_data, data_path, index=0)

    else:
        obj: bpy.types.Object = obj
        
        action : bpy.types.Action = obj.animation_data.action
        fcurve = action.fcurve_ensure_for_datablock(obj, "rotation_euler", index=0)
    
    if len(fcurve.keyframe_points) == 0:
        return -1

    return fcurve.keyframe_points[-1].co.x



def insert_location_keyframe(obj, values:list=None, frame_distance=1):
    """
    Inserir keyframe de posicao em um objeto no projeto blender

    :obj: Objeto do blender
    :values: lista com ate 3 posicoes referentes a x,y,z  (EX: [None, 1, None] "move só Y")
    :frame_distance: distancia de tempo entre um frame e outro
    """

    if not object_is_bpy_type(obj) or not object_ready_for_keyframe_animation(obj) \
        or values is None or frame_distance is None or len(values) == 0:
        return False

    keyframe = get_object_last_location_keyframe(obj)
    
    if keyframe is None:
        return False
    
    elif keyframe == -1: # inicio da animacao
        obj.keyframe_insert(data_path="location", frame=1)
        keyframe = 1

    # mover objeto nos eixos XYZ
    for i, value in enumerate(values):
        if i == 0 and value is not None:
            obj.location.x = value
        
        elif i == 1 and value is not None:
            obj.location.y = value

        elif i == 2 and value is not None:
            obj.location.z = value
        
        elif i > 2:
            break

    obj.keyframe_insert(
        data_path="location",
        frame= (keyframe + frame_distance)
    )

    return True

