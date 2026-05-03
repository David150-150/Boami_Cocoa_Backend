from ultralytics import YOLO
import numpy as np
import cv2

class Predictor:

    def __init__(self, model_path: str):
        self.model = YOLO(model_path)

    def predict(self, image_bytes: bytes):
        # Convert bytes → image
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        results = self.model(image)[0]

        if len(results.boxes) == 0:
            return {
                "disease": "No Disease Detected",
                "confidence": 0.0,
                "annotated_image": None
            }

        # 🔥 Get best prediction
        box = results.boxes[0]
        cls_id = int(box.cls[0])
        confidence = float(box.conf[0])
        label = self.model.names[cls_id]

        # 🔥 Draw bounding box
        annotated = results.plot()

        # Convert back to bytes
        _, buffer = cv2.imencode(".jpg", annotated)
        annotated_bytes = buffer.tobytes()

        return {
            "disease": label,
            "confidence": confidence,
            "annotated_image": annotated_bytes
        }