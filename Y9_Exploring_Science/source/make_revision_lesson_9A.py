"""Generate content_extra/9A_RV1.json: a 40-minute revision lesson for the gap between finishing 9A and Test 1.

The four gap-fill passages are written once, here, with the missing word marked [[like this]]. The same text is
turned into: the worksheet and card questions (blanks), the answer slides (answers in bold) and the answer key.
Edit the passages in this file, run it, then rebuild:  python3 make_revision_lesson_9A.py && python3 build_all.py 9A_RV1

Lessons covered: 9A lessons 1, 2, 6 and 7 (the ones taught). Lesson 3 (probability), 4 (DNA) and 5 (genetic
counselling) are left out. Chinese text comes from the existing lesson files and glossary_cn.json (draft).
The passages avoid the exact scenarios of Test 1 (the moths becoming pale again) so the lesson does not give away answers.
"""
import json, os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'content_extra', '9A_RV1.json')

# ---- key words (header box and vocabulary card): copied from the existing lesson files so wording and Chinese match
WANT = ['environment', 'abiotic factor', 'biotic factor', 'variation', 'inherited variation', 'gene', 'fertilisation',
        'adaptation', 'extinct', 'competition', 'natural selection', 'evolution']
pool = {}
for f in sorted(glob.glob(os.path.join(HERE, 'content', '9A_L0*.json'))):
    for k in json.load(open(f, encoding='utf-8'))['keywords']:
        pool.setdefault(k['en'], k)
keywords = [pool[w] for w in WANT]

# ---- the four passages. [[word]] marks the missing word.
PASSAGES = [
    {'n': 1, 'title': 'Variation and the environment', 'lesson': '9A L1',
     'box': ['abiotic', 'biotic', 'characteristic', 'continuous', 'discontinuous', 'environment', 'environmental', 'species'],
     'lines': [
         'The surroundings of an organism are its [[environment]].',
         'Non-living factors, such as temperature and light, are [[abiotic]] factors.',
         'Disease and predation come from living things, so they are [[biotic]] factors.',
         'A feature of an organism, such as its height, is a [[characteristic]].',
         'A scar is caused by the surroundings, so it is [[environmental]] variation and not inherited.',
         'Height can have any value in a range, so it is [[continuous]] variation.',
         'Blood group has only a few possible values, so it is [[discontinuous]] variation.',
         'A [[species]] is a group that can breed together to produce offspring that can breed.',
     ]},
    {'n': 2, 'title': 'Inherited variation', 'lesson': '9A L2',
     'box': ['fertilisation', 'gametes', 'gene', 'identical', 'inherited', 'normal', 'nucleus', 'zygote'],
     'lines': [
         'Differences passed on from parents to offspring are [[inherited]] variation.',
         'Genetic information is stored in the [[nucleus]] of every cell.',
         'A section of DNA that carries instructions for one characteristic is a [[gene]].',
         'Sperm cells and egg cells are sex cells called [[gametes]].',
         'A male gamete and a female gamete join together at [[fertilisation]].',
         'The fertilised egg cell is called a [[zygote]].',
         'Each gamete carries different genes, so brothers and sisters are not [[identical]].',
         'Grouped continuous data give a bell-shaped chart: a [[normal]] distribution.',
     ]},
    {'n': 3, 'title': 'Adaptation and extinction', 'lesson': '9A L6',
     'box': ['adaptation', 'biodiversity', 'breeding', 'competition', 'endangered', 'extinct', 'genes', 'native'],
     'lines': [
         'A feature that helps an organism survive in its habitat is an [[adaptation]].',
         'Adaptations come from an organism\'s [[genes]], so it cannot change them.',
         'If a species is in danger of dying out, it is [[endangered]].',
         'A species with no living members left is [[extinct]].',
         'Organisms needing the same limited resource, such as food, are in [[competition]].',
         'A species found naturally in a place, such as the UK red squirrel, is [[native]].',
         'The number of different species in an area is its [[biodiversity]].',
         'Nature reserves, [[breeding]] programmes and gene banks protect biodiversity.',
     ]},
    {'n': 4, 'title': 'Natural selection and evolution', 'lesson': '9A L7',
     'box': ['camouflaged', 'evolution', 'generation', 'genes', 'reproduced', 'selection', 'species', 'theory'],
     'lines': [
         'A few peppered moths had [[genes]] that made them black; most were pale.',
         'Soot blackened the trees, so the black moths were better [[camouflaged]].',
         'Birds ate more pale moths, so more black moths survived and [[reproduced]].',
         'They passed on their genes, so the next [[generation]] had more black moths.',
         'The environment selected the helpful variation. This is natural [[selection]].',
         'A change over time in the characteristics of organisms is [[evolution]].',
         'A new [[species]] can form if two populations can no longer breed together.',
         'An idea tested many times and supported by evidence is a scientific [[theory]].',
     ]},
]
# Stretch: no word box, first letter given. Blanks written as  c[[ompetition]]  (the first letter stays printed).
# This is the grey and red squirrel story from 9A lesson 6, not the moths-today scenario that Test 1 asks about.
STRETCH = {
    'title': 'Grey and red squirrels',
    'lines': [
        'Grey squirrels were brought to the UK from the USA in the 1870s.',
        'Greys and reds are in c[[ompetition]] for the same food, such as acorns.',
        'Greys can digest unripe acorns, so they eat the acorns f[[irst]].',
        'Greys carry squirrel pox, which k[[ills]] red squirrels but not greys.',
        'Greys store more fat, so more of them s[[urvive]] a long winter.',
        'So greys are better a[[dapted]] in many woods, and red squirrels have become r[[are]].',
        'Reds still do well in c[[onifer]] forests, because their light bodies suit thin branches.',
        'Which species is better adapted depends on the h[[abitat]].',
    ]}
EXIT = [('Differences between organisms of the same species are called [[variation]].', 'variation'),
        ('Organisms that are better adapted are more likely to [[survive]] and reproduce.', 'survive'),
        ('A change over time in the characteristics of organisms is called [[evolution]].', 'evolution')]
DONOW = ['Two minutes, in your book: write down every 9A key word you can remember.',
         '1. Which key words are about variation and the environment?',
         '2. Which key words are about genes and inheritance?',
         '3. Which key words are about adaptation and extinction?',
         '4. Which key words are about natural selection and evolution?']
CONFIDENCE = ['I can sort abiotic and biotic factors.', 'I can tell continuous from discontinuous variation.',
              'I can explain why brothers and sisters differ.', 'I can say where genetic information is stored.',
              'I can explain how a species becomes extinct.', 'I can name ways of preserving biodiversity.',
              'I can explain natural selection in four steps.', 'I can say what evolution is.']
WATCH = ['variation', 'environment', 'survive', 'reproduce', 'genes', 'generation', 'camouflage', 'natural selection']

BL = re.compile(r'(\w?)\[\[([^\]]+)\]\]')   # an optional printed first letter, then the hidden rest of the word
def blank(s):
    """text with [[answer]]  ->  text with ______  (a first letter written just before [[ stays printed)."""
    return BL.sub(lambda m: m.group(1) + '__________', s)
def bold(s):
    return BL.sub(lambda m: '**' + m.group(1) + m.group(2) + '**', s)
def plain(s):
    return BL.sub(lambda m: m.group(1) + m.group(2), s)
def answers_of(lines):
    return [m.group(1) + m.group(2) for l in lines for m in BL.finditer(l)]

VIDEOS = [
    {'rank': 1, 'title': 'Natural selection (Year 9)', 'source': 'Oak National Academy',
     'url': 'https://www.thenational.academy/pupils/lessons/natural-selection/video',
     'page': 'https://www.thenational.academy/teachers/programmes/science-secondary-ks3/units/adaptations-competition-natural-selection-and-evolution/lessons/natural-selection',
     'length': 'not shown on the page',
     'covers': 'Lesson 6 of Oak\'s Year 9 unit "Adaptations, competition, natural selection and evolution": variation, competition and the fittest surviving, peppered moths, heritable helpful traits becoming more common. KS3 level, narrated.',
     'use': 'This is a whole lesson video, so play only the first explanation, then stop and go to the passages. Open it tonight to choose the stopping point.',
     'licence': 'Open Government Licence v3.0 (Oak). Streamed only: the page offers no video download.'},
    {'rank': 2, 'title': 'Natural selection in peppered moths (Middle school biology)', 'source': 'Khan Academy, on YouTube',
     'url': '', 'page': '', 'length': '3 min 17 s (from a mirror listing)',
     'covers': 'Variation in a moth population, mostly pale moths in 1850s London, dark moths common by 1900, pale moths returning as pollution fell. The same story as Test 1 question 6.',
     'use': 'The best fit for time: a 3-minute clip for the video slot. Search for the title on YouTube or Khan Academy. I could not open the official page from here, so confirm the length and that it plays.',
     'licence': 'Free to watch; not open-licensed.'},
    {'rank': 3, 'title': 'Natural Selection', 'source': 'Amoeba Sisters, on YouTube',
     'url': 'https://dcmp.org/media/13829-the-amoeba-sisters-natural-selection', 'page': '', 'length': '7 min 48 s (DCMP listing)',
     'covers': 'Natural selection explained with antibiotic resistance in bacteria. Cartoon style, US high school level. It does not use the peppered moth, so it suits fast finishers more than the whole class.',
     'use': 'A good second clip for the Challenge group or homework. The link is the captioned-media listing; the video itself is on YouTube.',
     'licence': 'Free to watch; not open-licensed.'},
    {'rank': 4, 'title': 'What is natural selection? and Natural selection leads to evolution', 'source': 'BBC Bitesize KS3 Biology, Inheritance and genetics',
     'url': 'https://www.bbc.co.uk/bitesize/topics/zpffr82', 'page': '', 'length': 'not checked',
     'covers': 'KS3 articles with short videos. A school scheme of work links "What is natural selection?" at bbc.co.uk/bitesize/topics/zpffr82/articles/zc8txbk.',
     'use': 'I could not open bbc.co.uk from here and only saw copies on other sites, so check the titles and lengths yourself.',
     'licence': 'BBC; free to watch in the UK, access elsewhere varies.'},
    {'rank': 5, 'title': 'Gene banks: the Svalbard Global Seed Vault', 'source': 'seedvault.no media page, Vox and Britannica videos',
     'url': 'https://www.seedvault.no/media/', 'page': '', 'length': 'not checked',
     'covers': 'Why seeds are frozen as a back-up, which is the gene bank idea in 9A lesson 6.',
     'use': 'Optional extension for round 3 only. None of these is KS3-specific.', 'licence': 'Various.'},
    {'rank': 6, 'title': 'The Exploring Science book\'s own videos', 'source': 'Pearson ActiveTeach (login needed)',
     'url': '', 'page': '', 'length': 'not checked',
     'covers': 'The book text has video icons on the DNA spread (the Franklin and Wilkins X-ray photo), the Genes and extinction spread (the gene bank paragraph) and the Natural selection spread (hypothesis and theory, and the dinosaurs-to-birds paragraph).',
     'use': 'If your school has ActiveTeach, these are the videos written for this unit. I cannot see behind the login.', 'licence': 'Pearson, school licence.'},
]
ACCESS_NOTE = ('YouTube is normally blocked on school networks in mainland China, and I could not test whether Oak or Khan Academy stream '
               'there. Open your chosen video on the classroom computer tonight. If it will not play, use the next slide, '
               'which tells the same peppered moth story with a diagram, and carry on with the passages.')

def question(p):
    return {'q': f'Gap fill {p["n"]}: {p["title"].lower()}. Complete each sentence with a word from the box. Use each word once.',
            'word_box': p['box'], 'gap_lines': [blank(l) for l in p['lines']]}

lesson = {
    'id': '9A_RV1', 'unit': '9A', 'unit_title': 'Genetics and evolution', 'lesson': 8, 'n_lessons': 7,
    'label': 'Revision lesson before Test 1',
    'title': 'Revision lesson: genetics and evolution', 'title_cn': '复习课：遗传与进化',
    'slug': 'Revision_lesson',
    'book': {'pages': '5 to 9 and 16 to 20', 'spread': '9A lessons 1, 2, 6 and 7'},
    'workbook': {'pages': '3 to 6 and 11 to 14'},
    'oak': [
        {'unit': 'Adaptations, competition, natural selection and evolution, Year 9', 'lesson': 'Natural selection (lesson 6)', 'url': VIDEOS[0]['page']},
        {'unit': 'Adaptations, competition, natural selection and evolution, Year 9', 'lesson': 'Evolution (lesson 8)', 'url': 'https://www.thenational.academy/teachers/programmes/science-secondary-ks3/units/adaptations-competition-natural-selection-and-evolution/lessons/evolution'},
        {'unit': 'Adaptations, competition, natural selection and evolution, Year 9', 'lesson': 'Adaptations (lesson 3)', 'url': 'https://www.thenational.academy/teachers/programmes/science-secondary-ks3/units/adaptations-competition-natural-selection-and-evolution/lessons/adaptations'},
        {'unit': 'Variation (differences within species), Year 8', 'lesson': 'Variation within species', 'url': 'https://www.thenational.academy/teachers/programmes/science-secondary-ks3/units/variation-differences-within-species/lessons/variation-within-species'},
    ],
    'big_idea': 'A revision lesson for the gap between finishing 9A and Test 1: a short video, four gap-fill passages, exam technique and a plan for your own revision.',
    'goals': ['I can use the correct key words to complete passages on variation, inheritance, adaptation and natural selection.',
              'I can say which parts of 9A I am confident about and which I need to revise before Test 1.'],
    'keywords': keywords,
    'cards_stretch': True,   # fast finishers on cards need the Stretch passage too
    'card_flow': ['Do Now: key word brain dump', 'Watch a short video on natural selection', 'Four gap-fill rounds: fill, then check in green pen',
                  'Exam skills and your revision plan', 'Exit ticket'],
    'misconceptions': [
        'Students fill the gaps by matching the first word they see in the box. Read the whole sentence first, then choose.',
        'Organisms change themselves to suit the environment. Natural selection works on inherited variation that is already in the population; the moths did not change colour.',
        'Environmental variation (a scar, a suntan) is passed on. It is not; only genes are inherited.',
        '"Only a theory" means evolution is a guess. A scientific theory has been tested many times and is supported by a great deal of evidence.',
    ],
    'safety': 'None.',
    'equipment': ['Revision cards (A6, four to an A4 sheet) or the A4 worksheet, English or CN version, one per student', 'A green pen for self-marking',
                  'Projector and speakers, with the video opened and tested before the lesson'],
    'tiers': {'core': 'Four gap-fill passages with a word box, one for each 9A lesson taught, then a red, amber, green confidence check.',
              'stretch': 'A gap fill with no word box, first letters given: grey and red squirrels.',
              'challenge': 'Write your own gap fill for a partner to solve.'},
    'timeline': [
        {'phase': 'Do Now', 'min': 4, 'teacher': 'Sets the key word brain dump on the board.', 'students': 'Write the 9A key words they remember, in four groups.', 'resource': 'Slide 2; Quick Review card'},
        {'phase': 'Today', 'min': 1, 'teacher': 'Reads the goals and explains the four rounds.', 'students': 'Listen; get green pens ready.', 'resource': 'Slide 3'},
        {'phase': 'Video', 'min': 6, 'teacher': 'Plays the chosen clip, tested beforehand; uses the diagram slide if it will not play.', 'students': 'Tick the key words they hear; write one new thing.', 'resource': 'Slides 4 and 5; While You Watch card'},
        {'phase': 'Gap-fill rounds 1 to 4', 'min': 12, 'teacher': 'Times each round: 2 minutes to fill, 1 minute to check on the answer slide. Circulates.', 'students': 'Complete a passage, then mark it in green pen. Fast finishers start Stretch.', 'resource': 'Slides 6 to 10; Core cards 1 to 4'},
        {'phase': 'Exam skills', 'min': 2, 'teacher': 'Goes through marks and command words.', 'students': 'Note what earns the marks.', 'resource': 'Slide 11'},
        {'phase': 'Plan your revision', 'min': 4, 'teacher': 'Sets the confidence check; helps students pick two sections to revise.', 'students': 'Colour red, amber or green; circle their two reddest statements; find them in the revision guide.', 'resource': 'Slide 12; Core card 5'},
        {'phase': 'Teach it back', 'min': 3, 'teacher': 'Asks for the peppered moth story in one sentence using five key words.', 'students': 'Tell a partner, then write the key word they most need to practise.', 'resource': 'Slide 13'},
        {'phase': 'Exit ticket', 'min': 3, 'teacher': 'Collects the exit tickets.', 'students': 'Three short gap-fill sentences, no word box.', 'resource': 'Slide 14; Exit Ticket card'},
        {'phase': 'Summary', 'min': 1, 'teacher': 'Points to the revision guide and the Test yourself questions.', 'students': 'Note which sections to revisit.', 'resource': 'Slide 15'},
    ],
    'videos': VIDEOS, 'access_note': ACCESS_NOTE,
    'slides': [], 'worksheet': {}, 'answers': {},
}

# ---------------------------------------------------------------- slides
S = lesson['slides']
S.append({'type': 'title', 'subtitle': 'Revise 9A before Test 1: a video, four gap-fill passages and a plan for your revision', 'image': 'peppered_moth_dark',
          'notes': 'A single revision lesson for the gap between finishing 9A and Test 1. It covers the four 9A lessons taught: 1, 2, 6 and 7. It also works as a cover lesson: the slides carry the instructions and the notes say what to do. Print the cards (A6, four to an A4 sheet) or the A4 worksheet, English or CN version. Open and test the video before the lesson.'})
S.append({'type': 'donow', 'title': 'Do Now: key word brain dump', 'minutes': 4, 'prompt': DONOW,
          'notes': 'Two minutes of silent writing, then a minute to share. Do not reveal the words: the passages that follow do that. Useful words to listen for: environment, abiotic, biotic, variation, gene, gamete, adaptation, extinct, competition, natural selection, evolution.'})
S.append({'type': 'today', 'title': 'Today',
          'notes': 'Read the goals. Explain the rhythm: four rounds, two minutes to fill a passage and one minute to check it in green pen. Remind students to read the whole sentence before they choose a word from the box.'})
S.append({'type': 'video', 'title': 'Watch: how does natural selection work?', 'minutes': 6,
          'heading': 'Natural selection',
          'watch_for': WATCH,
          'instruction': 'Tick each key word when you hear it. Then write one thing you did not know.',
          'links': [{'label': 'Oak National Academy: Natural selection (Year 9)', 'url': VIDEOS[0]['url']},
                    {'label': 'Oak National Academy: Evolution (Year 9)', 'url': 'https://www.thenational.academy/pupils/lessons/evolution/video'}],
          'backup': 'A shorter option: Khan Academy, "Natural selection in peppered moths" (3 min 17 s). Stop it before the end if Test 1 has not been sat.',
          'notes': ACCESS_NOTE + ' VIDEO OPTIONS, best first: (1) Oak National Academy, Natural selection, Year 9: a whole-lesson video, so stop after the first explanation. (2) Khan Academy, Natural selection in peppered moths, 3 min 17 s, on YouTube: the best fit for a short slot, but its last part is about pale moths returning as pollution fell, which is the scenario in Test 1 question 6, so stop it before that if the test has not been sat. (3) Amoeba Sisters, Natural Selection, 7 min 48 s: antibiotic resistance rather than moths, good for fast finishers. (4) BBC Bitesize KS3, Inheritance and genetics. (5) The book\'s own ActiveTeach videos (login needed). I could not play any of these from here, so test the one you choose before the lesson. Full details are in the teacher notes.'})
S.append({'type': 'learn', 'title': 'If the video will not play: the peppered moth in four steps', 'image': 'diagram:natural_selection_moths',
          'vocab': ['variation', 'natural selection', 'reproduce', 'generation'],
          'text': ['Variation: a few moths had genes that made them black.', 'The environment changed: soot made the trees black.',
                   'Birds spotted and ate more pale moths. More black moths survived and reproduced, passing on their genes.',
                   'Each generation had more black moths. The environment "selected" the black variation.'],
          'key_idea': 'Natural selection: the environment selects the inherited variations that survive and are passed on.',
          'notes': 'Use this slide as the video if the clip will not play, or as the recap straight after it. Read the four steps aloud and let students tick the key words on their While You Watch card as they hear them.'})
S.append({'type': 'steps', 'title': 'The four rounds', 'minutes': 12,
          'steps': ['Round 1: variation and the environment. Round 2: inherited variation.', 'Round 3: adaptation and extinction. Round 4: natural selection and evolution.',
                    'Two minutes: read each whole sentence, then fill the gap with a word from the box. Use each word once.',
                    'One minute: check on the screen. Mark in green pen and correct any gap you missed.',
                    'Finished early? Start Stretch (no word box) or Challenge (write your own gap fill).'],
          'footer': 'Read the whole sentence first. The word that fits the meaning is the answer, not the first word in the box.',
          'notes': 'Run the rounds with a visible timer. Between rounds, put up the answer slide. Praise correcting in green pen.'})
for p in PASSAGES:
    S.append({'type': 'answers', 'title': f'Round {p["n"]} answers: {p["title"].lower()}', 'lines': [bold(l) for l in p['lines']],
              'notes': f'Answers: ' + ', '.join(answers_of(p['lines'])) + '. Most common slips: environment and environmental swapped in round 1; genes and gene mixed up in rounds 2 to 4.'})
S.append({'type': 'learn', 'title': 'Before the test: how to earn the marks',
          'text': ['Look at the marks. One mark is one point, so a 2-mark answer needs two points.',
                   'State or Give: a short answer. No reason is needed.',
                   'Describe: say what happens. Explain: say what happens and why, using the word "because".',
                   'Use the key words. Write "genes", "survive" and "reproduce", not "it changed to survive".'],
          'key_idea': 'Read the whole question, circle the command word and check the marks before you write.',
          'notes': 'Two minutes only. The command words are on the CN worksheet with Chinese. Point out that Test 1 questions show the marks in brackets, like [2].'})
S.append({'type': 'steps', 'title': 'Plan your revision', 'minutes': 4,
          'steps': ['On your confidence card, colour each statement: red (not sure), amber (nearly) or green (confident).',
                    'Circle your two reddest statements.',
                    'Find them in the revision guide: section 1 environmental variation, 2 inherited variation, 3 adaptation and extinction, 4 natural selection and evolution.',
                    'At home, do the Test yourself questions for those two sections and mark them with the answers at the back.'],
          'footer': 'Test 1 has biology, chemistry and physics parts. This lesson prepares you for the biology part.',
          'notes': 'Ask students to be honest: red is useful, not a failure. Walk round and ask two students which sections they will revise. Check the revision guide section numbers are right for the version they have.'})
S.append({'type': 'think', 'title': 'Teach it back', 'prompt': 'Tell your partner the peppered moth story in one or two sentences. Use at least five key words.',
          'frames': ['A few moths had ___ that made them black, but most were pale.', 'The environment changed because ___.',
                     'More ___ moths survived and ___, so the next ___ had more of them.', 'This is called natural ___.'],
          'notes': 'Then ask each student to write, in any language, the one key word they most need to practise. Collect two or three to revisit next lesson.'})
S.append({'type': 'exit', 'title': 'Exit ticket', 'minutes': 3, 'questions': [plain(e[0]).replace(e[1], '______') for e in EXIT],
          'instruction': 'On your exit ticket card or worksheet strip. Complete each sentence with no word box. Work alone.',
          'notes': 'Answers: ' + ', '.join(e[1] for e in EXIT) + '.'})
S.append({'type': 'summary', 'title': 'What we revised in 9A', 'next': 'Test 1. Use the revision guide, sections 1 to 4 (biology), and the Test yourself questions.',
          'points': ['Variation can be environmental (not inherited) or inherited (genes from two gametes joining at fertilisation).',
                     'Adaptations come from genes; when the environment changes a species can become endangered or extinct.',
                     'Natural selection: the environment selects the inherited variations that survive and reproduce, generation after generation.',
                     'Evolution is a change over time in the characteristics of organisms, and it can produce new species.'],
          'notes': 'Point students to the revision guide: section 1 (environmental variation), 2 (inherited variation), 3 (adaptation and extinction), 4 (natural selection and evolution).'})

# ---------------------------------------------------------------- worksheet and answers
ws = lesson['worksheet']
ws['core'] = [question(p) for p in PASSAGES]
ws['core'].append({'q': 'Plan your revision. Colour one box for each statement: red (not sure), amber (nearly) or green (confident). Then circle your two reddest statements.',
                   'table': {'headers': ['I can ...', 'Red', 'Amber', 'Green'], 'widths': [5800, 1000, 1000, 1000],
                             'rows': [[c, '', '', ''] for c in CONFIDENCE]}})
ws['stretch'] = [{'q': 'Gap fill 5: ' + STRETCH['title'].lower() + '. There is no word box. The first letter of each missing word is printed.',
                  'gap_lines': [blank(l) for l in STRETCH['lines']]}]
ws['challenge'] = [{'q': 'Write your own gap fill. Write four sentences that explain natural selection for one example (the peppered moth, or another example from 9A). Rub out five key words to make gaps. Write the answers on the back, swap with a partner and solve each other\'s.', 'lines': 5}]
ws['my_thinking'] = 'Which key word do you most need to practise before Test 1? Write it, then write what it means in your own words.'
ws['watch'] = {'title': 'While you watch', 'instruction': 'Tick each key word when you hear it.', 'words': WATCH, 'note': 'One thing the video showed that I did not know:'}
ws['exit'] = [plain(e[0]).replace(e[1], '______') for e in EXIT]
ws['exit_lines'] = [1, 1, 1]
lesson['answers'] = {
    'core': [', '.join(answers_of(p['lines'])) for p in PASSAGES] + ['Any honest colouring. Use it to point each student to the revision guide sections for their two reddest statements: 1 (abiotic and biotic, continuous and discontinuous), 2 (siblings, nucleus), 3 (extinction, biodiversity), 4 (natural selection, evolution).'],
    'stretch': [', '.join(answers_of(STRETCH['lines']))],
    'challenge': ['Any four correct sentences about natural selection with five key words rubbed out. Check that the answers on the back are the words that were removed, and that the sentences describe variation, a change in the environment, survival and reproduction, and the next generation.'],
    'exit': [e[1] for e in EXIT],
    'my_thinking': 'Any key word with a meaning in the student\'s own words. Use the answers to choose what to revisit next lesson.',
}
# full filled passages for the teacher notes
lesson['filled'] = [{'title': f'Round {p["n"]}: {p["title"]}', 'lesson': p['lesson'], 'lines': [bold(l) for l in p['lines']]} for p in PASSAGES] + \
                   [{'title': 'Stretch: ' + STRETCH['title'], 'lesson': '9A L7', 'lines': [bold(l) for l in STRETCH['lines']]}]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(lesson, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
n = sum(len(p['lines']) for p in PASSAGES)
print('wrote', os.path.relpath(OUT, HERE), '| slides', len(S), '| core gaps', n, '| stretch gaps', len(answers_of(STRETCH['lines'])))
