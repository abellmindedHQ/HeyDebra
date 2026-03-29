#!/bin/bash
# Build "Batman Killed the Ghost" animated video
# Syncs Avie's audio with generated crayon illustrations using Ken Burns effects

PROJ="/Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost"
FRAMES="$PROJ/frames"
AUDIO="/Users/debra/Downloads/Batman Killed the Ghost.m4a"
OUTPUT="$PROJ/batman-killed-the-ghost.mp4"

# Scene durations (in seconds) synced to audio timestamps
# scene01: title card (0-3s) - added before audio
# scene02: bedtime/what was it called (0-8s of audio)
# scene03: dark night (8-21s)
# scene05: looked up / rooftop combo (21-52s) 
# scene06: ghost alive (52-62s)
# scene07a: glowing book (62-75s)
# scene07b: running away (75-87s)
# scene08: happily lived ever again (87-100s)
# scene09: sequel pitches (100-124s)
# scene10: magic sparkles title (124-134s)
# scene11: night day forest (134-149s)
# scene12: hopping (149-167s)
# scene13: ghost scares sparkles (167-180s)
# scene14: moms and dads happy (180-192s)
# scene15: goodnight (192-204s)
# scene16: credits (overlay, 204-209s)

# Step 1: Create a 3-second title card video (silent, before audio starts)
ffmpeg -y -loop 1 -i "$FRAMES/scene01-title-card.png" \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,zoompan=z='min(zoom+0.0005,1.05)':d=75:s=1920x1080:fps=25" \
  -t 3 -c:v libx264 -pix_fmt yuv420p -r 25 "$PROJ/tmp_title.mp4"

# Step 2: Create each scene segment with Ken Burns zoom effects
# Each image gets a slow zoom in or out for visual interest

create_scene() {
  local input="$1"
  local output="$2" 
  local duration="$3"
  local zoom_dir="$4"  # "in" or "out"
  local frames=$((duration * 25))
  
  if [ "$zoom_dir" = "in" ]; then
    ZOOM="z='min(zoom+0.0003,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
  else
    ZOOM="z='if(eq(on,1),1.08,max(zoom-0.0003,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
  fi
  
  ffmpeg -y -loop 1 -i "$input" \
    -vf "scale=3840:2160:force_original_aspect_ratio=decrease,pad=3840:2160:(ow-iw)/2:(oh-ih)/2:black,zoompan=${ZOOM}:d=${frames}:s=1920x1080:fps=25" \
    -t "$duration" -c:v libx264 -pix_fmt yuv420p -r 25 "$output"
}

echo "Generating scene segments..."
create_scene "$FRAMES/scene02-bedtime.png" "$PROJ/tmp_s02.mp4" 8 "in"
create_scene "$FRAMES/scene03-dark-night.png" "$PROJ/tmp_s03.mp4" 13 "in"
create_scene "$FRAMES/scene05-looked-up.png" "$PROJ/tmp_s05.mp4" 31 "out"
create_scene "$FRAMES/scene06-ghost-alive.png" "$PROJ/tmp_s06.mp4" 10 "in"
create_scene "$FRAMES/scene07a-glowing-book.png" "$PROJ/tmp_s07a.mp4" 13 "in"
create_scene "$FRAMES/scene07b-running-away.png" "$PROJ/tmp_s07b.mp4" 12 "out"
create_scene "$FRAMES/scene08-happily-lived.png" "$PROJ/tmp_s08.mp4" 13 "in"
create_scene "$FRAMES/scene09-sequels.png" "$PROJ/tmp_s09.mp4" 24 "out"
create_scene "$FRAMES/scene10-sparkles-title.png" "$PROJ/tmp_s10.mp4" 10 "in"
create_scene "$FRAMES/scene11-night-day.png" "$PROJ/tmp_s11.mp4" 15 "in"
create_scene "$FRAMES/scene12-hopping.png" "$PROJ/tmp_s12.mp4" 18 "out"
create_scene "$FRAMES/scene13-ghost-scares-sparkles.png" "$PROJ/tmp_s13.mp4" 13 "in"
create_scene "$FRAMES/scene14-moms-dads-happy.png" "$PROJ/tmp_s14.mp4" 12 "out"
create_scene "$FRAMES/scene15-goodnight.png" "$PROJ/tmp_s15.mp4" 12 "in"
create_scene "$FRAMES/scene16-credits.png" "$PROJ/tmp_s16.mp4" 5 "in"

# Step 3: Create concat file
echo "Creating concat list..."
cat > "$PROJ/concat.txt" << EOF
file 'tmp_title.mp4'
file 'tmp_s02.mp4'
file 'tmp_s03.mp4'
file 'tmp_s05.mp4'
file 'tmp_s06.mp4'
file 'tmp_s07a.mp4'
file 'tmp_s07b.mp4'
file 'tmp_s08.mp4'
file 'tmp_s09.mp4'
file 'tmp_s10.mp4'
file 'tmp_s11.mp4'
file 'tmp_s12.mp4'
file 'tmp_s13.mp4'
file 'tmp_s14.mp4'
file 'tmp_s15.mp4'
file 'tmp_s16.mp4'
EOF

# Step 4: Concatenate all video segments
echo "Concatenating segments..."
ffmpeg -y -f concat -safe 0 -i "$PROJ/concat.txt" -c copy "$PROJ/tmp_video.mp4"

# Step 5: Add Avie's audio with 3s offset (title card is silent)
echo "Adding audio..."
ffmpeg -y -i "$PROJ/tmp_video.mp4" -i "$AUDIO" \
  -filter_complex "[1:a]adelay=3000|3000[delayed_audio]" \
  -map 0:v -map "[delayed_audio]" \
  -c:v copy -c:a aac -b:a 192k -shortest "$OUTPUT"

# Cleanup temp files
echo "Cleaning up..."
rm -f "$PROJ"/tmp_*.mp4 "$PROJ/concat.txt"

echo "Done! Output: $OUTPUT"
ls -lh "$OUTPUT"
