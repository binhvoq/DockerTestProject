#!/usr/bin/env python3
import os
import sys
import shutil

# Tạo test script cho Kokoro TTS
def test_kokoro():
    print("🧪 Testing Kokoro TTS...")
    
    # Tạo thư mục test
    test_dir = "/app/temp"
    audio_dir = "/app/temp/my_audio" 
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    
    # Tạo file script test
    test_content = """Hello! This is a test of Kokoro TTS integration.
Dark matter makes up about 27% of the universe.
Scientists are still trying to understand its properties."""
    
    script_file = os.path.join(test_dir, "current_script.txt")
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print(f"✅ Created test script: {script_file}")
    
    # Import và test audio generator
    try:
        from audio_generator import main as audio_main
        success = audio_main()
        
        if success:
            print("✅ Kokoro TTS test successful!")
            
            # Kiểm tra files đã tạo
            audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
            print(f"📊 Generated {len(audio_files)} audio files:")
            for file in audio_files:
                file_path = os.path.join(audio_dir, file)
                size = os.path.getsize(file_path)
                print(f"  - {file}: {size/1024:.1f}KB")
                
        else:
            print("❌ Kokoro TTS test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Kokoro TTS: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_kokoro()
    sys.exit(0 if success else 1) 