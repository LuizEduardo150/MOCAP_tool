import pickle
from python_utils.utils import file_name_check_extension
from pose.models import PoseInfos


class FramePoseWriter:

    def __init__(self, output_path:str, file_name:str):
        
        self._file_descriptor = None
        self._is_ready = None
        self._video_shape_stored = False
        self._body_shape_stored = False
        
        if file_name is None or len(file_name) == 0:
            self._is_ready = False

        if self._is_ready is None:
            file_name = file_name.rstrip().lstrip()

            file_name = file_name_check_extension(file_name, ".pkl")

            try:
                self._file_descriptor = open(f"{output_path}/{file_name}", "ab")
                self._is_ready = True
                
            except:
                self._is_ready = False
            

    def is_ready(self):
        return self._is_ready


    def write_shape_of_video(self, height:int, width:int):
        if height is None or width is None:
            return

        if not self._video_shape_stored:
            shape = (height, width)
            pickle.dump(shape, self._file_descriptor)
            self._video_shape_stored = True


    def write_landmarks(self, pose_list:list):

        for pose_info in pose_list:
            pose_info : PoseInfos = pose_info

            pickle.dump(pose_info, self._file_descriptor)

    
    def close_file_descriptor(self):
        self._file_descriptor.close()


class FramePoseReader:

    def __init__(self, file_name):
        self._file_descriptor = None
        self._is_ready = None
        self.records_list = None
        self.video_height = None
        self.video_width = None
        
        file_name = file_name_check_extension(file_name, ".pkl")

        try:
            self._file_descriptor = open(file_name, "rb")
            self._is_ready = True
        except:
            self._is_ready = False


    def is_ready(self):
        return self._is_ready
    

    def load_data_from_file(self):
        
        self.records_list = [[]]
        index = 0

        obj = pickle.load(self._file_descriptor)
        self.video_height, self.video_width = obj

        while True:
            try:
                obj = pickle.load(self._file_descriptor)

                if len(self.records_list[index]) == 33:
                    self.records_list.append([])
                    index += 1

                self.records_list[index].append(obj)

            except EOFError:
                break


    def close_file_descriptor(self):
        self._file_descriptor.close()


    def get_record_image_shape(self) -> int:
        """
            Obter altrua e largura respectivamente, do video utilizado para
            gerar o arquivo binario de registros de posicoes do corpo
            
            :Returns: height, width
        """

        if self.video_height is None or self.video_width is None:
            return 0, 0

        return self.video_height, self.video_width
