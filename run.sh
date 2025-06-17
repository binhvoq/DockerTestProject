#!/bin/bash

# Script tự động build và chạy Docker workflow cho Linux/macOS
# Tác giả: Demo Docker workflow app1.py -> app2.py -> app3.py

echo "🚀 Bắt đầu Docker workflow demo..."
echo "=================================="

# Tên image Docker
IMAGE_NAME="python-workflow-demo"

# Kiểm tra Docker có đang chạy không
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker không chạy hoặc chưa được cài đặt!"
    echo "Vui lòng khởi động Docker trước khi chạy script này."
    exit 1
fi

# Tạo thư mục output nếu chưa có
echo "📁 Tạo thư mục output..."
mkdir -p output

# Build Docker image
echo "🔨 Building Docker image: $IMAGE_NAME"
if docker build -t $IMAGE_NAME .; then
    echo "✅ Build thành công!"
else
    echo "❌ Build thất bại!"
    exit 1
fi

# Chạy container với volume mount
echo "🏃 Chạy container..."
echo "📂 Mount thư mục output: $(pwd)/output -> /app/output"
echo "=================================="

if docker run --rm -v "$(pwd)/output:/app/output" $IMAGE_NAME; then
    echo "=================================="
    echo "✅ Workflow hoàn thành thành công!"
    echo ""
    echo "📋 Kết quả:"
    echo "  - Kiểm tra thư mục: $(pwd)/output"
    echo "  - File temp.txt: $(pwd)/output/temp.txt"
    echo "  - File result.txt: $(pwd)/output/result.txt"
    echo ""
    
    # Hiển thị nội dung file result.txt nếu có
    if [ -f "output/result.txt" ]; then
        echo "📄 Nội dung file result.txt:"
        echo "----------------------------"
        cat output/result.txt
        echo "----------------------------"
    fi
    
    echo "🎉 Demo hoàn thành!"
else
    echo "❌ Container chạy thất bại!"
    exit 1
fi 