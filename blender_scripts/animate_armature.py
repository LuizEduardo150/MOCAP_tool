from blender_modules.utils import transform_all_pose_bones_to_quaternion_rotation, \
                                  find_any_armature, anim_data_and_action_check_create,\
                                  object_ready_for_keyframe_animation, reset_armature_pose

from blender_modules.key_frame_methods import insert_rotation_keyframe
from blender_modules.calculations import get_pose_bone_global_head_position, get_pose_bone_vector, vector_similarity
from blender_modules.armature_checker import ArmatureChecker


from pose.storage import FramePoseReader
from pose.calculations import convert_mp_world_data_to_blender_format, get_body_part_horizontal_rotation
from pose.models import BODY_POSE_CONECTIONS_FOR_BLENDER, PoseInfos

from python_utils.bone_map_storage import get_bone_map_from_file

import bpy # type: ignore
from mathutils import Euler, Vector # type: ignore
from math import radians




def check_armature(map_bones):
    
    arm_checker = ArmatureChecker()

    if ('a') in map_bones.keys():
        arm_checker.set_armature(map_bones[('a')])

    if arm_checker.get_armature() is None:
        name = find_any_armature()
        arm_checker.set_armature(name)
        if name is not None:
            # warning
            print(f'|!| Não existia no arquivo de mapeamento uma armature definida ou válida. Programa utilizará: "{name}"')

    if (0) in map_bones.keys():
        arm_checker.set_main_control_pose_bone(map_bones[(0)])

    arm_checker.bone_map_mp_blender = map_bones

    ready, message = arm_checker.check_attribute_instances()
    print(message)
    
    if not ready:
        return None

    
    ready, message = arm_checker.armature_bones_configuration_is_correct()
    if not ready:
        print(message)
        return None


    if not object_ready_for_keyframe_animation(arm_checker.get_armature()):
        anim_data_and_action_check_create(arm_checker.get_armature())
        print('|!| Objeto não possuia um animation data, e foi criado com nome de "MocapAction"')

    return True


def get_hip_bone() -> None | bpy.types.PoseBone:
    if not "c" in map_bones.keys():
        return None

    bones = map_bones['c']
    if type(bones) is list:
        if len(bones) == 0:
            return None
        
        bone_name = bones[-1]

    else:
        bone_name = bones

    return arm.pose.bones.get(bone_name)


def get_media_pipe_bone_vector(pose_info1: PoseInfos, pose_info2:PoseInfos)-> Vector:

    vector1 = Vector((
        pose_info1.x_world,
        pose_info1.y_world,
        pose_info1.z_world
    ))
    vector2 = Vector((
        pose_info2.x_world,
        pose_info2.y_world,
        pose_info2.z_world
    ))

    return vector2 - vector1

def get_fake_waist_vector() -> Vector:
    bone1 : bpy.types.PoseBone = arm.pose.bones.get(map_bones[(24, 26)])
    bone2 : bpy.types.PoseBone = arm.pose.bones.get(map_bones[(23, 25)])
    p1 = get_pose_bone_global_head_position(arm, bone1)
    p2 = get_pose_bone_global_head_position(arm, bone2)
    return Vector(p2) - Vector(p1)


def apply_spine_rotation(mp_data):
    
    hip_bone = get_hip_bone()
    if hip_bone is None:
        return None

    mp_v = get_media_pipe_bone_vector(mp_data[24], mp_data[23])
    blender_v = get_fake_waist_vector()
    init = hip_bone.matrix.inverted() @ blender_v.normalized()
    than = hip_bone.matrix.inverted() @ mp_v.normalized()
    ret = init.rotation_difference(than)
    hip_bone.rotation_quaternion = ret.normalized()


def apply_rotation_self_axis(map_bones, mp_data):
    main_bone : bpy.types.PoseBone = arm.pose.bones.get(map_bones[0])
    rot = round(get_body_part_horizontal_rotation(mp_data, 12, 11))
    main_bone.rotation_quaternion = Euler((0, radians(rot), 0), "XYZ").to_quaternion()
    


def approximation_shifting_quaternion_w_value(key_value, mp_vector):
    """
        Aproximar vetor do blender com o do media pipe, ajustando o valor de W do
        quaternion de rotacao, com uma abordagem de busca local gulosa.
    """
    is_fake_bone = None
    def get_blender_vector():
        bpy.context.view_layer.update()
        if is_fake_bone:
            return get_fake_waist_vector()
        else:
            return get_pose_bone_vector(arm, pose_bone)

    if not key_value in map_bones.keys():
        return
    
    if key_value == "c":
        is_fake_bone = True
        pose_bone : bpy.types.PoseBone = get_hip_bone()
    else:
        is_fake_bone = False
        pose_bone : bpy.types.PoseBone = arm.pose.bones.get(map_bones[key_value])
    
    blender_v = get_blender_vector()
    value = vector_similarity(blender_v, mp_vector)

    w_original_value = pose_bone.rotation_quaternion.w
    original_sim = value

    cont = 0
    signal = None
    amt = 0.1
    current_w_value = None
    current_sim = None
    
    while True:

        if signal is None: # descobrir a direcao da exploracao

            pose_bone.rotation_quaternion.w = w_original_value + amt
            bpy.context.view_layer.update()
            increased_w_value = vector_similarity(get_blender_vector(), mp_vector)

            pose_bone.rotation_quaternion.w = w_original_value - amt
            bpy.context.view_layer.update()
            reduced_w_value = vector_similarity(get_blender_vector(), mp_vector)

            if increased_w_value > reduced_w_value:
                signal = 1
            else:
                signal = -1

            pose_bone.rotation_quaternion.w = w_original_value
            bpy.context.view_layer.update()

        cont += 1
        current_w_value = pose_bone.rotation_quaternion.w
        current_sim = vector_similarity(get_blender_vector(), mp_vector)

        # Explorar
        pose_bone.rotation_quaternion.w += (amt*signal)
        bpy.context.view_layer.update()

        sim = vector_similarity(get_blender_vector(), mp_vector)
        
        if sim < current_sim:
            pose_bone.rotation_quaternion.w = current_w_value
            bpy.context.view_layer.update()
            break
        
        # limite
        if cont == 1000:
            break

    # Avaliar resultado da aproximacao
    if current_sim < original_sim:
        pose_bone.rotation_quaternion.w = w_original_value

    bpy.context.view_layer.update()


    

def animate_armature(records_list):
    steps = len(records_list)

    # _ percorrer frames
    for i, mp_data in enumerate(records_list):
        reset_armature_pose(arm)

        apply_rotation_self_axis(map_bones, mp_data)
        bpy.context.view_layer.update()
        insert_rotation_keyframe(main_bone, 5)


        apply_spine_rotation(mp_data)
        bpy.context.view_layer.update()
        
        # check result
        mp_v = get_media_pipe_bone_vector(mp_data[24], mp_data[23])
        approximation_shifting_quaternion_w_value("c", mp_v)
        insert_rotation_keyframe(get_hip_bone(), 5)

        
        # _ percorrer os ossos da armature
        for bone_key in BODY_POSE_CONECTIONS_FOR_BLENDER:
            
            # __ Vetor do osso blender
            pose_bone : bpy.types.PoseBone =  arm.pose.bones.get(map_bones[bone_key])
            blender_bone_vector = get_pose_bone_vector(arm, pose_bone)

            # __ Vetor do osso media Pipe
            mp_bone_vector = get_media_pipe_bone_vector(mp_data[bone_key[0]], mp_data[bone_key[1]])

            # __ Transformar vetores para orientacao local do PoseBone
            init = pose_bone.matrix.inverted() @ blender_bone_vector.normalized()
            than = pose_bone.matrix.inverted() @ mp_bone_vector.normalized()

            ret = init.rotation_difference(than)
            pose_bone.rotation_quaternion = ret.normalized()

            approximation_shifting_quaternion_w_value(bone_key, mp_bone_vector)
            insert_rotation_keyframe(pose_bone, 5)

        print(f"\r>> passo {i+1} de {steps}", end="")



def main():
    global arm, map_bones, main_bone

    props = bpy.context.scene.mocap_form
    file = props.pose_file
    map_file = props.bone_map_file

    map_bones = get_bone_map_from_file(map_file)
    if map_bones is None:
        print(f'XXX Arquivo de mapeamento "{map_file}" não existe XXX')
        return None

    ret = check_armature(map_bones)
    if not ret:
        return None


    arm  = bpy.data.objects.get(map_bones[('a')])
    main_bone = arm.pose.bones.get(map_bones[(0)])

    reader = FramePoseReader(file)
    if not reader.is_ready():
        print(f'XXX Arquivo "{file}" não existe XXX')
        return None

    reader.load_data_from_file()
    reader.close_file_descriptor()
    print("Informações lidas dos arquivos.")

    convert_mp_world_data_to_blender_format(reader.records_list)
    transform_all_pose_bones_to_quaternion_rotation(arm)

    animate_armature(reader.records_list)



# **************************
#   main function
# **************************
arm : bpy.types.Armature = None
main_bone : bpy.types.PoseBone = None
map_bones = None

main()
