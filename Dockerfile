# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system-level dependencies for OpenCV, Torch, EasyOCR
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Environment port for Render
ENV PORT=5000
EXPOSE 5000

# Launch the app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]

