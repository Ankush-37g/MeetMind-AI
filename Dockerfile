# ==========================================
# STAGE 1: Build React Frontend
# ==========================================
FROM node:20 AS frontend-builder
WORKDIR /app/frontend

# Install dependencies and build
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build


# ==========================================
# STAGE 2: Setup FastAPI Backend
# ==========================================
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies (ffmpeg required for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user required by Hugging Face Spaces
RUN useradd -m -u 1000 user
RUN chown -R user:user /app
USER user

# Set environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

# Install Python dependencies
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY --chown=user:user . .

# Copy the built React app from Stage 1
COPY --from=frontend-builder --chown=user:user /app/frontend/dist /app/frontend/dist

# Expose the standard Hugging Face Spaces port
EXPOSE 7860

# Run the FastAPI server on port 7860
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
