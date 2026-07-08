from blender_modules.utils import object_is_bpy_type, object_ready_for_keyframe_animation, get_object_last_rotation_keyframe

from math import degrees, radians




def get_blender_object_rotation_euler_degrees_transform(obj)-> tuple:
    """
    Obter o valor de rotacao em Transform. (orientacao de transformacao LOCAL)
    """
    if not object_is_bpy_type(obj):
        return None, None, None
    
    # garante que o objeto esteja operando em rotacao euleriana
    obj.rotation_mode = 'XYZ'

    return (
        round(degrees(obj.rotation_euler[0])),
        round(degrees(obj.rotation_euler[1])),
        round(degrees(obj.rotation_euler[2]))
    )


def set_object_degrees_rotations_euler(obj, rot_axes:list):
    """
    Função para aplicar rotacoes em todos os eixos de um PoseBone.
    (orientacao de transformacao LOCAL)
    
    :pose_bone: Objeto de um osso em pose mode (PoseBone)
    :rot_axes: Lista com valores inteiros para rotação. X:[0] Y:[1] Z:[2]
    """

    if not object_is_bpy_type(obj) or rot_axes is None or len(rot_axes) == 0:
        return
    
    for i, value in enumerate(rot_axes):
        if type(value) == float:
            value = round(value)
        
        if i == 0 and value is not None:
            obj.rotation_euler.x = radians(value)
        
        elif i == 1 and value is not None:
            obj.rotation_euler.y = radians(value)
        
        elif i == 2 and value is not None:
            obj.rotation_euler.z = radians(value)
        
        else:
            break


def insert_rotation_keyframe(obj, values:list=None, frame_distance=1):
    """
    Inserir keyframe de rotacao em um objeto no projeto blender

    :obj: Objeto do blender
    :values: lista com ate 3 valores de rotacao referentes a x,y,z  (EX: [None, 1, None] "move só Y")
    :frame_distance: distancia de tempo entre um frame e outro
    """

    if not object_is_bpy_type(obj) or not object_ready_for_keyframe_animation(obj) \
        or values is None or frame_distance is None or len(values) == 0:
        return False

    keyframe = get_object_last_rotation_keyframe(obj)
    
    if keyframe is None:
        return False
    
    elif keyframe == -1: # inicio da animacao
        obj.keyframe_insert(data_path="rotation_euler", frame=1)
        keyframe = 1

    # fazer a(s) rotacao(oes)
    set_object_degrees_rotations_euler(obj, values)

    obj.keyframe_insert(
        data_path="rotation_euler",
        frame= (keyframe + frame_distance)
    )

    return True
