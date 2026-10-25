# Ziyue Ma — Personal Homepage

Bilingual academic homepage for Ziyue Ma (马子越), with English as the default language and a dark default theme.

## GitHub Pages

Repository: `abczyxabczyxa/abczyxabczyxa.github.io`

Website: https://abczyxabczyxa.github.io/

The visible site name is `mzy.github.io`; the GitHub Pages address follows the account name.

Publish from the `main` branch and `/ (root)` in Settings → Pages. The generated HTML and assets are committed; `.nojekyll` enables direct static serving.

## Local preview

Run `sh start.sh`, then open http://127.0.0.1:4000/.

## Editing

- `profile.json`: Chinese profile, publications, projects, and shared settings.
- `locales/en.json`: English translations; update both languages when changing translated content.
- `scripts/build.py`: generates `index.html` (English) and `zh.html` (Chinese).
- `assets/css/site.css`: custom styles.
- `assets/js/site.js`: theme switching, language links, and section navigation.

After edits, run `python3 scripts/build.py` and commit the generated pages along with the changed sources.

## Credits

Adapted from the Minimal Mistakes styling used by https://github.com/Chenxxxxxx06/Chenxxxxxx06.github.io. See `LICENSE` and `THIRD_PARTY_NOTICES.md`.
