import subprocess
import sys

print("🚀 Bắt đầu chạy app1.py")
print("📞 Gọi app2.py...")

try:
    result = subprocess.run([sys.executable, "app2.py"], check=True, capture_output=True, text=True)
    print("✅ app2.py chạy thành công!")
    if result.stdout:
        print("📤 Output từ app2.py:", result.stdout.strip())
except subprocess.CalledProcessError as e:
    print("❌ Lỗi khi chạy app2.py:", e)
    sys.exit(1)

print("🎉 app1.py hoàn thành!") 