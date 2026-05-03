# app/ai/predictor.py
import joblib
from app.ai.model_loader import ModelLoader
from app.ai.utils import preprocess_input  # tabular preprocessing

class DiseasePredictor:
    """Predict disease from symptom data (tabular)"""
    def __init__(self):
        loader = ModelLoader.load()
        self.model = loader.model
        self.encoder = loader.disease_encoder

    def predict(self, data: dict):
        # Preprocess tabular data
        processed_data = preprocess_input(data)  # expects dict with 'humidity', 'spots', 'pod_color'
        
        # Predict
        prediction = self.model.predict([processed_data])[0]
        probabilities = self.model.predict_proba([processed_data])[0]
        confidence = float(max(probabilities))
        disease = self.encoder.inverse_transform([prediction])[0]

        return {
            "disease": disease,
            "confidence": round(confidence, 4)
        }