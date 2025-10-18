# app.py
from flask import Flask, request, jsonify
from functools import wraps
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import requests
from audio_processor import download_audio, split_audio, get_audio_info
from language_utils import get_supported_languages, validate_language_code
from transcription import transcribe_audio_parallel_local, transcribe_with_gemini
from translation import translate_to_english
from summarization import summarize_with_gemini, suggest_actions_with_gemini
from utils import cleanup_files_and_folder
from config import FLASK_API_KEY, logger, TASK_URL

app = Flask(__name__)

# API Key Decorator
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-Key")
        if api_key != FLASK_API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# Routes
@app.route('/', methods=['GET'])
def welcome():
    return "<h1>Audio Processing API</h1>"

@app.route('/process_audio', methods=['POST'])
# @require_api_key
def process_audio():
    local_paths = []
    try:
        audio_url = request.form.get('audio_url')
        if not audio_url:
            return jsonify({"error": "No audio URL provided"}), 400

        speech_languages, translate_languages = get_supported_languages()

        # Download & preprocess
        local_path = download_audio(audio_url)
        local_paths = split_audio(local_path, chunk_length_ms=15000)

        # Parallel transcription
        transcript = transcribe_audio_parallel_local(local_paths, language_code="te-IN")

        # Fallback to Gemini if Google STT fails or confidence is low
        if not transcript.strip():
            logger.info("Falling back to Gemini transcription")
            with ThreadPoolExecutor(max_workers=4) as executor:
                results = executor.map(transcribe_with_gemini, local_paths)
            transcript = " ".join(results).strip()

        if not transcript:
            return jsonify({"error": "No transcription results"}), 200

        # Translate to English if needed
        translated_transcript = translate_to_english(transcript, "te-IN", translate_languages)

        # Summarization & Action Suggestion (parallel)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_summary = executor.submit(summarize_with_gemini, translated_transcript)
            future_action = executor.submit(lambda: suggest_actions_with_gemini(future_summary.result()))

            summary = future_summary.result()
            suggested_action = future_action.result()

        url = TASK_URL

        payload = {
            "customerno": "7013680237", 
            "agentno": "9030555086", 
            "taskactivity": "Call", 
            "duedate": "2025-10-12 15:30",
            "remarks": "Need to call the Customer"
        }

        # -----------------------------
        # Send payload to external API
        # -----------------------------
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()  # Raises HTTPError if the response is 4xx/5xx
            logger.info(f"Task sent successfully: {response.text}")
        except requests.RequestException as req_err:
            logger.error(f"Failed to send task: {req_err}")

        # Return the transcription summary and suggested action
        return jsonify({
            "summary": summary,
            "suggested_action": suggested_action
        }), 200

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

    finally:
        cleanup_files_and_folder()


# Entry Point
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
