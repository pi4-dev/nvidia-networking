FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NVIDIA_DATA_PATH=/data/nvidia-interconnects.json \
    DEVICE_PROFILES_PATH=/profiles/device-profiles.json \
    MAX_DATA_BYTES=2097152 \
    MAX_PROFILE_BYTES=524288 \
    COMPAT_CACHE_MAX_ENTRIES=256 \
    FORWARDED_ALLOW_IPS=127.0.0.1

WORKDIR /app

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home-dir /nonexistent --shell /usr/sbin/nologin app

COPY compatibility-validator/requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --require-hashes --index-url https://pypi.org/simple -r /app/requirements.txt \\
    && python -m pip check

COPY compatibility-validator/app /app/app
COPY compatibility-validator/data/device-profiles.json /profiles/device-profiles.json
COPY data/nvidia-interconnects.json /data/nvidia-interconnects.json

USER 10001:10001

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).read()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--limit-concurrency", "100", "--backlog", "128", "--timeout-keep-alive", "5", "--proxy-headers"]
