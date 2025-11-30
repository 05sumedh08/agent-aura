import os
import requests
import base64
from typing import Optional

class ElevenLabsService:
    """Service for interacting with ElevenLabs Text-to-Speech API."""
    
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") # Default to Rachel
        self.api_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

    def generate_audio(self, text: str) -> Optional[str]:
        """
        Generate audio from text using ElevenLabs API.
        
        Args:
            text: The text to convert to speech.
            
        Returns:
            Base64 encoded audio string, or None if generation fails.
        """
        if not self.api_key:
            print("Warning: ELEVENLABS_API_KEY not set. Skipping TTS generation.")
            return None

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        try:
            response = requests.post(self.api_url, json=data, headers=headers)
            
            if response.status_code == 200:
                # Return base64 encoded audio
                return base64.b64encode(response.content).decode('utf-8')
            else:
                print(f"ElevenLabs API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            return None
