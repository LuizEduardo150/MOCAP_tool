import bpy # type: ignore

from blender_modules.utils import object_is_armature, \
    object_is_pose_bone, get_all_pose_bones_name_list_from_armature

from blender_modules.calculations import get_pose_bone_local_y_axis_basic_direction

from pose.models import BODY_POSE_CONECTIONS_FOR_BLENDER



class ArmatureChecker:
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

    def get_main_bone(self):
        return self._main_pose_bone


    def check_attribute_instances(self):
        ready = True
        message = ""

        if not object_is_armature(self._armature):
            ready = False
            message += "|X| É preciso informar a armature\n"

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


    def armature_bones_configuration_is_correct(self) -> tuple:
        if self._armature is None or self.bone_map_mp_blender is None:
            return False, "Objeto não configurado ainda"

        ready = True
        message = ""

        for conection in self.bone_map_mp_blender.keys():
            
            if conection == ('a'): # ignorar armature
                continue
            
            elif conection != ('c') and conection != (0) and len(conection) == 2:

                content = self.bone_map_mp_blender[conection]
                bone = self._armature.pose.bones.get(content)
                x, y, z = get_pose_bone_local_y_axis_basic_direction(bone.matrix.to_3x3())

                # Pernas e canelas: esquerda e direita
                if conection == (23, 25) or conection == (24, 26) or conection == (25, 27) or conection == (26, 28):
                    if x == 0 and y == 0 and z != -1:
                        ready = False
                        message += "Os ossos que constituem as pernas devem estar apontados para baixo:\n" \
                                   "  |_ Cabeça do osso mais alta que a cauda.\n"

            
            elif conection == ('c'): # Coluna, pode conter mais de um objeto
                content = self.bone_map_mp_blender[conection]
                if type(content) is list and len(content) > 0:
                    for bone_name in content:
                        bone = self._armature.pose.bones.get(bone_name)
                        x, y, z = get_pose_bone_local_y_axis_basic_direction(bone.matrix.to_3x3())

                        if x == 0 and y == 0 and z != 1:
                            ready = False
                            message += f"Problema no osso da coluna: {bone_name}\n" \
                            "  |  O(s) osso(s) da coluna deve(m) estar apontados para cima:\n" \
                            "  |_ (Cabeça do osso mais baixa que a cauda)\n"
                
                else:
                    content = self.bone_map_mp_blender[conection]
                    bone = self._armature.pose.bones.get(content)
                    x, y, z = get_pose_bone_local_y_axis_basic_direction(bone.matrix.to_3x3())

                    if x == 0 and y == 0 and z != 1:
                            ready = False
                            message += f"Problema no osso da coluna: {bone_name}\n" \
                            "  |  O(s) osso(s) da coluna deve(m) estar apontados para cima:\n" \
                            "  |_ (Cabeça do osso mais baixa que a cauda)\n"


        return ready, message

