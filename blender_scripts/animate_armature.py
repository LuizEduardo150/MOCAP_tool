from blender_modules.utils import transform_all_pose_bones_to_eulerian_rotation, \
                                  find_any_armature, anim_data_and_action_check_create,\
                                  object_ready_for_keyframe_animation

from blender_modules.armature_animator import ArmatureAnimator

from blender_modules.calculations import search_for_forward_direction


from pose.storage import FramePoseReader
from pose.calculations import convert_mp_world_data_to_blender_format

from python_utils.bone_map_storage import get_bone_map_from_file




# Utilizar main em funcao pois no blender comandos como exit() quebram a aplicacao
def main():
    mppose_output_path = "/home/luiz-eduardo/Documents/tcc_project/files/output"
    file = "eu_frente.pkl"
    map_file = "MapBonesBlender.txt"


    ''' CARREGAR RECURSOS EM ARQUIVOS ============================================= '''

    reader = FramePoseReader(mppose_output_path, file)
    if not reader.is_ready():
        print(f'XXX Arquivo "{file}" não existe em: "{mppose_output_path}" XXX')
        return None
    
    map_bones = get_bone_map_from_file(mppose_output_path, map_file)
    if map_bones is None:
        print(f'XXX Arquivo de mapeamento "{map_file}" não existe em: "{mppose_output_path}" XXX')
        return None

    reader.load_data_from_file()
    reader.close_file_descriptor()
    print("Informações lidas dos arquivos.")
    
    ''' =========================================================================== '''


    ''' PREPARAR O ANIMADOR ======================================================= '''
    
    animator = ArmatureAnimator()

    if ('a') in map_bones.keys():
        animator.set_armature(map_bones[('a')])

    if animator.get_armature() is None:
        name = find_any_armature()
        animator.set_armature(name)
        if name is not None:
            # warning
            print(f'|!| Não existia no arquivo de mapeamento uma armature definida ou válida. Programa utilizará: "{name}"')

    if (0) in map_bones.keys():
        animator.set_main_control_pose_bone(map_bones[(0)])
    
    if ("forward") in map_bones.keys():
        animator.set_forward_axis(map_bones[("forward")])

    animator.bone_map_mp_blender = map_bones

    ready, message = animator.check_attribute_instances()
    print(message)
    
    if not ready:
        return None
    
    ready, message = animator.armature_bones_configuration_is_correct()
    if not ready:
        print(message)
        return None
    
    has_errors, message = animator.armature_bones_relationship_has_errors()
    if has_errors:
        print(message)
        return None

    if not object_ready_for_keyframe_animation(animator.get_armature()):
        anim_data_and_action_check_create(animator.get_armature())
        print('|!| Objeto não possuia um animation data, e foi criado com nome de "MocapAction"')

    if animator.get_forward_axis() == "":
        ret = search_for_forward_direction(animator.get_armature(), map_bones)
        if ret is not None:
            print(f'|!| Não foi encontrado uma direção "FORWARD", mas foi deduzido; utilizando {ret} para "FORWARD"')
        else:
            print('|X| Não foi encontrado uma direção para "FORWARD" e nem pode ser deduzido')
            return None

    ''' =========================================================================== '''

    
    ''' COMPATIBILIDADE DE DADOS E CONFIGURACOES ================================== '''

    steps = len(reader.records_list)
    convert_mp_world_data_to_blender_format(reader.records_list)
    transform_all_pose_bones_to_eulerian_rotation(animator.get_armature())
    
    ''' =========================================================================== '''

    ''' FAZER ANIMACAO ============================================================ '''
    
    # _ percorrer frames
    for i, data in enumerate(reader.records_list):
        # TODO
        print(data)
        print(f"passo {i+1} de {steps}")

    ''' =========================================================================== '''



# **************************
#   main function
# **************************
main()
