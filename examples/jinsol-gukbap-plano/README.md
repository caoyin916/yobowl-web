# Jinsol Gukbap (Plano, TX) — dry run

A second worked example of the template pipeline, this time for a **brand-new,
still-"soft-opening" location** with very little public presence yet — a
realistic stress test of how far you can get from research alone vs. what a
human/owner has to supply.

To preview it:

```bash
cp -r examples/jinsol-gukbap-plano sites/jinsol-gukbap-plano
python3 build.py --site jinsol-gukbap-plano
cd sites/jinsol-gukbap-plano/dist && python3 -m http.server 8080
# then open http://localhost:8080/
```

## Where the data came from

- **Brand identity, menu concept, copy** — from
  [jinsolgukbap.net](https://www.jinsolgukbap.net/) (the brand's LA/Buena Park
  site): Busan-style gukbap, 24-hour-simmered pork bone broth, dwaeji/sundae
  gukbap, jjimdak, etc.
- **Address, phone, hours** — from the Google Business Profile for "Jinsol
  Gukbap Plano TX" (4.3★, 6 reviews): 111 W Spring Creek Pkwy Ste #102, Plano,
  TX 75023 — in the Spring Creek Pointe shopping center, near 99 Ranch Market.
- **Instagram** — `@jinsolgukbap.tx` (https://www.instagram.com/jinsolgukbap.tx/),
  the Plano-specific account; its profile picture is the only Plano-specific
  brand asset found.
- **Photos** — real Jinsol Gukbap dish photography from jinsolgukbap.net (the
  LA locations' professional food photos — same brand/menu, not Plano-specific).

## Real photos already wired up

| `media.*` key | File | Provenance | Used on |
|---|---|---|---|
| `hero_bg` / `og_image` | `branding-photo/jinsol-hero.jpg` | Real Jinsol Gukbap pork-soup (dwaeji gukbap) photo from jinsolgukbap.net, resized to 1600×1600 | Home hero background, social previews |
| `logo` | `branding-photo/jinsol-logo.jpg` | Instagram profile picture for `@jinsolgukbap.tx` (the Plano account) — circular "진솔국밥 JINSOL GUKBAP" badge, 100×100 | Home — hero logo plate |
| `ingredients_photo` | `gallery-photo/2.jpg` | Real Jinsol Gukbap dish photo (gold-pot soup) from jinsolgukbap.net | Home — ingredients feature |
| `instagram_photos[0-5]` | `gallery-photo/1–5.jpg` (cycled) | Same 5 real dish photos | Home — Instagram grid |
| Gallery page | `gallery-photo/1–5.jpg` (jjimdak, gold-pot soup, budae-jjigae, suyuk, dwaeji gukbap) | Real Jinsol Gukbap dish photos from jinsolgukbap.net | Gallery |

## Still to do before this goes live

- **`gallery-photo/*` and `branding-photo/jinsol-hero.jpg`** — all sourced from
  Jinsol Gukbap's LA/Buena Park locations (same brand, same menu), not the
  Plano storefront/kitchen. Swap for real Plano photography once the location
  has some.
- **`media.logo`** — the only Plano-specific brand asset is a 100×100
  Instagram profile picture, so it'll look soft at larger sizes. Replace with
  a higher-resolution logo file from the owner.
- **`media.hero_bg` / `og_image`** — `jinsol-hero.jpg` is a square dish photo
  (1600×1600), not landscape, so `object-fit: cover` will center-crop it into
  the wide hero band/social-preview box. It's a real, on-brand food photo, so
  this is a soft-quality tradeoff rather than a placeholder — a landscape
  photo of the Plano dining room or storefront would be an upgrade.
- **`media.menu_image_1` / `menu_image_2`** — still the generic placeholder
  SVGs; need real photos of the Plano menu board/signage.
- **`media.location_storefront_image`** — still the generic placeholder SVG;
  need a real storefront/parking photo of 111 W Spring Creek Pkwy Ste #102.
- **`site.domain` / `site.base_url`** — `jinsolgukbapplano.com` is a made-up
  placeholder domain (not registered); replace once this location has its own
  site/domain.
- **`site.web3forms_key`** — still `REPLACE_WITH_YOUR_WEB3FORMS_KEY`; generate
  a real key at web3forms.com for the Location page contact form.
- **`links.order_online`** — no online-ordering platform was found for this
  location yet, so it currently points at the Google Business listing (which
  itself surfaces "Order pickup"/"Order delivery" buttons). Replace with a
  direct ordering-platform link (Toast/Chowbus/Square/etc.) once one exists.
- **`reviews[]`** — currently 3 brand **press quotes** (Eater LA, LA Weekly,
  Infatuation LA) about Jinsol Gukbap's LA locations, attributed to those
  outlets rather than customers. Swap in real customer reviews from the Plano
  Google Business Profile (4.3★ from 6 reviews as of this writing) once there
  are enough to choose from.
- **`hours.*`** — Google's listing shows Friday as "12 AM–3 PM, 5–9:30 PM",
  which looks like a data-entry typo (likely meant 11 AM, matching the
  Mon–Wed pattern) — verify the real Friday hours with the owner. Also,
  `hours.display`/`schema_opens`/`schema_closes` are a simplified single-block
  summary ("Daily 11AM–9:30PM, closed 3–5PM Mon–Wed & Fri") — this template's
  single-`OpeningHoursSpecification` model can't represent Thursday's later
  close (until midnight) or the day-by-day variation precisely. A per-day
  hours table would be a worthwhile template enhancement for restaurants with
  non-uniform hours.
- **`gallery_admin.passcode`** — currently `"jinsolgukbap"` (matches
  `site_key`, same pattern as the Yo Bowl example); change to something
  private before going live.
- **`restaurant.has_catering`** is `"False"` — no catering program was found
  for this brand, so `Catering.html` and its nav/footer links are dropped
  entirely (a working example of that optional-page flag). Flip to `"True"`
  and add `media.catering_menu` + `pages.catering.*` if this location offers
  catering.
