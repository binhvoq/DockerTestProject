#!/usr/bin/env python3
import os
import re
import shutil

# Paths
CONTENT_FILE = "/app/temp/content.txt"
PLAN_DIR = "/app/temp/plan"
PLAN_FILE = "/app/temp/plan.txt"

def setup_directories():
    """Setup required directories"""
    # Clean and create plan directory
    if os.path.exists(PLAN_DIR):
        shutil.rmtree(PLAN_DIR)
    os.makedirs(PLAN_DIR, exist_ok=True)
    print(f"✅ Created plan directory: {PLAN_DIR}")

def sanitize_filename(title):
    """Convert title to valid filename"""
    return "".join(c if c.isalnum() or c in " -_" else "_" for c in title).strip()

def process_script():
    """Read content from CONTENT_FILE, process and save as separate files"""
    scripts = []
    current_title = None
    current_content = []

    # Read input file
    with open(CONTENT_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Detect new title
            title_match = re.match(r"^Mytitle:\s*(.+)", line)
            if title_match:
                # Save previous script content (if exists)
                if current_title and current_content:
                    scripts.append((current_title, "\n".join(current_content)))

                # Update to new title
                current_title = title_match.group(1).strip()
                current_content = []
            else:
                # Add line to current content
                if current_title:
                    current_content.append(line)

    # Save the last script if exists
    if current_title and current_content:
        scripts.append((current_title, "\n".join(current_content)))

    # Write data to files
    with open(PLAN_FILE, "w", encoding="utf-8") as plan_file:
        for title, content in scripts:
            safe_title = sanitize_filename(title)
            script_filename = f"{safe_title}.txt"
            script_path = os.path.join(PLAN_DIR, script_filename)

            # Save content to separate file
            with open(script_path, "w", encoding="utf-8") as script_file:
                script_file.write(content)

            # Write to plan.txt
            plan_file.write(f"{title} | {script_filename}\n")

    print(f"✅ Processing completed! Files saved to: {PLAN_DIR}")
    print(f"✅ Plan file created: {PLAN_FILE}")
    print(f"✅ Created {len(scripts)} script files")

def main():
    """Main function"""
    print("📋 Creating plan from content...")
    
    # Check if content file exists
    if not os.path.exists(CONTENT_FILE):
        print(f"❌ Content file not found: {CONTENT_FILE}")
        return False
    
    # Setup directories
    setup_directories()
    
    # Process script
    process_script()
    
    print("✅ Plan creation completed!")
    return True

if __name__ == "__main__":
    main() 