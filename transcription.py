# transcription.py
import os
import time
import google.generativeai as genai
from google.api_core.retry import Retry
from google.api_core.exceptions import DeadlineExceeded, ServiceUnavailable
from google.cloud import speech_v1p1beta1 as speech
from audio_processor import get_audio_info
from config import logger, GEMINI_API_KEY
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydub import AudioSegment

# --- Configure Clients ---
genai.configure(api_key=GEMINI_API_KEY)

encoding_map = {
    "mp3": speech.RecognitionConfig.AudioEncoding.MP3,
    "mpeg": speech.RecognitionConfig.AudioEncoding.MP3,
    "wav": speech.RecognitionConfig.AudioEncoding.LINEAR16,
    "flac": speech.RecognitionConfig.AudioEncoding.FLAC,
    "ogg": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
    "amr": speech.RecognitionConfig.AudioEncoding.AMR
}

# Retry policy for Google Speech
retry_policy = Retry(
    initial=2.0,  # initial wait
    maximum=60.0, # max wait
    multiplier=2.0,
    deadline=900.0 # total retry window (15 min)
)


def transcribe_audio_chunk_local(audio_bytes, format="wav", sample_rate=16000, language_code="te-IN", timeout=600):
    """
    Transcribes a single audio chunk using Google STT.
    """
    try:
        encoding = encoding_map.get(format, speech.RecognitionConfig.AudioEncoding.LINEAR16)
        audio = speech.RecognitionAudio(content=audio_bytes)

        config = speech.RecognitionConfig(
        encoding=encoding,
        sample_rate_hertz=sample_rate,
        language_code=language_code,  # primary language
        alternative_language_codes=["en-IN", "hi-IN"],  # secondary detection
        enable_automatic_punctuation=True,
        model="latest_long",
    )

        client = speech.SpeechClient()  # safer per-thread
        operation = client.long_running_recognize(config=config, audio=audio, retry=retry_policy)
        response = operation.result(timeout=timeout)

        transcripts = []
        for result in response.results:
            if result.alternatives:
                best = result.alternatives[0]
                if best.confidence >= 0.5:  # stricter threshold
                    transcripts.append(best.transcript)

        return " ".join(transcripts)

    except (DeadlineExceeded, ServiceUnavailable) as e:
        logger.error(f"Google STT timeout/unavailable: {e}")
        return ""
    except Exception as e:
        logger.warning(f"Chunk transcription failed: {e}")
        return ""


def transcribe_audio_parallel_local(file_paths, language_code="te-IN", max_workers=4, timeout=600):
    """
    Transcribes multiple audio files in parallel.
    """
    transcripts = []

    def worker(path):
        try:
            audio = AudioSegment.from_file(path).set_channels(1).set_frame_rate(16000)
            audio_bytes = audio.raw_data
            format = path.split(".")[-1].lower()
            sample_rate = audio.frame_rate
            return transcribe_audio_chunk_local(audio_bytes, format, sample_rate, language_code, timeout)
        except Exception as e:
            logger.warning(f"Failed reading {path}: {e}")
            return ""

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(worker, path): path for path in file_paths}
        for future in as_completed(futures):
            try:
                result = future.result(timeout=timeout + 30)  # cushion
                if result:
                    transcripts.append(result)
            except Exception as e:
                logger.error(f"Worker failed for {futures[future]}: {e}")

    return " ".join(transcripts)


def transcribe_with_gemini(file_path, language_code="te-IN", timeout=300):
    """
    Transcribes audio using Gemini multimodal.
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        with open(file_path, "rb") as f:
            audio_bytes = f.read()

        prompt = f"Transcribe this audio in {language_code} with speaker tags if multiple speakers: [Speaker]: <text>"

        # Timeout wrapper
        start = time.time()
        response = model.generate_content(
            [{"mime_type": "audio/wav", "data": audio_bytes}, prompt]
        )
        if time.time() - start > timeout:
            logger.error("Gemini transcription timeout exceeded")
            return ""

        return response.text.strip() if response and hasattr(response, "text") else ""

    except Exception as e:
        logger.error(f"Gemini transcription failed: {e}")
        return ""
