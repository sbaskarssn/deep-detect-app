from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import os
import torch

app = FastAPI()

# Load model (do this once)
model = torch.hub.load('yolov5', 'yolov5s', source='local')  # using local repo

@app.get("/")
def root():
    return {"message": "YOLOv5 API is live"}

@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    # Save uploaded image
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Perform detection
    results = model(temp_path)
    os.remove(temp_path)  # cleanup

    # Parse detection results
    detected_objects = results.pandas().xyxy[0].to_dict(orient="records")
    return JSONResponse(content={"detections": detected_objects})

@app.post("/detect/")
async def detect(file: UploadFile = File(...)):
    image_bytes = await file.read()
    detections = detect_objects(image_bytes)
    return {"detections": detections}

@app.post("/detect/")
async def detect(data: dict):
    image_base64 = data["image"]
    # decode, process, return result
