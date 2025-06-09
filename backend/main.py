from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import os
import torch

app = FastAPI()

# Load model once at startup
model = torch.hub.load('./yolov5', 'yolov5s', source='local')  # local yolov5 repo

@app.get("/")
def root():
    return {"message": "YOLOv5 API is live"}

@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    # Save temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Perform detection
    results = model(temp_path)
    os.remove(temp_path)

    # Parse results
    detected_objects = results.pandas().xyxy[0].to_dict(orient="records")
    return JSONResponse(content={"detections": detected_objects})

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
