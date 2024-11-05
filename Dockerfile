FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies using apt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg 
   

# Copy all files from current directory to /app
COPY . .

# Install required dependencies
RUN python -m pip install --upgrade pip \
    && pip install paddlepaddle==3.0.0b1 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/ \
    && pip install https://paddle-model-ecology.bj.bcebos.com/paddlex/whl/paddlex-3.0.0b1-py3-none-any.whl \
    && pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
