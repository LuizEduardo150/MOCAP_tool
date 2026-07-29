import bpy # type: ignore

from blender_modules.utils import object_is_armature
from blender_modules.key_frame_methods import remove_all_pose_bones_keyframes


def main():

    arm = bpy.data.objects.get("skeleton")

    if not object_is_armature(arm):
        print("Objeto selecionado incompatível ou inexistente")
        return

    if remove_all_pose_bones_keyframes(arm):
        print("Keyframes de pose bones removidos")
    else:
        print("Impossível remover keyframes")

    for bone_ in arm.pose.bones:
        bone_.rotation_quaternion = (1.0, 0, 0, 0)

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_set(1)

main()