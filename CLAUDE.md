# Working notes for this repository

Standing preferences from the teacher who owns these materials:

- **Delivery**: whenever a piece of work produces more than one document, also build a zip of the whole pack and send it. The pack zip is `Y9_Exploring_Science_Biology_9A_9B_9C.zip` in the repository root (gitignored), built with:
  `zip -qr Y9_Exploring_Science_Biology_9A_9B_9C.zip Y9_Exploring_Science -x 'Y9_Exploring_Science/source/images_grey/*' 'Y9_Exploring_Science/source/diagrams_grey/*' '*/__pycache__/*' '*/node_modules/*'`
- **Writing style**: British English. Never use em dashes. Keep prose practical and specific.
- **Chinese text** in any file is a draft that needs a native-speaker check; say so in the README and in any report.
- **Materials**: slides in the school brand; worksheets, cards, guides and tests print in greyscale on A4; exercise-book cards are A6 landscape, four to an A4 sheet. Every lesson or document is built from a content JSON in `Y9_Exploring_Science/source/` (see that folder's README section "Rebuilding"); change the JSON and rebuild rather than editing outputs by hand.
- **Photographs**: open licence only, with the credit line naming the author, licence and source site; the register is `Y9_Exploring_Science/images/Image_Register.md`.
- **Test 1 weighting** (agreed with Albert, November 2026): the 40-minute paper is split by time, 40% biology, 20% chemistry, 40% physics, which is 16, 8 and 16 marks of 40. Keep each part to its marks; about a quarter of each part is Stretch and Challenge, placed as the last question of the part. Physics is not written until its topics are supplied.
- Commit and push to the working branch after each piece of work.
