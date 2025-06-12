import random

import requests

from utils import settings


class OpenAITTS:
    """
    A Text-to-Speech engine that uses an OpenAI-like TTS API endpoint to generate audio from text.

    Attributes:
        max_chars (int): Maximum number of characters allowed per API call.
        api_key (str): API key loaded from settings.
        api_url (str): The complete API endpoint URL, built from a base URL provided in the config.
        available_voices (list): Static list of supported voices (according to current docs).
    """

    def __init__(self):
        # Set maximum input size based on API limits (4096 characters per request)
        self.max_chars = 4096
        self.api_key = settings.config["settings"]["tts"].get("openai_api_key")
        if not self.api_key:
            raise ValueError(
                "No OpenAI API key provided in settings! Please set 'openai_api_key' in your config."
            )

        # Lese den Basis-URL aus der Konfiguration (z. B. "https://api.openai.com/v1" oder "https://api.openai.com/v1/")
        base_url = settings.config["settings"]["tts"].get(
            "openai_api_url", "https://api.openai.com/v1"
        )
        # Entferne ggf. den abschließenden Slash
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        # Hänge den TTS-spezifischen Pfad an
        self.api_url = base_url + "/audio/speech"

        # Set the available voices to a static list as per OpenAI TTS documentation.
        self.available_voices = self.get_available_voices()

    def get_available_voices(self):
        """
        Return a static list of supported voices for the OpenAI TTS API.

        According to the documentation, supported voices include:
            "alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"
        """
        return ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]

    def randomvoice(self):
        """
        Select and return a random voice from the available voices.
        """
        return random.choice(self.available_voices)

    def run(self, text, filepath, random_voice: bool = False):
        """
        Convert the provided text to speech and save the resulting audio to the specified filepath.

        Args:
            text (str): The input text to convert.
            filepath (str): The file path where the generated audio will be saved.
            random_voice (bool): If True, select a random voice from the available voices.
        """
        # Choose voice based on configuration or randomly if requested.
        if random_voice:
            voice = self.randomvoice()
        else:
            voice = settings.config["settings"]["tts"].get("openai_voice_name", "alloy")
            voice = str(voice).lower()  # Ensure lower-case as expected by the API

        # Select the model from configuration; default to 'tts-1'
        model = settings.config["settings"]["tts"].get("openai_model", "tts-1")

        # Create Payload for API-request
        payload = {
            "model": model,
            "voice": voice,
            "input": text,
            "response_format": "mp3",  # allowed formats: "mp3", "aac", "opus", "flac", "pcm" or "wav"
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"Error from TTS API: {response.status_code} {response.text}")
            # Write response as binary into file.
            with open(filepath, "wb") as f:
                f.write(response.content)
        except Exception as e:
            raise RuntimeError(f"Failed to generate audio with OpenAI TTS API: {str(e)}")
