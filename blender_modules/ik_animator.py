import bpy # type: ignore

from blender_modules.utils import object_is_armature, object_is_pose_bone
    

class IK_animator:
    def __init__(self):
        self._armature  : bpy.types.Armature = None
        self._L_hand_ik : bpy.types.PoseBone = None
        self._R_hand_ik : bpy.types.PoseBone = None
        self._L_foot_ik : bpy.types.PoseBone = None
        self._R_foot_ik : bpy.types.PoseBone = None
        self._ik_targets = []
        self.media_pipe_body_height = None
        self.media_pipe_body_width = None


    def set_armature(self, name:str) -> bool:
        obj = bpy.data.objects.get(name)
        
        if object_is_armature(obj):
            self._armature = obj

            for bone in obj.pose.bones:
                for c in bone.constraints:
                    if c.type == "IK":
                        self._ik_targets.append(c.subtarget)

            return True
        
        else:
            return False
    

    def set_left_hand_ik(self, bone_name:str) -> bool:
        
        if len(self._ik_targets) == 0:
            return False

        if bone_name in self._ik_targets:
            self._L_hand_ik = self._armature.pose.bones.get(bone_name)
            return True
        
        else:
            return False


    def set_right_hand_ik(self, bone_name:str) -> bool:
        
        if len(self._ik_targets) == 0:
            return False

        if bone_name in self._ik_targets:
            self._R_hand_ik = self._armature.pose.bones.get(bone_name)
            return True
        
        else:
            return False


    def set_left_foot_ik(self, bone_name:str) -> bool:
        
        if len(self._ik_targets) == 0:
            return False

        if bone_name in self._ik_targets:
            self._L_foot_ik = self._armature.pose.bones.get(bone_name)
            return True
        
        else:
            return False


    def set_right_foot_ik(self, bone_name:str) -> bool:
        
        if len(self._ik_targets) == 0:
            return False

        if bone_name in self._ik_targets:
            self._R_foot_ik = self._armature.pose.bones.get(bone_name)
            return True
        
        else:
            return False
    

    def is_ready(self):
        ready = True
        message = ""

        if not object_is_armature(self._armature):
            ready = False
            message += "|!| É preciso informar a armature\n"

        if not object_is_pose_bone(self._L_hand_ik):
            ready = False
            message += "|!| É preciso definir o osso controlador IK da mão esquerda\n"

        if not object_is_pose_bone(self._R_hand_ik):
            ready = False
            message += "|!| É preciso definir o osso controlador IK da mão direita\n"

        if not object_is_pose_bone(self._L_foot_ik):
            ready = False
            message += "|!| É preciso definir o osso controlador IK do pé esquerdo\n"

        if not object_is_pose_bone(self._R_foot_ik):
            ready = False
            message += "|!| É preciso definir o osso controlador IK do pé direito\n"

        if self.media_pipe_body_height is None or self.media_pipe_body_height == 0:
            ready = False
            message += "|!| É preciso informar a altura do corpo rastreado pelo media pipe para ajustar a escala\n"

        if self.media_pipe_body_width is None or self.media_pipe_body_width == 0:
            ready = False
            message += "|!| É preciso informar a largura do corpo rastreado pelo media pipe para ajustar a escala\n"

        return ready, message
    