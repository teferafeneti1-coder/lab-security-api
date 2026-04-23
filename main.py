from fastapi import FastAPI, File, UploadFile
import numpy as np
import cv2
from ultralytics import YOLO

app = FastAPI()

model = YOLO("yolov8n.pt")

LAB_EQUIPMENT = {"monitor", "mouse", "keyboard", "desktop", "tv"}
PROHIBITED_ITEMS = {"backpack", "handbag", "cell phone", "laptop", "bag"}

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    contents = await file.read()
    
    np_arr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    results = model(frame, conf=0.3, verbose=False)

    detections = []

    for r in results:
        for box in r.boxes:
            cls_name = r.names[int(box.cls)].lower()
            detections.append(cls_name)

    return {
        "detections": detections,
        "theft_risk": any(item in LAB_EQUIPMENT for item in detections),
        "prohibited_risk": any(item in PROHIBITED_ITEMS for item in detections)
    }