#!/usr/bin/env python3
import os
import sys
import shutil
from openai import OpenAI
from dotenv import load_dotenv
from icrawler.builtin import GoogleImageCrawler
from PIL import Image

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=api_key)

# Paths
SCRIPT_FILE = "/app/temp/current_script.txt"
KEYWORDS_FILE = "/app/temp/keywords.txt"
IMAGES_DIR = "/app/temp/my_images"
AUDIO_DIR = "/app/temp/my_audio"  # To count audio files

def setup_directories():
    """Setup and clean directories"""
    # Clean images directory
    if os.path.exists(IMAGES_DIR):
        shutil.rmtree(IMAGES_DIR)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"✅ Images directory setup: {IMAGES_DIR}")

def chunk_text_by_audio_count():
    """Split text based on number of audio files (1 line = 1 audio = 1 image)"""
    # Count audio files to determine how many chunks we need
    audio_count = 0
    if os.path.exists(AUDIO_DIR):
        audio_files = [f for f in os.listdir(AUDIO_DIR) if f.endswith('.wav')]
        audio_count = len(audio_files)
    
    if audio_count == 0:
        print("⚠️ No audio files found, reading lines directly from script")
        # Fallback: read lines directly from script file
        with open(SCRIPT_FILE, "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
        return lines[:5]  # Default to first 5 lines
    
    print(f"📊 Found {audio_count} audio files, will create {audio_count} images")
    
    # Read script content line by line (since 1 line = 1 audio = 1 image)
    with open(SCRIPT_FILE, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
    
    # Return exactly the number of lines that match audio count
    # This ensures 1:1 mapping between lines, audio files, and images
    result_lines = lines[:audio_count]
    
    if len(result_lines) < audio_count:
        print(f"⚠️ Script has {len(lines)} lines but {audio_count} audio files")
        # Pad with empty lines if needed
        while len(result_lines) < audio_count:
            result_lines.append("Content continued...")
    
    print(f"📝 Using {len(result_lines)} lines for image generation")
    return result_lines

def generate_keyword_for_text(text, index):
    """Generate keyword for a text chunk using OpenAI"""
    print(f"🔍 Generating keyword for chunk {index+1}...")
    
    prompt = f"""
    You are helping a YouTube video editor find the best possible illustration image for a narration. 
    Given a paragraph from the video script, your task is to extract the most visually representative and specific concept from that paragraph. 

    This concept should be used as a concise image search keyword. Focus on the most central visual idea in the paragraph — something that could be shown as a background or main visual to accompany the narration. 

    Avoid abstract concepts, non-visual metaphors, or generic keywords. Instead, choose a specific, vivid subject that would return clear and relevant image results (e.g., "black hole in space", "supernova explosion", "neutron star collision", "Milky Way core", "falling man in sky", etc).

    ---

    Examples:
    1. "In 1969, humanity set foot on the Moon for the first time."  
    → surface of the Moon

    2. "Armstrong's famous words as he stepped down were: 'This is one small step for a man, but one giant leap for mankind.'"  
    → Neil Armstrong on the Moon

    3. "Have you ever imagined falling from over 10,000 meters without a parachute and surviving?"  
    → man falling from sky

    4. "On January 26, 1972, Vesna Vulović, a Yugoslavian flight attendant, was on duty aboard JAT Flight 367 when the plane suddenly exploded mid-air."  
    → mid-air plane explosion

    5. "As you can see, this line of reasoning leads us to Zeno's second paradox, known as the Dichotomy Paradox."
    → Dichotomy Paradox

    6. "Finally, we encounter the Arrow Paradox, which posits that a flying arrow is motionless at every instant in time."
    → Arrow Paradox
    ---

    Now, based on the following paragraph from a video script, suggest the best possible image keyword to illustrate it:

    \"\"\"{text}\"\"\"

    Return only the keyword phrase without any explanation or quotation marks.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        keyword = response.choices[0].message.content.strip().replace('"', '')
        print(f"✅ Generated keyword: {keyword}")
        return keyword
        
    except Exception as e:
        print(f"❌ Error generating keyword: {e}")
        # Return a generic keyword based on text
        words = text.split()[:3]
        return ' '.join(words) if words else "generic concept"

def download_image_with_icrawler(keyword, save_path, index):
    """Download image using icrawler"""
    print(f"📥 Downloading image for: {keyword}")

    # Create temp folder for this download
    temp_folder = os.path.join(IMAGES_DIR, f"temp_{index}")
    os.makedirs(temp_folder, exist_ok=True)

    try:
        # Use icrawler to download 3 images (to increase success rate)
        crawler = GoogleImageCrawler(storage={"root_dir": temp_folder})
        crawler.crawl(keyword=keyword, max_num=3)

        # Get downloaded files
        downloaded_files = [f for f in os.listdir(temp_folder) 
                          if os.path.isfile(os.path.join(temp_folder, f))]
        
        if not downloaded_files:
            print(f"⚠️ No images found for keyword: {keyword}")
            return False
            
        # Sort by file size (prefer larger images)
        downloaded_files.sort(key=lambda x: os.path.getsize(os.path.join(temp_folder, x)), reverse=True)
        
        # Try each downloaded file
        for file_name in downloaded_files:
            temp_file_path = os.path.join(temp_folder, file_name)
            
            try:
                # Verify image is valid
                image = Image.open(temp_file_path)
                
                # Save to final location
                final_path = save_path
                image.save(final_path, "JPEG", quality=90)
                print(f"✅ Downloaded image: {final_path}")
                return True
                
            except Exception as e:
                print(f"⚠️ Invalid image {temp_file_path}: {e}")
                continue
                
        print(f"❌ No valid images found for keyword: {keyword}")
        return False
        
    except Exception as e:
        print(f"❌ Error downloading image for keyword {keyword}: {e}")
        return False
    finally:
        # Clean up temp folder
        try:
            shutil.rmtree(temp_folder)
        except Exception as e:
            print(f"⚠️ Cannot clean temp folder: {e}")

def create_placeholder_image(save_path, text, index):
    """Create a placeholder image if download fails"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a colored background
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
        color = colors[index % len(colors)]
        
        # Create image
        img = Image.new('RGB', (1280, 720), color=color)
        draw = ImageDraw.Draw(img)
        
        # Add text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        words = text.split()[:10]  # First 10 words
        text_to_draw = ' '.join(words)
        if len(text_to_draw) > 50:
            text_to_draw = text_to_draw[:47] + "..."
        
        # Center text
        bbox = draw.textbbox((0, 0), text_to_draw, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (1280 - text_width) // 2
        y = (720 - text_height) // 2
        
        draw.text((x, y), text_to_draw, fill='white', font=font)
        
        # Save
        img.save(save_path, "JPEG", quality=90)
        print(f"✅ Created placeholder image: {save_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating placeholder: {e}")
        return False

def main():
    """Main function"""
    print("🖼️ Processing images...")
    
    # Setup directories
    setup_directories()
    
    # Check if script file exists
    if not os.path.exists(SCRIPT_FILE):
        print(f"❌ Script file not found: {SCRIPT_FILE}")
        return False
    
    # Split text into chunks based on audio count
    text_chunks = chunk_text_by_audio_count()
    print(f"📝 Created {len(text_chunks)} text chunks for image generation")
    
    # Generate keywords and download images
    keywords = []
    success_count = 0
    
    for i, text_chunk in enumerate(text_chunks):
        if not text_chunk.strip():
            continue
            
        # Generate keyword
        keyword = generate_keyword_for_text(text_chunk, i)
        keywords.append(keyword)
        
        # Download image
        image_path = os.path.join(IMAGES_DIR, f"output_{i}.jpg")
        
        # Try to download image
        success = download_image_with_icrawler(keyword, image_path, i)
        
        # Create placeholder if download failed
        if not success:
            print(f"⚠️ Download failed, creating placeholder for chunk {i+1}")
            success = create_placeholder_image(image_path, text_chunk, i)
        
        if success:
            success_count += 1
    
    # Save keywords to file
    with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(keywords))
    
    print(f"\n✅ Image processing completed!")
    print(f"📊 Successfully processed {success_count}/{len(text_chunks)} images")
    print(f"💾 Keywords saved to: {KEYWORDS_FILE}")
    
    if success_count == 0:
        print("❌ No images were generated!")
        return False
    
    return True

if __name__ == "__main__":
    if not main():
        sys.exit(1) 