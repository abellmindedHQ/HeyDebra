#!/bin/bash
# Poll Kling animations, download completed ones, and build final video
FAL_KEY="9bce9a0b-28b1-42e4-97be-c7c0ecd8dc8b:41498985bbc7b896baa1ea1019487fb0"
PROJ="/Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost"
VIDEOS="$PROJ/videos-v2"
AUDIO="/Users/debra/Downloads/Batman Killed the Ghost.m4a"
OUTPUT="$PROJ/batman-killed-the-ghost-v2.mp4"

SCENES="scene01-title scene02-bedtime scene03-darknight scene04-rooftop scene05-lookup scene06-ghostalive scene07a-book scene07b-running scene08-happily scene09-sequels scene10-sparkles scene11-nightday scene12-hopping scene13-ghost scene14-family scene15-goodnight scene16-credits"

echo "=== POLLING FOR COMPLETED ANIMATIONS ==="
MAX_POLLS=60
poll=0
while [ $poll -lt $MAX_POLLS ]; do
  poll=$((poll + 1))
  all_done=true
  completed=0
  total=0
  
  for scene in $SCENES; do
    total=$((total + 1))
    req_file="$VIDEOS/${scene}.request_id"
    vid_file="$VIDEOS/${scene}.mp4"
    
    if [ -f "$vid_file" ]; then
      completed=$((completed + 1))
      continue
    fi
    
    if [ ! -f "$req_file" ]; then
      echo "  SKIP $scene: no request ID"
      continue
    fi
    
    all_done=false
    req_id=$(cat "$req_file")
    
    status=$(curl -s "https://queue.fal.run/fal-ai/kling-video/v1.6/standard/image-to-video/requests/$req_id/status" \
      -H "Authorization: Key $FAL_KEY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','UNKNOWN'))" 2>/dev/null)
    
    if [ "$status" = "COMPLETED" ]; then
      echo "  DONE: $scene - downloading..."
      video_url=$(curl -s "https://queue.fal.run/fal-ai/kling-video/v1.6/standard/image-to-video/requests/$req_id" \
        -H "Authorization: Key $FAL_KEY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('video',{}).get('url',''))" 2>/dev/null)
      
      if [ -n "$video_url" ] && [ "$video_url" != "" ]; then
        curl -s -o "$vid_file" "$video_url"
        size=$(ls -lh "$vid_file" | awk '{print $5}')
        echo "    Saved: $vid_file ($size)"
        completed=$((completed + 1))
      else
        echo "    ERROR: no video URL"
      fi
    elif [ "$status" = "FAILED" ]; then
      echo "  FAILED: $scene"
      completed=$((completed + 1))  # count as done
    fi
  done
  
  echo "Poll $poll: $completed/$total complete"
  
  if $all_done; then
    echo "All animations complete!"
    break
  fi
  
  sleep 15
done

echo ""
echo "=== BUILDING FINAL VIDEO ==="

# Count available videos
available=0
for scene in $SCENES; do
  vid_file="$VIDEOS/${scene}.mp4"
  if [ -f "$vid_file" ] && [ -s "$vid_file" ]; then
    available=$((available + 1))
  fi
done
echo "Available video clips: $available"

# For scenes without video, fall back to Ken Burns on the image
# Build concat file with scene durations matching audio timestamps
# Scene durations (seconds): title=3, s02=8, s03=13, s04=11, s05=20, s06=10, s07a=13, s07b=12, s08=13, s09=24, s10=10, s11=15, s12=18, s13=13, s14=12, s15=12, s16=5
declare -A DURATIONS
DURATIONS[scene01-title]=3
DURATIONS[scene02-bedtime]=8
DURATIONS[scene03-darknight]=13
DURATIONS[scene04-rooftop]=11
DURATIONS[scene05-lookup]=20
DURATIONS[scene06-ghostalive]=10
DURATIONS[scene07a-book]=13
DURATIONS[scene07b-running]=12
DURATIONS[scene08-happily]=13
DURATIONS[scene09-sequels]=24
DURATIONS[scene10-sparkles]=10
DURATIONS[scene11-nightday]=15
DURATIONS[scene12-hopping]=18
DURATIONS[scene13-ghost]=13
DURATIONS[scene14-family]=12
DURATIONS[scene15-goodnight]=12
DURATIONS[scene16-credits]=5

# Process each scene: stretch/trim video to target duration or generate from image
TMPDIR="$PROJ/tmp-v2"
mkdir -p "$TMPDIR"

for scene in $SCENES; do
  vid_file="$VIDEOS/${scene}.mp4"
  img_file="$PROJ/frames-v2/${scene}.jpg"
  out_file="$TMPDIR/${scene}.mp4"
  dur=${DURATIONS[$scene]}
  
  if [ -f "$vid_file" ] && [ -s "$vid_file" ]; then
    # Have animation - stretch/loop to target duration
    vid_dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$vid_file" 2>/dev/null | cut -d. -f1)
    vid_dur=${vid_dur:-5}
    
    if [ "$dur" -le "$vid_dur" ]; then
      # Trim to duration
      ffmpeg -y -i "$vid_file" -t "$dur" -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -pix_fmt yuv420p -r 25 -an "$out_file" 2>/dev/null
    else
      # Loop video to fill duration
      loops=$((dur / vid_dur + 1))
      ffmpeg -y -stream_loop "$loops" -i "$vid_file" -t "$dur" -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -pix_fmt yuv420p -r 25 -an "$out_file" 2>/dev/null
    fi
    echo "  $scene: animated ($dur s)"
  elif [ -f "$img_file" ]; then
    # Fallback to Ken Burns
    frames=$((dur * 25))
    ffmpeg -y -loop 1 -i "$img_file" \
      -vf "scale=3840:2160:force_original_aspect_ratio=decrease,pad=3840:2160:(ow-iw)/2:(oh-ih)/2:black,zoompan=z='min(zoom+0.0003,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${frames}:s=1920x1080:fps=25" \
      -t "$dur" -c:v libx264 -pix_fmt yuv420p -r 25 "$out_file" 2>/dev/null
    echo "  $scene: Ken Burns fallback ($dur s)"
  else
    echo "  $scene: MISSING - no video or image!"
  fi
done

# Build concat file
cat > "$TMPDIR/concat.txt" << EOF
$(for scene in $SCENES; do echo "file '${scene}.mp4'"; done)
EOF

# Concatenate
ffmpeg -y -f concat -safe 0 -i "$TMPDIR/concat.txt" -c copy "$TMPDIR/combined.mp4" 2>/dev/null

# Add audio with 3s offset (title card is silent)
ffmpeg -y -i "$TMPDIR/combined.mp4" -i "$AUDIO" \
  -filter_complex "[1:a]adelay=3000|3000[delayed_audio]" \
  -map 0:v -map "[delayed_audio]" \
  -c:v copy -c:a aac -b:a 192k -shortest "$OUTPUT" 2>/dev/null

echo ""
echo "=== DONE ==="
ls -lh "$OUTPUT"

# Cleanup
rm -rf "$TMPDIR"
