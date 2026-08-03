import bpy # type: ignore
from bpy.props import StringProperty, PointerProperty # type: ignore

from sys import path as sys_path


# -----------------------------------------------------
# Propriedades
# -----------------------------------------------------
class MOCAPForm(bpy.types.PropertyGroup):

    mocap_src_path: StringProperty(
        name="project src",
        subtype='DIR_PATH',
        default=sys_path[-1]
    ) # type: ignore

    pose_file: StringProperty(
        name="pose file",
        subtype='FILE_PATH',
        default=sys_path[-1]
    ) # type: ignore

    bone_map_file: StringProperty(
        name="bone map path",
        subtype='FILE_PATH',
        default=sys_path[-1]
    ) # type: ignore


# -----------------------------------------------------
# Operador Confirmar
# -----------------------------------------------------
class MOCAPTL_OT_confirmar(bpy.types.Operator):
    bl_idname = "mocap.exec"
    bl_label = "Executar"

    def execute(self, context):

        props = context.scene.mocap_form
        
        if props.mocap_src_path[-1] == "/":
            project_src = props.mocap_src_path[:len(props.mocap_src_path)-1]
        else:
            project_src = props.mocap_src_path

        # __ Executar script externo
        bpy.ops.script.python_file_run(filepath=f"{project_src}/blender_scripts/animate_armature.py")
        
        return {'FINISHED'}


# -----------------------------------------------------
# Operador Cancelar
# -----------------------------------------------------
class MOCAPTL_OT_cancelar(bpy.types.Operator):
    bl_idname = "mocap.cancel"
    bl_label = "Cancelar"

    def execute(self, context):

        props = context.scene.mocap_form

        props.mocap_src_path = sys_path[-1]
        props.pose_file = sys_path[-1]
        props.bone_map_file = sys_path[-1]

        self.report({'INFO'}, "Campos resetados")

        return {'FINISHED'}


# -----------------------------------------------------
# Operador Limpar animacao
# -----------------------------------------------------
class MOCAPTL_OT_clean_animation(bpy.types.Operator):
    bl_idname = "mocap.clean_anm"
    bl_label = "Clean Animation"

    def execute(self, context):
        self.report({'INFO'}, "Remover animação !")

        props = context.scene.mocap_form
                
        if props.mocap_src_path[-1] == "/":
            project_src = props.mocap_src_path[:len(props.mocap_src_path)-1]
        else:
            project_src = props.mocap_src_path

        bpy.ops.script.python_file_run(filepath=f"{project_src}/blender_scripts/clear_all_posebones_keyframes.py")

        return {'FINISHED'}



# -----------------------------------------------------
# INTERFACE
# -----------------------------------------------------
class MOCAPTL_PT_panel(bpy.types.Panel):
    bl_label = "MOCAP TOOL"
    bl_idname = "MOCAPTL_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MOCAP"

    def draw(self, context):

        layout = self.layout
        props = context.scene.mocap_form

        layout.prop(props, "mocap_src_path")
        layout.prop(props, "pose_file")
        layout.prop(props, "bone_map_file")

        layout.separator()
        row = layout.row()
        row.operator(
            "mocap.exec",
            icon='CHECKMARK'
        )

        row = layout.row()
        row.operator(
            "mocap.cancel",
            icon='CANCEL'
        )

        row = layout.row()
        row.operator(
            "mocap.clean_anm",
            icon='LOOP_BACK'
        )



# -----------------------------------------------------
# Registro
# -----------------------------------------------------
classes = (
    MOCAPForm,
    MOCAPTL_OT_confirmar,
    MOCAPTL_OT_cancelar,
    MOCAPTL_OT_clean_animation,
    MOCAPTL_PT_panel
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.mocap_form = PointerProperty(
        type=MOCAPForm
    )


if __name__ == "__main__":
    register()
