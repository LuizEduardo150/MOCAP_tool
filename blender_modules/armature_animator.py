import bpy # type: ignore

from blender_modules.utils import object_is_armature, \
    object_is_pose_bone, get_blender_object_degrees_euler_rotation, \
    get_all_pose_bones_name_list_from_armature

from pose.models import BODY_POSE_CONECTIONS_FOR_BLENDER




class ArmatureAnimator:
    def __init__(self):
        self._armature : bpy.types.Armature = None
        self._main_pose_bone : bpy.types.PoseBone = None
        self.bone_map_mp_blender : dict = None


    def set_armature(self, name:str) -> bool:
        obj = bpy.data.objects.get(name)
        
        if object_is_armature(obj):
            self._armature = obj

            return True
        else:
            return False


    def set_main_control_pose_bone(self, pose_bone_name:str):
        
        if not object_is_armature(self._armature):
            return False
        
        pose_bone = self._armature.pose.bones.get(pose_bone_name)

        if not object_is_pose_bone(pose_bone):
            return False
        
        self._main_pose_bone = pose_bone
        return True


    def get_armature(self):
        return self._armature
    

    def is_ready(self):
        ready = True
        message = ""

        if not object_is_armature(self._armature):
            ready = False
            message += "|X| É preciso informar a armature\n"

        if self._armature is not None:
            rot = get_blender_object_degrees_euler_rotation(self._armature)
            if rot[0] != 0 or rot[1] != 0 or rot[2] != 0:
                ready = False
                message += "|X| Antes é preciso aplicar as transformações da armature\n"

        if self._main_pose_bone is None:
            ready = False
            message += "|X| É preciso que a armature possua e que seja identificado, um osso de controle ao centro do corpo.\n"
            
        else:
            # Conferir inclinação do osso main em relação ao eixo Z global
            local_y_orientation = self._main_pose_bone.matrix.to_3x3().col[1]
            
            if local_y_orientation[0] >= 0.01 or \
                local_y_orientation[1] >= 0.01 or \
                abs(local_y_orientation[2] - 1) >= 0.01:
                
                message += "|!| AVISO: O osso central de controle está inclinado. Isso pode gerar problemas.\n"

        if self.bone_map_mp_blender is None:
            ready = False
            message += "|x| É preciso carregar o arquivo de mapeamento entre o MediaPipe e Blender\n"
        else:
            # Conferir existência de todos os ossos identificados no arquivo
            temp_unnow = []
            pose_bones_list = get_all_pose_bones_name_list_from_armature(self._armature)

            if pose_bones_list is not None:

                for key in self.bone_map_mp_blender.keys():
                    if key == ('a'):
                        continue

                    item = self.bone_map_mp_blender[key]

                    if type(item) is str:
                       
                        file_bone_name = item
                    
                        if file_bone_name in pose_bones_list:
                            pose_bones_list.remove(file_bone_name)
                        else:
                            temp_unnow.append(file_bone_name)
    
                    elif type(item) is list and key == ('c'):
                        
                        for file_bone_name in item:
                            if file_bone_name in pose_bones_list:
                                pose_bones_list.remove(file_bone_name)
                            else:
                                temp_unnow.append(file_bone_name)


                if len(temp_unnow) > 0:
                    ready = False
                    message += "|X| O arquivo contem nomes de ossos não encontrados no projeto blender: \n"
                    for name in temp_unnow:
                        message += f"    |_ {name}\n"

        

            # Conferir se todos ossos foram atribuidos
            check_conections = list(self.bone_map_mp_blender.keys())
            not_found = []
            for conection in BODY_POSE_CONECTIONS_FOR_BLENDER:
                if conection in check_conections:
                    check_conections.remove(conection)
                else:
                    not_found.append(conection)

            if len(not_found) > 0:
                ready = False
                message += "|X| Há partes do corpo rastradas pelo MediaPipe não mapeados para o Blender:\n"
                for item in not_found:
                    message += f"    |_ {item}\n"

        return ready, message
