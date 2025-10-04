import sys
from core.wake_listener import start_wake_listener
from core.audio_input import listen
from core.audio_output import speak
from core.ai_engine import get_response

goodbye_phrases = [
    "bye", "stop", "cancel", "that’s all", "thank you debra", "i’m done", "nothing else"
]

def activate_debra():
    while True:
        print("🎙️ Debra is listening...")
        user_input = listen()

        if not user_input:
            speak("You still there, baby?")
            continue

        if any(phrase in user_input.lower() for phrase in goodbye_phrases):
            speak("Alright sugar, holler if you need me.")
            break

        print(f"You said: {user_input}")
        speak("Let me think on that a sec...")
        response = get_response(user_input)
        speak(response)

if __name__ == "__main__":
    print("[DEBUG] Debra (headless mode) is ready.")
    start_wake_listener(callback=activate_debra)
