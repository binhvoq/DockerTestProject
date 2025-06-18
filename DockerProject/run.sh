#!/bin/bash

# Script tự động build và chạy Docker workflow cho Linux
# Tác giả: Docker Video Generation Pipeline

echo "🚀 Bắt đầu Docker Video Generation Pipeline..."
echo "================================================"

# Tên image Docker
IMAGE_NAME="video-generation-pipeline"

# Kiểm tra Docker có đang chạy không
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker không chạy hoặc chưa được cài đặt!"
    echo "Vui lòng khởi động Docker trước khi chạy script này."
    exit 1
fi

# Kiểm tra file subjects.txt
if [ ! -f "subjects.txt" ]; then
    echo "❌ Không tìm thấy file subjects.txt!"
    echo "Vui lòng tạo file subjects.txt với danh sách chủ đề video."
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

# Kiểm tra OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ OPENAI_API_KEY chưa được set!"
    echo "Vui lòng set biến môi trường OPENAI_API_KEY:"
    echo "export OPENAI_API_KEY=your_api_key_here"
    exit 1
fi

# Chạy container với volume mount và environment variable
echo "🏃 Chạy container..."
echo "📂 Mount thư mục output: $(pwd)/output -> /app/output"
echo "🔑 Using OpenAI API Key: ${OPENAI_API_KEY:0:10}..."
echo "================================================"

if docker run --rm \
    -v "$(pwd)/output:/app/output" \
    -v "$(pwd)/subjects.txt:/app/subjects.txt" \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    $IMAGE_NAME; then
    
    echo "================================================"
    echo "✅ Pipeline hoàn thành thành công!"
    echo ""
    echo "📋 Kết quả:"
    echo "  - Thư mục output: $(pwd)/output"
    echo "  - File plan.txt: $(pwd)/output/plan.txt"
    echo "  - Video files: $(pwd)/output/my_result/"
    echo ""
    
    # Hiển thị plan.txt nếu có
    if [ -f "output/plan.txt" ]; then
        echo "📄 Nội dung file plan.txt:"
        echo "----------------------------"
        cat output/plan.txt
        echo "----------------------------"
    fi
    
    # Hiển thị danh sách video
    if [ -d "output/my_result" ] && [ "$(ls -A output/my_result)" ]; then
        echo "🎥 Danh sách video đã tạo:"
        ls -la output/my_result/
    else
        echo "⚠️ Không tìm thấy video nào trong my_result/"
    fi
    
    echo "🎉 Pipeline hoàn thành!"
else
    echo "❌ Container chạy thất bại!"
    exit 1
fi 