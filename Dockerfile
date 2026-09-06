FROM python:3.11-slim

# ffmpeg: broader audio format support for faster-whisper (voice query, WAV ingestion)
# libgl1: required by opencv (a dependency of easyocr) even in headless environments
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
