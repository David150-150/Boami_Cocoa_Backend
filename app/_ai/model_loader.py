import joblib
import os
from tensorflow.keras.models import load_model

MODEL_DIR = os.path.join("app", "ai", "models")

class ModelLoader:
    """Loads tabular and image models"""

    # -----------------------------
    # Tabular / symptom model
    # -----------------------------
    model = None
    disease_encoder = None
    humidity_encoder = None
    spots_encoder = None
    color_encoder = None

    @classmethod
    def load(cls):
        if cls.model is None:
            cls.model = joblib.load(os.path.join(MODEL_DIR, "cocoa_disease_model.pkl"))
            cls.disease_encoder = joblib.load(os.path.join(MODEL_DIR, "disease_encoder.pkl"))
            cls.humidity_encoder = joblib.load(os.path.join(MODEL_DIR, "humidity_encoder.pkl"))
            cls.spots_encoder = joblib.load(os.path.join(MODEL_DIR, "spots_encoder.pkl"))
            cls.color_encoder = joblib.load(os.path.join(MODEL_DIR, "color_encoder.pkl"))
        return cls

    # -----------------------------
    # Image model
    # -----------------------------
    image_model = None
    image_encoder = None

    @classmethod
    def load_image_model(cls):
        if cls.image_model is None:
            # Load Keras image model
            cls.image_model = load_model(os.path.join(MODEL_DIR, "cocoa_image_model.h5"))
            # Load label encoder for images
            cls.image_encoder = joblib.load(os.path.join(MODEL_DIR, "image_disease_encoder.pkl"))
        return cls