from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import torch
import matplotlib
import logging
import sys

# Avoid font caching issues on Render
matplotlib.use('Agg')

# Create FastAPI app
app = FastAPI()

# Add CORS middleware for frontend support (like from Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy-loaded model
model = None


@app.get("/")
def root():
    logger.info("Health check accessed.")
    return {
        "message": "YOLOv5 Service is live ✅",
        "cwd": os.getcwd(),
        "files_in_cwd": os.listdir("."),
        "model_file_exists": os.path.exists("yolov5s.pt"),
        "yolov5_hubconf_exists": os.path.exists("yolov5/hubconf.py")
    }


@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    global model

    logger.info(f"Received file: {file.filename}")

    # Lazy load model
    if model is None:
        try:
            logger.info("Loading YOLOv5 model for the first time...")
            model = torch.hub.load('yolov5', 'custom', path='yolov5s.pt', source='local')
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise HTTPException(status_code=500, detail="Model loading failed.")

    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved temporary file: {temp_path}")
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded image.")

    # Perform detection
    try:
        logger.info(f"Running detection on {temp_path}...")
        results = model(temp_path)
        detected_objects = results.pandas().xyxy[0].to_dict(orient="records")
        logger.info(f"Detection complete. Found {len(detected_objects)} objects.")
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        raise HTTPException(status_code=500, detail="Model inference failed.")
    finally:
        # Clean up temp file
        try:
            os.remove(temp_path)
            logger.info(f"Deleted temp file: {temp_path}")
        except OSError as e:
            logger.warning(f"Could not delete temp file: {temp_path} - {e}")

    return JSONResponse(content={"detections": detected_objects})
