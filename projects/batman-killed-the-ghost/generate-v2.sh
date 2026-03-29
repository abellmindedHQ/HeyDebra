#!/bin/bash
# Batman Killed the Ghost v2 - Flux illustrations + Kling animations
# Uses fal.ai API for both Flux (images) and Kling (video)

FAL_KEY="9bce9a0b-28b1-42e4-97be-c7c0ecd8dc8b:41498985bbc7b896baa1ea1019487fb0"
PROJ="/Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost"
FRAMES="$PROJ/frames-v2"
mkdir -p "$FRAMES"

generate_image() {
  local name="$1"
  local prompt="$2"
  echo "Generating: $name"
  
  local result=$(curl -s -X POST "https://fal.run/fal-ai/flux/dev" \
    -H "Authorization: Key $FAL_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"prompt\": \"$prompt\",
      \"image_size\": \"landscape_16_9\",
      \"num_images\": 1
    }")
  
  local url=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('images',[{}])[0].get('url',''))" 2>/dev/null)
  
  if [ -n "$url" ] && [ "$url" != "" ]; then
    curl -s -o "$FRAMES/$name.jpg" "$url"
    echo "  Saved: $FRAMES/$name.jpg ($(ls -lh "$FRAMES/$name.jpg" | awk '{print $5}'))"
    echo "$url" > "$FRAMES/$name.url"
  else
    echo "  FAILED: $result" | head -c 200
  fi
  
  # Small delay to avoid rate limits
  sleep 2
}

echo "=== GENERATING V2 ILLUSTRATIONS WITH FLUX ==="
echo ""

# Scene 1: Title Card
generate_image "scene01-title" \
  "Children's crayon drawing title card on black construction paper. Large scratchy white and yellow crayon text reading BATMAN KILLED THE GHOST. Below in smaller text by Avie Abell age 3. Small wobbly crayon drawing of Batman with pointy bat ears and cape in bottom left corner, simple white sheet ghost with dot eyes in bottom right corner. Childlike adorable storybook aesthetic. Hand drawn feel."

# Scene 2: Bedtime setup
generate_image "scene02-bedtime" \
  "Children's storybook illustration in crayon colored pencil style on cream paper. Cozy bedroom at night with warm golden lamplight. A small 3 year old girl with blonde hair tucked in bed surrounded by stuffed animals, gesturing excitedly telling a story. Her dad sits on the edge of the bed listening with a smile. Wobbly charming crayon lines, bright warm colors, bedtime story atmosphere."

# Scene 3: Dark night cityscape
generate_image "scene03-darknight" \
  "Children's crayon drawing of a dramatically dark city at night. Thick black crayon buildings with yellow square windows against deep purple blue sky. Wobbly white stars and a big bright yellow moon. Overly dramatic and moody but drawn in adorable childlike crayon style on construction paper. Simple bold shapes."

# Scene 4: Batman and Spider-Man on roof with ghost
generate_image "scene04-rooftop" \
  "Children's crayon drawing. Cute chunky Batman with pointy bat ear cowl, dark cape and yellow bat symbol standing next to cute chunky Spider-Man in red and blue with web pattern on suit. They stand triumphantly on a house rooftop at night with arms raised. A simple defeated white sheet ghost with dot eyes lies flat on the roof. Through a window below someone sleeps with Z above their head. Starry night. Wobbly childlike crayon lines on cream paper, funny and adorable."

# Scene 5: Person looks up and sees them
generate_image "scene05-lookup" \
  "Children's crayon drawing. A confused person in pajamas lying in bed looking up at their ceiling with wide surprised eyes. Through a hole in the roof above, cute crayon Batman with bat ears and Spider-Man with web pattern peer down at them along with a white sheet ghost. Stars visible in night sky behind them. Comic style surprise lines. Wobbly childlike crayon art on cream paper."

# Scene 6: Ghost alive again
generate_image "scene06-ghostalive" \
  "Children's crayon drawing. A cute white sheet ghost with surprised happy dot eyes popping back to life, yellow sparkle effects all around it. Multiple smaller ghosts appearing behind it looking cheerful. Inside a house with knocked over crayon furniture. Dramatic joyful revival. Adorable childlike crayon style, bright colors, wobbly lines on cream paper."

# Scene 7a: Glowing book scares Batman
generate_image "scene07a-book" \
  "Children's crayon drawing. A magical glowing yellow book floating in darkness with a spooky grin face drawn on its cover. Yellow glow lines radiating outward. Cute chunky Batman with pointy bat ear cowl cowering in fear, arms up, eyes huge with shock. Dark purple night background. Childlike crayon art on construction paper, funny and charming."

# Scene 7b: Batman runs away over fences
generate_image "scene07b-running" \
  "Children's crayon drawing. Cute chunky Batman with pointy bat ear cowl and cape running away in panic, jumping over white picket fences. His dark cape flies behind him. Speed motion lines. He runs toward a small house in the distance. Night sky with stars. Childlike crayon style on cream paper, hilarious and adorable. Batman looks genuinely scared."

# Scene 8: Happily lived ever again
generate_image "scene08-happily" \
  "Children's crayon drawing. Split scene. On the left, cute Batman with bat ears peeking nervously out his house window with big worried eyes. On the right, a happy white sheet ghost waving cheerfully outside in moonlight. Below in wobbly childlike handwriting the words they happily lived ever again with a red crayon heart. Night sky with stars. Crayon on cream paper. Heartwarming funny ending."

# Scene 9: Sequel pitches montage
generate_image "scene09-sequels" \
  "Children's crayon drawing movie poster montage. Three panels side by side like movie posters drawn by a child. Panel 1: Ghost standing over fallen Batman titled THE GHOST KILLED BATMAN. Panel 2: Batman over ghost with a gold star sticker titled BATMAN KILLED THE GHOST THE ORIGINAL. Panel 3: Spider-Man standing over Batman titled SPIDER-MAN KILLED BATMAN. Wobbly crayon style, colorful, absurd and funny on construction paper."

# Scene 10: Magic Sparkles title
generate_image "scene10-sparkles" \
  "Children's crayon drawing title card. The words MAGIC SPARKLES written in big rainbow crayon colors with stars hearts and glitter sparkle effects all around. Bright pink purple gold and silver crayon colors. Sparkly magical atmosphere on light blue construction paper. Adorable and whimsical."

# Scene 11: Night day forest
generate_image "scene11-nightday" \
  "Children's crayon drawing of a magical forest where half the sky is nighttime dark blue with stars and moon and half is daytime bright yellow sun. The sky splits diagonally. Cute round sparkle creatures like glowing cotton balls with dot eyes and tiny legs hop through green crayon trees. Everything has a magical glow. Whimsical childlike crayon art on cream paper."

# Scene 12: Sparkles hopping chase
generate_image "scene12-hopping" \
  "Children's crayon drawing. Cute round glowing sparkle creatures chasing other sparkle creatures through a colorful forest. The chasers hop excitedly with bouncing motion lines. The ones being chased look back with wide surprised eyes while running. Bright rainbow trail effects. Energetic funny adorable chase scene. Childlike crayon style with lots of movement on cream paper."

# Scene 13: Ghost scares sparkles, rainy day
generate_image "scene13-ghost" \
  "Children's crayon drawing. The same cute white sheet ghost from earlier popping up and trying to scare round glowing sparkle creatures in a forest. The sparkles scatter hopping away toward a tiny glowing house in the distance. Rain drops falling from gray crayon clouds above. Crossover episode. Childlike crayon art on cream paper, funny and charming."

# Scene 14: Moms and dads happy, bedtime
generate_image "scene14-family" \
  "Children's crayon drawing. Inside a cozy glowing sparkle house, small round sparkle creatures tucked into tiny beds with colorful blankets. Larger parent sparkle creatures one with tiny bow and one with tiny hat look down at them with happy smiles. Red crayon hearts float above. Warm golden glow. The sweetest most wholesome crayon drawing ever. Pure bedtime warmth on cream paper."

# Scene 15: Back to bedroom, good night
generate_image "scene15-goodnight" \
  "Children's crayon drawing. Return to the cozy bedroom. Small 3 year old girl with blonde hair falling asleep in bed, eyes closing, tiny peaceful smile. Her dad tucks her in. Above her head dream bubbles float containing tiny Batman, a ghost, Spider-Man, sparkle creatures, and a glowing book, all peaceful and sleeping too. Stars twinkle. Warmest bedtime moment. Crayon art on cream paper."

# Scene 16: End credits
generate_image "scene16-credits" \
  "Children's crayon end credits on black construction paper. White and yellow crayon text centered. Written and Directed by Avie Abell. Below that Produced by Dad. Below that in smaller text No Batmans were harmed in the making of this film. At the bottom a big red crayon heart and the text they happily lived ever again. Simple charming childlike handwriting."

echo ""
echo "=== ALL ILLUSTRATIONS GENERATED ==="
ls -la "$FRAMES/"
