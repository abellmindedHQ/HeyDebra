import os
from dotenv import load_dotenv

load_dotenv()

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import play
    use_elevenlabs = True
    print("[DEBUG] ElevenLabs SDK loaded.")
except ImportError as e:
    print(f"[DEBUG] ElevenLabs import failed: {e}")
    use_elevenlabs = False

# Always import pyttsx3 just in case
import pyttsx3

api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=api_key) if use_elevenlabs else None

def speak(text):
    print(f"Debra: {text}")

    if use_elevenlabs and client:
        try:
            audio = client.text_to_speech.convert(
                voice_id="w6INrsHCejnExFzTH8Nm",
                model_id="eleven_monolingual_v1",
                text=text
            )
            play(audio)
        except Exception as e:
            print(f"[ERROR] ElevenLabs failed: {e}")
            print("[FALLBACK] Using pyttsx3 instead.")
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
    else:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()