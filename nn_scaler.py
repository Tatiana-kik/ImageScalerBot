import cv2
from cv2 import dnn_superres


def img_scale_nn(path_to_img, path_to_model='./EDSR_x3.pb', scale=3):
    # Create an SR object
    sr = dnn_superres.DnnSuperResImpl_create()

    # Read image
    image = cv2.imread(path_to_img)

    # Read the desired model
    sr.readModel(path_to_model)
    # Make dict with available models
    models_dict = {"EDSR": "edsr", "ESPCN": "espcn"}

    # Set the desired model and scale to get correct pre- and post-processing
    sr.setModel(models_dict[path_to_model.split('/')[-1].split('_')[0]], scale)

    # Upscale the image
    result = sr.upsample(image)
    return result
