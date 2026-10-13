# Open Day English | Kindergarten demo lesson

**Let's Go to the Zoo!** A 23-minute (25 maximum) interactive English lesson for 12 kindergarten children: 4 Lower KG (age 4) and 8 Upper KG (age 4 to 5). Built to be picked up and delivered by the Grade 1 and 2 homeroom teacher with no planning: the slides sequence the lesson, a grey "Teacher:" line at the foot of every slide says what to do next, the speaker notes carry the full script, and the two-page run card is the only thing to read beforehand.

## Files

| File | What it is | Print |
|---|---|---|
| `Lets_Go_To_The_Zoo_Slides.pptx` | The screen presentation, 24 slides, speaker notes on every slide | Open full screen on the classroom display |
| `Lets_Go_To_The_Zoo_Slides.pdf` | The same deck as a PDF, in case the classroom machine has no PowerPoint | |
| `printables/Teacher_Run_Card.pdf` | Two pages: minute-by-minute run sheet, what to set up, the three chants in full, the six animals with action and sound, Lower KG vs Upper KG expectations, management tips | 1 copy, A4 |
| `printables/Flashcards_A4.pdf` | Six A4 picture cards (elephant, kangaroo, monkey, penguin, snake, polar bear) | 1 set, A4 landscape, colour, laminate if possible |
| `printables/Mini_Cards.pdf` | Small cards for the Stand up game, 6 per page | Print pages 1 and 2 (12 cards, 2 of each animal). Page 3 is spare. Cut along the dashed lines |
| `printables/English_Star_Badges.pdf` | 12 round "English Star" badges for the end of the lesson | 1 sheet, A4, on sticker paper or plain paper plus tape |
| `printables/Take_Home_Sheet.pdf` | Colouring sheet with the six words and a bilingual note for families | 12 copies plus spares, A4 |
| `src/` | Build scripts and artwork, only needed if the lesson is edited (see Rebuilding below) | |

## The lesson at a glance

| Min | Slides | Phase | What happens |
|---|---|---|---|
| 0 to 3 | 1 to 3 | Hello | Hello chant with actions, then pass a soft toy: "What's your name?" |
| 3 to 5 | 4 to 5 | To the zoo | March on the spot, drive the bus, "Shh, listen..." |
| 5 to 11 | 6 to 11 | Meet the animals | One animal per slide: say it loud, quiet and slow, do the action, make the sound. A4 flashcard goes up on the board after each |
| 11 to 14 | 12 to 18 | What's missing? | Eyes closed, click, "What's missing?", click to reveal. Three rounds, all on the slides |
| 14 to 17 | 19 | Zoo chant | "Let's go to the zoo! What can we do? Stomp like an elephant!" All six animals with actions |
| 17 to 21 | 20 | Stand up game | One mini card each. "Elephants, stand up! Stomp!" Swap cards and repeat |
| 21 to 23 | 22 to 23 | Goodbye | Goodbye chant, sticker for every child, take-home sheet for every family |
| Spare | 21, 24 | Teacher says; How many monkeys? | Only if time allows |

**Language.** Six animal words, each paired with an action verb and a sound. Target for every child: join in the actions and say at least one animal word. Target for Upper KG: "It's a monkey!" and "I'm a monkey!"

**Two age groups in one room.** Every activity has a physical response (the Lower KG target) and a spoken response (the Upper KG target), so nobody is waiting and nobody is put on the spot. Lower KG are only ever asked questions as part of the whole group. Upper KG children are asked by name and used as models. The run card spells this out per phase.

**Why these six animals.** They are the six animals, in the same order, of the Super Simple Songs track "Let's Go To The Zoo", so if the school has the song downloaded it drops straight onto slide 19. If not, the chant on the slide does the same job with no audio at all.

## Set-up before the children arrive (10 minutes)

1. Open the slides full screen on slide 1. Test the clicker.
2. 12 carpet spots in a semicircle facing the screen. Parents behind.
3. Six A4 flashcards face down beside the teacher's spot, with tape or Blu Tack to put them on the board.
4. 12 mini cards (2 of each animal) and 12 badges in the teacher's pocket.
5. Take-home sheets by the door.
6. One soft toy or ball for the name game.
7. Optional: if using the song, test the downloaded file through the speakers now.

## Resource sites used and checked

These are the sources the lesson draws on. All links were checked on 13 October 2026. **YouTube does not load at school in China**, so anything video-based must be downloaded in advance or played through the Super Simple app.

- Super Simple Songs, "Let's Go To The Zoo" song page: https://supersimple.com/song/lets-go-to-the-zoo/ . The animal order and actions on slide 19 match this song. The page links free printables (free account needed to download): "Animals Complete Flashcards" https://supersimple.com/free-printables/super-simple-songs-animals-complete-flashcards/ , a lyrics poster https://supersimple.com/free-printables/lets-go-to-the-zoo-lyrics-poster/ , a vocabulary colouring worksheet https://supersimple.com/free-printables/lets-go-to-the-zoo-worksheet-vocabulary-coloring-2/ , and colouring pages for each of the six animals.
- Super Simple Songs, "How to teach Let's Go To The Zoo" (teaching video): https://supersimple.com/how-to-teach-super-simple-songs/how-to-teach-lets-go-to-the-zoo/
- Super Simple Songs, "Hello!" https://supersimple.com/song/hello/ and "Bye Bye Goodbye" https://supersimple.com/song/bye-bye-goodbye/ . The Hello and Goodbye chants in this lesson are original and follow the same action-based pattern, so the teacher needs no audio.
- Super Simple Songs, "Walking In The Jungle": https://supersimple.com/song/walking-in-the-jungle/ . An alternative song with a listen-and-guess structure if the teacher wants a second song for a longer session.
- ESL KidStuff, Zoo animals lesson plan (free PDF): https://www.eslkidstuff.com/lesson-plans/pdf/zoo-animals-lesson-plan-GB.pdf . Source of the Pass the animals, Animals walk and Teacher says games. Their flashcards and song are members-only, which is why this pack includes its own cards.
- Twinkl, Zoo Animals Photo Flashcards: https://www.twinkl.com/resource/t-tp-700-zoo-animals-photo-flashcards . Photographic alternative to the picture cards here if the school has a Twinkl subscription.

**Artwork.** All animal and icon artwork is from the Noto Color Emoji font (Google, open licence), rendered to PNG so it prints and projects identically on any machine. Colouring outlines on the take-home sheet are traced from the same images. School logos are from `design/assets/`.

## Rebuilding

Only needed if the content is changed. From `src/` with Node 18+ and Python 3:

```
npm install pptxgenjs            # once
node render_emoji.js             # regenerates img/*.png from the emoji font (optional)
NODE_PATH=./node_modules node build_deck.js
python3 dedupe_media.py Lets_Go_To_The_Zoo_Slides.pptx ../Lets_Go_To_The_Zoo_Slides.pptx
python3 build_printables.py && node topdf.js   # HTML to PDF via Playwright Chromium
```

`build_deck.js` expects the two school logos copied into `img/` from `design/assets/` and the pptx skill's `apply_theme.js` on the path given at the top of the file.
