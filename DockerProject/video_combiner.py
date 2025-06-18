#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from PIL import Image

# Paths
IMAGES_DIR = "/app/temp/my_images"
AUDIO_DIR = "/app/temp/my_audio"
OUTPUT_VIDEO = "/app/temp/final_video.mp4"

# Video settings
TARGET_WIDTH = 1280
TARGET_HEIGHT = 720

def extract_number(filename):
    """Extract number from filename for sorting"""
    match = re.search(r"(\d+)", filename)
    return int(match.group(1)) if match else float('inf')

def resize_image(image_path, target_width, target_height):
    """Resize and crop image to target dimensions"""
    with Image.open(image_path) as img:
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
            else:
                background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Calculate ratio for resizing
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        if img_ratio > target_ratio:
            # Image is wider, resize by height
            new_height = target_height
            new_width = int(img_ratio * new_height)
        else:
            # Image is taller, resize by width
            new_width = target_width
            new_height = int(new_width / img_ratio)

        # Resize image
        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Calculate crop position
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        # Crop image
        cropped = resized.crop((left, top, right, bottom))
        
        # Save processed image
        temp_path = image_path + ".temp.jpg"
        cropped.save(temp_path, "JPEG", quality=95)
        return temp_path

def get_audio_duration(audio_path):
    """Get duration of audio file"""
    try:
        duration_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", audio_path
        ]
        duration = float(subprocess.check_output(duration_cmd).decode().strip())
        return duration
    except:
        return 3.0  # Default duration if cannot read

def create_video_from_images_and_audio():
    """Create video from images and audio using FFmpeg"""
    print("🎬 Creating video from images and audio...")
    
    # Check directories exist
    if not os.path.exists(IMAGES_DIR) or not os.path.exists(AUDIO_DIR):
        print(f"❌ Missing directories - Images: {os.path.exists(IMAGES_DIR)}, Audio: {os.path.exists(AUDIO_DIR)}")
        return False

    # Get file lists and sort them
    image_files = sorted(
        [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
        key=extract_number
    )
    audio_files = sorted(
        [f for f in os.listdir(AUDIO_DIR) if f.lower().endswith('.wav')],
        key=extract_number
    )

    print(f"📊 Found {len(image_files)} images and {len(audio_files)} audio files")

    if not image_files or not audio_files:
        print("❌ Missing images or audio files!")
        return False

    # Ensure we have equal numbers or handle the mismatch
    min_files = min(len(image_files), len(audio_files))
    if len(image_files) != len(audio_files):
        print(f"⚠️ File count mismatch - using first {min_files} files from each")
        image_files = image_files[:min_files]
        audio_files = audio_files[:min_files]

    # Process each image-audio pair
    video_clips = []
    for i, (img_file, aud_file) in enumerate(zip(image_files, audio_files)):
        img_path = os.path.join(IMAGES_DIR, img_file)
        aud_path = os.path.join(AUDIO_DIR, aud_file)
        
        print(f"🔄 Processing clip {i+1}/{len(image_files)}: {img_file} + {aud_file}")
        
        # Resize and crop image
        processed_img = resize_image(img_path, TARGET_WIDTH, TARGET_HEIGHT)
        
        # Get audio duration
        duration = get_audio_duration(aud_path)
        print(f"📏 Audio duration: {duration:.2f}s")
        
        # Create video clip from static image
        clip_output = f"/app/temp/clip_{i}.mp4"
        clip_cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", processed_img,
            "-i", aud_path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-r", "30",
            clip_output
        ]
        
        try:
            result = subprocess.run(clip_cmd, check=True, capture_output=True, text=True)
            video_clips.append(clip_output)
            print(f"✅ Created clip {i+1}: {clip_output}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating clip {i+1}: {e}")
            if e.stderr:
                print(f"FFmpeg error: {e.stderr}")
            continue
        finally:
            # Clean up temporary image
            if os.path.exists(processed_img):
                os.remove(processed_img)

    if not video_clips:
        print("❌ No video clips were created!")
        return False

    # If only one clip, rename it directly
    if len(video_clips) == 1:
        try:
            os.rename(video_clips[0], OUTPUT_VIDEO)
            print(f"✅ Video created successfully: {OUTPUT_VIDEO}")
            return True
        except Exception as e:
            print(f"❌ Error creating final video: {e}")
            return False
    
    # If multiple clips, concatenate them
    elif len(video_clips) > 1:
        # Create concat list file
        concat_file = "/app/temp/concat_list.txt"
        with open(concat_file, "w", encoding="utf-8") as f:
            for clip in video_clips:
                f.write(f"file '{clip}'\n")
        
        # Concatenate clips
        final_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            OUTPUT_VIDEO
        ]
        
        try:
            result = subprocess.run(final_cmd, check=True, capture_output=True, text=True)
            print(f"✅ Video created successfully: {OUTPUT_VIDEO}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error concatenating video: {e}")
            if e.stderr:
                print(f"FFmpeg error: {e.stderr}")
            return False
        finally:
            # Clean up
            for clip in video_clips:
                if os.path.exists(clip):
                    os.remove(clip)
            if os.path.exists(concat_file):
                os.remove(concat_file)
    
    return False

def main():
    """Main function"""
    print("🎬 Combining audio and images into video...")
    
    success = create_video_from_images_and_audio()
    
    if success:
        print("✅ Video combination completed!")
        
        # Check final video file
        if os.path.exists(OUTPUT_VIDEO):
            file_size = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)  # MB
            print(f"📊 Final video size: {file_size:.2f} MB")
        
        return True
    else:
        print("❌ Video combination failed!")
        return False

if __name__ == "__main__":
    if not main():
        sys.exit(1) 