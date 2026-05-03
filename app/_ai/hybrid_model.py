# app/_ai/hybrid_model.py
from sqlalchemy.orm import Session
from app.models.disease import Disease
from typing import Dict, Any


class HybridDiagnosis:
    def __init__(self):
        self.predictor = None  # No ML predictor needed - using rule-based only

    def _is_voice_input(self, data: dict) -> bool:
        if not data:
            return False
        bool_count = sum(1 for v in data.values() if isinstance(v, bool))
        return bool_count > 0

    def diagnose(self, data: dict, db: Session = None) -> Dict[str, Any]:
        is_voice = self._is_voice_input(data)
        if is_voice:
            return self._diagnose_from_voice(data, db)
        else:
            return self._diagnose_from_form(data, db)

    def _diagnose_from_voice(self, symptoms: Dict[str, bool], db: Session) -> Dict[str, Any]:
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
            return {"predicted_disease": "Unknown", "confidence": 0.0,
                    "urgency_level": "Medium", "input_type": "voice"}

        urgency = self._get_urgency(best_score)
        return {
            "predicted_disease": best_disease.name,
            "confidence": round(best_score, 2),
            "ai_confidence": 0.0,
            "rule_score": round(best_score, 2),
            "symptom_boost": 0.0,
            "description": best_disease.description,
            "symtoms": best_disease.symtoms,
            "treatments": [{"treatment_id": t.treatment_id, "treatment_name": t.treatment_name,
                "dosage": t.dosage, "duration": t.duration} for t in best_disease.treatments],
            "requirements": [r.requirement for r in best_disease.requirement],
            "urgency_level": urgency,
            "input_type": "voice"
        }

    def _diagnose_from_form(self, data: dict, db: Session) -> Dict[str, Any]:
        # Always use rule-based path (no ML predictor)
        return self._diagnose_from_voice(
            {k: bool(v) for k, v in data.items()}, db
        )

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
            "Witches_Broom":     {"witches_broom": 0.3, "swelling": 0.2},
            "Healthy":           {},
        }
        boost = 0.0
        for symptom, weight in boost_rules.get(predicted_disease, {}).items():
            if symptoms.get(symptom, False):
                boost += weight
        return min(boost, 0.3)
