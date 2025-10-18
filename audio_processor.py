import os
import time
import requests
import mimetypes
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range, high_pass_filter, low_pass_filter
from config import UPLOAD_FOLDER, SUPPORTED_FORMATS, logger, FFMPEG_PATH

AudioSegment.converter = FFMPEG_PATH

def download_audio(audio_url, retries=3, backoff=2):
    try:
        if not audio_url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL")
        logger.info(f"Downloading {audio_url}")
        for attempt in range(retries):
            try:
                response = requests.get(audio_url, timeout=(30, 300))
                response.raise_for_status()
                break
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                logger.warning(f"Retry {attempt+1} failed: {e}")
                time.sleep(backoff)
                backoff *= 2
        content_type = response.headers.get("content-type", "")
        extension = mimetypes.guess_extension(content_type) or ".wav"
        if extension not in SUPPORTED_FORMATS:
            extension = ".wav"
        local_path = os.path.join(UPLOAD_FOLDER, f"downloaded_audio_{int(time.time())}{extension}")
        with open(local_path, "wb") as f:
            f.write(response.content)
        logger.info(f"Downloaded audio to {local_path}")

        # Preprocess
        audio = AudioSegment.from_file(local_path)
        audio = normalize(compress_dynamic_range(audio))
        audio = high_pass_filter(audio, 250)
        audio = low_pass_filter(audio, 3000)
        audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        processed_path = os.path.join(UPLOAD_FOLDER, f"processed_{int(time.time())}.wav")
        audio.export(processed_path, format="wav", parameters=["-acodec", "pcm_s16le", "-ar", "16000"])
        logger.info(f"Processed audio to {processed_path}")
        return processed_path
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise e

def split_audio(audio_path, chunk_length_ms=60000):
    audio = AudioSegment.from_file(audio_path)
    duration = len(audio)
    if duration <= chunk_length_ms:
        return [audio_path]
    chunks = []
    overlap_ms = 1000
    for i in range(0, duration, chunk_length_ms - overlap_ms):
        chunk = audio[i:i+chunk_length_ms]
        chunk_path = os.path.join(UPLOAD_FOLDER, f"chunk_{int(time.time())}_{i}.wav")
        chunk.export(chunk_path, format="wav", parameters=["-acodec", "pcm_s16le", "-ar", "16000"])
        chunks.append(chunk_path)
    return chunks

def get_audio_info(audio_path):
    audio = AudioSegment.from_file(audio_path)
    return os.path.splitext(audio_path)[1][1:].lower(), audio.frame_rate
