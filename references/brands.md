# Brand configuration

The template ships with a generic teal palette and IBM Plex Sans Arabic (400 and 700), licensed under the SIL Open Font License. Font files and their license are in `assets/fonts/`.

Replace `BRAND` in your copied builder with assets you own or may use. Font paths may be absolute or relative to the working directory. Provide the weights you need; missing font files fail rather than silently falling back. The demo synthesizes other weights from 400/700.

Optional `logo_on_dark`, `mark_svg`, and `cover_art_svg` accept local paths or `None`. No logo is required. Use `tokens` for CSS variable overrides; keep changes specific to a document in `EXTRA_CSS`.

Example palette: `{'--ink': '#192B31', '--accent': '#286B76', '--accent-hi': '#8FE4E0', '--dark': '#142A30'}`.

Never redistribute client fonts, logos, documents or screenshots without authorization. This public package includes no client assets.
