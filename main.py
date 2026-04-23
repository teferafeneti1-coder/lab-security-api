from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
from ultralytics import YOLO
import base64
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = YOLO("yolov8n.pt")

LAB_EQUIPMENT = {"monitor", "mouse", "keyboard", "desktop", "tv"}
PROHIBITED_ITEMS = {"backpack", "handbag", "cell phone", "laptop", "bag"}

# MEMORY
equipment_last_seen = {}
last_person_time = 0
prohibited_start_time = None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global equipment_last_seen, last_person_time, prohibited_start_time

    await websocket.accept()

    while True:
        data = await websocket.receive_text()

        # Decode base64 image
        img_data = base64.b64decode(data.split(",")[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        results = model(frame, conf=0.3, verbose=False)

        current_time = time.time()

        detections = []
        boxes = []
        person_present = False
        prohibited_present = False

        for r in results:
            for box in r.boxes:
                cls_name = r.names[int(box.cls)].lower()
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                detections.append(cls_name)
                boxes.append({
                    "label": cls_name,
                    "box": [x1, y1, x2, y2]
                })

                if cls_name == "person":
                    person_present = True
                    last_person_time = current_time

                if cls_name in LAB_EQUIPMENT:
                    equipment_last_seen[cls_name] = current_time

                if cls_name in PROHIBITED_ITEMS:
                    prohibited_present = True

        # 🚨 Theft
        theft_alert = any(current_time - t > 5 for t in equipment_last_seen.values())

        # 🚨 Abandoned
        abandoned_alert = False
        if prohibited_present and not person_present:
            if prohibited_start_time is None:
                prohibited_start_time = current_time
            elif current_time - prohibited_start_time > 5:
                abandoned_alert = True
        else:
            prohibited_start_time = None

        await websocket.send_json({
            "detections": detections,
            "boxes": boxes,
            "theft_alert": theft_alert,
            "abandoned_alert": abandoned_alert
        })