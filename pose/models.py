POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7),
    (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),
    (11, 12),
    (11, 13), (13, 15),
    (12, 14), (14, 16),
    (15, 17), (17, 19), (19, 21),
    (15, 21),
    (16, 18), (18, 20), (20, 22),
    (16, 22),
    (11, 23), (12, 24),
    (23, 24),
    (23, 25), (25, 27), (27, 29), (29, 31),
    (24, 26), (26, 28), (28, 30), (30, 32),
    (27, 31), (28, 32)
]


BODY_POSE_CONECTIONS_FOR_BLENDER = [
    
    #(11, 12), # Nao trabalhamos no blender com ombro inteiro
    (11, 13), (12, 14), # arms
    (13, 15), (14, 16), # Forearms
    (15, 17), (16, 18), # Hands
    #(11, 23), (12, 24), # Belly
    (23, 25), (24, 26), # UpperLeg
    (25, 27), (26, 28), # LowerLeg
    (27, 31), (28, 32), # FOOT
    (9, 1) # HEAD
    #(29, 31), (30, 32), (27, 31), (28, 32) # Outros possiveis valores para foot
]


class PoseInfos:
    def __init__(self, id:int=None, x_p:float=None, y_p:float=None, z_p:float=None, v_p:float=None, p_p:float=None, 
                 x_w:float=None, y_w:float=None, z_w:float=None, v_w:float=None, p_w:float=None):
        
        self.id = id
        
        self.x_pose = x_p
        self.y_pose = y_p
        self.z_pose = z_p
        self.v_pose = v_p
        self.p_pose = p_p

        self.x_world = x_w
        self.y_world = y_w
        self.z_world = z_w
        self.v_world = v_w
        self.p_world = p_w


    @staticmethod
    def buid_object_through_mediapipe_result(pose_landmark, world_landmark, id):
        pose = PoseInfos()

        pose.id = id

        pose.x_pose = pose_landmark.x
        pose.y_pose = pose_landmark.y
        pose.z_pose = pose_landmark.z
        pose.v_pose = pose_landmark.visibility
        pose.p_pose = pose_landmark.presence

        pose.x_world = world_landmark.x
        pose.y_world = world_landmark.y
        pose.z_world = world_landmark.z
        pose.v_world = world_landmark.visibility
        pose.p_world = world_landmark.presence
        
        return pose


    def get_pose_landmakrs(self):
        return self.x_pose, self.y_pose, self.z_pose, self.v_pose, self.p_pose
    

    def get_world_landmakrs(self):
        return self.x_world, self.y_world, self.z_world, self.v_world, self.p_world
    

    def get_combined_certainty(self):
        return (self.p_world * 0.5) + (self.v_world * 0.5)
    

    def __str__(self):

        return "------------------------------------------------------\n" \
        f"x_pose: {self.x_pose} y_pose: {self.y_pose} z_pose: {self.z_pose} visibility_pose: {self.v_pose} presence_pose: {self.p_pose}\n" \
        f"x_world: {self.x_world} y_world: {self.y_world} z_world: {self.z_world} visibility_world: {self.v_world} presence_world: {self.p_world}\n"