# API Dockerfile


FROM python:3.12-slim
LABEL authors="alex"

# Install system dependencies needed for pycairo and svglib
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./__init__.py /app/orchestrator/__init__.py
COPY ./routes.py   /app/orchestrator/routes.py
COPY ./models.py  /app/orchestrator/models.py
COPY ./main.py    /app/main.py
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# port this container exposes
EXPOSE 8000

ENV PYTHONPATH=/app

# =====================================================
# ===== Set the command to run the uvicorn server =====
# =====================================================

# Set the command to run the uvicorn server.
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
