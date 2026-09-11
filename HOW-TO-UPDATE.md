# How to update your site

Your site is live at **https://currcw26-a11y.github.io/**

You don't need to know how to code to update it — the easiest way is to open
Claude Code in this `drone-portfolio` folder and just describe what you want
in plain English, like:

> "I added new photos to a folder called `photos/locations/Big Sur` — sort
> them, add a cover photo, and publish the update."

Claude will handle the resizing, privacy-stripping, page-building, and
publishing for you. Below is what's actually happening behind the scenes,
for your own reference.

## Adding photos to a location that already exists

1. Copy (don't move) the new photos into that location's folder, e.g.
   `photos/locations/Oregon Coast/`.
2. Run the photo processor — this resizes them, strips their hidden GPS/
   camera info, and creates the small + large web versions:
   `scripts/process-photos.ps1`
3. Rebuild the site pages: `scripts/generate_site.py`
4. Publish (see "Publishing your changes" below).

## Adding a brand-new location

1. Create a new folder under `photos/locations/` named after the place,
   e.g. `photos/locations/Big Sur/`, and copy the photos into it.
2. Open `locations.txt` and add one new line at the bottom (or wherever
   you want it to appear on the Portfolio page — order follows the file):
   `Big Sur | 2026-08-01 to 2026-08-03 |`
   (Name, then date range, then an optional cover photo filename.)
3. Run `scripts/process-photos.ps1`, then `scripts/generate_site.py`.
4. Publish.

If the new location has fewer than 4 photos, it still gets its own page —
just let Claude know if you'd rather it not appear at all, or want it
merged into an existing location instead.

## Changing a location's cover photo

Open `locations.txt`, find that location's line, and type the exact
filename (e.g. `DJI_0142.JPG`) after the last `|`. Leave it blank to let
the site auto-pick the first photo. Then run `scripts/generate_site.py`
and publish.

## Reordering locations on the Portfolio page

Locations appear in the same order as the lines in `locations.txt` — just
move a line up or down, then rebuild and publish.

## Editing your About text or contact info

Edit `about.txt` directly (it's plain text), then run
`scripts/generate_site.py` and publish.

## Publishing your changes

Once you've rebuilt the pages, three commands push the update live
(Claude will run these for you if you ask):

```
git add -A
git commit -m "Update site"
git push
```

GitHub usually has the live site updated within a minute or two.

## A few things to remember

- Your original, full-resolution photos are never touched or uploaded —
  only compressed, privacy-stripped copies in `photos/web/` get published.
- Deleting a photo from `photos/locations/<name>/` and re-running the two
  scripts above will remove it from the site too.
- If something looks broken after a change, just tell Claude what you're
  seeing — it can check the live site and fix it.
