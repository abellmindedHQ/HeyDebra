#!/bin/bash
PROJ="/Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost"
FRAMES="$PROJ/frames-v4"
AUDIO="/Users/debra/Downloads/Batman Killed the Ghost.m4a"
TMPDIR="$PROJ/tmp-v4"
mkdir -p "$TMPDIR"

# 42 frames with durations in seconds (total ~207s = 3s title + 204.5s audio)
DURATIONS="3 4 4 2 4 7 5 6 4 6 10 6 4 8 5 7 5 3 3 10 6 2 2 2 6 6 6 4 6 5 7 10 5 6 5 2 7 5 4 4 4 5"

echo "=== BUILDING V4 COMEDY CUT ==="

i=0
for dur in $DURATIONS; do
  i=$((i + 1))
  scene=$(printf "frame%02d" $i)
  img="$FRAMES/${scene}.jpg"
  out="$TMPDIR/${scene}.mp4"
  
  if [ ! -f "$img" ]; then
    echo "MISSING: $scene"
    continue
  fi
  
  ffmpeg -y -loop 1 -i "$img" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:white" \
    -t "$dur" -c:v libx264 -pix_fmt yuv420p -r 25 -an "$out" 2>/dev/null
  echo "✓ $scene (${dur}s)"
done

# Concat
> "$TMPDIR/concat.txt"
for j in $(seq 1 42); do
  scene=$(printf "frame%02d" $j)
  echo "file '${scene}.mp4'" >> "$TMPDIR/concat.txt"
done

echo "Concatenating..."
ffmpeg -y -f concat -safe 0 -i "$TMPDIR/concat.txt" -c copy "$TMPDIR/combined.mp4" 2>/dev/null

echo "Adding audio..."
ffmpeg -y -i "$TMPDIR/combined.mp4" -i "$AUDIO" \
  -filter_complex "[1:a]adelay=3000|3000[delayed_audio]" \
  -map 0:v -map "[delayed_audio]" \
  -c:v copy -c:a aac -b:a 192k -shortest "$PROJ/batman-v4-comedy.mp4" 2>/dev/null

echo "Compressing..."
ffmpeg -y -i "$PROJ/batman-v4-comedy.mp4" \
  -c:v libx264 -crf 30 -preset medium -vf "scale=960:540" \
  -c:a aac -b:a 96k "$PROJ/batman-v4-comedy-sm.mp4" 2>/dev/null

ls -lh "$PROJ/batman-v4-comedy.mp4" "$PROJ/batman-v4-comedy-sm.mp4"
rm -rf "$TMPDIR"
echo "=== DONE ==="
