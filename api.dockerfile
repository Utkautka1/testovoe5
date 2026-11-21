FROM node:20-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py api.py ./
COPY api/ ./api/
COPY core/ ./core/
COPY services/ ./services/
COPY utils/ ./utils/
COPY data/ ./data/
COPY --from=frontend-builder /build/dist ./frontend/dist

EXPOSE 8000
CMD ["python", "api.py"]
