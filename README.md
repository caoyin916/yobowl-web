# Yo Bowl Carrollton — Website

A multi-page replica/redesign of the Yo Bowl Carrollton restaurant site
(Home, Gallery, Location & Hours, Contact, Catering).

---

## How to add photos to the Gallery

The Gallery upload controls are **hidden from the public**. Only you can see
them, after unlocking admin mode.

### Step 1 — Open admin mode
The easiest way: scroll to the very bottom of **any** page and click the small
**"Owner login"** link in the footer. (It's intentionally subtle so customers
don't notice it.)

Alternatively, go to the Gallery page with `#admin` on the end of the URL:

```
Gallery.html#admin
```

(On the live site this is `https://your-domain.com/Gallery.html#admin`.)

### Step 2 — Enter the passcode
A prompt appears. Enter the passcode:

```
yobowl
```

If correct, the upload controls appear. Your browser stays unlocked from then
on, so you won't be asked again on this device.

### Step 3 — Upload your photos
Click **↑ Upload Photos** and select one or more image files from your
computer (you can select several at once), **or** drag-and-drop image files
onto the drop zone that appears.

- Each photo is added to its own full-width row, stacked below the previous
  one, in the order you upload them.
- Photos keep their natural shape (no cropping) — portrait or landscape both
  work.
- A running count ("3 photos") is shown next to the button.

### Removing photos
- **Remove one:** hover over a photo and click the **✕** in its top-right corner.
- **Remove all:** click **Clear all**.

### Hiding the controls again
Click **Lock** to hide the upload controls. The public never sees them; this
just re-locks your own browser. To get back in, repeat Steps 1–2.

---

## ⚠️ Important: two different ways photos get published

There are **two** sets of gallery photos, and they behave very differently:

1. **Photos everyone sees (the real site gallery).** These are actual image
   files stored in the `gallery-photo/` folder and listed in
   `gallery-photo/photos.json`. Every visitor sees these. To publish photos for
   the public, the image files must be added to that folder on the live server
   (your developer/host does this, or ask us to set it up).

2. **Photos only YOU see (the in-browser admin uploads).** When you use the
   hidden **↑ Upload Photos** tool, those photos are saved **only in the
   browser you uploaded them from** — they are a private preview on your own
   laptop/phone and are **NOT visible to the public** and **NOT** on any other
   device. This is useful for previewing how photos will look, but it does not
   publish them to visitors.

**So:** uploading through the admin tool will *not* make a photo appear for
customers. For that, the image file needs to live in `gallery-photo/` on the
live site. Reach out and we can wire up a proper backend so the admin
upload publishes for everyone automatically.

## Notes

- **Where in-browser uploads are stored:** the admin tool saves photos in *your
  browser's* local storage (IndexedDB). They persist across refreshes on the
  same browser and device, but they are **not** uploaded to a public server —
  see the warning above.

- **Changing the passcode:** open `js/gallery.js` and edit this line near the
  bottom:

  ```js
  const ADMIN_PASSCODE = 'yobowl';
  ```

  Replace `'yobowl'` with your chosen passcode and save.

- **Security level:** this gate hides the controls from casual visitors, which
  is the right level for a restaurant gallery. It is not bank-grade security —
  true authentication would live in a backend on the live site.

---

## Files

| File | Purpose |
|------|---------|
| `index.html` | Home page |
| `Gallery.html` | Photo gallery (with hidden admin upload) |
| `Location.html` | Location, hours, map & contact form |
| `Catering.html` | Catering page |
| `css/styles.css` | Shared site styles |
| `js/gallery.js` | Gallery upload, layout & admin logic |
