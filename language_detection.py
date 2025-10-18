from langdetect import detect
from transcription import transcribe_audio_from_gcs, transcribe_with_gemini
from config import COMMON_LANGUAGES, logger
from language_utils import get_supported_languages

def detect_language(gcs_uris, local_file_paths, speech_languages, translate_languages):
    try:
        transcripts = {}
        for lang in COMMON_LANGUAGES[:4]:
            for gcs_uri, local_path in zip(gcs_uris, local_file_paths):
                t, c, s = transcribe_audio_from_gcs(gcs_uri, local_path, lang)
                if t:
                    avg_conf = sum(c)/len(c) if c else 0
                    score = avg_conf * (1 + len(t.split())/100)
                    transcripts[lang] = {"transcript": t, "confidence": avg_conf, "score": score}
        if transcripts:
            detected_lang = max(transcripts.items(), key=lambda x: x[1]["score"])[0]
            return detected_lang, transcripts[detected_lang]["transcript"]

        # fallback
        t, c, s = transcribe_audio_from_gcs(gcs_uris[0], local_file_paths[0], "en-US")
        lang = detect(t[:2000])
        lang_map = {
            "en": "en-US", "te": "te-IN", "hi": "hi-IN", "ta": "ta-IN", 
            "kn": "kn-IN", "ml": "ml-IN", "mr": "mr-IN", "fr": "fr-FR",
            "es": "es-ES", "bn": "bn-IN", "gu": "gu-IN", "pa": "pa-IN",
            "ur": "ur-IN", "de": "de-DE", "it": "it-IT", "ja": "ja-JP",
            "zh": "zh-CN", "or": "or-IN", "as": "as-IN", "si": "si-LK",
            "ar": "ar-SA", "ru": "ru-RU", "pt": "pt-BR", "ko": "ko-KR"
        }
        detected_lang = lang_map.get(lang, "te-IN")
        t, _, _ = transcribe_audio_from_gcs(gcs_uris[0], local_file_paths[0], detected_lang)
        return detected_lang, t

    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
        return "te-IN", ""
