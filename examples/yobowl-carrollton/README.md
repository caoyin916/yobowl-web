# Yo Bowl Carrollton — example site

A complete, filled-in example of the template pipeline: a real `config.json`
plus real photos for Yo Bowl Carrollton (Carrollton, TX). Use it as a
reference for what a finished `sites/<slug>/` looks like, and as a checklist
of what's real vs. placeholder for a new restaurant.

To preview it:

```bash
cp -r examples/yobowl-carrollton sites/yobowl-carrollton
python3 build.py --site yobowl-carrollton
cd sites/yobowl-carrollton/dist && python3 -m http.server 8080
# then open http://localhost:8080/
```

## Real photos already wired up

| `media.*` key | File | Provenance | Used on |
|---|---|---|---|
| `ingredients_photo` | `gallery-photo/2.jpg` | Real Yo Bowl Carrollton photo | Home — ingredients feature |
| `instagram_photos[0-5]` | `gallery-photo/1.jpg`, `2.jpg`, `3.jpg` (cycled) | Real Yo Bowl Carrollton photos | Home — Instagram grid |
| Gallery page | `gallery-photo/1.jpg`, `2.jpg`, `3.jpg` (`photos.json`) | Real Yo Bowl Carrollton photos | Gallery |
| `menu_image_1` | `menu-photo/main-menu.webp` | Real Yo Bowl Carrollton menu photo | Menu (main board) |
| `menu_image_2` | `menu-photo/snacks-menu.webp` | Real Yo Bowl Carrollton menu photo | Menu (snacks) |
| `catering_menu` | `menu-photo/main-menu.webp` (reused) | same as above | Catering |
| `location_storefront_image` | `location-photo/where-to-park-storefront.png` | Real Yo Bowl Carrollton storefront/parking photo (1774×887, exact match for this slot) | Location |
| `logo` | `branding-photo/yobowl-logo.png` | Downloaded from the HungerRush/Menufy CDN URL referenced in the original (pre-template) Yo Bowl Carrollton site (clean bowl/chopsticks icon + "Yo!! bowl" wordmark, 600×262, white bg) | Home — hero logo plate |
| `hero_bg` / `og_image` | `branding-photo/yobowl-hero.png` | Same CDN source as above (1920×268 wordmark banner, white bg) — the original site used this same image for both hero and `og:image` | Home/Catering hero background, social previews |

## Still to do before this goes live

- **`media.hero_bg`** — `yobowl-hero.png` is a wide wordmark/branding banner
  (white background, black text), not a food/interior photo. With
  `object-fit: cover` it gets upscaled ~2.4x and center-cropped into the
  640px-tall hero band, so it'll look a bit soft/pixelated. The original site
  used this same image for its hero, so it's consistent with that branding,
  but a real photo of food or the storefront would look sharper if one becomes
  available.
- **`site.web3forms_key`** — still `REPLACE_WITH_YOUR_WEB3FORMS_KEY`; generate
  a real key at web3forms.com for the Location page contact form.
- **`reviews[]`** — the 3 quotes are real customer feedback sourced from
  yo-bowl.res-menu.net and attributed "— Customer review" (not verbatim
  Google reviews). Swap in actual Google review quotes (with permission) if
  available.
- **`catering_menu`** currently reuses the main menu photo — a
  catering-specific flyer/photo would be more accurate if the restaurant has
  one.
- Only 3 unique gallery photos exist total, so they're recycled across the
  ingredients feature, Instagram grid, and gallery. More photo variety would
  reduce repetition on the homepage.
