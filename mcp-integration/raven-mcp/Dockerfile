# Raven Pro MCP Server Dockerfile
# Includes Python + R runtime with Rraven for bioacoustic analysis

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    r-base \
    r-base-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libfontconfig1-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libfreetype6-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg-dev \
    sox \
    libsox-dev \
    libsox-fmt-all \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install R packages for bioacoustic analysis
RUN R -e "install.packages(c('Rraven', 'warbleR', 'seewave', 'tuneR', 'monitoR'), repos='https://cloud.r-project.org/')"

# Copy server code
COPY server.py .

# Create workspace directory
RUN mkdir -p /workspace/shared

# Expose MCP port
EXPOSE 7085

# Run server
CMD ["python", "server.py"]
