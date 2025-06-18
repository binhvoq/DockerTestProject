#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

# Cấu hình paths
BASE_DIR = "/app"
INPUT_DIR = "/app"
OUTPUT_DIR = "/app/output"
TEMP_DIR = "/app/temp"

# Files
SUBJECTS_FILE = os.path.join(INPUT_DIR, "subjects.txt")
CONTENT_FILE = os.path.join(TEMP_DIR, "content.txt")
PLAN_FILE = os.path.join(TEMP_DIR, "plan.txt")

def setup_directories():
    """Tạo các thư mục cần thiết"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "my_result"), exist_ok=True)
    print("✅ Đã tạo các thư mục cần thiết")

def check_input():
    """Kiểm tra file input"""
    if not os.path.exists(SUBJECTS_FILE):
        print(f"❌ Không tìm thấy file subjects.txt tại {SUBJECTS_FILE}")
        return False
    
    with open(SUBJECTS_FILE, 'r', encoding='utf-8') as f:
        subjects = [line.strip() for line in f if line.strip()]
    
    if not subjects:
        print("❌ File subjects.txt trống")
        return False
    
    print(f"✅ Tìm thấy {len(subjects)} chủ đề trong subjects.txt")
    return True

def run_pipeline():
    """Chạy toàn bộ pipeline"""
    print("🚀 Bắt đầu chạy pipeline...")
    
    try:
        # Bước 1: Tạo nội dung
        print("\n📝 Bước 1: Tạo nội dung...")
        result = subprocess.run([sys.executable, "generate_content.py"], 
                              check=True, capture_output=True, text=True)
        print("✅ Hoàn thành tạo nội dung")
        
        # Bước 2: Tạo plan
        print("\n📋 Bước 2: Tạo plan...")
        result = subprocess.run([sys.executable, "create_plan.py"], 
                              check=True, capture_output=True, text=True)
        print("✅ Hoàn thành tạo plan")
        
        # Bước 3: Xử lý videos
        print("\n🎥 Bước 3: Xử lý videos...")
        result = subprocess.run([sys.executable, "process_videos.py"], 
                              check=True, capture_output=True, text=True)
        print("✅ Hoàn thành xử lý videos")
        
        # Copy plan.txt vào output
        if os.path.exists(PLAN_FILE):
            shutil.copy(PLAN_FILE, os.path.join(OUTPUT_DIR, "plan.txt"))
            print("✅ Đã copy plan.txt vào output")
        
        # Copy content.txt vào output để review
        if os.path.exists(CONTENT_FILE):
            shutil.copy(CONTENT_FILE, os.path.join(OUTPUT_DIR, "content.txt"))
            print("✅ Đã copy content.txt vào output")
        
        # Copy toàn bộ plan folder (chứa script files) vào output
        plan_dir = os.path.join(TEMP_DIR, "plan")
        if os.path.exists(plan_dir):
            output_plan_dir = os.path.join(OUTPUT_DIR, "scripts")
            if os.path.exists(output_plan_dir):
                shutil.rmtree(output_plan_dir)
            shutil.copytree(plan_dir, output_plan_dir)
            print("✅ Đã copy scripts vào output/scripts/")
        
        print("\n🎉 Pipeline hoàn thành thành công!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi chạy pipeline: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Lỗi không mong đợi: {e}")
        return False

def main():
    """Hàm main"""
    print("🐳 Docker Video Generation Pipeline")
    print("=" * 50)
    
    # Setup
    setup_directories()
    
    # Kiểm tra input
    if not check_input():
        sys.exit(1)
    
    # Chạy pipeline
    if run_pipeline():
        print("\n✅ Tất cả hoàn thành!")
        print(f"📁 Kết quả được lưu tại: {OUTPUT_DIR}")
        print("   - plan.txt: Danh sách các video")
        print("   - content.txt: Nội dung gốc được generate")
        print("   - scripts/: Thư mục chứa script từng video")
        print("   - my_result/: Thư mục chứa video")
    else:
        print("\n❌ Pipeline thất bại!")
        sys.exit(1)

if __name__ == "__main__":
    main() 