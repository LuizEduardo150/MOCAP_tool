import bpy # type: ignore

from blender_modules.utils import remove_all_pose_bones_keyframes, object_is_armature



def main():

    arm = bpy.data.objects.get("skeleton")

    if not object_is_armature(arm):
        print("Objeto selecionado incompatível ou inexistente")
        return

    if remove_all_pose_bones_keyframes(arm):
        print("Keyframes de pose bones removidos")
    else:
        print("Impossível remover keyframes")


main()