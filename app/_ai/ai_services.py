import logging
from app._ai.image_predictor import ImagePredictor
from app._ai.hybrid_model import HybridDiagnosis
from app._ai.voice_processor import VoiceProcessor


logger = logging.getLogger(__name__)


class AIService:
    _image_model = None
    _hybrid_model = None
    _voice_model = None
    

    @classmethod
    def image_model(cls):
        if cls._image_model is None:
            logger.info("Loading ImagePredictor model...")
            cls._image_model = ImagePredictor()
        return cls._image_model

    @classmethod
    def hybrid_model(cls):
        if cls._hybrid_model is None:
            logger.info("Loading HybridDiagnosis model...")
            cls._hybrid_model = HybridDiagnosis()
        return cls._hybrid_model

    @classmethod
    def voice_model(cls):
        if cls._voice_model is None:
            logger.info("Loading VoiceProcessor model...")
            cls._voice_model = VoiceProcessor()
        return cls._voice_model
    

    
    

   