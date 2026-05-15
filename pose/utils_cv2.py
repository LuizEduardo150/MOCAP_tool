import cv2
import numpy as np

from pose.models import PoseInfos, POSE_CONNECTIONS


def draw_landmarks_on_image(rgb_image, pose_list:list, different_points:list=None, show_conections=True):
    
    if len(pose_list) < 1:
        return rgb_image

    annotated_image = np.copy(rgb_image)
    h, w, _ = rgb_image.shape
    
    # Desenhando pontos rastreados
    for i in range(33):
        lm : PoseInfos = pose_list[i]

        x = int(lm.x_pose * w)
        y = int(lm.y_pose * h)

        if different_points is not None and len(different_points) > 0 and i in different_points:
            cv2.circle(annotated_image, (x, y), 2, (0, 0, 255), 3)
        else:
            cv2.circle(annotated_image, (x, y), 2, (0, 255, 0), -1)

    # desenhar conexoes
    if show_conections:
        for conection in POSE_CONNECTIONS:
            init, end = conection
            lm_i : PoseInfos = pose_list[init]
            lm_e : PoseInfos = pose_list[end]

            p1 = (int(lm_i.x_pose * w), int(lm_i.y_pose * h))
            p2 = (int(lm_e.x_pose * w), int(lm_e.y_pose * h) )

            # Desenha linha verde
            if different_points and (init in different_points and end in different_points):
                cv2.line(annotated_image, p1, p2, (0, 0, 255), 1)
            elif different_points and (init in different_points or end in different_points):
                cv2.line(annotated_image, p1, p2, (0, 255, 255), 1)
            else:
                cv2.line(annotated_image, p1, p2, (0, 255, 0), 1)

    return annotated_image
