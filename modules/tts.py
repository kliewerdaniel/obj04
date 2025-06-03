import edge_tts
import asyncio
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def generate_audio_edge(text: str, output_filename: str = "broadcast_audio.mp3") -> str:
    """
    Asynchronously generates speech audio from text using Edge TTS and saves it to a file.
    """
    output_dir = "static/audio"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    logging.info(f"Generating audio for text (first 50 chars): '{text[:50]}...'")
    logging.info(f"Output path: {output_path}")

    try:
        communicate = edge_tts.Communicate(text, voice="en-US-JennyNeural")
        await communicate.save(output_path)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logging.info(f"Audio generated successfully: {output_path}")
            return output_path
        else:
            logging.error("Audio generation failed or file is empty.")
            raise Exception("Audio file was not created or is empty.")
    except Exception as e:
        logging.error(f"Error generating audio with edge-tts: {e}", exc_info=True)
        raise

def generate_audio(text: str, output_filename: str = "broadcast_audio.mp3") -> str:
    """
    Synchronous wrapper for the async Edge TTS generator.
    """
    return asyncio.run(generate_audio_edge(text, output_filename))

if __name__ == "__main__":
    sample_text = "This is a test broadcast. The news of the day is very important."
    try:
        generated_file = generate_audio(sample_text)
        print(f"Audio generated and saved to: {generated_file}")
    except Exception as e:
        print(f"Failed to generate audio: {e}")