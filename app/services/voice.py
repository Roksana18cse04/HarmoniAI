from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os

def text_to_audio(text, output_file="output.mp3", lang='en', slow=False, play_audio=False):
    """
    Convert text to audio using Google's Text-to-Speech (offline-capable)
    
    Args:
        text (str): Text to convert
        output_file (str): Output file path
        lang (str): Language code (e.g., 'en', 'es', 'fr')
        slow (bool): Slow down speech
        play_audio (bool): Play audio after generation
    """
    try:
        # Create speech
        tts = gTTS(text=text, lang=lang, slow=slow)
        
        # Save to file
        tts.save(output_file)
        print(f"Audio saved to {output_file}")
        
        # Play audio if requested
        if play_audio:
            audio = AudioSegment.from_mp3(output_file)
            play(audio)
            
    except Exception as e:
        print(f"Error: {e}")

# Example usage
if __name__ == "__main__":
    text = "This is another approach to text to speech conversion."
    text_to_audio(text, output_file="speech.mp3", lang='en', play_audio=True)