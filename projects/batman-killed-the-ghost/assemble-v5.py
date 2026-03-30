#!/usr/bin/env python3
"""
Batman Killed the Ghost v5 - Video Assembly (Python version)
Correctly handles xfade chain offset math.
"""

import os
import subprocess
import sys

FRAMES_DIR = '/Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost/frames-v5'
AUDIO = '/Users/debra/Downloads/Batman Killed the Ghost.m4a'
WORKDIR = '/Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost'
OUTPUT = os.path.join(WORKDIR, 'batman-v5-final.mp4')
OUTPUT_SM = os.path.join(WORKDIR, 'batman-v5-final-sm.mp4')
TMPDIR = os.path.join(WORKDIR, 'tmp-v5')

os.makedirs(TMPDIR, exist_ok=True)

# Frame filenames and their durations (seconds)
FRAMES = [
    ("frame01_title.jpg",        3),
    ("frame02_bedtime.jpg",      8),
    ("frame03_darknight.jpg",   13),
    ("frame04_rooftop.jpg",     11),
    ("frame05_lookedup.jpg",    20),
    ("frame06_ghostalive.jpg",  10),
    ("frame07a_glowingbook.jpg",13),
    ("frame07b_batmanruns.jpg", 12),
    ("frame08_happily.jpg",     13),
    ("frame09_sequels.jpg",     24),
    ("frame10_sparkletitle.jpg",10),
    ("frame11_nightday.jpg",    15),
    ("frame12_hoppedhopped.jpg",18),
    ("frame13_ghostscares.jpg", 13),
    ("frame14_momsanddads.jpg", 14),
    ("frame15_goodnight.jpg",   10),
    ("frame16_credits.jpg",      5),
]

CROSSFADE = 0.8  # seconds

# Ken Burns zoom/pan configs (cycle through these)
KB_CONFIGS = [
    # (zoom_expr, x_expr, y_expr)
    ("zoom='min(1.15,1.0+on/500)'", "x='iw/2-(iw/zoom/2)'", "y='ih/2-(ih/zoom/2)'"),    # zoom in from center
    ("zoom='min(1.15,1.0+on/500)'", "x='0'",                 "y='0'"),                    # zoom in from top-left
    ("zoom='1.1'",                   "x='(iw-iw/zoom)*on/200'", "y='ih/2-(ih/zoom/2)'"), # pan right
    ("zoom='max(1.0,1.15-on/500)'", "x='iw/2-(iw/zoom/2)'", "y='ih/2-(ih/zoom/2)'"),    # zoom out
    ("zoom='1.1'",                   "x='(iw-iw/zoom)*(1-on/200)'", "y='ih*0.6-(ih/zoom/2)'"),  # pan left
    ("zoom='min(1.15,1.0+on/500)'", "x='iw-iw/zoom'",        "y='ih-ih/zoom'"),           # zoom in from bottom-right
]


def run(cmd, **kwargs):
    print(f"  $ {' '.join(cmd[:6])}{'...' if len(cmd)>6 else ''}")
    result = subprocess.run(cmd, **kwargs, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  STDERR: {result.stderr[-2000:]}")
        raise RuntimeError(f"Command failed: {cmd[0]}")
    return result


def step1_ken_burns():
    """Apply Ken Burns effect to each frame, output as short clip."""
    print("\nStep 1: Ken Burns clips...")
    clips = []
    for i, (fname, dur) in enumerate(FRAMES):
        clip_path = os.path.join(TMPDIR, f'clip_{i:02d}.mp4')
        clips.append(clip_path)
        
        if os.path.exists(clip_path):
            print(f"  Skip {i}: {fname} (exists)")
            continue
        
        input_path = os.path.join(FRAMES_DIR, fname)
        zexpr, xexpr, yexpr = KB_CONFIGS[i % len(KB_CONFIGS)]
        total_frames = dur * 25
        
        # zoompan filter
        zp = f"zoompan={zexpr}:{xexpr}:{yexpr}:d={total_frames}:s=1920x1080:fps=25"
        
        cmd = [
            'ffmpeg', '-y', '-loglevel', 'error',
            '-loop', '1', '-i', input_path,
            '-vf', f'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,{zp},setsar=1',
            '-t', str(dur),
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
            '-r', '25',
            clip_path
        ]
        print(f"  {i:02d}: {fname} ({dur}s)...")
        run(cmd)
    
    return clips


def step2_concat_xfade(clips):
    """Concatenate clips with xfade transitions."""
    print("\nStep 2: Concat with xfade transitions...")
    
    video_only = os.path.join(TMPDIR, 'video_only.mp4')
    
    # Build ffmpeg command with chained xfade filters
    # Key: in a chain, the offset for xfade N is the cumulative OUTPUT duration
    # of the chain up to that point minus CROSSFADE.
    # Output duration after xfade(A, B) = dur_A + dur_B - crossfade
    # So offset for next transition = running_output_dur - crossfade
    
    # Build inputs
    input_args = []
    for clip in clips:
        input_args += ['-i', clip]
    
    # Build filtergraph
    n = len(clips)
    filter_parts = []
    
    # running_dur tracks output duration of the accumulated chain
    running_dur = FRAMES[0][1]  # duration of first clip
    prev_label = '[0:v]'
    
    for i in range(1, n):
        dur_i = FRAMES[i][1]
        offset = running_dur - CROSSFADE  # offset from start of chain output
        
        if i < n - 1:
            out_label = f'[v{i}]'
        else:
            out_label = '[vout]'
        
        filter_parts.append(
            f"{prev_label}[{i}:v]xfade=transition=fade:duration={CROSSFADE}:offset={offset:.3f}{out_label}"
        )
        
        prev_label = f'[v{i}]'
        running_dur = running_dur + dur_i - CROSSFADE
    
    filter_str = ';'.join(filter_parts)
    total_dur = running_dur
    print(f"  Total video duration: {total_dur:.1f}s")
    
    cmd = [
        'ffmpeg', '-y', '-loglevel', 'warning',
    ] + input_args + [
        '-filter_complex', filter_str,
        '-map', '[vout]',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
        '-r', '25',
        video_only
    ]
    
    run(cmd)
    return video_only, total_dur


def step3_add_audio(video_only):
    """Mix in the original audio."""
    print("\nStep 3: Adding audio...")
    
    cmd = [
        'ffmpeg', '-y', '-loglevel', 'warning',
        '-i', video_only,
        '-i', AUDIO,
        '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '128k',
        '-map', '0:v:0', '-map', '1:a:0',
        '-shortest',
        OUTPUT
    ]
    run(cmd)


def step4_compress(total_dur):
    """Create compressed version for iMessage (<10MB)."""
    print("\nStep 4: Compressing for iMessage...")
    
    # Target 9.5MB = 9.5 * 1024 * 8 kbits total / duration
    target_total_kbits = 9500 * 8
    target_video_kbps = int(target_total_kbits / total_dur) - 64  # reserve 64k for audio
    print(f"  Target video bitrate: {target_video_kbps}kbps")
    
    cmd = [
        'ffmpeg', '-y', '-loglevel', 'warning',
        '-i', OUTPUT,
        '-c:v', 'libx264', '-preset', 'slow',
        '-b:v', f'{target_video_kbps}k',
        '-c:a', 'aac', '-b:a', '64k',
        '-vf', 'scale=1280:720',
        '-movflags', '+faststart',
        OUTPUT_SM
    ]
    run(cmd)
    
    # Copy to /tmp
    import shutil
    shutil.copy2(OUTPUT_SM, '/tmp/batman-v5-final-sm.mp4')


def main():
    print("=== Batman Killed the Ghost v5 - Assembly ===")
    print(f"Frames: {len(FRAMES)}")
    print(f"Output: {OUTPUT}")
    
    clips = step1_ken_burns()
    video_only, total_dur = step2_concat_xfade(clips)
    step3_add_audio(video_only)
    step4_compress(total_dur)
    
    print("\n=== DONE ===")
    for path in [OUTPUT, OUTPUT_SM, '/tmp/batman-v5-final-sm.mp4']:
        size = os.path.getsize(path)
        print(f"  {os.path.basename(path)}: {size/1024/1024:.1f}MB")
    
    # Check duration
    result = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-show_format', '-i', OUTPUT],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if 'duration' in line:
            print(f"  Duration: {line.strip()}")
            break


if __name__ == '__main__':
    main()
