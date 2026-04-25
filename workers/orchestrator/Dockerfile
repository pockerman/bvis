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

WORKDIR /analysis_coordinator

# Copy the utils in the container
COPY ./core_utils /analysis_coordinator/analysis_coordinator/core_utils
COPY ./summarization_utils /analysis_coordinator/analysis_coordinator/summarization_utils
COPY ./pdf_generation_utils /analysis_coordinator/analysis_coordinator/pdf_generation_utils

COPY ./api /analysis_coordinator/analysis_coordinator/api
COPY ./assets /analysis_coordinator/analysis_coordinator/assets
COPY ./api/main.py .
COPY api_reqs.txt .

RUN pip install --no-cache-dir -r api_reqs.txt

# port this container exposes
EXPOSE 8000

ENV PYTHONPATH=/analysis_coordinator

# =====================================================
# ===== Set the command to run the uvicorn server =====
# =====================================================

# Set the command to run the uvicorn server.
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
