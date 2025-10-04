import os
import pvporcupine
import sounddevice as sd
import struct
from dotenv import load_dotenv
load_dotenv()

access_key = os.getenv("PORCUPINE_ACCESS_KEY")
print("[DEBUG] Access key:", access_key)

def start_wake_listener(callback):
    porcupine = pvporcupine.create(
        access_key=access_key,
        keyword_paths=["core/wake_words/hey-debra.ppn"],
        sensitivities=[0.6]
    )

    def audio_callback(indata, frames, time, status):
        pcm = struct.unpack_from("h" * frames, indata)
        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print("🟣 Wake word detected: Hey Debra")
            callback()

    print("🎧 Debra is standing by for: 'Hey Debra'...")

    with sd.RawInputStream(
        samplerate=porcupine.sample_rate,
        blocksize=porcupine.frame_length,
        dtype='int16',
        channels=1,
        callback=audio_callback
    ):
        try:
            while True:
                sd.sleep(1000)
        except KeyboardInterrupt:
            print("👋 Wake word listener stopped.")
        finally:
            porcupine.delete()