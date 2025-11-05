import cv2
import mediapipe as mp
import numpy as np
from PIL import Image

mp_selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

def remove_background(input_path, mask_output_path, person_output_path):
    image = cv2.imread(input_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_selfie_segmentation as segment:
        results = segment.process(image_rgb)

    mask = (results.segmentation_mask > 0.5).astype(np.uint8) * 255  # Binary mask
    cv2.imwrite(mask_output_path, mask)

    # Create transparent image for person only
    b,g,r = cv2.split(image)
    rgba = cv2.merge([b,g,r, mask])
    cv2.imwrite(person_output_path, rgba)

    return mask_output_path, person_output_path
