#!/usr/bin/env python3
import os
import subprocess
import soundfile as sf
import numpy as np
import tempfile
import sys
import shutil
import re

# Import Kokoro TTS
try:
    import kokoro
    import torch
    KOKORO_AVAILABLE = True
    print("✅ Kokoro TTS imported successfully")
except ImportError as e:
    KOKORO_AVAILABLE = False
    print(f"❌ Cannot import Kokoro TTS: {e}")

# Paths
SCRIPT_FILE = "/app/temp/current_script.txt"
AUDIO_DIR = "/app/temp/my_audio"
TEMP_AUDIO_DIR = "/app/temp/audio_segments"  # Thư mục tạm cho segments

# Config
MAX_CHARS_PER_SEGMENT = 400  # Giới hạn ký tự cho mỗi segment

def setup_directories():
    """Setup and clean directories"""
    # Clean audio directory
    if os.path.exists(AUDIO_DIR):
        shutil.rmtree(AUDIO_DIR)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    # Clean temp audio segments directory
    if os.path.exists(TEMP_AUDIO_DIR):
        shutil.rmtree(TEMP_AUDIO_DIR)
    os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
    
    print(f"✅ Audio directory setup: {AUDIO_DIR}")
    print(f"✅ Temp segments directory setup: {TEMP_AUDIO_DIR}")

def split_text_into_segments(text, max_chars=MAX_CHARS_PER_SEGMENT):
    """Chia text thành các segments dựa trên câu và giới hạn ký tự"""
    if len(text) <= max_chars:
        return [text]
    
    # Chia theo câu trước
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    segments = []
    current_segment = ""
    
    for sentence in sentences:
        # Nếu câu đơn lẻ đã vượt quá giới hạn
        if len(sentence) > max_chars:
            # Lưu segment hiện tại nếu có
            if current_segment:
                segments.append(current_segment.strip())
                current_segment = ""
            
            # Chia câu dài theo từ
            words = sentence.split()
            temp_sentence = ""
            for word in words:
                if len(temp_sentence + " " + word) <= max_chars:
                    temp_sentence += (" " + word) if temp_sentence else word
                else:
                    if temp_sentence:
                        segments.append(temp_sentence.strip())
                    temp_sentence = word
            
            if temp_sentence:
                segments.append(temp_sentence.strip())
        else:
            # Kiểm tra nếu thêm câu này có vượt quá giới hạn không
            if len(current_segment + " " + sentence) <= max_chars:
                current_segment += (" " + sentence) if current_segment else sentence
            else:
                # Lưu segment hiện tại và bắt đầu segment mới
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
    
    # Lưu segment cuối cùng
    if current_segment:
        segments.append(current_segment.strip())
    
    return segments

def text_to_speech_kokoro(text, output_file, pipeline=None):
    """Use Kokoro TTS for high-quality audio generation"""
    try:
        if not KOKORO_AVAILABLE or pipeline is None:
            return False
            
        print(f"🎵 Creating speech with Kokoro TTS ({len(text)} chars)...")
        
        # Generate speech with high quality voice - sử dụng pipeline được truyền vào
        audio_result = pipeline(text, voice="af_heart")
        
        # Process audio result
        if hasattr(audio_result, '__iter__') and not isinstance(audio_result, (list, np.ndarray)):
            audio_list = list(audio_result)
            if audio_list:
                audio_item = audio_list[0]
                
                # Extract audio from Result object
                if hasattr(audio_item, 'output'):
                    if hasattr(audio_item.output, 'audio'):
                        audio = audio_item.output.audio
                    else:
                        audio = audio_item.output
                else:
                    audio = audio_item
                    
                # Convert tensor to numpy
                if torch.is_tensor(audio):
                    audio = audio.detach().cpu().numpy()
                
                # Flatten if needed
                if audio.ndim > 1:
                    audio = audio.flatten()
                    
                # Save file with 24kHz sample rate
                sf.write(output_file, audio, 24000)
                
                duration = len(audio) / 24000
                print(f"✅ Created Kokoro audio: {duration:.2f}s - {output_file}")
                return True
            else:
                print("❌ Empty audio list")
                return False
        else:
            print("❌ Audio result format incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Kokoro TTS error: {e}")
        return False

def create_demo_audio(text, output_file, duration_seconds=8):
    """Create demo audio if TTS fails"""
    try:
        sample_rate = 24000
        t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds))
        
        word_count = len(text.split())
        base_freq = 440
        
        audio = np.zeros_like(t)
        segment_length = len(t) // max(1, word_count)
        
        for i in range(min(word_count, 8)):
            start_idx = i * segment_length
            end_idx = min((i + 1) * segment_length, len(t))
            
            if start_idx < len(t):
                freq = base_freq + (i * 30)
                segment_t = t[start_idx:end_idx] - t[start_idx]
                segment_audio = 0.3 * np.sin(2 * np.pi * freq * segment_t) * np.exp(-segment_t * 2)
                audio[start_idx:end_idx] = segment_audio
        
        # Apply fade in/out
        fade_samples = int(0.1 * sample_rate)
        audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
        audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        sf.write(output_file, audio, sample_rate)
        print(f"✅ Created demo audio: {duration_seconds}s - {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Demo audio error: {e}")
        return False

def concatenate_audio_files(audio_files, output_file):
    """Ghép nhiều file audio thành 1 file"""
    try:
        if not audio_files:
            return False
        
        if len(audio_files) == 1:
            # Chỉ có 1 file, copy trực tiếp
            shutil.copy(audio_files[0], output_file)
            print(f"✅ Single audio copied: {output_file}")
            return True
        
        # Ghép nhiều file
        combined_audio = []
        sample_rate = 24000
        
        for audio_file in audio_files:
            try:
                audio_data, sr = sf.read(audio_file)
                if sr != sample_rate:
                    print(f"⚠️ Sample rate mismatch: {sr} != {sample_rate}")
                
                # Thêm khoảng lặng ngắn giữa các segment (0.1s)
                if combined_audio:
                    silence = np.zeros(int(0.1 * sample_rate))
                    combined_audio.extend(silence)
                
                combined_audio.extend(audio_data)
            except Exception as e:
                print(f"⚠️ Error reading {audio_file}: {e}")
                continue
        
        if combined_audio:
            sf.write(output_file, np.array(combined_audio), sample_rate)
            duration = len(combined_audio) / sample_rate
            print(f"✅ Concatenated audio: {duration:.2f}s - {output_file}")
            return True
        else:
            print("❌ No valid audio data to concatenate")
            return False
            
    except Exception as e:
        print(f"❌ Concatenation error: {e}")
        return False

def process_line_audio(line_text, line_index, pipeline):
    """Xử lý 1 dòng: chia segments → tạo audio → ghép lại"""
    print(f"\n🔊 Processing line {line_index+1} ({len(line_text)} chars)...")
    
    # Chia text thành segments
    segments = split_text_into_segments(line_text, MAX_CHARS_PER_SEGMENT)
    print(f"📝 Split into {len(segments)} segments")
    
    # Tạo audio cho từng segment
    segment_audio_files = []
    success_count = 0
    
    for seg_idx, segment in enumerate(segments):
        segment_file = os.path.join(TEMP_AUDIO_DIR, f"line_{line_index}_seg_{seg_idx}.wav")
        print(f"   🎵 Segment {seg_idx+1}/{len(segments)} ({len(segment)} chars)...")
        
        success = False
        
        # Thử Kokoro TTS trước
        if KOKORO_AVAILABLE and pipeline:
            success = text_to_speech_kokoro(segment, segment_file, pipeline)
        
        # Fallback: Demo audio
        if not success:
            print("   [FALLBACK] Using demo audio...")
            words_per_minute = 150
            duration = max(3, len(segment.split()) / words_per_minute * 60)
            success = create_demo_audio(segment, segment_file, duration)
        
        if success:
            segment_audio_files.append(segment_file)
            success_count += 1
        else:
            print(f"   ❌ Failed to create audio for segment {seg_idx+1}")
    
    print(f"📊 Created {success_count}/{len(segments)} audio segments")
    
    # Ghép tất cả segments thành 1 audio cho dòng này
    final_audio_file = os.path.join(AUDIO_DIR, f"output_{line_index}.wav")
    
    if segment_audio_files:
        concatenate_success = concatenate_audio_files(segment_audio_files, final_audio_file)
        
        # Clean up temp files
        for temp_file in segment_audio_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        if concatenate_success:
            # Verify final audio
            try:
                audio_data, sr = sf.read(final_audio_file)
                duration = len(audio_data) / sr
                print(f"✅ Final audio for line {line_index+1}: {duration:.2f}s")
                return True
            except Exception as e:
                print(f"⚠️ Cannot verify final audio: {e}")
                return False
        else:
            print(f"❌ Failed to concatenate audio for line {line_index+1}")
            return False
    else:
        print(f"❌ No valid audio segments for line {line_index+1}")
        return False

def chunk_text(text, max_length=100):
    """Split text into smaller chunks"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def main():
    """Main function"""
    print("🎵 Generating audio with new segmentation logic...")
    
    # Setup directories
    setup_directories()
    
    # Check if script file exists
    if not os.path.exists(SCRIPT_FILE):
        print(f"❌ Script file not found: {SCRIPT_FILE}")
        return False
    
    # Read content from file - line by line
    try:
        with open(SCRIPT_FILE, "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
        
        if not lines:
            print("❌ Script file is empty")
            return False
            
    except Exception as e:
        print(f"❌ Error reading script file: {e}")
        return False

    print(f"📝 Found {len(lines)} lines to process")

    # Initialize Kokoro pipeline once (if available)  
    kokoro_pipeline = None
    kokoro_available = KOKORO_AVAILABLE
    if kokoro_available:
        try:
            kokoro_pipeline = kokoro.KPipeline(lang_code='a')
            print("✅ Kokoro TTS pipeline ready!")
        except Exception as e:
            print(f"⚠️ Cannot create Kokoro pipeline: {e}")
            kokoro_available = False

    # Process each line
    success_count = 0
    for line_idx, line_text in enumerate(lines):
        if process_line_audio(line_text, line_idx, kokoro_pipeline):
            success_count += 1

    print(f"\n✅ Audio generation completed!")
    print(f"📊 Successfully processed {success_count}/{len(lines)} lines")
    
    # Clean up temp directory
    if os.path.exists(TEMP_AUDIO_DIR):
        shutil.rmtree(TEMP_AUDIO_DIR)
        print("🧹 Cleaned up temporary files")
    
    if success_count == 0:
        print("❌ No audio files were generated!")
        return False
    
    return True

if __name__ == "__main__":
    if not main():
        sys.exit(1) 