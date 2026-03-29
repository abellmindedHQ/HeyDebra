#!/bin/bash
# Queue all Kling animations for Batman Killed the Ghost v2
FAL_KEY="9bce9a0b-28b1-42e4-97be-c7c0ecd8dc8b:41498985bbc7b896baa1ea1019487fb0"
PROJ="/Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost"
FRAMES="$PROJ/frames-v2"
VIDEOS="$PROJ/videos-v2"
mkdir -p "$VIDEOS"

queue_video() {
  local name="$1"
  local prompt="$2"
  local image_url=$(cat "$FRAMES/${name}.url" 2>/dev/null)
  
  if [ -z "$image_url" ]; then
    echo "SKIP $name: no URL file"
    return
  fi
  
  echo "Queuing: $name"
  local result=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/v1.6/standard/image-to-video" \
    -H "Authorization: Key $FAL_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"prompt\": \"$prompt\",
      \"image_url\": \"$image_url\",
      \"duration\": \"5\",
      \"aspect_ratio\": \"16:9\"
    }")
  
  local req_id=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('request_id',''))" 2>/dev/null)
  
  if [ -n "$req_id" ]; then
    echo "$req_id" > "$VIDEOS/${name}.request_id"
    echo "  Queued: $req_id"
  else
    echo "  FAILED: $(echo "$result" | head -c 200)"
  fi
  
  sleep 1
}

echo "=== QUEUING KLING ANIMATIONS ==="

queue_video "scene01-title" \
  "Title card text slowly fading in with subtle sparkle effects. Dark background with gentle floating particles. Crayon drawing style animation."

queue_video "scene02-bedtime" \
  "Young blonde girl in bed gesturing excitedly telling a story, dad listening. Warm lamplight flickers gently. Subtle breathing movement. Cozy bedroom. Children crayon drawing animation."

queue_video "scene03-darknight" \
  "Dark city at night with twinkling stars and a glowing moon. Windows flickering with warm light. Subtle fog drifting. Dramatic atmosphere. Children crayon drawing animation style."

queue_video "scene04-rooftop" \
  "Batman and Spider-Man standing on rooftop, capes blowing in wind. Ghost floating gently. Stars twinkling. Person sleeping below with Z bubbles. Children crayon drawing animation."

queue_video "scene05-lookup" \
  "Person in bed looking up in surprise. Batman Spider-Man and ghost peer down through roof hole. Stars twinkling above. Comic surprise effect. Children crayon drawing animation."

queue_video "scene06-ghostalive" \
  "White ghost popping back to life with sparkle effects. Multiple ghosts appearing. Magical revival energy. Bright sparks. Children crayon drawing animation."

queue_video "scene07a-book" \
  "Glowing magical book floating and pulsing with yellow light. Batman cowering in fear, arms shaking. Dark dramatic scene. Children crayon drawing animation."

queue_video "scene07b-running" \
  "Batman running in panic jumping over picket fences. Cape flowing behind. Fast movement toward distant house. Speed lines. Night sky. Children crayon drawing animation."

queue_video "scene08-happily" \
  "Batman peeking nervously from window. Ghost waving happily outside. Gentle movement. Heartwarming ending. Stars twinkling. Children crayon drawing animation."

queue_video "scene09-sequels" \
  "Three movie poster panels with subtle zoom effects. Characters posing dramatically in each panel. Fun comic energy. Children crayon drawing animation."

queue_video "scene10-sparkles" \
  "Rainbow text MAGIC SPARKLES with floating sparkles and stars. Glitter effects drifting across screen. Magical whimsical energy. Children crayon drawing animation."

queue_video "scene11-nightday" \
  "Half night half day magical forest. Cute sparkle creatures hopping through trees. Leaves swaying gently. Magical glow pulsing. Children crayon drawing animation."

queue_video "scene12-hopping" \
  "Sparkle creatures chasing each other through colorful forest. Bouncing hopping movement. Rainbow trails. Energetic chase scene. Children crayon drawing animation."

queue_video "scene13-ghost" \
  "Ghost popping up scaring sparkle creatures who scatter in all directions. Rain falling from clouds. Sparkles fleeing to tiny house. Children crayon drawing animation."

queue_video "scene14-family" \
  "Parent sparkle creatures looking lovingly at sleeping baby sparkles. Hearts floating upward. Warm golden glow pulsing gently. Cozy peaceful scene. Children crayon drawing animation."

queue_video "scene15-goodnight" \
  "Father tucking blonde daughter into bed. Dream bubbles floating above with tiny sleeping characters. Stars twinkling. Eyes slowly closing. Warm bedtime. Children crayon drawing animation."

queue_video "scene16-credits" \
  "End credits text slowly appearing line by line on black background. Red heart pulsing gently. Subtle crayon texture. Children crayon drawing animation."

echo ""
echo "=== ALL ANIMATIONS QUEUED ==="
echo "Request IDs saved to $VIDEOS/"
ls "$VIDEOS/"*.request_id 2>/dev/null | wc -l
echo "animations queued"
