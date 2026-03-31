#!/usr/bin/env python3.14
"""
Voice Clone TTS - Generate speech using cloned voice profiles.
Powered by Chatterbox-TTS (ResembleAI) running natively on Apple Silicon (MPS).

Usage:
    python3 voice-clone-tts.py --voice debra --text "Hello world" --output hello.wav
    python3 voice-clone-tts.py --voice alex --text "Hey what's up" --output output.wav

Options:
    --voice     Voice profile to use: debra | alex (or path to a custom profile.json)
    --text      Text to synthesize (use quotes for multi-word text)
    --output    Output WAV file path
    --ref       Override reference audio file (optional)
    --exaggeration  Expression level 0.0-1.0 (default: from profile or 0.4)
    --cfg-weight    CFG weight 0.0-1.0 (default: from profile or 0.5)
    --device    Force device: mps | cpu (default: auto-detect MPS)

Examples:
    # Debra voice
    python3 voice-clone-tts.py --voice debra --text "Hey sugar, call me back." --output debra.wav

    # Alex voice
    python3 voice-clone-tts.py --voice alex --text "What's up, this is Alex." --output alex.wav

    # Custom reference file
    python3 voice-clone-tts.py --voice debra --ref /path/to/custom_ref.wav --text "Hello" --output out.wav
"""

import argparse
import json
import os
import sys
import warnings

# Suppress deprecation warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

VOICE_PROFILES_DIR = os.path.join(os.path.dirname(__file__), "..", "voice-clones")
BUILTIN_VOICES = {
    "debra": os.path.join(VOICE_PROFILES_DIR, "debra", "profile.json"),
    "alex": os.path.join(VOICE_PROFILES_DIR, "alex", "profile.json"),
}


def load_profile(voice: str) -> dict:
    """Load voice profile from name or path."""
    # Check if it's a builtin voice name
    if voice.lower() in BUILTIN_VOICES:
        profile_path = BUILTIN_VOICES[voice.lower()]
    elif os.path.isfile(voice):
        profile_path = voice
    else:
        print(f"Error: Unknown voice '{voice}'. Available voices: {', '.join(BUILTIN_VOICES.keys())}")
        print(f"Or provide a path to a profile.json file.")
        sys.exit(1)

    profile_path = os.path.realpath(profile_path)
    if not os.path.exists(profile_path):
        print(f"Error: Profile not found at {profile_path}")
        sys.exit(1)

    with open(profile_path) as f:
        profile = json.load(f)

    # Resolve relative reference paths relative to profile directory
    profile_dir = os.path.dirname(profile_path)
    if "primary_reference" in profile:
        ref_path = profile["primary_reference"]
        if not os.path.isabs(ref_path):
            profile["_resolved_ref"] = os.path.join(profile_dir, ref_path)
        else:
            profile["_resolved_ref"] = ref_path
    
    return profile


def generate_speech(text: str, profile: dict, output_path: str, 
                    ref_override: str = None, device: str = None,
                    exaggeration: float = None, cfg_weight: float = None):
    """Generate speech using Chatterbox TTS with voice profile."""
    import torch
    import soundfile as sf
    from chatterbox.tts import ChatterboxTTS

    # Determine device
    if device is None:
        device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"🎙️  Using device: {device}")

    # Load model
    print("📦 Loading Chatterbox TTS model...")
    model = ChatterboxTTS.from_pretrained(device=device)

    # Determine reference audio
    if ref_override:
        ref_path = ref_override
    elif "_resolved_ref" in profile:
        ref_path = profile["_resolved_ref"]
    else:
        print("Error: No reference audio file specified in profile or via --ref")
        sys.exit(1)

    if not os.path.exists(ref_path):
        print(f"Error: Reference audio not found: {ref_path}")
        sys.exit(1)

    # Get generation parameters (CLI args override profile defaults)
    params = profile.get("generation_params", {})
    exag = exaggeration if exaggeration is not None else params.get("exaggeration", 0.4)
    cfg = cfg_weight if cfg_weight is not None else params.get("cfg_weight", 0.5)

    voice_name = profile.get("display_name", profile.get("voice_id", "unknown"))
    print(f"🎤 Voice: {voice_name}")
    print(f"📁 Reference: {os.path.basename(ref_path)}")
    print(f"⚙️  Exaggeration: {exag}, CFG weight: {cfg}")
    print(f"💬 Text: {text[:80]}{'...' if len(text) > 80 else ''}")
    print("🔄 Generating speech...")

    wav = model.generate(
        text,
        audio_prompt_path=ref_path,
        exaggeration=exag,
        cfg_weight=cfg,
    )

    # Save output
    audio_np = wav.squeeze().cpu().numpy()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    sf.write(output_path, audio_np, model.sr)

    duration = len(audio_np) / model.sr
    print(f"✅ Saved to: {output_path}")
    print(f"⏱️  Duration: {duration:.2f}s")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Voice Clone TTS - Generate speech with cloned voices on Apple Silicon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--voice", "-v", required=True,
                        help="Voice name (debra|alex) or path to profile.json")
    parser.add_argument("--text", "-t", required=True,
                        help="Text to synthesize")
    parser.add_argument("--output", "-o", required=True,
                        help="Output WAV file path")
    parser.add_argument("--ref", "-r", default=None,
                        help="Override reference audio file path")
    parser.add_argument("--device", "-d", default=None,
                        choices=["mps", "cpu"],
                        help="Force device (default: auto-detect MPS)")
    parser.add_argument("--exaggeration", "-e", type=float, default=None,
                        help="Expression exaggeration 0.0-1.0 (default: from profile)")
    parser.add_argument("--cfg-weight", "-c", type=float, default=None,
                        help="CFG weight 0.0-1.0 (default: from profile)")
    parser.add_argument("--list-voices", "-l", action="store_true",
                        help="List available voice profiles")

    # Allow --list-voices without required args
    if "--list-voices" in sys.argv or "-l" in sys.argv:
        for name, path in BUILTIN_VOICES.items():
            if os.path.exists(path):
                try:
                    with open(path) as f:
                        p = json.load(f)
                    print(f"  {name:10s} - {p.get('description', 'No description')}")
                except Exception:
                    print(f"  {name:10s} - (profile unreadable)")
            else:
                print(f"  {name:10s} - (profile not found)")
        return

    args = parser.parse_args()

    if args.list_voices:
        print("Available built-in voices:")
        for name, path in BUILTIN_VOICES.items():
            if os.path.exists(path):
                try:
                    with open(path) as f:
                        p = json.load(f)
                    print(f"  {name:10s} - {p.get('description', 'No description')}")
                except Exception:
                    print(f"  {name:10s} - (profile unreadable)")
            else:
                print(f"  {name:10s} - (profile not found)")
        return

    if not args.text.strip():
        print("Error: --text cannot be empty")
        sys.exit(1)

    profile = load_profile(args.voice)
    generate_speech(
        text=args.text,
        profile=profile,
        output_path=args.output,
        ref_override=args.ref,
        device=args.device,
        exaggeration=args.exaggeration,
        cfg_weight=args.cfg_weight,
    )


if __name__ == "__main__":
    main()
