# Kibble's Rune Library (UO Outlands)

**🗺️ Open the map: https://runes.kibs.cc/**

A static, self-hosted rune map for UO Outlands. Works on GitHub Pages as-is.

## Files
- `index.html`: the whole app (Leaflet map, sidebar, search, ClassicUO XML export)
- `data/creatures.json`: creature spawn locations, decoded from [Outlands Butler](https://www.outlandsbutler.com/creaturelibrary)'s creature library (credit to them). Format: `{ n: name, s: [[spot, x, y]] (overworld), ds: [[dungeon level, x, y]] (inside dungeons, aligned to this map), d: [dungeon levels without a placed position] }`
- `data/library.json`: all sets, books and runes. Edit this to add or change runes.
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
