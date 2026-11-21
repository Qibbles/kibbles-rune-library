# Kibble's Rune Library (UO Outlands)

**🗺️ Open the map: https://runes.kibs.cc/**

A static, self-hosted rune map for UO Outlands. Works on GitHub Pages as-is.

## Files
- `index.html`: the whole app (Leaflet map, sidebar, search, ClassicUO XML export)
- `data/creatures.json`: creature spawn locations, decoded from [Outlands Butler](https://www.outlandsbutler.com/creaturelibrary)'s creature library (credit to them). Format: `{ n: name, s: [[spot, x, y]] (overworld), ds: [[dungeon level, x, y]] (inside dungeons, aligned to this map), d: [dungeon levels without a placed position] }`
- `data/library.json`: all sets, books and runes. Edit this to add or change runes.
- Extra strip at x 7680+: the lava island from the client's map5 (Inferno Level 2), plus 4 dungeon levels shown as Outlands Butler's level pictures (Shadowspire Cathedral 3, Darkmire Temple 3.5, Ossuary 4, Tidal Tomb 3) because they aren't in the rendered client maps
- `data/dungeon-markers.json`: world moongates, dungeon red/yellow moongates, stairs (with destinations) and labels for the extra areas
- `tiles/{z}/{x}/{y}.png`: map tiles rendered from the Outlands client (zoom 0–5, z5 = 1 px per game tile)

## Editing runes
`data/library.json` has two parts:
- `runes`: `{ "<id>": { "id", "fullName", "location": { "x", "y" } } }`
- `sets`: `[{ "setName", "setType", "totalRunes", "vendorSearchUrl": { "shortUrl" }, "books": [{ "name", "runeIds": [...] }] }]`

To add a rune: add an entry under `runes` with a unique id, then put that id in a book's `runeIds` (order = rune number in the book).

## Re-rendering the map after an Outlands map update
Run `render.py` against the client's `map0.uoo`, then re-cut the tiles (see `uorunes-build` on the PC), or ask Claude to do it.

## Hosting on GitHub Pages
Push this folder to a repo, then Settings → Pages → Deploy from branch → `main` / root.
