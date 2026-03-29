#!/bin/bash

FAL_KEY="9bce9a0b-28b1-42e4-97be-c7c0ecd8dc8b:41498985bbc7b896baa1ea1019487fb0"
BASE_URL="https://fal.run/fal-ai/flux/dev"
OUT_DIR="frames-v4"
STYLE="Drawn by a 3 year old child with crayons on white paper. Stick figures with circle heads. Wobbly terrible lines. Colors scribbled outside the lines. Crude naive authentic toddler art. NOT professional. NOT cute storybook. Actual refrigerator art quality. Thick waxy crayon texture. Bad proportions. Simple shapes only."

SUCCESS=0
FAILED=0
FAILED_LIST=""

generate_frame() {
  local frame_num=$1
  local prompt=$2
  local padded=$(printf "%02d" $frame_num)
  local out_file="${OUT_DIR}/frame${padded}.jpg"
  local url_file="${OUT_DIR}/frame${padded}.url"
  
  echo "Generating frame ${padded}..."
  
  local full_prompt="${prompt} ${STYLE}"
  
  local response=$(curl -s -X POST "$BASE_URL" \
    -H "Authorization: Key $FAL_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": $(echo "$full_prompt" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))'), \"image_size\": \"landscape_16_9\", \"num_images\": 1}")
  
  local img_url=$(echo "$response" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data['images'][0]['url'])" 2>/dev/null)
  
  if [ -z "$img_url" ]; then
    echo "ERROR: Frame ${padded} failed. Response: $response"
    FAILED=$((FAILED + 1))
    FAILED_LIST="${FAILED_LIST} frame${padded}"
    return 1
  fi
  
  echo "$img_url" > "$url_file"
  curl -s -o "$out_file" "$img_url"
  
  if [ -f "$out_file" ] && [ -s "$out_file" ]; then
    echo "✓ Frame ${padded} saved ($(du -h "$out_file" | cut -f1))"
    SUCCESS=$((SUCCESS + 1))
  else
    echo "ERROR: Frame ${padded} download failed"
    FAILED=$((FAILED + 1))
    FAILED_LIST="${FAILED_LIST} frame${padded}"
  fi
  
  sleep 2
}

cd /Users/debra/.openclaw/workspace/projects/batman-killed-the-ghost

# Frame 01
generate_frame 1 "Black background with scratchy white and yellow crayon text spelling BATMAN KILLED THE GHOST in big wobbly letters. Below in smaller wobbly letters: by Avie (age 3). Title card. Black paper."

# Frame 02
generate_frame 2 "A giant question mark drawn in crayon filling the whole white page. Nothing else on the page. Big wobbly question mark in brown crayon."

# Frame 03
generate_frame 3 "A tiny stick figure Batman with circle head and two triangle ears on top, standing next to a tiny white blob ghost. The ghost has a big X scribbled over it. Below the drawing in terrible kid handwriting the words: batman kild the gost. White paper background."

# Frame 04
generate_frame 4 "The entire page scribbled over with dark blue and black crayon. Just pure darkness covering everything. Two tiny white dots for eyes peeking out from somewhere in the dark scribbles. Nothing else visible."

# Frame 05
generate_frame 5 "Same dark blue and black crayon scribbled page but now a tiny red scribble appears somewhere. A crooked arrow points to the red scribble with the label spidr man written in kid handwriting next to the arrow. Everything else is dark scribbles."

# Frame 06
generate_frame 6 "Very dark page covered in scribbles. Two stick figures floating in the darkness. One stick figure has triangle ears on its circle head (Batman). The other stick figure is colored red and blue (Spider-Man). They are just standing there in the void. Even more dark scribbling everywhere."

# Frame 07
generate_frame 7 "A house drawn as a simple square with a triangle roof. Batman stick figure (circle head with triangle ears) and Spider-Man stick figure (red and blue) standing on top of the roof but they are WAY too big for the house. Their feet touch the roof but their heads are up in the sky. A white blob ghost with X eyes lies flat on the ground. Yellow dot stars in sky. White paper."

# Frame 08
generate_frame 8 "Same simple square house with triangle roof but now the front wall is see-through transparent like kids draw. Inside the house you can see a stick figure lying in a rectangle bed with a HUGE letter Z floating above them. The stick figure is fast asleep. You can see the feet of Batman and Spider-Man poking through the ceiling from above."

# Frame 09
generate_frame 9 "The sleeping stick figure in the rectangle bed has a giant question mark above their head. A thought bubble shows them dreaming about a scribbled cookie or random scribble shape. White paper background."

# Frame 10
generate_frame 10 "The sleeping stick figure now has HUGE circle eyes wide open looking scared. Looking up at the ceiling. Through the transparent roof Batman, Spider-Man, and a ghost (white blob, now alive again) are all staring down with dot eyes. All characters are crammed together at the top looking down."

# Frame 11
generate_frame 11 "CHAOS inside the house box. All the characters are crammed inside the square house. The rectangle bed is flipped sideways. One stick figure is upside down. Batman is sideways. The ghost is going through a wall. Everything is overlapping. In terrible kid handwriting somewhere: they all floo in."

# Frame 12
generate_frame 12 "The ghost (white blob) is popping back up with a big smiley face. Sparkle scribble lines around it. A word bubble coming from the ghost says IM BAK! The other stick figure characters have big O-shaped surprised mouths."

# Frame 13
generate_frame 13 "Five ghosts of slightly different blob shapes all on the same page. One ghost blob has legs for no reason. One is just a plain circle. One has arms. One is tall. One is fat. They are all different and wrong looking. The ghosts multiplied."

# Frame 14
generate_frame 14 "A yellow rectangle with a creepy grin face drawn on it (dot eyes and jagged grin). Wobbly scribble lines radiating outward from it showing it glows. It floats in dark black space. A crooked arrow points to it with the label scary book in kid handwriting."

# Frame 15
generate_frame 15 "Close up of Batman's face which is just a circle with two triangle ears. His mouth is a GIANT O shape. Eyes are huge circles. Sweat drops drawn around the head. Stick arms raised straight up in the air showing maximum fear. Behind Batman looms the huge yellow glowing scary book rectangle with creepy face."

# Frame 16
generate_frame 16 "Wide panoramic scene. Batman stick figure is SPRINTING from left to right with speed lines behind him. He is jumping over tiny fence posts (vertical lines with horizontal bars). His cape scribble streams behind. In the far distance a tiny house labeled batmans hous in kid writing. On the left side the ghost waves goodbye and the scary book waves goodbye."

# Frame 17
generate_frame 17 "Batman stick figure is inside his house. The door is shut with a big circle lock and keyhole drawn on it. Batman peeks through a tiny square window cut in the wall with just his terrified dot eyes showing. Outside the house the ghost stands there happily waving with a big curved smile."

# Frame 18
generate_frame 18 "Big wobbly crayon text in the center of the white page spelling THE END in large uneven letters. The words are crossed out with a different color crayon scribbled over them."

# Frame 19
generate_frame 19 "Same wobbly crayon text THE END with the cross-out scribble on it but now a big question mark has been added next to the words in a different color crayon. Like someone came back and edited it."

# Frame 20
generate_frame 20 "Batman stick figure is inside his house with terrified peeking dot eyes through the tiny square window. The ghost stands outside waving with a big happy smile. Below the whole scene in wobbly kid writing: they hapily livd ever agen. A big red crayon heart drawn below that. Sweet and simple. Lots of white space."

# Frame 21
generate_frame 21 "A small blonde stick figure girl (Avie) with arms on her hips in a confident proud pose. She has yellow scribble hair. A thought bubble above her head contains three tiny scribbled rectangles inside (movie posters). She looks very satisfied with herself."

# Frame 22
generate_frame 22 "The ghost (white blob) standing triumphant with arms raised. Below the ghost lies a fallen Batman stick figure flat on the ground with X eyes. The ghost has arms now for flexing. Scrawled title text above: THE GOST KILD BATMAN. Quick sketchy looking."

# Frame 23
generate_frame 23 "Batman stick figure standing triumphant over a fallen ghost (white blob) lying flat. Batman looks proud. A gold star sticker shape drawn next to the scene. Quick sketchy looking. Same basic layout as a previous scene."

# Frame 24
generate_frame 24 "Spider-Man (red and blue stick figure) standing triumphant over a fallen Batman stick figure lying flat with X eyes. Batman has X eyes. Spider-Man looks victorious. Quick sketchy looking. Batman is having a terrible day."

# Frame 25
generate_frame 25 "All three fallen stick figures lying in a pile together: Batman, ghost, and Spider-Man all piled on top of each other with X eyes. It is a tiny battlefield of stick figure carnage. To the side stands a taller stick figure dad with a concerned worried expression and O shaped mouth looking at the pile."

# Frame 26
generate_frame 26 "Avie stick figure shrugging with arms out to the sides. A thought bubble above her head has stick figures fighting in it but a big X is crossed over the thought bubble. A NEW thought bubble next to it shows sparkles and stars and hearts with no fighting."

# Frame 27
generate_frame 27 "Title card on white paper. The words MAGIC SPARKLES written in rainbow crayon colors with each letter a different color and very wobbly. Stars and hearts drawn everywhere around the words. Pure sparkle chaos energy."

# Frame 28
generate_frame 28 "Two stick figures standing together. Dad stick figure is taller with a plain circle head and raised eyebrow lines on his forehead looking interested. Avie stick figure is shorter with yellow scribble hair and action lines radiating from around her mouth like she is clearing her throat preparing to talk."

# Frame 29
generate_frame 29 "The page split diagonally by a wobbly line. One half is colored solid black crayon (night side). The other half is colored solid yellow crayon (day side). A circle sun is drawn on the yellow day side. A circle moon and tiny dot stars are drawn on the black night side. Both sun and moon visible at the same time."

# Frame 30
generate_frame 30 "Same diagonal split page with black night side and yellow day side. But now EVERYTHING has yellow scribble lines radiating off it. The stick trees glow. The ground glows. The grass scribbles glow. Yellow radiating lines coming off everything. Overwhelming glow everywhere. Over the top."

# Frame 31
generate_frame 31 "Little circle creatures (sparkles) with dot eyes and two stick legs each hopping through scribble trees (green vertical scribble lines). The circles have no arms. Just circles with two stick legs and dot eyes. Bouncy arc dotted lines show their hopping paths. They look like bouncing balls with faces."

# Frame 32
generate_frame 32 "Sparkle chase scene. Circle sparkle creatures running with speed lines behind them at the front. Other circle sparkles chasing them from behind with angry dot eyebrows. Every circle is a slightly different size. The forest around them is just green vertical scribble lines for trees."

# Frame 33
generate_frame 33 "Circle sparkle creatures running away and looking back with terrified wide dot eyes. One sparkle circle has its stick legs tangled together tripping. Another sparkle is hiding behind a tree scribble but its round body sticks out obviously. A third sparkle circle is running in the completely wrong direction away from the others."

# Frame 34
generate_frame 34 "THE GHOST from the first story (white blob with dot eyes and a big smile) pops up from behind a tree scribble. A word bubble from the ghost says BOO! The circle sparkle creatures scatter in every direction with arrows drawn showing which way each one flew. Complete chaos."

# Frame 35
generate_frame 35 "Circle sparkle creatures running toward a tiny simple house. The house has a small sign on it that says sparkl hous in kid handwriting. Behind the fleeing sparkles the ghost watches them go with a happy expression. The sparkles are fleeing to safety."

# Frame 36
generate_frame 36 "Rain falling. Grey cloud scribbles at the top of the page. Blue rain scribble lines falling down from the clouds. Everything below is wet looking. Simple. That is it. Just rain. A deadpan rainy day drawing."

# Frame 37
generate_frame 37 "Inside the sparkle house shown with see-through transparent walls. Little circle sparkle creatures lying in small rectangle beds with blanket scribbles over them. Two bigger circles stand nearby. The bigger mom circle has a bow drawn on top. The bigger dad circle has a hat. Both have HUGE curved smiles. Hearts floating everywhere in the air above them all."

# Frame 38
generate_frame 38 "Crayon text in the center of white page: THE END (for reel this time) written in wobbly uneven letters. A gold star sticker shape drawn on the paper. This looks different from the previous THE END to show this story actually finished."

# Frame 39
generate_frame 39 "A stick figure dad with a big thumbs up gesture. His arm is extended pointing the thumb up. A thought bubble above his head contains a thumbs up emoji drawn in crayon style. Simple scene on white paper."

# Frame 40
generate_frame 40 "Avie stick figure lying in a rectangle bed with arms crossed on her chest like a boss. She has a satisfied closed-eye smile on her circle face. Yellow scribble hair. She is very pleased with herself. Pure confidence."

# Frame 41
generate_frame 41 "Avie stick figure is asleep in bed with peaceful closed line eyes and a tiny smile. Dad stick figure is tiptoeing away on stick tiptoe feet. Above Avie's head floats a big cloud dream bubble. Inside the dream cloud are tiny versions of all the characters: tiny Batman with scared eyes, Ghost with happy smile, Spider-Man, little circle sparkles, and the yellow scary book. Everyone is sleeping peacefully inside the dream cloud. Stars and hearts scattered through the dream cloud. The sweetest scene."

# Frame 42
generate_frame 42 "Black background like a movie credits page. Crayon text in white and yellow: Written and Directed by Avie Abell. Below that: Produced by Dad. Below that: No Batmans were harmd in the making of this film. Below that: they hapily livd ever agen. A red crayon heart at the bottom."

echo ""
echo "============================="
echo "GENERATION COMPLETE"
echo "Success: $SUCCESS"
echo "Failed: $FAILED"
if [ -n "$FAILED_LIST" ]; then
  echo "Failed frames:$FAILED_LIST"
fi
echo "============================="
