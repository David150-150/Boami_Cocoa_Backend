# app/_ai/image_predictor.py
import logging
import numpy as np
import cv2
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class ImagePredictor:

    MODEL_PATH = "app/_ai/model/best.pt"
    CONFIDENCE_THRESHOLD = 0.25

    def __init__(self):
        logger.info("Loading YOLO model from %s ...", self.MODEL_PATH)
        self.model = YOLO(self.MODEL_PATH)
        logger.info("YOLO model loaded. Classes: %s", self.model.names)

    def calibrate_confidence(self, raw_conf):
        low, high = 0.25, 0.95
        calibrated = (raw_conf - low) / (high - low)
        return round(max(0.0, min(1.0, calibrated)), 4)

    def annotate(self, img, result):
        annotated = img.copy()
        colors = {
            "Black_Pod_Disease": (0, 0, 255),
            "Frosty_Pod_Rot":    (0, 165, 255),
            "Healthy":           (0, 200, 0),
        }
        for box in result.boxes:
            class_id   = int(box.cls[0])
            raw_conf   = float(box.conf[0])
            conf       = self.calibrate_confidence(raw_conf)
            class_name = self.model.names[class_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            color = colors.get(class_name, (255, 255, 0))
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            label = f"{class_name.replace(chr(95), chr(32))} {conf * 100:.1f}%"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
            cv2.rectangle(annotated, (x1, y1 - th - 10), (x1 + tw + 6, y1), color, -1)
            cv2.putText(annotated, label, (x1 + 3, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
        return annotated

    def _encode(self, img):
        try:
            success, buffer = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
            return buffer.tobytes() if success and buffer is not None else None
        except Exception as e:
            logger.error("Encoding error: %s", e)
            return None

    def _error_response(self, message):
        return {"status": "Error", "disease": None, "confidence": 0.0,
                "confidence_percent": "0.00%", "annotated_image": None, "message": message}

    def predict(self, image_bytes):
        np_img = np.frombuffer(image_bytes, np.uint8)
        img    = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        if img is None:
            return self._error_response("Could not decode image.")
        try:
            results = self.model(img, conf=self.CONFIDENCE_THRESHOLD, verbose=False)
        except Exception as e:
            logger.exception("YOLO inference failed")
            return self._error_response(str(e))
        result = results[0]
        if result.boxes is None or len(result.boxes) == 0:
            return {"status": "Uncertain", "disease": None, "confidence": 0.0,
                    "confidence_percent": "0.00%",
                    "annotated_image": self._encode(img),
                    "message": "No disease detected. Retake in good lighting."}
        best_box = max(result.boxes, key=lambda b: float(b.conf[0]))
        class_id = int(best_box.cls[0])
        raw_conf = float(best_box.conf[0])
        conf     = self.calibrate_confidence(raw_conf)
        label    = self.model.names[class_id]
        annotated_bytes = self._encode(self.annotate(img, result))
        if label.lower() == "healthy":
            return {"status": "Healthy", "disease": None, "confidence": conf,
                    "confidence_percent": f"{conf * 100:.2f}%",
                    "annotated_image": annotated_bytes}
        return {"status": "Diseased", "disease": label, "confidence": conf,
                "confidence_percent": f"{conf * 100:.2f}%",
                "annotated_image": annotated_bytes}

    def get_model_info(self):
        return {"model": self.MODEL_PATH, "classes": self.model.names,
                "threshold": self.CONFIDENCE_THRESHOLD}
