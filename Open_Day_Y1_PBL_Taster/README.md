# Open Day | Year 1 international-stream taster lesson

**Fur, Feathers or Scales?** A 24-minute (25 maximum) project-based taster for 12 kindergarten children (4 Lower KG, age 4; 8 Upper KG, age 4 to 5), delivered by the Grade 1 and 2 homeroom teacher at the Open Day. Its purpose is to show parents what a Year 1 classroom in the international stream is like: a real question, hands-on exploration, mixed-age teamwork, a product the children make, every child presenting, and thinking with reasons, all in English.

Zero planning needed: the slides sequence everything, a grey "Teacher:" line at the foot of every slide says what to do next, the speaker notes hold the script, and the two-page run card is the only thing to read beforehand.

## Files

| File | What it is | Print |
|---|---|---|
| `Fur_Feathers_or_Scales_Slides.pptx` | The screen presentation, 17 slides, speaker notes on every slide | Open full screen |
| `Fur_Feathers_or_Scales_Slides.pdf` | Same deck as PDF, in case the classroom machine has no PowerPoint | |
| `printables/Teacher_Run_Card.pdf` | Two pages: set-up, minute-by-minute run sheet, materials list with where to buy, language table, Lower KG vs Upper KG, circulating questions, what to say to parents | 1, A4 |
| `printables/Sorting_Mat_A3.pdf` | The team sorting board: fur, feathers, scales columns | 3, A3 (or A4 if no A3 printer; cards still fit). Laminate if time |
| `printables/Animal_Cards.pdf` | Pages 1 to 3: three identical sets of the 9 animals. Page 4: six extension animals (optional) | 3 or 4 pages, A4, colour. Cut along the dashed lines |
| `printables/Labels_and_Extras.pdf` | Texture labels to tape onto the swatches (3 sets), a mystery bag label, 3 Team Captain labels | 1, A4 |
| `printables/Animal_Scientist_Badges.pdf` | 12 round badges | 1, A4, sticker paper or paper plus tape |
| `printables/Parent_Handout.pdf` | Bilingual, double-sided: side 1 "What you saw today" (the six steps, what was learned, why we teach this way, Year 1 in the international stream); side 2 a ten-minute activity for tonight (sorting hunt, cut and sort) | 12 plus spares, A4 double-sided, colour |
| `src/` | Build scripts and artwork, only needed to edit the lesson | |

## The lesson

| Min | Slides | Phase | What happens |
|---|---|---|---|
| 0 to 1 | 1 to 2 | Hello | Hello chant. "Today we are animal scientists." Three scientist actions: look, feel, talk |
| 1 to 4 | 3 | Mystery bag | Three children feel inside and describe: soft, smooth, bumpy. Reveal fur, a feather, something scaly |
| 4 to 8 | 4 to 7 | Learn | The big question. Fur, feathers, scales: one slide each, swatch passed round, three animals each. "The cat has fur." |
| 8 to 9 | 8 to 9 | Model and rules | Teacher sorts one animal aloud. Four steps: look, feel, talk, stick. Team Captains named |
| 9 to 16 | 10 | Team time | Three mixed teams of four sort nine animal cards onto an A3 board, feeling the swatches, saying the sentence. Teacher circulates with "How does it feel? Fur, feathers or scales? Why?" |
| 16 to 20 | 11 to 12 | Show time and check | Each team presents; every child says one thing. Then the class checks column by column. Disagreements are re-felt and decided by the team |
| 20 to 22 | 13 | Think (optional) | Four new animals sorted by pointing. "Wool is fur." Skip if over time |
| 22 to 24 | 14 to 16 | Finish | Badges, handout to parents, goodbye chant. Slide 16, "What you saw today", stays on screen |

**Two age groups, one task.** Every step has a physical response (the Lower KG target: feel, stick, point, one word) and a spoken response (the Upper KG target: "The duck has feathers. It is soft."). Lower KG children sit beside confident Upper KG children, never beside each other, and are never questioned alone in front of the room. Upper KG children are Team Captains and present full sentences.

**What this shows parents.** Six things, which are also the six tiles on the parent handout and the closing slide: Ask, Explore, Team, Make, Share, Think. The run card gives the teacher three sentences to say to parents afterwards.

## Materials to acquire

All cheap and local. Full detail with search terms on page 2 of the run card.

- **Fur** ×4: faux fur offcut (fabric shop or Taobao), or a fluffy sock, plush toy or fleece glove
- **Feathers** ×4: a bag of craft feathers; tape four or five to a card so they can be stroked
- **Scales** ×4: sequin or snakeskin-print fabric, a pine cone, or a textured plastic crocodile or fish toy
- Mystery bag: any opaque cloth bag or pillowcase
- Per team: a tray and 2 glue sticks (or Blu Tack if the mats are laminated for reuse)

Three of each swatch go to the teams, one of each goes in the mystery bag.

## Before printing: two checks

1. **Stream wording.** The parent handout (side 1, green box) and the run card ("Three things to say to parents") describe Year 1 in the international stream in one sentence: learning in English across subjects through questions, projects and teamwork, alongside daily phonics, reading and maths. Admissions should confirm this matches the school's own wording for the two pathways. The handout deliberately does not characterise the domestic stream; it points parents to the admissions team for that conversation.
2. **Chinese text:** draft, needs a native-speaker check (parent handout, sorting mat, cards, badges, closing slides).

## Sources and background

- Super Simple Songs, "Hello!" https://supersimple.com/song/hello/ and "Bye Bye Goodbye" https://supersimple.com/song/bye-bye-goodbye/ : the Hello and Goodbye chants here are original and follow the same action pattern, so no audio is needed (YouTube does not load at school).
- ESL KidStuff, Zoo animals lesson plan (free PDF): https://www.eslkidstuff.com/lesson-plans/pdf/zoo-animals-lesson-plan-GB.pdf : the hello routine, pass-the-animal and animal-sentence patterns.
- Animals including humans is a Year 1 science topic in the English National Curriculum (identify and classify animals; describe and compare structure). "Fur, feathers or scales" is a standard Year 1 sorting activity in that unit, which is why it was chosen as the taster.
- Artwork: Noto Color Emoji (Google, open licence), rendered to PNG; texture swatches drawn as SVG. School logos from `design/assets/`.

A simpler, non-project alternative (a 23-minute "Let's Go to the Zoo!" vocabulary lesson) is in `Open_Day_KG_English/` as a fallback.

## Rebuilding

From `src/`, Node 18+ and Python 3, after copying the two school logos from `design/assets/` into `img/`:

```
npm install pptxgenjs
node render_emoji.js
NODE_PATH=./node_modules node build_deck.js
python3 dedupe_media.py Fur_Feathers_or_Scales_Slides.pptx ../Fur_Feathers_or_Scales_Slides.pptx
python3 build_printables.py && node topdf.js
```
