# Docker Video Generation Pipeline

Một pipeline tự động để tạo video từ các chủ đề sử dụng Docker, OpenAI API, và FFmpeg.

## Yêu cầu

- Docker đã được cài đặt và đang chạy
- OpenAI API Key
- Kết nối internet (để tải hình ảnh từ Google)

## Cách sử dụng

### 1. Chuẩn bị môi trường

```bash
# Set OpenAI API Key
export OPENAI_API_KEY="your_openai_api_key_here"
```

### 2. Chuẩn bị file input

Chỉnh sửa file `subjects.txt` và thêm các chủ đề video bạn muốn tạo:

```
The Mystery of Dark Matter in the Universe
What Are Black Holes and How Do They Form
The Science Behind Time Travel Theories
Your Custom Topic Here
```

### 3. Chạy pipeline

```bash
# Cấp quyền thực thi cho script
chmod +x run.sh

# Chạy pipeline
./run.sh
```

### 4. Kết quả

Sau khi hoàn thành, bạn sẽ có:

- `output/plan.txt` - Danh sách các video đã tạo
- `output/my_result/` - Thư mục chứa các file video (.mp4)

## Cấu trúc Pipeline

1. **Generate Content** - Tạo kịch bản từ chủ đề sử dụng OpenAI API
2. **Create Plan** - Chia kịch bản thành các phần nhỏ
3. **Process Videos** - Xử lý từng video:
   - Tạo audio từ text (Google TTS)
   - Tạo keywords cho hình ảnh (OpenAI API)
   - Tải hình ảnh từ Google Images
   - Kết hợp audio và hình ảnh thành video (FFmpeg)

## Chạy thủ công

Nếu muốn chạy từng bước thủ công:

```bash
# Build image
docker build -t video-generation-pipeline .

# Chạy container
docker run --rm \
    -v "$(pwd)/output:/app/output" \
    -v "$(pwd)/subjects.txt:/app/subjects.txt" \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    video-generation-pipeline
```

## Cấu hình

Có thể chỉnh sửa các tham số trong code:

- `MIN_WORD_COUNT` trong `generate_content.py` - Độ dài tối thiểu của script
- `TARGET_WIDTH`, `TARGET_HEIGHT` trong `video_combiner.py` - Độ phân giải video
- `TIMEOUT_SECONDS` trong `process_videos.py` - Thời gian timeout cho mỗi video

## Troubleshooting

### Lỗi OPENAI_API_KEY

```bash
export OPENAI_API_KEY="your_actual_api_key"
```

### Lỗi tải hình ảnh

Pipeline sẽ tự động tạo placeholder images nếu không tải được hình ảnh từ Google.

### Lỗi ffmpeg

Đảm bảo Docker container có quyền truy cập mạng và đủ dung lượng disk.

## Output cho YouTube Upload

Kết quả tạo ra sẽ tương thích với input cho `uploadTuDongYoutube.py`:

- `plan.txt` - Chứa danh sách video và script files
- `my_result/` - Chứa các file video .mp4

Bạn có thể copy 2 thứ này về Windows và sử dụng với script upload YouTube của mình. 