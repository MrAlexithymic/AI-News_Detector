# Use base image

FROM python:3.11-slim


# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 👇 Pre-download EasyOCR model (en+hi+mr)
RUN python -c "import easyocr; easyocr.Reader(['en', 'hi', 'mr'])"

# Copy app files
COPY . .

# Set port and start app
ENV PORT=5000
EXPOSE 5000
CMD bash -c "gunicorn app:app --bind 0.0.0.0:${PORT:-5000}"
