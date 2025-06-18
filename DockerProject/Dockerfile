# Sử dụng Python 3.10 với base image có ffmpeg
FROM python:3.10-slim

# Thiết lập biến môi trường
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Cài đặt system dependencies bao gồm espeak-ng cho Kokoro TTS
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    git \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy requirements và cài đặt Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy tất cả code vào container
COPY . .

# Tạo thư mục output để mount
RUN mkdir -p /app/output

# Set OpenAI API key từ environment variable
ENV OPENAI_API_KEY=""

# Set permissions
RUN chmod +x *.py

# Lệnh mặc định khi container khởi động  
CMD ["python", "main.py"] 