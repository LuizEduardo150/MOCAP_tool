import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from pose.models import PoseInfos


BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


class MPPoseProcessor:
    
    def __init__(self, trained_model:str):
        self._mp_options_video = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=trained_model),
            running_mode=VisionRunningMode.VIDEO
        )
        
        self._mp_options_image = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=trained_model),
            running_mode=VisionRunningMode.IMAGE
        )

        self.processing_result = None
        self._landmarker_video = PoseLandmarker.create_from_options(self._mp_options_video)
        self._landmarker_image = PoseLandmarker.create_from_options(self._mp_options_image)
        self.pose_info_result = None

    @staticmethod
    def test_existing_model(trained_model:str):
        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=trained_model),
            running_mode=VisionRunningMode.VIDEO
        )
        
        try:
            with PoseLandmarker.create_from_options(options) as _:
                pass
            return True
        
        except:    
            return False


    def process_frame(self, img, frame_timestamp_ms):
        if type(frame_timestamp_ms) == float:
            frame_timestamp_ms = int(frame_timestamp_ms)
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)

        self.processing_result = self._landmarker_video.detect_for_video(mp_image, frame_timestamp_ms)

        if len(self.processing_result.pose_landmarks) < 1 or len(self.processing_result.pose_world_landmarks) < 1:
            self.pose_info_result = []
            return

        pose_landmarks = self.processing_result.pose_landmarks[0] # Apenas um corpo !
        world_landmarks = self.processing_result.pose_world_landmarks[0] # Apenas um corpo !

        self.pose_info_result = []
        for i in range(33):
            self.pose_info_result.append(
                PoseInfos.buid_object_through_mediapipe_result(
                    pose_landmarks[i], world_landmarks[i], i
            ))


    def process_image(self, img):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
        self.processing_result = self._landmarker_image.detect(mp_image)

        if len(self.processing_result.pose_landmarks) < 1 or len(self.processing_result.pose_world_landmarks) < 1:
            self.pose_info_result = []
            return
        
        pose_landmarks = self.processing_result.pose_landmarks[0] # Apenas um corpo !
        world_landmarks = self.processing_result.pose_world_landmarks[0] # Apenas um corpo !
        
        self.pose_info_result = []
        for i in range(33):
            self.pose_info_result.append(
                PoseInfos.buid_object_through_mediapipe_result(
                    pose_landmarks[i], world_landmarks[i], i
            ))


    def get_pose_info_list(self):
        return self.pose_info_result


    def close_landmarker(self):
        self._landmarker_video.close()
        self._landmarker_image.close()



