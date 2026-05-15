from math import sqrt, acos, degrees, atan2


def euclidean_distance_3d(pose_list, bone_index_1:int, bone_index_2:int):
    if pose_list is None or len(pose_list) < 0 or \
        bone_index_1 >= len(pose_list) or bone_index_2 >= len(pose_list):
        
        return None
    
    d_x = pose_list[bone_index_2].x_world - pose_list[bone_index_1].x_world
    d_y = pose_list[bone_index_2].y_world - pose_list[bone_index_1].y_world
    d_z = pose_list[bone_index_2].z_world - pose_list[bone_index_1].z_world
    
    return sqrt((d_x**2) + (d_y**2) + (d_z**2))


def direct_angle_x_3d(pose_list, bone_index_1, bone_index_2):
    if pose_list is None or len(pose_list) < 0 or \
        bone_index_1 >= len(pose_list) or bone_index_2 >= len(pose_list):
        
        return None
    
    IvI = euclidean_distance_3d(pose_list, bone_index_1, bone_index_2)
    
    d_x = pose_list[bone_index_2].x_world - pose_list[bone_index_1].x_world
    angle = acos ( (d_x / IvI) )

    return degrees(angle)


"""
def direct_angle_x_2d(x1, x2, y1, y2):
    dx = x2 - x1
    dy = y2 - y1
    
    print("2d_X: ", degrees(atan2( dy, dx )))


def direct_angle_y_2d(x1, x2, y1, y2):
    dx = x2 - x1
    dy = y2 - y1
    
    degrees(atan2( dx, dy ))
"""


