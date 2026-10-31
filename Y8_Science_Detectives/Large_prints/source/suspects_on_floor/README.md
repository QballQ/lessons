# Winter lab map with suspects (table cover)

Room cropped to the full 119 cm table height; the four suspect cards sit on the empty floor squares D6 to J7 (no lesson refers to these squares). Title, time and key are in the 12 cm strip on the right.

Rebuild:

    python3 build4.py 8.8                      # writes composite4.html (8.8 = card font size)
    node render2.js composite4.html composite4.pdf
    python3 ../../../../design/export_tools/tile_a3.py composite4.pdf tiles.pdf 1190 7

`build.py` holds the suspect data (copied from the Week 1 suspect cards); `map.svg` is the vector scene map.
