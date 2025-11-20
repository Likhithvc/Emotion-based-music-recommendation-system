# utils/camera.py
import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
from typing import Tuple, List
from config import EMOTION_NAMES, MODEL_PATH, CONFIDENCE

# load model once (call load_model() from main)
def load_model(model_path: str = MODEL_PATH):
    p = Path(model_path)
    if not p.exists():
        raise FileNotFoundError(f"Model not found at {model_path}")
    model = YOLO(str(p))
    return model

def _read_results(results):
    """
    Convert ultralytics Results to list of detections:
    returns list of (x1,y1,x2,y2, class_id, conf)
    """
    dets = []
    if not results:
        return dets
    r = results[0]  # single image results
    boxes = getattr(r, "boxes", None)
    if boxes is None or len(boxes) == 0:
        return dets
    # boxes.xyxy, boxes.cls, boxes.conf — may be tensors
    try:
        xyxy = boxes.xyxy.cpu().numpy()
        cls = boxes.cls.cpu().numpy().astype(int)
        conf = boxes.conf.cpu().numpy()
    except Exception:
        # fallback if not tensors
        xyxy = np.array(boxes.xyxy)
        cls = np.array(boxes.cls).astype(int)
        conf = np.array(boxes.conf)
    for i in range(len(conf)):
        x1, y1, x2, y2 = xyxy[i].astype(int).tolist()
        dets.append((x1, y1, x2, y2, int(cls[i]), float(conf[i])))
    return dets

def predict_on_face_crop(model, crop, imgsz=640, conf=CONFIDENCE, iou=0.45):
    """
    Run YOLO on a face crop and return the top class and confidence (or None,0.0).
    """
    results = model.predict(source=crop, imgsz=imgsz, conf=conf, iou=iou, verbose=False)
    dets = _read_results(results)
    if not dets:
        return None, 0.0
    # pick detection with highest confidence
    best = max(dets, key=lambda x: x[5])
    cls_id = best[4]
    cls_conf = best[5]
    return int(cls_id), float(cls_conf)

def detect_and_draw(frame, model, face_cascade, imgsz=640, conf=CONFIDENCE, iou=0.45) -> Tuple[np.ndarray, str, float]:
    """
    Detect faces with Haar; for each face crop run the model and pick the dominant emotion.
    Draw boxes and labels onto frame. Returns (annotated_frame, dominant_emotion_name_or_None, confidence)
    """
    h, w = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40,40))

    dominant_emotion = None
    dominant_conf = 0.0

    if len(faces) > 0:
        for (x, y, fw, fh) in faces:
            pad = int(0.15 * max(fw, fh))
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(w, x + fw + pad)
            y2 = min(h, y + fh + pad)
            crop = frame[y1:y2, x1:x2]

            cls_id, cls_conf = predict_on_face_crop(model, crop, imgsz=imgsz, conf=conf, iou=iou)
            if cls_id is not None and cls_conf > dominant_conf:
                dominant_conf = cls_conf
                dominant_emotion = EMOTION_NAMES[cls_id] if cls_id < len(EMOTION_NAMES) else str(cls_id)

            # draw box on original frame
            label = f"{(EMOTION_NAMES[cls_id] if (cls_id is not None and cls_id < len(EMOTION_NAMES)) else '...')} {cls_conf:0.2f}" if cls_id is not None else "..."
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,200,0), 2)
    else:
        # fallback: run model on full frame (some models detect faces directly)
        results = model.predict(source=frame, imgsz=imgsz, conf=conf, iou=iou, verbose=False)
        dets = _read_results(results)
        for (x1, y1, x2, y2, cls_id, cls_conf) in dets:
            if cls_id is not None and cls_conf > dominant_conf:
                dominant_conf = cls_conf
                dominant_emotion = EMOTION_NAMES[cls_id] if cls_id < len(EMOTION_NAMES) else str(cls_id)
            label = f"{(EMOTION_NAMES[cls_id] if cls_id is not None and cls_id < len(EMOTION_NAMES) else '...')} {cls_conf:0.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 100, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,100,0), 2)

    return frame, dominant_emotion, dominant_conf

