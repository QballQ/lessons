# One-pagers, Years 7 and 8

One A4 page per lesson: the lesson at a glance (big idea, goals, key words, the five phases), the prep for one class with when, minutes and who could do it, and what to print, get and have ready from earlier weeks. `Year_7_One_pagers.pdf` and `Year_8_One_pagers.pdf` hold all ten for each year.

## How they are made

1. `00_Requisition/source/lessons_week_data.json` holds, for every lesson, the full resource list, every prep task and the one-pager content, extracted from the lesson file (lesson plan, kit card, printables), the designed printables, the Teacher Guide prep calendar and the Year 8 Case Bible, then checked independently.
2. `source/one_pager_text.json` is the same content condensed to short lines for the page, checked again against the full data.
3. `python3 source/build_one_pagers.py` lays out each page (brand fonts, series colours), shrinks it slightly if needed so it fits one page, and writes the PDFs. Needs Node with Playwright, curl and pikepdf.

Prep minutes come from the kit cards where they give them; the rest are estimates. If a lesson file changes, update its record in both JSON files and run the builder again.
