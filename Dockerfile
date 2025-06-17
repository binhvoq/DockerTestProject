# Sử dụng Python 3.10 slim để tiết kiệm dung lượng
FROM python:3.10-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy tất cả file Python vào container
COPY app1.py .
COPY app2.py .
COPY app3.py .

# Tạo thư mục output để chứa temp.txt và result.txt
# Thư mục này sẽ được mount với thư mục thật trên máy host
RUN mkdir -p /app/output

# Đặt quyền thực thi cho các file Python (tùy chọn)
RUN chmod +x *.py

# Lệnh mặc định khi container khởi động
CMD ["python", "app1.py"] 