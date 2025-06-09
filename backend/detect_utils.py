# detect_utils.py

import torch
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.datasets import letterbox
from yolov5.utils.general import non_max_suppression, scale_coords
import numpy as np
import cv2
from PIL import Image
from io import BytesIO

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)  # or your path

def detect_objects(image_bytes):
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    results = model(img, size=640)
    return results.pandas().xyxy[0].to_dict(orient="records")
