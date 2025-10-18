from langdetect import detect, DetectorFactory
from config import COMMON_LANGUAGES, logger

DetectorFactory.seed = 0

def get_supported_languages():
    speech_languages = set(COMMON_LANGUAGES)
    translate_languages = {
        "en", "te", "hi", "ta", "kn", "ml", "mr", "fr", "es", "bn", "gu",
        "pa", "ur", "de", "it", "ja", "zh", "or", "as", "si", "ar", "ru",
        "pt", "ko"
    }
    return speech_languages, translate_languages

def validate_language_code(language_code, speech_languages, translate_languages):
    if not language_code or not isinstance(language_code, str):
        logger.warning(f"Invalid language code: {language_code}. Defaulting to te-IN")
        return "te-IN"
    if language_code in speech_languages:
        return language_code
    base_lang = language_code.split('-')[0]
    if base_lang in speech_languages or base_lang in translate_languages:
        logger.warning(f"Using base language code: {base_lang}")
        return base_lang
    logger.warning(f"Language code {language_code} not supported. Defaulting to te-IN")
    return "te-IN"
