#!/usr/bin/env python3
import os
import openai
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

# Configuration
MIN_WORD_COUNT = 1500

# Paths
SUBJECTS_FILE = "/app/subjects.txt"
CONTENT_FILE = "/app/temp/content.txt"

def call_llm(prompt, model="gpt-4o-mini", temperature=0.7):
    """Call LLM with prompt and return result"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional video script writer. You help create engaging, insightful, and interesting content in English."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=4000
    )
    return response.choices[0].message.content

def generate_content_for_subject(title):
    """Generate content for a specific title"""
    print(f"Generating content for: {title}")
    
    # Step 1: Topic analysis
    analysis_prompt = f"""
    Analyze the topic: "{title}"
    
    1. Identify 5-7 potential viewer groups for this video.
    2. For each group, list 3-5 questions they typically ask about this topic.
    3. Identify the 10 most important knowledge points to convey.
    4. Suggest 5 unique approaches to make this topic engaging.
    
    Please provide a detailed and well-structured response.
    """
    
    analysis_result = call_llm(analysis_prompt)
    print("✅ Topic analysis completed!")
    
    # Step 2: Content structure
    structure_prompt = f"""
    Based on the following analysis of the topic "{title}":
    
    {analysis_result}
    
    Create a detailed structure for the video script with:
    
    1. A shocking/surprising introduction to immediately capture viewers' attention (30-45 seconds)
    2. Divide the main content into 5-7 sections with specific titles
    3. For each section, list:
       - Specific statistics and dates to mention
       - Visual examples or comparisons to explain concepts
       - Open-ended questions to maintain curiosity
    4. A conclusion with an impactful message (not just "like & subscribe")
    
    Please provide a detailed, information-rich structure.
    """
    
    structure_result = call_llm(structure_prompt)
    print("✅ Content structure completed!")
    
    # Step 3: Research and details
    details_prompt = f"""
    Based on the following script structure for the topic "{title}":
    
    {structure_result}
    
    Research and add details to each section with:
    
    1. Factual information, accurate and reliable statistics
    2. Engaging stories about the topic
    3. Visual examples, easy-to-understand comparisons for complex concepts
    4. Connections to modern discoveries and their impact on our understanding
    5. Surprising or little-known points
    
    Please provide detailed, accurate, and interesting information.
    """
    
    details_result = call_llm(details_prompt)
    print("✅ Content details completed!")
    
    # Step 4: Hooks and questions
    hooks_prompt = f"""
    Based on the structure and details of the video script about "{title}":
    
    {details_result}
    
    Create:
    
    1. 5 different shocking/surprising opening sentences to immediately capture attention
    2. 10 open-ended questions to place throughout the video, stimulating curiosity
    3. 5 natural transitions between sections
    4. 5 different conclusions, each powerful and memorable
    
    Ensure these elements are tightly connected to the content and create coherence.
    """
    
    hooks_result = call_llm(hooks_prompt)
    print("✅ Hooks and questions completed!")
    
    # Step 5: Complete script synthesis
    target_word_count = max(2500, int(MIN_WORD_COUNT * 1.2))
    
    script_prompt = f"""
    Synthesize a complete, detailed video script about the topic "{title}" based on the following parts:
    
    TOPIC ANALYSIS:
    {analysis_result}
    
    CONTENT STRUCTURE:
    {structure_result}
    
    CONTENT DETAILS:
    {details_result}
    
    HOOKS AND QUESTIONS:
    {hooks_result}
    
    Requirements:
    1. Create a long, detailed script (minimum {target_word_count} words)
    2. Use a friendly, accessible but professional tone
    3. Incorporate hooks and open-ended questions throughout to continuously engage
    4. Provide specific data, statistics, and examples
    5. Create a coherent story from beginning to end
    6. Avoid formulaic endings like "like & subscribe"
    
    This should be a complete script, ready for video production.
    """
    
    script_result = call_llm(script_prompt, temperature=0.8)
    print("✅ Complete script completed!")
    
    # Step 6: Convert to natural narration
    narration_prompt = f"""
    Convert the following video script into a NATURAL English NARRATION with natural formatting:

    {script_result}

    IMPORTANT REQUIREMENTS:
    1. Keep paragraphs natural as you would normally write, DO NOT force line breaks after each sentence
    2. However, DIVIDE INTO MULTIPLE PARAGRAPHS (about 5-7 sentences each) to create natural pauses
    3. DO NOT use marking symbols like "**", "-", "###", "*" or any special formatting
    4. DO NOT mention "images", "narration", "examples", or any editing instructions
    5. ESPECIALLY IMPORTANT: Create narration as if you're speaking directly to the viewer
    6. DO NOT end with phrases like "Hope you...", "Thanks for watching...", or "Like and subscribe..."
    7. Use open-ended questions within the content to create natural connections
    8. Create long content (minimum {MIN_WORD_COUNT} words)
    
    The result should be multiple natural paragraphs, with spaces between paragraphs, without too much special formatting.
    """
    
    narration_result = call_llm(narration_prompt, model="gpt-4o-mini", temperature=0.7)
    print("✅ Narration conversion completed!")
    
    # Check paragraph count and word count
    paragraph_count = len([p for p in narration_result.split("\n\n") if p.strip()])
    word_count = len(narration_result.split())
    print(f"Paragraph count: {paragraph_count}")
    print(f"Word count: {word_count}")
    
    # Ensure content is long enough
    if word_count < MIN_WORD_COUNT:
        print(f"Content too short ({word_count} words < {MIN_WORD_COUNT} words), expanding...")
        expand_prompt = f"""
        Here is a narration:

        {narration_result}

        Please expand this narration to at least {MIN_WORD_COUNT} words by:
        1. Adding more details to each existing paragraph
        2. Delving deeper into examples and applications
        3. Adding information about history and related research
        4. Including more findings and debates
        5. Expanding explanations of complex concepts
        
        Please ensure:
        - Still divided into natural paragraphs
        - Each paragraph has space between it and others (double line break between paragraphs)
        - Content remains continuous and coherent
        - Total word count EXACTLY between {MIN_WORD_COUNT} and {MIN_WORD_COUNT + 500} words
        """
        
        narration_result = call_llm(expand_prompt, model="gpt-4o-mini", temperature=0.7)
        new_word_count = len(narration_result.split())
        print(f"Expanded narration. New word count: {new_word_count}")
    
    if paragraph_count < 10:
        print("Too few paragraphs, adjusting...")
        adjust_prompt = f"""
        Here is a narration:

        {narration_result}

        Please divide it into more paragraphs for easier reading. Each paragraph should contain only 4-6 related sentences.
        
        Need at least 15-20 separate paragraphs.
        
        Please ensure:
        - Each paragraph has space from others (double line break between paragraphs)
        - Content remains continuous and coherent
        - No titles or numbering for paragraphs
        - Everything is still one continuous piece, just divided into more paragraphs for readability
        - Word count remains the same, content not changed
        """
        
        narration_result = call_llm(adjust_prompt, model="gpt-4o-mini", temperature=0.7)
        new_paragraph_count = len([p for p in narration_result.split('\n\n') if p.strip()])
        print(f"Adjusted narration. New paragraph count: {new_paragraph_count}")
    
    # Return result
    return f"Mytitle: {title}\n{narration_result}"

def main():
    print("Starting content generation for each topic...")
    
    # Read list of topics from subjects.txt
    with open(SUBJECTS_FILE, "r", encoding="utf-8") as file:
        subjects = [line.strip() for line in file if line.strip()]
    
    print(f"Found {len(subjects)} topics to process.")
    
    # Generate content and save to file
    with open(CONTENT_FILE, "w", encoding="utf-8") as output_file:
        for subject in subjects:
            print(f"\n--- Processing topic: {subject} ---")
            # Extract thumbnail part from "thumbnail | title" format if exists
            thumbnail = subject.split(" | ")[0] if " | " in subject else subject
            content = generate_content_for_subject(subject)
            
            # Split content
            content_parts = content.split('\n')
            # Recreate content with only thumbnail part
            new_content = ['Mytitle: ' + thumbnail] + content_parts[1:]
            # Join parts back with \n
            final_content = '\n'.join(new_content)
            
            output_file.write(final_content + "\n\n")
    
    print(f"\nContent generation completed!")
    print(f"All content saved to: {CONTENT_FILE}")

if __name__ == "__main__":
    main() 