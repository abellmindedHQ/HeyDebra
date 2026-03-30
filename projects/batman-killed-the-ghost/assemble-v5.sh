#!/bin/bash
# Batman Killed the Ghost v5 - Video Assembly
# Ken Burns effect (slow zoom/pan) + crossfades, synced to audio timestamps
# Total runtime: ~209 seconds (3:29 - audio 3:24.5 + 5s credits)

set -e

FRAMES="/Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost/frames-v5"
AUDIO="/Users/debra/Downloads/Batman Killed the Ghost.m4a"
WORKDIR="/Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost"
OUTPUT="$WORKDIR/batman-v5-final.mp4"
OUTPUT_SM="$WORKDIR/batman-v5-final-sm.mp4"
TMPDIR="$WORKDIR/tmp-v5"

mkdir -p "$TMPDIR"

# Frame timestamps (start_time duration)
# Based on screenplay timestamps
# Format: frame_file start_sec duration_sec
declare -a FRAME_FILES=(
  "frame01_title.jpg"         # 0:00 - 0:03 (3s)
  "frame02_bedtime.jpg"       # 0:00 - 0:08 (8s) overlap with title
  "frame03_darknight.jpg"     # 0:08 - 0:21 (13s)
  "frame04_rooftop.jpg"       # 0:21 - 0:32 (11s)
  "frame05_lookedup.jpg"      # 0:32 - 0:52 (20s)
  "frame06_ghostalive.jpg"    # 0:52 - 1:02 (10s)
  "frame07a_glowingbook.jpg"  # 1:02 - 1:15 (13s)
  "frame07b_batmanruns.jpg"   # 1:15 - 1:27 (12s)
  "frame08_happily.jpg"       # 1:27 - 1:40 (13s)
  "frame09_sequels.jpg"       # 1:40 - 2:04 (24s)
  "frame10_sparkletitle.jpg"  # 2:04 - 2:14 (10s)
  "frame11_nightday.jpg"      # 2:14 - 2:29 (15s)
  "frame12_hoppedhopped.jpg"  # 2:29 - 2:47 (18s)
  "frame13_ghostscares.jpg"   # 2:47 - 3:00 (13s)
  "frame14_momsanddads.jpg"   # 3:00 - 3:14 (14s)
  "frame15_goodnight.jpg"     # 3:14 - 3:24 (10s)
  "frame16_credits.jpg"       # 3:24 - 3:29 (5s)
)

declare -a DURATIONS=(
  3
  8
  13
  11
  20
  10
  13
  12
  13
  24
  10
  15
  18
  13
  14
  10
  5
)

NFRAMES=${#FRAME_FILES[@]}
CROSSFADE=0.8  # seconds for crossfade transitions

echo "=== Batman Killed the Ghost v5 - Assembly ==="
echo "Frames: $NFRAMES"
echo "Output: $OUTPUT"
echo ""

# Step 1: Apply Ken Burns effect to each frame and output as clip
echo "Step 1: Applying Ken Burns effect to each frame..."

CLIP_LIST=""
for i in "${!FRAME_FILES[@]}"; do
  FNAME="${FRAME_FILES[$i]}"
  DUR="${DURATIONS[$i]}"
  INPUT="$FRAMES/$FNAME"
  CLIP_OUT="$TMPDIR/clip_$(printf '%02d' $i).mp4"
  
  # Different Ken Burns directions for each frame for variety
  case $((i % 6)) in
    0) # Slow zoom in from center
      ZOOM_EXPR="zoom='min(1.15,1.0+in/500)'"
      X_EXPR="x='iw/2-(iw/zoom/2)'"
      Y_EXPR="y='ih/2-(ih/zoom/2)'"
      ;;
    1) # Slow zoom in from top-left
      ZOOM_EXPR="zoom='min(1.15,1.0+in/500)'"
      X_EXPR="x='0'"
      Y_EXPR="y='0'"
      ;;
    2) # Slow pan right while zoomed
      ZOOM_EXPR="zoom='1.1'"
      X_EXPR="x='(iw/zoom/2)*in/200'"
      Y_EXPR="y='ih/2-(ih/zoom/2)'"
      ;;
    3) # Slow zoom out from center
      ZOOM_EXPR="zoom='max(1.0,1.15-in/500)'"
      X_EXPR="x='iw/2-(iw/zoom/2)'"
      Y_EXPR="y='ih/2-(ih/zoom/2)'"
      ;;
    4) # Slow pan left to right, bottom third
      ZOOM_EXPR="zoom='1.1'"
      X_EXPR="x='(iw/zoom/10)*in/200'"
      Y_EXPR="y='ih*0.6-(ih/zoom/2)'"
      ;;
    5) # Slow zoom in from bottom-right
      ZOOM_EXPR="zoom='min(1.15,1.0+in/500)'"
      X_EXPR="x='iw-iw/zoom'"
      Y_EXPR="y='ih-ih/zoom'"
      ;;
  esac
  
  echo "  Frame $i: $FNAME ($DUR s)..."
  
  ffmpeg -y -loglevel error \
    -loop 1 -i "$INPUT" \
    -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=$ZOOM_EXPR:$X_EXPR:$Y_EXPR:d=$((DUR * 25)):s=1920x1080:fps=25,setsar=1" \
    -t "$DUR" \
    -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
    -r 25 \
    "$CLIP_OUT"
  
  CLIP_LIST="$CLIP_LIST|$CLIP_OUT"
done

echo ""
echo "Step 2: Concatenating clips with crossfades..."

# Build complex filtergraph for crossfade transitions
# Using xfade filter for smooth crossfades

FILTER=""
INPUTS=""
for i in "${!FRAME_FILES[@]}"; do
  CLIP="$TMPDIR/clip_$(printf '%02d' $i).mp4"
  INPUTS="$INPUTS -i $CLIP"
done

# Build xfade chain
# xfade needs offset = sum of durations minus crossfade time for each transition

# Compute cumulative offsets
CUM=0
PREV_LABEL="[0:v]"
FILTER_PARTS=""

for i in "${!FRAME_FILES[@]}"; do
  if [ $i -eq 0 ]; then
    CUM=${DURATIONS[$i]}
    continue
  fi
  
  OFFSET=$((CUM - 1))  # 1 second before end of previous clip
  NEXT_IDX=$i
  
  if [ $i -lt $((NFRAMES - 1)) ]; then
    OUT_LABEL="[v${i}]"
  else
    OUT_LABEL="[vout]"
  fi
  
  FILTER_PARTS="${FILTER_PARTS}${PREV_LABEL}[${NEXT_IDX}:v]xfade=transition=fade:duration=${CROSSFADE}:offset=${OFFSET}${OUT_LABEL};"
  PREV_LABEL="[v${i}]"
  CUM=$((CUM + ${DURATIONS[$i]}))
done

# Remove trailing semicolon
FILTER_PARTS="${FILTER_PARTS%;}"

echo "  Building filter graph..."
echo "  Total duration: ~$CUM seconds"

ffmpeg -y -loglevel warning \
  $INPUTS \
  -filter_complex "$FILTER_PARTS" \
  -map "[vout]" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -r 25 \
  "$TMPDIR/video_only.mp4"

echo ""
echo "Step 3: Mixing in audio..."

ffmpeg -y -loglevel warning \
  -i "$TMPDIR/video_only.mp4" \
  -i "$AUDIO" \
  -c:v copy \
  -c:a aac -b:a 128k \
  -map 0:v:0 -map 1:a:0 \
  -shortest \
  "$OUTPUT"

echo ""
echo "Step 4: Creating compressed version for iMessage (<10MB)..."

# Target size: 9.5MB = 9.5 * 8192 kbits / duration
TOTAL_DUR=$CUM
TARGET_KB=$((9500 * 8 / TOTAL_DUR))
echo "  Target bitrate: ${TARGET_KB}kbps for ${TOTAL_DUR}s"

ffmpeg -y -loglevel warning \
  -i "$OUTPUT" \
  -c:v libx264 -preset slow -b:v $((TARGET_KB - 64))k \
  -c:a aac -b:a 64k \
  -vf "scale=1280:720" \
  -movflags +faststart \
  "$OUTPUT_SM"

# Copy small version to /tmp
cp "$OUTPUT_SM" /tmp/batman-v5-final-sm.mp4

echo ""
echo "=== DONE ==="
echo "Final:      $OUTPUT"
echo "Compressed: $OUTPUT_SM"
echo "iMessage:   /tmp/batman-v5-final-sm.mp4"

# Show file sizes
ls -lh "$OUTPUT" "$OUTPUT_SM" /tmp/batman-v5-final-sm.mp4

echo ""
echo "Cleanup temp files..."
# Keep tmp for debugging, but note it
echo "  Temp clips in $TMPDIR (can delete manually)"
