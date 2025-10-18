from google.cloud import translate_v2 as translate
import google.generativeai as genai
from config import GEMINI_API_KEY, logger

def translate_to_english(text, source_lang, translate_languages):
    try:
        if source_lang.startswith("en"):
            return text
        target_lang = source_lang.split("-")[0] if source_lang not in translate_languages else source_lang
        client = translate.Client()
        translated_text = ""
        max_len = 4000
        for i in range(0, len(text), max_len):
            chunk = text[i:i+max_len]
            result = client.translate(chunk, source_language=target_lang, target_language="en")
            translated_text += result["translatedText"] + " "
        return translated_text.strip()
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = f"Translate this from {source_lang} to English: {text}"
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as ge:
            logger.error(f"Gemini translation failed: {ge}")
            return text
