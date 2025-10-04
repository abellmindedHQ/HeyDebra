import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np
import os

# Load once, not on every call
model = whisper.load_model("tiny")

# Optional: lock to specific devices you know work for you.
# You told me (8,10) (DirectSound) worked; set them here if desired.
DEFAULT_DEVICES = (8, 10)   # (input_index, output_index) or (input_name, output_name)
DEFAULT_SR = 44100          # 44.1k is fine; Whisper will resample internally.

def _trim_leading_silence(x: np.ndarray, threshold=0.01, chunk=1024):
    """Simple VAD-like trim to remove initial silence."""
    i = 0
    n = len(x)
    while i + chunk < n and float(np.max(np.abs(x[i:i+chunk]))) < threshold:
        i += chunk
    return x[i:]

def listen(seconds: float = 6.0) -> str:
    """
    Records speech, avoids initial truncation by priming the stream,
    saves to temp_audio.wav, then transcribes with Whisper.
    Returns the transcript (empty string on failure).
    """
    print("🎙️ Debra is listening... Speak after the beep (half a second)…")

    # Optionally lock devices for reliability
    try:
        if DEFAULT_DEVICES:
            sd.default.device = DEFAULT_DEVICES  # (in, out)
        sd.default.latency = ('low', 'low')
    except Exception:
        pass  # not critical

    fs = DEFAULT_SR
    priming = 0.5  # seconds to let the stream spin up
    total = seconds + priming
    nframes = int(total * fs)

    try:
        # Prime + record
        recording = sd.rec(nframes, samplerate=fs, channels=1, dtype='float32')
        sd.wait()

        # Drop priming and optionally trim initial silence
        audio = np.squeeze(recording[int(priming * fs):])
        audio = _trim_leading_silence(audio, threshold=0.01, chunk=1024)

        # Debug amplitude (helps confirm we captured voice)
        amp = float(np.max(np.abs(audio))) if audio.size else 0.0
        print(f"[DEBUG] Max amplitude after trim: {amp:.4f}")

    except Exception as e:
        print(f"[ERROR] Microphone error: {e}")
        return ""

    # Persist to wav for Whisper
    file_path = os.path.abspath("temp_audio.wav")
    try:
        sf.write(file_path, audio, fs)
        print(f"[DEBUG] Audio saved to: {file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write WAV: {e}")
        return ""

    # Transcribe with Whisper
    try:
        result = model.transcribe(file_path)
        transcript = (result.get("text") or "").strip()
        print(f"You said: {transcript}")
        return transcript
    except Exception as e:
        print(f"Debra couldn’t transcribe that: {e}")
        return ""