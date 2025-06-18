#!/usr/bin/env python3
import os
import shutil
import subprocess
import json
import sys

# Paths
PLAN_DIR = "/app/temp/plan"
PLAN_FILE = "/app/temp/plan.txt"
OUTPUT_DIR = "/app/output"
RESULT_DIR = "/app/output/my_result"
TEMP_DIR = "/app/temp"
PROGRESS_FILE = "/app/temp/progress.json"

# Files for current video processing
CURRENT_SCRIPT_FILE = "/app/temp/current_script.txt"
FINAL_VIDEO = "/app/temp/final_video.mp4"

# Timeout and retry settings
TIMEOUT_SECONDS = 1800
MAX_RETRIES = 2

def load_progress():
    """Load progress from file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_progress(progress):
    """Save progress to file"""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=4)

def read_plan():
    """Read task list from plan.txt"""
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    tasks = []
    for line in lines:
        parts = line.split("|")
        if len(parts) != 2:
            continue  # Skip invalid lines
        
        title, script_filename = parts
        title = title.strip()
        script_filename = script_filename.strip()
        script_path = os.path.join(PLAN_DIR, script_filename)

        tasks.append({"title": title, "script": script_path, "retries": 0})
    
    return tasks

def sanitize_filename(title):
    """Convert title to valid filename"""
    return "".join(c if c.isalnum() or c in " -_" else "_" for c in title)

def process_single_video(title, script_path):
    """Process a single video"""
    print(f"🎥 Processing video: {title}")
    
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script file not found: {script_path}")
    
    # Copy script content to current script file
    shutil.copy(script_path, CURRENT_SCRIPT_FILE)
    
    # Step 1: Clean up and generate audio
    print("🔹 Step 1: Generating audio...")
    subprocess.run([sys.executable, "audio_generator.py"], 
                  check=True, timeout=TIMEOUT_SECONDS)
    
    # Step 2: Generate keywords and download images
    print("🔹 Step 2: Generating keywords and downloading images...")
    subprocess.run([sys.executable, "image_processor.py"], 
                  check=True, timeout=TIMEOUT_SECONDS)
    
    # Step 3: Combine audio and images into video
    print("🔹 Step 3: Combining audio and images...")
    subprocess.run([sys.executable, "video_combiner.py"], 
                  check=True, timeout=TIMEOUT_SECONDS)
    
    # Move final video to result directory
    if os.path.exists(FINAL_VIDEO):
        safe_title = sanitize_filename(title)
        output_filename = f"{safe_title}.mp4"
        output_path = os.path.join(RESULT_DIR, output_filename)
        shutil.move(FINAL_VIDEO, output_path)
        print(f"✅ Video saved: {output_path}")
        return True
    else:
        raise FileNotFoundError("Final video not found")

def process_videos():
    """Process all videos"""
    tasks = read_plan()
    progress = load_progress()

    print(f"📋 Found {len(tasks)} videos to process")

    # Filter out completed tasks
    tasks_to_process = []
    for task in tasks:
        title = task["title"]
        if title in progress and progress[title].get("status") == "done":
            print(f"✅ Video '{title}' already completed, skipping.")
        else:
            # If there's intermediate status, get retry count
            if title in progress:
                task["retries"] = progress[title].get("retries", 0)
            tasks_to_process.append(task)
    
    pending_tasks = tasks_to_process[:]  # List of videos to process

    while pending_tasks:
        next_round = []  # Save videos that need retry
        for task in pending_tasks:
            title = task["title"]
            script_path = task["script"]

            try:
                process_single_video(title, script_path)
                progress[title] = {"status": "done", "retries": task["retries"]}
                save_progress(progress)
                
            except subprocess.TimeoutExpired:
                task["retries"] += 1
                progress[title] = {"status": "timeout", "retries": task["retries"]}
                save_progress(progress)
                if task["retries"] < MAX_RETRIES:
                    print(f"⏳ Retrying video: {title} (Attempt {task['retries']})")
                    next_round.append(task)
                else:
                    print(f"❌ Video {title} timed out {MAX_RETRIES} times, skipping.")
                    progress[title] = {"status": "failed", "message": "timeout exceeded", "retries": task["retries"]}
                    save_progress(progress)
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Error processing {title}: {e}")
                progress[title] = {"status": "error", "message": str(e), "retries": task["retries"]}
                save_progress(progress)
                
            except Exception as e:
                print(f"❌ Unexpected error processing {title}: {e}")
                progress[title] = {"status": "error", "message": str(e), "retries": task["retries"]}
                save_progress(progress)

        pending_tasks = next_round  # Retry failed videos

    print("🎉 All videos processed!")

def main():
    """Main function"""
    print("🎥 Processing videos...")
    
    # Check if plan file exists
    if not os.path.exists(PLAN_FILE):
        print(f"❌ Plan file not found: {PLAN_FILE}")
        return False
    
    # Ensure result directory exists
    os.makedirs(RESULT_DIR, exist_ok=True)
    
    # Process videos
    process_videos()
    
    print("✅ Video processing completed!")
    return True

if __name__ == "__main__":
    main() 