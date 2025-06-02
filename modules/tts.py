from gtts import gTTS
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_audio(text: str, output_filename: str = "broadcast_audio.mp3"):
    """
    Generates speech audio from text using gTTS and saves it to a file.
    """
    output_dir = "static/audio"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    logging.info(f"Attempting to generate audio for text (first 50 chars): '{text[:50]}...'")
    logging.info(f"Output path: {output_path}")

    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        
        # Verify file size
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 0:
                logging.info(f"Audio generated successfully. File size: {file_size} bytes.")
                return output_path
            else:
                logging.error(f"Generated audio file is empty: {output_path}")
                raise Exception("Generated audio file is empty.")
        else:
            logging.error(f"Audio file was not created at: {output_path}")
            raise Exception("Audio file was not created.")
            
    except Exception as e:
        logging.error(f"Error generating audio with gTTS: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Example usage
    sample_text = "This is a test broadcast. The news of the day is very important."
    try:
        generated_file = generate_audio(sample_text)
        print(f"Audio generated and saved to: {generated_file}")
    except Exception as e:
        print(f"Failed to generate audio in example: {e}")
