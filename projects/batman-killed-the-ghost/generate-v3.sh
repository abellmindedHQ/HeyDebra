#!/bin/bash
# Batman Killed the Ghost v3 - REAL kid crayon scribble style
FAL_KEY="9bce9a0b-28b1-42e4-97be-c7c0ecd8dc8b:41498985bbc7b896baa1ea1019487fb0"
PROJ="/Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost"
FRAMES="$PROJ/frames-v3"
mkdir -p "$FRAMES"

STYLE="Very messy crayon scribble drawn by a 3 year old toddler on white paper. Thick waxy crayon texture. Wobbly uneven lines, coloring outside the lines, imperfect naive childlike drawing. Like actual kids art on a refrigerator. Not professional. Real toddler scribble quality."

generate_image() {
  local name="$1"
  local subject="$2"
  echo "Generating: $name"
  
  local full_prompt="$subject $STYLE"
  local json_prompt=$(echo "$full_prompt" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")
  
  local result=$(curl -s -X POST "https://fal.run/fal-ai/flux/dev" \
    -H "Authorization: Key $FAL_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"prompt\": $json_prompt,
      \"image_size\": \"landscape_16_9\",
      \"num_images\": 1
    }")
  
  local url=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('images',[{}])[0].get('url',''))" 2>/dev/null)
  
  if [ -n "$url" ] && [ "$url" != "" ]; then
    curl -s -o "$FRAMES/$name.jpg" "$url"
    echo "$url" > "$FRAMES/$name.url"
    local size=$(ls -lh "$FRAMES/$name.jpg" | awk '{print $5}')
    echo "  OK ($size)"
  else
    echo "  FAILED"
  fi
  sleep 2
}

echo "=== V3: REAL KID CRAYON SCRIBBLE STYLE ==="

generate_image "scene01-title" \
  "Title card on black construction paper. Scratchy white and yellow crayon text reading BATMAN KILLED THE GHOST. Below it says by Avie age 3. Small wobbly crayon Batman with pointy ears in one corner and a blobby white ghost in the other corner."

generate_image "scene02-bedtime" \
  "A bedroom at night with a little blonde girl in bed telling a story excitedly. Her dad sits on the bed listening. A lamp glows yellow. Stuffed animals around. Warm cozy bedtime scene."

generate_image "scene03-darknight" \
  "A very dark city at night. Black and purple crayon sky with yellow dot stars and a big yellow circle moon. Tall rectangle buildings with yellow square windows. Spooky dark night."

generate_image "scene04-rooftop" \
  "Batman with pointy triangle ears on his head, a yellow bat shape on his chest, and a black cape. Spider-Man in red and blue with web lines on his suit. They stand on top of a brown house roof at night. A flat white blob ghost with dot eyes lies between them. Through a window below a person sleeps with Z letters. Stars in the sky."

generate_image "scene05-lookup" \
  "A person in bed looking up with huge surprised eyes. Above them through the ceiling Batman with pointy ears and Spider-Man are looking down at them. A white ghost peeks through too. Stars visible above. Surprised face. Funny."

generate_image "scene06-ghostalive" \
  "A white ghost shape coming back to life with yellow sparkle scribbles around it. More little ghosts appearing. Messy happy ghost revival. Inside a house with knocked over furniture. Bright and magical."

generate_image "scene07a-book" \
  "A glowing yellow book floating in the dark with a scary grin face drawn on it. Yellow scribble glow lines around it. Batman with pointy ears is scared, arms up, big scared eyes. Spooky dark purple background."

generate_image "scene07b-running" \
  "Batman with pointy ears and cape running away scared over white picket fences at night. His cape flies behind him. He runs toward a little house. Speed scribble lines behind him. Stars in sky. Funny scared Batman."

generate_image "scene08-happily" \
  "Two scenes side by side. Left: Batman peeking nervously out a window of his house looking scared. Right: a happy white ghost waving outside with a big smile. Below in wobbly kid handwriting it says they happily lived ever again with a red heart. Night sky with stars."

generate_image "scene09-sequels" \
  "Three crayon drawings side by side like movie posters. First one shows a ghost standing over Batman. Second shows Batman standing over a ghost with a gold star. Third shows Spider-Man standing over Batman. Each has a scribbled title. Funny kid movie posters."

generate_image "scene10-sparkles" \
  "The words MAGIC SPARKLES written big in rainbow crayon colors. Stars and hearts and sparkle shapes all around. Pink purple gold silver colors. On light blue paper. Magical and sparkly."

generate_image "scene11-nightday" \
  "A magical forest where half the sky is dark night with stars and half is bright day with a sun. Little round sparkle blob creatures with dot eyes hopping through green scribble trees. A night day. Magical and glowy."

generate_image "scene12-hopping" \
  "Round glowing sparkle blob creatures chasing other sparkle creatures through a forest. They bounce and hop. The ones being chased look back with scared dot eyes. Rainbow scribble trails behind them. Fun chase scene."

generate_image "scene13-ghost" \
  "The same white ghost from earlier popping up to scare little round sparkle creatures in a forest. The sparkles run away toward a tiny house. Rain drops fall from grey crayon cloud scribbles. Funny and cute crossover."

generate_image "scene14-family" \
  "Inside a cozy sparkle house. Little round sparkle creatures tucked into tiny beds. Bigger parent sparkle creatures with a bow and a hat look down at them smiling. Red hearts float above. Warm golden glow. Sweet bedtime."

generate_image "scene15-goodnight" \
  "A cozy bedroom scene. A father tucking in his young blonde daughter who is falling asleep with a smile. Above her head floating dream bubble circles contain tiny drawings of a caped hero, a ghost, sparkle creatures, and a magical book. Stars twinkle. Warm and sleepy."

generate_image "scene16-credits" \
  "End credits on black paper in white and yellow crayon. It says Written and Directed by Avie Abell. Then Produced by Dad. Then No Batmans were harmed in the making of this film. A big red crayon heart at the bottom. And they happily lived ever again."

echo ""
echo "=== V3 ILLUSTRATIONS COMPLETE ==="
ls "$FRAMES/"*.jpg | wc -l
echo "images generated"
