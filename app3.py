import os
from datetime import datetime

print("🔧 Đang chạy app3.py")

# Đọc file temp.txt
temp_file_path = "/app/output/temp.txt"
result_file_path = "/app/output/result.txt"

print(f"📖 Đọc file: {temp_file_path}")
try:
    with open(temp_file_path, "r", encoding="utf-8") as f:
        temp_data = f.read()
    print(f"✅ Đã đọc temp.txt: {temp_data}")
except Exception as e:
    print(f"❌ Lỗi khi đọc temp.txt: {e}")
    exit(1)

# Xử lý dữ liệu và tạo kết quả cuối cùng
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
final_result = f"""
=== KẾT QUÀ CUỐI CÙNG ===
Thời gian xử lý: {current_time}
Dữ liệu từ bước trước: {temp_data}

Workflow đã hoàn thành:
✅ app1.py -> app2.py -> app3.py
✅ Tạo temp.txt -> Đọc temp.txt -> Tạo result.txt

Trạng thái: THÀNH CÔNG 🎉
"""

print(f"💾 Tạo file kết quả: {result_file_path}")
try:
    with open(result_file_path, "w", encoding="utf-8") as f:
        f.write(final_result)
    print("✅ Đã tạo result.txt thành công!")
except Exception as e:
    print(f"❌ Lỗi khi tạo result.txt: {e}")
    exit(1)

print("🎉 app3.py hoàn thành! File result.txt đã được tạo.") 