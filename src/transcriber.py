import os
import openai
from pydub import AudioSegment
from decouple import config
from src.utils import ogg2mp3

openai.api_key = config("OPENAI_API_KEY")

class Transcriber:
    """Transcriber component with Whisper OpenAI model"""
    def transcribe(self, media_url):
        # Convert the OGG audio to MP3 using ogg2mp3() function
        mp3_file_path = ogg2mp3(media_url)

        with open(mp3_file_path, "rb") as audio_file:
        # Call the OpenAI API to transcribe the audio using Whisper API
            whisper_response = openai.Audio.transcribe(
                file=audio_file,
                model="whisper-1",
                language="en",
                temperature=0.5,
            )
        
        # Remove .ogg and .mp3 files
        try:
            os.remove('audio.ogg')
            os.remove('audio.mp3')
        except:...

        return whisper_response.get("text")
