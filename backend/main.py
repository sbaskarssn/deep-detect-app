from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import os
import torch
import matplotlib

# Prevent font caching (avoids memory issues on Render)
matplotlib.use('Agg')

app = FastAPI()

model = None  # Lazy load on first use to avoid high memory usage at startup

@app.get("/")
def root():
    return {"message": "YOLOv5 API is live"}

@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    global model

    # Load model only on first request
    if model is None:
        model = torch.hub.load('yolov5', 'custom', path='backend/yolov5s.pt', source='local')

    # Save image temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Perform detection
    results = model(temp_path)

    # Clean up temp file
    os.remove(temp_path)

    # Parse results
    detected_objects = results.pandas().xyxy[0].to_dict(orient="records")
    return JSONResponse(content={"detections": detected_objects})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
