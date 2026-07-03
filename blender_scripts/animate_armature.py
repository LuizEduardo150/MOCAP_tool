from blender_modules.utils import transform_all_pose_bones_to_eulerian_rotation, find_any_armature
from blender_modules.armature_animator import ArmatureAnimator

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
    
    animator.bone_map_mp_blender = map_bones

    ready, message = animator.is_ready()
    print(message)
    
    if not ready:
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


        print(f"passo {i} de {steps}")


    

    ''' =========================================================================== '''



# **************************
#   main function
# **************************
main()
