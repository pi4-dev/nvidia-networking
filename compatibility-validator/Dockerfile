FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NVIDIA_DATA_PATH=/data/nvidia-interconnects.json \
    DEVICE_PROFILES_PATH=/profiles/device-profiles.json

WORKDIR /app

COPY compatibility-validator/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY compatibility-validator/app /app/app
COPY compatibility-validator/data/device-profiles.json /profiles/device-profiles.json
COPY data/nvidia-interconnects.json /data/nvidia-interconnects.json

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).read()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
