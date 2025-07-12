# Use base image
FROM python:3.10-slim-buster



# Set working directory
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt \
 && apt-get clean \
 && rm -rf /root/.cache /tmp/*

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

# Copy app files
COPY . .

# Set port and start app
ENV PORT=5000
EXPOSE 5000
CMD bash -c "gunicorn app:app --bind 0.0.0.0:${PORT:-5000}"
