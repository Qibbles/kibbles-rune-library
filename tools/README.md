# Build tools

Scripts used to build the map and dungeon data. Not needed to run the site.

## Map tiles
- `render.py <map0.uoo>` / `render_any.py <mapN.uoo> <out>`: render a client map file (Outlands `.uoo` format) to a radar-colour image using `radarcol.mul` from the same folder. Format: 18-byte header (block width/height at bytes 10 and 14), 8x8 blocks of 6-byte land cells (tile u16, flags u16, z i16), then a per-block i64 statics offset index, then statics blocks (u32 count + 9-byte entries: cell-delta u8, id u16, hue u16, ?, z i16).
- `extend.py`: builds the extra strip at x 7680+ (map5 lava island + Outlands Butler pictures for levels not present in the client maps) and cuts tiles.

## Dungeon alignment
- `align_final.json`: where each Outlands Butler dungeon-level picture sits on this map (x, y, w, h in map tiles). Dungeon spot positions = x + px*w/imageWidth, y + py*h/imageHeight.
- `match2.py`, `match3.py`, `fit_region.py`, `fit_red.py`, `search_facets.py`: the image-matching used to find those positions (needs `dungeon-maps.json`, a bundle of Butler's level pictures, which can be re-downloaded from outlandsbutler.com).
- `markers_raw.json`: Butler's dungeon markers (entries, exits, red/yellow moongates) in picture coordinates.
- `EXCLUDED.md`: markers removed after in-game checks.
