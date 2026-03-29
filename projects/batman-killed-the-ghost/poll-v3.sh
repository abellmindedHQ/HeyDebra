#!/bin/bash
# Poll and download v3 Kling animations, build both 16:9 and 9:16 final videos
FAL_KEY="9bce9a0b-28b1-42e4-97be-c7c0ecd8dc8b:41498985bbc7b896baa1ea1019487fb0"
PROJ="/Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost"
VIDEOS="$PROJ/videos-v3"
FRAMES="$PROJ/frames-v3"
FRAMES_VERT="$PROJ/frames-v3-vertical"
AUDIO="/Users/debra/Downloads/Batman Killed the Ghost.m4a"

SCENES="scene01-title scene02-bedtime scene03-darknight scene04-rooftop scene05-lookup scene06-ghostalive scene07a-book scene07b-running scene08-happily scene09-sequels scene10-sparkles scene11-nightday scene12-hopping scene13-ghost scene14-family scene15-goodnight scene16-credits"

echo "=== POLLING V3 KLING ANIMATIONS ==="
MAX_POLLS=80
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
    
    if [ -f "$vid_file" ] && [ -s "$vid_file" ]; then
      completed=$((completed + 1))
      continue
    fi
    
    if [ ! -f "$req_file" ]; then continue; fi
    all_done=false
    req_id=$(cat "$req_file")
    
    status=$(curl -s "https://queue.fal.run/fal-ai/kling-video/v1.6/standard/image-to-video/requests/$req_id/status" \
      -H "Authorization: Key $FAL_KEY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','UNKNOWN'))" 2>/dev/null)
    
    if [ "$status" = "COMPLETED" ]; then
      video_url=$(curl -s "https://queue.fal.run/fal-ai/kling-video/v1.6/standard/image-to-video/requests/$req_id" \
        -H "Authorization: Key $FAL_KEY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('video',{}).get('url',''))" 2>/dev/null)
      
      if [ -n "$video_url" ] && [ "$video_url" != "" ]; then
        curl -s -o "$vid_file" "$video_url"
        echo "  ✓ $scene downloaded"
        completed=$((completed + 1))
      fi
    elif [ "$status" = "FAILED" ]; then
      echo "  ✗ $scene FAILED"
      touch "$vid_file"  # create empty to skip
      completed=$((completed + 1))
    fi
  done
  
  echo "Poll $poll: $completed/$total"
  
  if $all_done; then
    echo "All done!"
    break
  fi
  
  sleep 20
done

echo ""
echo "=== BUILDING FINAL VIDEOS ==="

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

build_version() {
  local aspect="$1"  # "16:9" or "9:16"
  local res_w="$2"
  local res_h="$3"
  local frame_dir="$4"
  local output="$5"
  local tmpdir="$PROJ/tmp-${aspect//:/x}"
  mkdir -p "$tmpdir"
  
  echo "Building $aspect version ($res_w x $res_h)..."
  
  for scene in $SCENES; do
    local vid_file="$VIDEOS/${scene}.mp4"
    local img_file="$frame_dir/${scene}.jpg"
    local out_file="$tmpdir/${scene}.mp4"
    local dur=${DURATIONS[$scene]}
    
    if [ -f "$vid_file" ] && [ -s "$vid_file" ]; then
      vid_dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$vid_file" 2>/dev/null | cut -d. -f1)
      vid_dur=${vid_dur:-5}
      
      if [ "$dur" -le "$vid_dur" ]; then
        ffmpeg -y -i "$vid_file" -t "$dur" -vf "scale=${res_w}:${res_h}:force_original_aspect_ratio=decrease,pad=${res_w}:${res_h}:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -pix_fmt yuv420p -r 25 -an "$out_file" 2>/dev/null
      else
        loops=$((dur / vid_dur + 1))
        ffmpeg -y -stream_loop "$loops" -i "$vid_file" -t "$dur" -vf "scale=${res_w}:${res_h}:force_original_aspect_ratio=decrease,pad=${res_w}:${res_h}:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -pix_fmt yuv420p -r 25 -an "$out_file" 2>/dev/null
      fi
    elif [ -f "$img_file" ]; then
      local frames=$((dur * 25))
      ffmpeg -y -loop 1 -i "$img_file" \
        -vf "scale=$((res_w*2)):$((res_h*2)):force_original_aspect_ratio=decrease,pad=$((res_w*2)):$((res_h*2)):(ow-iw)/2:(oh-ih)/2:black,zoompan=z='min(zoom+0.0003,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${frames}:s=${res_w}x${res_h}:fps=25" \
        -t "$dur" -c:v libx264 -pix_fmt yuv420p -r 25 "$out_file" 2>/dev/null
    fi
  done
  
  # Concat
  > "$tmpdir/concat.txt"
  for scene in $SCENES; do
    echo "file '${scene}.mp4'" >> "$tmpdir/concat.txt"
  done
  
  ffmpeg -y -f concat -safe 0 -i "$tmpdir/concat.txt" -c copy "$tmpdir/combined.mp4" 2>/dev/null
  
  # Add audio
  ffmpeg -y -i "$tmpdir/combined.mp4" -i "$AUDIO" \
    -filter_complex "[1:a]adelay=3000|3000[delayed_audio]" \
    -map 0:v -map "[delayed_audio]" \
    -c:v copy -c:a aac -b:a 192k -shortest "$output" 2>/dev/null
  
  echo "  Output: $output ($(ls -lh "$output" 2>/dev/null | awk '{print $5}'))"
  
  # Compressed version for sharing
  local compressed="${output%.mp4}-compressed.mp4"
  ffmpeg -y -i "$output" -c:v libx264 -crf 30 -preset medium -vf "scale=iw/2:ih/2" -c:a aac -b:a 96k "$compressed" 2>/dev/null
  echo "  Compressed: $compressed ($(ls -lh "$compressed" 2>/dev/null | awk '{print $5}'))"
  
  rm -rf "$tmpdir"
}

# Build 16:9 (landscape)
build_version "16:9" 1920 1080 "$FRAMES" "$PROJ/batman-v3-landscape.mp4"

# Build 9:16 (vertical/stories)
build_version "9:16" 1080 1920 "$FRAMES_VERT" "$PROJ/batman-v3-vertical.mp4"

echo ""
echo "=== ALL DONE ==="
ls -lh "$PROJ/batman-v3-"*.mp4
