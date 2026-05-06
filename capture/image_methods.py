import cv2
from numpy import ndarray, uint8, array


def resize_by_scale(image:ndarray, scale:float):
    h, w, _ = image.shape
    w, h = int( w * scale ), int( h * scale )
    image = cv2.resize( image, ( w,  h))  
    return image


def rotate_image(img:ndarray, angulo):
    h, w, _ = img.shape
    centro = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(centro, angulo, 1.0)

    # calcula o novo tamanho
    cos = abs(M[0, 0])
    sin = abs(M[0, 1])

    novo_w = int((h * sin) + (w * cos))
    novo_h = int((h * cos) + (w * sin))

    # ajusta a matriz para translação
    M[0, 2] += (novo_w / 2) - centro[0]
    M[1, 2] += (novo_h / 2) - centro[1]

    return cv2.warpAffine(img, M, (novo_w, novo_h))


def image_green_filter(image:ndarray):
    fatores = array([0.5, 0.8, 0.5])
    image = (image * fatores).astype(uint8)
    return image


def horizontal_flip(image):
    return image[:, ::-1].copy()

    
    
    

    
    