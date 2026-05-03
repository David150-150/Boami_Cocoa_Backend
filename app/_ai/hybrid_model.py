


# app/ai/hybrid_dygnosis_model.py
from sqlalchemy.orm import Session
from app.ai.predictor import DiseasePredictor
from app.models.disease import Disease
from typing import Dict, Any


class HybridDiagnosis:
    def __init__(self):
        self.predictor = DiseasePredictor()

    def _is_voice_input(self, data: dict) -> bool:
        """Voice input has boolean values; form input has strings/floats."""
        if not data:
            return False
        bool_count = sum(1 for v in data.values() if isinstance(v, bool))
        return bool_count > 0  # ✅ if ANY value is bool, it's voice input

    def diagnose(self, data: dict, db: Session = None) -> Dict[str, Any]:
        is_voice = self._is_voice_input(data)
        if is_voice:
            return self._diagnose_from_voice(data, db)
        else:
            return self._diagnose_from_form(data, db)

    # ------------------------------------------------------------------
    # VOICE PATH — rule-based only, no ML predictor
    # ------------------------------------------------------------------
    def _diagnose_from_voice(self, symptoms: Dict[str, bool], db: Session) -> Dict[str, Any]:
        """Match voice symptoms against disease requirements without the ML model."""
        best_disease = None
        best_score = 0.0

        diseases = db.query(Disease).all()
        for disease in diseases:
            boost = self._symptom_rules_boost(symptoms, disease.name)
            matched = 0
            total = len(disease.requirement)
            for req in disease.requirement:
                req_text = req.requirement.lower()
                for key, value in symptoms.items():
                    if value and any(word in req_text for word in [key]):
                        matched += 1
                        break
            rule_score = matched / total if total else 0
            combined = min(1.0, rule_score * 0.7 + boost * 0.3)
            if combined > best_score:
                best_score = combined
                best_disease = disease

        if not best_disease:
            return {
                "predicted_disease": "Unknown",
                "confidence": 0.0,
                "urgency_level": "Medium",
                "input_type": "voice"
            }

        urgency = self._get_urgency(best_score)
        return {
            "predicted_disease": best_disease.name,
            "confidence": round(best_score, 2),
            "ai_confidence": 0.0,
            "rule_score": round(best_score, 2),
            "symptom_boost": 0.0,
            "description": best_disease.description,
            "symtoms": best_disease.symtoms,
            "treatments": [
                {
                    "treatment_id": t.treatment_id,
                    "treatment_name": t.treatment_name,
                    "dosage": t.dosage,
                    "duration": t.duration
                } for t in best_disease.treatments
            ],
            "requirements": [r.requirement for r in best_disease.requirement],
            "urgency_level": urgency,
            "input_type": "voice"
        }

    # ------------------------------------------------------------------
    # FORM PATH — ML + rule hybrid with fallback
    # ------------------------------------------------------------------
    def _diagnose_from_form(self, data: dict, db: Session) -> Dict[str, Any]:
        try:
            ai_result = self.predictor.predict(data)
        except Exception as e:
            # ✅ Fallback to voice/rule path if ML predictor fails
            return self._diagnose_from_voice(
                {k: bool(v) for k, v in data.items()}, db
            )

        ai_disease = ai_result["disease"]
        ai_confidence = ai_result["confidence"]

        disease = db.query(Disease).filter(Disease.name == ai_disease).first()
        if not disease:
            return ai_result

        matched_requirements = 0
        total_requirements = len(disease.requirement)
        for req in disease.requirement:
            req_text = req.requirement.lower()
            for key, value in data.items():
                value_str = str(value).lower()
                if value_str in ["true", "yes"] and any(word in req_text for word in [key, value_str]):
                    matched_requirements += 1
                    break

        rule_score = matched_requirements / total_requirements if total_requirements else 0
        symptom_boost = self._symptom_rules_boost(data, ai_disease)
        final_confidence = min(1.0, (ai_confidence * 0.6 + rule_score * 0.3 + symptom_boost * 0.1))
        urgency = self._get_urgency(final_confidence)

        return {
            "predicted_disease": disease.name,
            "confidence": round(final_confidence, 2),
            "ai_confidence": round(ai_confidence, 2),
            "rule_score": round(rule_score, 2),
            "symptom_boost": round(symptom_boost, 2),
            "description": disease.description,
            "symtoms": disease.symtoms,
            "treatments": [
                {
                    "treatment_id": t.treatment_id,
                    "treatment_name": t.treatment_name,
                    "dosage": t.dosage,
                    "duration": t.duration
                } for t in disease.treatments
            ],
            "requirements": [r.requirement for r in disease.requirement],
            "urgency_level": urgency,
            "input_type": "form"
        }

    # ------------------------------------------------------------------
    # SHARED HELPERS
    # ------------------------------------------------------------------
    def _get_urgency(self, confidence: float) -> str:
        if confidence >= 0.75:
            return "High"
        elif confidence >= 0.45:
            return "Medium"
        return "Low"

    def _symptom_rules_boost(self, symptoms: dict, predicted_disease: str) -> float:
        boost_rules = {
            "Black_Pod_Disease": {"black_pods": 0.3, "pod_rot": 0.2},
            "Frosty_Pod_Rot":    {"frosty_pod": 0.3, "pod_rot": 0.2},
            "Witches__Broom":    {"witches_broom": 0.3, "swelling": 0.2},
            "Pod_Borer":         {"pod_borer": 0.3, "swelling": 0.1},
        }
        boost = 0.0
        for symptom, weight in boost_rules.get(predicted_disease, {}).items():
            if symptoms.get(symptom, False):
                boost += weight
        return min(boost, 0.3)