# Use smaller Python base
FROM python:3.10-slim-buster

# Set working directory
WORKDIR /app

# Install only what EasyOCR needs
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set PORT for Render/Railway/etc.
ENV PORT=5000
EXPOSE 5000

# Run your Flask app with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
