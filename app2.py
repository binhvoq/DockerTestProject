import subprocess
import sys
import os

print("⚙️ Đang chạy app2.py")

# Tạo file temp.txt với nội dung
temp_content = "Dữ liệu từ app2.py - Thời gian xử lý: Thành công"
temp_file_path = "/app/output/temp.txt"

print(f"📝 Tạo file tạm: {temp_file_path}")
try:
    # Đảm bảo thư mục output tồn tại
    os.makedirs("/app/output", exist_ok=True)
    
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(temp_content)
    print("✅ Đã tạo temp.txt thành công")
except Exception as e:
    print(f"❌ Lỗi khi tạo temp.txt: {e}")
    sys.exit(1)

# Gọi app3.py
print("📞 Gọi app3.py...")
try:
    result = subprocess.run([sys.executable, "app3.py"], check=True, capture_output=True, text=True)
    print("✅ app3.py chạy thành công!")
    if result.stdout:
        print("📤 Output từ app3.py:", result.stdout.strip())
except subprocess.CalledProcessError as e:
    print(f"❌ Lỗi khi chạy app3.py: {e}")
    sys.exit(1)

print("🎉 app2.py hoàn thành!") 