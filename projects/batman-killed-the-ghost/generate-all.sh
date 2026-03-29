#!/bin/bash
set -e

cd /Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost

FAL_KEY="9bce9a0b-28b1-42e4-97be-c7c0ecd8dc8b:41498985bbc7b896baa1ea1019487fb0"
FRAMES_DIR="frames-v3-vertical"
VIDEOS_DIR="videos-v3-vertical"

STYLE="Very messy crayon scribble drawn by a 3 year old toddler on white paper. Thick waxy crayon texture. Wobbly uneven lines, coloring outside the lines, imperfect naive childlike drawing. Like actual kids art on a refrigerator. Not professional. Real toddler scribble quality. Vertical portrait composition."

# Scene names
SCENES=(
  "scene01-title"
  "scene02-bedtime"
  "scene03-darknight"
  "scene04-rooftop"
  "scene05-lookup"
  "scene06-ghostalive"
  "scene07a-book"
  "scene07b-running"
  "scene08-happily"
  "scene09-sequels"
  "scene10-sparkles"
  "scene11-nightday"
  "scene12-hopping"
  "scene13-ghost"
  "scene14-family"
  "scene15-goodnight"
  "scene16-credits"
)

# Scene prompts (subject only)
PROMPTS=(
  "Title card on black paper. BATMAN KILLED THE GHOST in scratchy crayon. By Avie age 3. Tiny Batman and ghost drawings."
  "A bedroom. Little blonde girl in bed telling story excitedly. Dad listening. Warm lamp."
  "Dark spooky city at night. Black buildings yellow windows. Purple sky yellow moon and stars."
  "Batman with pointy ears and Spider-Man in red blue on house roof at night. White ghost between them. Person sleeping below."
  "Person in bed looking up surprised. Batman Spider-Man and ghost peer down through ceiling. Stars."
  "White ghost coming back to life with sparkles. More ghosts appearing. Magical revival."
  "Glowing yellow book with scary grin floating in dark. Batman scared arms up."
  "Batman running scared over picket fences at night. Cape flying. Speed lines."
  "Batman peeking from window nervously. Ghost waving outside. They happily lived ever again with red heart."
  "Three stacked movie posters. Ghost over Batman. Batman over ghost. Spider-Man over Batman."
  "MAGIC SPARKLES in rainbow crayon. Stars hearts sparkles everywhere."
  "Magical forest half night half day. Sparkle creatures hopping through trees."
  "Sparkle creatures chasing each other. Bouncing hopping. Rainbow trails."
  "Ghost scaring sparkle creatures. Rain falling. Sparkles running to tiny house."
  "Inside sparkle house. Baby sparkles in beds. Parent sparkles watching lovingly. Hearts."
  "Father tucking blonde daughter into bed. Dream bubbles with tiny characters above."
  "Credits on black paper. Written and Directed by Avie Abell. Produced by Dad. Red heart."
)

# Motion prompts for Kling
MOTION_PROMPTS=(
  "Title text appearing with sparkle effects. Crayon animation."
  "Girl telling story excitedly in bed. Dad listening. Warm lamplight. Crayon animation."
  "Stars twinkling, moon glowing, windows flickering. Spooky atmosphere. Crayon animation."
  "Batman and Spider-Man celebrating on roof. Capes blowing. Ghost floating. Crayon animation."
  "Person looking up surprised at heroes through ceiling. Crayon animation."
  "Ghost popping to life with sparkles. More ghosts appearing. Crayon animation."
  "Glowing book pulsing with light. Batman cowering. Dark dramatic. Crayon animation."
  "Batman running scared over fences. Cape flying. Speed lines. Crayon animation."
  "Batman peeking nervously from window. Ghost waving happily. Crayon animation."
  "Movie poster panels with subtle zoom effects. Crayon animation."
  "Rainbow sparkle text with floating stars and glitter. Crayon animation."
  "Half night half day forest. Sparkle creatures hopping. Magical glow. Crayon animation."
  "Sparkle creatures bouncing through forest chase. Rainbow trails. Crayon animation."
  "Ghost scaring sparkles who scatter. Rain falling. Crayon animation."
  "Parent sparkles watching sleeping babies. Hearts floating. Warm glow. Crayon animation."
  "Father tucking daughter in. Dream bubbles floating. Eyes closing. Crayon animation."
  "Credits appearing line by line. Heart pulsing. Crayon animation."
)

echo "=== STEP 1: Generating 17 illustrations with Flux ==="

for i in "${!SCENES[@]}"; do
  SCENE="${SCENES[$i]}"
  PROMPT="${PROMPTS[$i]} ${STYLE}"
  
  if [ -f "${FRAMES_DIR}/${SCENE}.url" ]; then
    echo "[$SCENE] Already exists, skipping..."
    continue
  fi
  
  echo "[$SCENE] Generating illustration..."
  
  RESPONSE=$(curl -s -X POST "https://fal.run/fal-ai/flux/dev" \
    -H "Authorization: Key ${FAL_KEY}" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg prompt "$PROMPT" '{prompt: $prompt, image_size: "portrait_16_9", num_images: 1}')")
  
  IMAGE_URL=$(echo "$RESPONSE" | jq -r '.images[0].url // empty')
  
  if [ -z "$IMAGE_URL" ]; then
    echo "[$SCENE] ERROR: No image URL in response"
    echo "$RESPONSE" > "${FRAMES_DIR}/${SCENE}.error"
    continue
  fi
  
  echo "$IMAGE_URL" > "${FRAMES_DIR}/${SCENE}.url"
  curl -s -o "${FRAMES_DIR}/${SCENE}.jpg" "$IMAGE_URL"
  echo "[$SCENE] Done: $IMAGE_URL"
  
  # Small delay to avoid rate limits
  sleep 1
done

echo ""
echo "=== STEP 2: Queueing Kling animations ==="

for i in "${!SCENES[@]}"; do
  SCENE="${SCENES[$i]}"
  MOTION="${MOTION_PROMPTS[$i]}"
  
  if [ -f "${VIDEOS_DIR}/${SCENE}.request_id" ]; then
    echo "[$SCENE] Animation already queued, skipping..."
    continue
  fi
  
  URL_FILE="${FRAMES_DIR}/${SCENE}.url"
  if [ ! -f "$URL_FILE" ]; then
    echo "[$SCENE] No image URL file, skipping..."
    continue
  fi
  
  IMAGE_URL=$(cat "$URL_FILE")
  
  echo "[$SCENE] Queueing animation..."
  
  RESPONSE=$(curl -s -X POST "https://queue.fal.run/fal-ai/kling-video/v1.6/standard/image-to-video" \
    -H "Authorization: Key ${FAL_KEY}" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg prompt "$MOTION" --arg image_url "$IMAGE_URL" '{prompt: $prompt, image_url: $image_url, duration: "5", aspect_ratio: "9:16"}')")
  
  REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id // empty')
  
  if [ -z "$REQUEST_ID" ]; then
    echo "[$SCENE] ERROR: No request_id"
    echo "$RESPONSE" > "${VIDEOS_DIR}/${SCENE}.error"
    continue
  fi
  
  echo "$REQUEST_ID" > "${VIDEOS_DIR}/${SCENE}.request_id"
  echo "[$SCENE] Queued: $REQUEST_ID"
  
  sleep 1
done

echo ""
echo "=== STEP 3: Polling for Kling completions ==="

MAX_WAIT=1800  # 30 minutes
POLL_INTERVAL=20
START_TIME=$(date +%s)

while true; do
  ALL_DONE=true
  PENDING=0
  COMPLETED=0
  FAILED=0
  
  for i in "${!SCENES[@]}"; do
    SCENE="${SCENES[$i]}"
    
    # Already downloaded
    if [ -f "${VIDEOS_DIR}/${SCENE}.mp4" ]; then
      COMPLETED=$((COMPLETED + 1))
      continue
    fi
    
    # No request ID
    if [ ! -f "${VIDEOS_DIR}/${SCENE}.request_id" ]; then
      FAILED=$((FAILED + 1))
      continue
    fi
    
    REQUEST_ID=$(cat "${VIDEOS_DIR}/${SCENE}.request_id")
    
    # Check status
    STATUS_RESPONSE=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/${REQUEST_ID}/status" \
      -H "Authorization: Key ${FAL_KEY}")
    
    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // empty')
    
    if [ "$STATUS" = "COMPLETED" ]; then
      echo "[$SCENE] COMPLETED - downloading..."
      
      RESULT=$(curl -s "https://queue.fal.run/fal-ai/kling-video/requests/${REQUEST_ID}" \
        -H "Authorization: Key ${FAL_KEY}")
      
      VIDEO_URL=$(echo "$RESULT" | jq -r '.video.url // empty')
      
      if [ -n "$VIDEO_URL" ]; then
        curl -s -o "${VIDEOS_DIR}/${SCENE}.mp4" "$VIDEO_URL"
        echo "[$SCENE] Downloaded!"
        COMPLETED=$((COMPLETED + 1))
      else
        echo "[$SCENE] ERROR: No video URL in result"
        echo "$RESULT" > "${VIDEOS_DIR}/${SCENE}.result_error"
        FAILED=$((FAILED + 1))
      fi
    elif [ "$STATUS" = "FAILED" ]; then
      echo "[$SCENE] FAILED"
      echo "$STATUS_RESPONSE" > "${VIDEOS_DIR}/${SCENE}.status_error"
      FAILED=$((FAILED + 1))
    else
      ALL_DONE=false
      PENDING=$((PENDING + 1))
    fi
  done
  
  ELAPSED=$(( $(date +%s) - START_TIME ))
  echo "[Poll] Completed: $COMPLETED | Pending: $PENDING | Failed: $FAILED | Elapsed: ${ELAPSED}s"
  
  if $ALL_DONE; then
    echo "All animations resolved!"
    break
  fi
  
  if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo "TIMEOUT after ${MAX_WAIT}s"
    break
  fi
  
  sleep $POLL_INTERVAL
done

echo ""
echo "=== Generation complete ==="
echo "Frames in: ${FRAMES_DIR}/"
echo "Videos in: ${VIDEOS_DIR}/"
ls -la "${FRAMES_DIR}/"
ls -la "${VIDEOS_DIR}/"
