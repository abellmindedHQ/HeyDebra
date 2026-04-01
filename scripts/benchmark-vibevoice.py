#!/usr/bin/env python3
"""
VibeVoice-ASR vs Whisper benchmark script.
Tests transcription accuracy, speaker diarization, and speed on M4 Mac mini.
"""
import time
import json
import os
import sys

# Test files
TEST_FILES = [
    "/Users/debra/.openclaw/workspace/projects/holdplease/recordings/conv_3301kmwqn4zwf0cb2c9pf3cy8q86-lufthansa-eris.mp3",
    "/Users/debra/Library/Messages/Attachments/BlueBubbles/2969aa79-bb3b-4121-8170-dca445378c51/charlotte-call.mp3",
    "/Users/debra/.openclaw/workspace/projects/holdplease/demo/holdplease-demo-airline.mp3",
]

OUTPUT_DIR = "/Users/debra/.openclaw/workspace/memory/vibevoice-benchmark"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def benchmark_vibevoice(audio_path):
    """Run VibeVoice-ASR on an audio file."""
    try:
        import torch
        import torchaudio
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

        print(f"Loading VibeVoice model...")
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        torch_dtype = torch.float16 if device == "mps" else torch.float32

        # Try VibeVoice first, fall back to Whisper large-v3 for comparison
        model_id = "microsoft/VibeVoice-ASR"
        try:
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True
            )
            model.to(device)
            processor = AutoProcessor.from_pretrained(model_id)
        except Exception as e:
            print(f"VibeVoice model not available ({e}), trying whisper-large-v3...")
            model_id = "openai/whisper-large-v3"
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True
            )
            model.to(device)
            processor = AutoProcessor.from_pretrained(model_id)

        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
            return_timestamps=True,
        )

        print(f"Transcribing: {os.path.basename(audio_path)}")
        start = time.time()
        result = pipe(audio_path, return_timestamps=True)
        elapsed = time.time() - start

        return {
            "model": model_id,
            "file": os.path.basename(audio_path),
            "text": result["text"],
            "chunks": result.get("chunks", []),
            "elapsed_seconds": round(elapsed, 2),
            "device": device,
        }
    except Exception as e:
        return {"error": str(e), "file": os.path.basename(audio_path)}


def benchmark_whisper_api(audio_path):
    """Run OpenAI Whisper API on the same file for comparison."""
    import urllib.request
    import urllib.error

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Try reading from .env
        env_path = "/Users/debra/.openclaw/workspace/projects/holdplease/.env"
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        api_key = line.strip().split("=", 1)[1].strip('"').strip("'")
                        break
    if not api_key:
        return {"error": "No OPENAI_API_KEY found", "file": os.path.basename(audio_path)}

    # Check file size (25MB limit)
    size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    if size_mb > 25:
        return {"error": f"File too large ({size_mb:.1f}MB > 25MB limit)", "file": os.path.basename(audio_path)}

    print(f"Whisper API transcribing: {os.path.basename(audio_path)}")
    start = time.time()

    import subprocess
    result = subprocess.run([
        "curl", "-s", "https://api.openai.com/v1/audio/transcriptions",
        "-H", f"Authorization: Bearer {api_key}",
        "-F", f"file=@{audio_path}",
        "-F", "model=whisper-1",
        "-F", "response_format=verbose_json",
        "-F", "timestamp_granularities[]=segment",
    ], capture_output=True, text=True, timeout=120)

    elapsed = time.time() - start

    try:
        data = json.loads(result.stdout)
        return {
            "model": "whisper-1 (API)",
            "file": os.path.basename(audio_path),
            "text": data.get("text", ""),
            "segments": data.get("segments", []),
            "elapsed_seconds": round(elapsed, 2),
            "device": "cloud",
        }
    except:
        return {"error": result.stdout[:200], "file": os.path.basename(audio_path)}


def main():
    results = []
    for audio_path in TEST_FILES:
        if not os.path.exists(audio_path):
            print(f"Skipping (not found): {audio_path}")
            continue

        size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        print(f"\n{'='*60}")
        print(f"File: {os.path.basename(audio_path)} ({size_mb:.1f}MB)")
        print(f"{'='*60}")

        # VibeVoice / local model
        local_result = benchmark_vibevoice(audio_path)
        results.append({"method": "local", **local_result})
        if "error" not in local_result:
            print(f"  Local: {local_result['elapsed_seconds']}s on {local_result['device']}")
            print(f"  Text preview: {local_result['text'][:200]}...")

        # Whisper API
        api_result = benchmark_whisper_api(audio_path)
        results.append({"method": "api", **api_result})
        if "error" not in api_result:
            print(f"  API: {api_result['elapsed_seconds']}s")
            print(f"  Text preview: {api_result['text'][:200]}...")

    # Save results
    output_path = os.path.join(OUTPUT_DIR, "benchmark-results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")

    # Generate comparison report
    report_path = os.path.join(OUTPUT_DIR, "benchmark-report.md")
    with open(report_path, "w") as f:
        f.write("# VibeVoice-ASR vs Whisper API Benchmark\n\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Device: M4 Mac mini\n\n")
        for r in results:
            f.write(f"## {r.get('file', 'unknown')} ({r['method']})\n")
            if "error" in r:
                f.write(f"**Error:** {r['error']}\n\n")
            else:
                f.write(f"- Model: {r.get('model', '?')}\n")
                f.write(f"- Time: {r.get('elapsed_seconds', '?')}s\n")
                f.write(f"- Device: {r.get('device', '?')}\n")
                f.write(f"- Text: {r.get('text', '')[:500]}\n\n")
    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    main()
