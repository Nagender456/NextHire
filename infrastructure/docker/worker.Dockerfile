FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY workers/worker.py .
COPY backend/app ./app
USER nobody
EXPOSE 8010
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8010/health')"
CMD ["uvicorn", "worker:app", "--host", "0.0.0.0", "--port", "8010"]
