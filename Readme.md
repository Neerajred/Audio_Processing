These modules separate the code into logical components:

config.py: Handles environment variables, logging setup, and constants.
audio_processor.py: Manages audio downloading, preprocessing, and splitting.
language_utils.py: Manages language-related utilities like supported languages and validation.
transcription.py: Contains transcription logic for Google Cloud Speech-to-Text and Gemini fallback.
language_detection.py: Implements language detection logic.
translation.py: Handles translation to English using Google Translate or Gemini.
summarization.py: Manages summarization and action suggestion using Gemini.
utils.py: Contains utility functions like cleanup.
app.py: The main Flask application integrating all modules.