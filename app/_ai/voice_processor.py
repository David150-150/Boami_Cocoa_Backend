



# import whisper
# import tempfile
# import os
# import logging
# import re

# logger = logging.getLogger(__name__)


# class VoiceProcessor:
#     def __init__(self, model_size="medium"):
#         self.model = whisper.load_model(model_size)
#         logger.info(f"Whisper '{model_size}' loaded")

#     def process_voice(self, audio_bytes):
#         try:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
#                 tmp.write(audio_bytes)
#                 tmp_path = tmp.name

#             try:
#                 result = self.model.transcribe(
#                     tmp_path,
#                     language=None,
#                     task="translate",
#                     fp16=False
#                 )

#                 text = result.get("text", "").lower()
#                 lang = result.get("language", "unknown")

#                 symptoms = self.extract_symptoms(text)

#                 return {
#                     "transcript": text,
#                     "language": lang,
#                     "symptoms": symptoms
#                 }

#             finally:
#                 if os.path.exists(tmp_path):
#                     os.remove(tmp_path)

#         except Exception as e:
#             logger.exception("Voice processing failed")
#             return {
#                 "transcript": "",
#                 "language": "unknown",
#                 "symptoms": {}
#             }

#     def extract_symptoms(self, text):
#         return {
#             "spots": bool(re.search(r"spot", text)),
#             "leaf_curl": bool(re.search(r"curl", text)),
#             "yellow_leaf": bool(re.search(r"yellow", text)),
#             "pod_rot": bool(re.search(r"rot", text)),
#             "black_pods": bool(re.search(r"black", text)),
#             "swelling": bool(re.search(r"swollen", text)),
#             "witches_broom": bool(re.search(r"broom", text)),
#             "pod_borer": bool(re.search(r"borer", text)),
#             "frosty_pod": bool(re.search(r"frosty", text))
#         }









# app/_ai/voice_processor.py

import os
import re
import logging
import tempfile

logger = logging.getLogger(__name__)


class VoiceProcessor:
    """
    Transcribes farmer voice notes using Whisper and extracts
    cocoa disease symptoms from the transcript.

    Supports: English, Twi, Fante, Ga, Hausa (via Whisper auto-detect)
    """

    # Use 'base' — good accuracy, runs on CPU, ~140MB
    # Options: tiny (fastest), base (recommended), small, medium (best but slow)
    MODEL_SIZE = "base"

    # ------------------------------------------------------------------ #
    #  SYMPTOM KEYWORDS
    #  English + Twi + common farmer descriptions
    # ------------------------------------------------------------------ #
    SYMPTOM_KEYWORDS = {
        "spots": [
            # English
            "spot", "spots", "mark", "marks", "dot", "dots", "lesion",
            "patch", "patches", "discolor",
            # Twi
            "nsensanee", "aware", "nsesane",
        ],
        "leaf_curl": [
            "curl", "curling", "twisted", "twist", "wrinkle", "wilt",
            # Twi
            "hyehye", "twetwe",
        ],
        "yellow_leaf": [
            "yellow", "yellowing", "pale", "fading", "chlorosis",
            # Twi
            "akokɔ sradeɛ", "fitaa",
        ],
        "pod_rot": [
            "rot", "rotten", "rotting", "decay", "decaying", "soft",
            "mushy", "smell", "stink",
            # Twi
            "popo", "bɔne",
        ],
        "black_pods": [
            "black", "blacken", "blackening", "dark", "brown", "dead pod",
            # Twi
            "tuntum", "fifiri",
        ],
        "swelling": [
            "swell", "swollen", "swelling", "bump", "bulge", "enlarge",
            "big stem", "thick stem",
            # Twi
            "hyɛso", "boaboabo",
        ],
        "witches_broom": [
            "broom", "witches", "abnormal", "bushy", "many shoots",
            "extra branch", "cluster",
            # Twi
            "dua dodow", "branches",
        ],
        "pod_borer": [
            "borer", "worm", "insect", "hole", "holes", "larvae",
            "pest", "eaten", "chew",
            # Twi
            "aboa", "hwammono", "loch",
        ],
        "frosty_pod": [
            "frosty", "frost", "white", "powder", "fuzzy", "fluffy",
            "cotton", "mold", "mould",
            # Twi
            "fitaa powder", "white powder",
        ],
    }

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            import whisper
            logger.info("Loading Whisper '%s' model...", self.MODEL_SIZE)
            self.model = whisper.load_model(self.MODEL_SIZE)
            logger.info("✅ Whisper model loaded.")
        except ImportError:
            logger.error("❌ whisper not installed. Run: pip install openai-whisper")
        except Exception as e:
            logger.exception("❌ Failed to load Whisper model: %s", e)

    def is_ready(self) -> bool:
        return self.model is not None

    # ------------------------------------------------------------------ #
    #  PROCESS VOICE
    # ------------------------------------------------------------------ #
    def process_voice(self, audio_bytes: bytes) -> dict:
        """
        Transcribe audio bytes and extract symptoms.

        Returns
        -------
        dict:
            transcript  : str   — full transcribed text
            language    : str   — detected language code
            symptoms    : dict  — {symptom_name: bool}
        """
        if not self.is_ready():
            logger.warning("Whisper model not loaded — returning empty symptoms")
            return self._empty_response("Model not loaded.")

        tmp_path = None
        try:
            # Write audio bytes to temp file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".wav"
            ) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            # Transcribe — auto-detect language, translate to English
            result = self.model.transcribe(
                tmp_path,
                language=None,      # auto-detect (Twi, English, etc.)
                task="translate",   # translate to English for symptom matching
                fp16=False,         # CPU-safe
                verbose=False,
            )

            text = result.get("text", "").strip().lower()
            lang = result.get("language", "unknown")

            logger.info("Transcript [%s]: %s", lang, text[:100])

            symptoms = self.extract_symptoms(text)

            return {
                "transcript": text,
                "language":   lang,
                "symptoms":   symptoms,
            }

        except Exception as e:
            logger.exception("Voice processing failed: %s", e)
            return self._empty_response(str(e))

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    # ------------------------------------------------------------------ #
    #  EXTRACT SYMPTOMS
    # ------------------------------------------------------------------ #
    def extract_symptoms(self, text: str) -> dict:
        """
        Match keywords in transcript to symptom flags.
        Returns dict of {symptom: bool}
        """
        text = text.lower()
        symptoms = {}

        for symptom, keywords in self.SYMPTOM_KEYWORDS.items():
            matched = any(
                re.search(rf"\b{re.escape(kw)}\b", text)
                for kw in keywords
            )
            symptoms[symptom] = matched

        detected = [k for k, v in symptoms.items() if v]
        logger.info("Symptoms detected: %s", detected or "none")

        return symptoms

    # ------------------------------------------------------------------ #
    #  HELPERS
    # ------------------------------------------------------------------ #
    def _empty_response(self, message: str = "") -> dict:
        return {
            "transcript": "",
            "language":   "unknown",
            "symptoms":   {s: False for s in self.SYMPTOM_KEYWORDS},
            "message":    message,
        }

    def get_model_info(self) -> dict:
        return {
            "ready":      self.is_ready(),
            "model_size": self.MODEL_SIZE,
            "languages":  "auto-detect (English, Twi, Fante, Ga, Hausa)",
            "symptoms":   list(self.SYMPTOM_KEYWORDS.keys()),
        }