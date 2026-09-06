FROM python:3.11-slim

# ffmpeg: broader audio format support for faster-whisper (voice query, WAV ingestion)
# libgl1: required by opencv (a dependency of easyocr) even in headless environments
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# torch defaults to the CUDA/GPU build on Linux; install the CPU-only build
# first (everything here runs device="cpu" explicitly) so the rest of
# requirements.txt's install picks up an already-satisfied torch instead of
# pulling ~1GB+ of unused NVIDIA CUDA libraries.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
