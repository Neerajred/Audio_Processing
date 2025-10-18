# Runtime with CUDA libraries (host provides the NVIDIA driver)
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# System deps (FFmpeg required by pydub)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip ffmpeg ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Ensure upload dir exists (your code also recreates it)
RUN mkdir -p /app/Uploads

# Environment expected by your code
ENV FFMPEG_PATH=/usr/bin/ffmpeg
# Flask listens on 5000 inside the container (matches app.py)
EXPOSE 5000

# Start the Flask app
CMD ["python3", "app.py"]
