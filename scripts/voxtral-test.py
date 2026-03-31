#!/usr/bin/env python3
"""
Voxtral TTS test script - Apple Silicon optimized via MLX
Model: mlx-community/Voxtral-4B-TTS-2603-mlx-4bit (~2.5GB, runs faster than real-time on M-series)

Usage:
    python3 voxtral-test.py
    python3 voxtral-test.py --voice casual_female
    python3 voxtral-test.py --voice neutral_female --output /tmp/test.wav

Performance (measured on Mac mini M-series):
    - Model load time: ~4-5 seconds (cached)
    - Generation RTF: ~0.9x (faster than real-time at 4-bit quantization)
    - Audio output: 24kHz WAV

Notes:
    - Uses mlx-community/Voxtral-4B-TTS-2603-mlx-4bit (2.4GB, 4-bit quantized)
    - Native Apple Silicon (MLX) inference — no CUDA required
    - 20 preset voices across 9 languages
    - True arbitrary voice cloning requires vllm-omni server (Linux/CUDA only)
    - Preset "voice cloning" uses fixed embeddings, not reference audio inference
"""

import argparse
import time
import sys
import os
import warnings
warnings.filterwarnings("ignore")

MODEL_ID = "mlx-community/Voxtral-4B-TTS-2603-mlx-4bit"
OUTPUT_WAV = "/Users/debra/.openclaw/media/voxtral-test.wav"
OUTPUT_MP3 = "/Users/debra/.openclaw/media/voxtral-test.mp3"
REFERENCE_AUDIO = "/Users/debra/.openclaw/media/angie-poem.mp3"

TEST_TEXT = (
    "Hey Marshall, it's Debra. I just wanted to let you know your KBUDDS membership "
    "has been reinstated. The tribunal decided to show mercy. This time."
)

AVAILABLE_VOICES = [
    "casual_female", "casual_male", "cheerful_female",
    "neutral_male", "neutral_female",
    "fr_male", "fr_female", "es_male", "es_female",
    "de_male", "de_female", "it_male", "it_female",
    "pt_male", "pt_female", "nl_male", "nl_female",
    "ar_male", "hi_male", "hi_female",
]


def save_audio(audio_np, sample_rate: int, path: str) -> str:
    """Save audio array to file. Handles .wav and .mp3. Returns final path."""
    import numpy as np

    # Normalize if needed
    max_val = float(abs(audio_np).max())
    if max_val > 1.0:
        audio_np = audio_np / max_val

    if path.endswith(".mp3"):
        import subprocess
        wav_tmp = path.replace(".mp3", "_tmp.wav")
        try:
            import soundfile as sf
            sf.write(wav_tmp, audio_np, sample_rate)
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", wav_tmp, "-q:a", "2", path],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                os.remove(wav_tmp)
                print(f"  Saved MP3: {path}")
                return path
            else:
                print(f"  ffmpeg failed — saved as WAV: {wav_tmp}")
                return wav_tmp
        except Exception as e:
            print(f"  MP3 conversion failed: {e}")
            return wav_tmp
    else:
        import soundfile as sf
        sf.write(path, audio_np, sample_rate)
        print(f"  Saved WAV: {path}")
        return path


def run_tts(text: str, voice: str = "casual_female", output_path: str = OUTPUT_WAV):
    """Run TTS and save output. Returns (audio_duration_sec, generation_time_sec)."""
    import numpy as np
    from mlx_audio.tts.utils import load_model

    print(f"\n{'='*60}")
    print(f"Voxtral TTS Test")
    print(f"{'='*60}")
    print(f"Model  : {MODEL_ID}")
    print(f"Voice  : {voice}")
    print(f"Text   : {text[:80]}{'...' if len(text) > 80 else ''}")
    print(f"Output : {output_path}")
    print(f"{'='*60}\n")

    print("Loading model (downloading if not cached)...")
    load_start = time.time()
    model = load_model(MODEL_ID)
    load_time = time.time() - load_start
    print(f"Model loaded in {load_time:.1f}s\n")

    print("Generating speech...")
    gen_start = time.time()

    all_audio = []
    sample_rate = 24000

    for result in model.generate(
        text=text,
        voice=voice,
        verbose=True,
    ):
        audio_chunk = result.audio
        all_audio.append(np.array(audio_chunk.tolist(), dtype=np.float32))
        sample_rate = result.sample_rate

    gen_time = time.time() - gen_start

    if not all_audio:
        print("ERROR: No audio generated!")
        return None, gen_time

    # Concatenate all chunks
    audio_np = np.concatenate(all_audio, axis=0)
    audio_duration_sec = len(audio_np) / sample_rate

    print(f"\nGeneration complete!")
    print(f"  Audio duration   : {audio_duration_sec:.2f}s")
    print(f"  Generation time  : {gen_time:.2f}s")
    print(f"  Real-time factor : {gen_time/audio_duration_sec:.3f}x  (<1 = faster than real-time)")

    saved_path = save_audio(audio_np, sample_rate, output_path)

    # Also save as MP3 if output was WAV
    if saved_path.endswith(".wav") and not output_path.endswith(".mp3"):
        mp3_path = saved_path.replace(".wav", ".mp3")
        import subprocess
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", saved_path, "-q:a", "2", mp3_path],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  Saved MP3: {mp3_path}")

    return audio_duration_sec, gen_time


def run_voice_clone_test(text: str, ref_audio_path: str, output_path: str):
    """
    Voice cloning test using a reference audio file.

    NOTE: Voxtral's MLX port uses preset voice embeddings (fixed .pt files).
    True zero-shot voice cloning from arbitrary reference audio requires the
    vllm-omni server, which needs Linux + CUDA (not available on Mac).

    What we CAN do:
    - Extract/inspect the reference audio
    - Generate with the closest preset voice (neutral_female)
    - Document what voice cloning would look like via the vllm-omni API

    The vllm-omni API for voice cloning looks like:
    payload = {
        "input": text,
        "model": "mistralai/Voxtral-4B-TTS-2603",
        "response_format": "wav",
        "voice_reference": {
            "audio": "<base64_encoded_10s_clip>",
            "transcript": "optional transcript"
        }
    }
    """
    print(f"\n{'='*60}")
    print(f"Voice Clone Test (Reference-based)")
    print(f"{'='*60}")
    print(f"Reference audio: {ref_audio_path}")
    print()
    print("NOTE: MLX Voxtral uses preset voice embeddings, not arbitrary voice cloning.")
    print("True zero-shot voice cloning requires the vllm-omni server (Linux/CUDA).")
    print("Generating with 'neutral_female' preset as stand-in comparison voice.")
    print()

    if not os.path.exists(ref_audio_path):
        print(f"Reference audio not found: {ref_audio_path}")
        print("Skipping voice clone test.")
        return

    # Extract first 10s of reference audio for documentation
    try:
        import subprocess
        ref_clip = ref_audio_path.replace(".mp3", "_10s_ref.wav")
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", ref_audio_path, "-t", "10", "-ar", "24000", ref_clip],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            size_kb = os.path.getsize(ref_clip) / 1024
            print(f"Extracted 10s reference clip: {ref_clip} ({size_kb:.0f} KB)")
        else:
            print(f"ffmpeg clip extraction failed (non-fatal)")
    except Exception as e:
        print(f"Could not extract clip: {e}")

    print()
    run_tts(text, voice="neutral_female", output_path=output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Voxtral TTS Test — Debra voice comparison",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 voxtral-test.py
  python3 voxtral-test.py --voice casual_female
  python3 voxtral-test.py --voice cheerful_female --output /tmp/cheerful.wav
  python3 voxtral-test.py --list-voices
  python3 voxtral-test.py --skip-clone
        """
    )
    parser.add_argument("--voice", default="casual_female", choices=AVAILABLE_VOICES,
                        help="Voice preset to use (default: casual_female)")
    parser.add_argument("--output", default=OUTPUT_WAV, help="Output audio path (.wav or .mp3)")
    parser.add_argument("--text", default=TEST_TEXT, help="Text to synthesize")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    parser.add_argument("--skip-clone", action="store_true", help="Skip voice clone test")
    args = parser.parse_args()

    if args.list_voices:
        print("Available Voxtral voices:")
        for v in AVAILABLE_VOICES:
            print(f"  {v}")
        return

    # Primary TTS test
    audio_dur, gen_time = run_tts(args.text, voice=args.voice, output_path=args.output)

    if audio_dur:
        print(f"\n✅ Primary test PASSED")
        print(f"   {audio_dur:.2f}s of audio in {gen_time:.2f}s (RTF: {gen_time/audio_dur:.3f})")

    # Voice clone test (uses reference audio)
    if not args.skip_clone:
        clone_output = args.output.replace(".wav", "-clone.wav").replace(".mp3", "-clone.wav")
        run_voice_clone_test(args.text, REFERENCE_AUDIO, clone_output)

    print(f"\n{'='*60}")
    print("Output files:")
    for f in [args.output, OUTPUT_MP3, OUTPUT_WAV.replace(".wav", "-clone.wav")]:
        if os.path.exists(f):
            size_kb = os.path.getsize(f) / 1024
            dur_s = size_kb * 1024 / (24000 * 2) if f.endswith(".wav") else "?"
            print(f"  {f} ({size_kb:.0f} KB)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
