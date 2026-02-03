# Photo Collage Generator

A simple Python tool that turns a large folder of photos into print-ready 4×6 collages with 4 photos per print. Zero cropping, zero distortion, and full support for iPhone HEIC images. This vibe-coded project exists to make printing large photo collections easy, predictable, and high-quality, without needing Photoshop or manual layout work.

---

## ✨ Why this exists

If you’ve ever tried to print hundreds of photos, you’ve probably run into at least one of these problems:

- Photos get **cropped unexpectedly**
- Portrait photos waste space on landscape prints (or vice versa)
- HEIC photos from phones don’t open correctly
- Printing services want **4×6 @ 300 DPI**, but your files aren’t set up that way
- You don’t want to manually build collages one by one

This script solves all of that by:
- Automatically grouping photos into sets of 4
- Laying them out in a clean 2×2 grid
- Preserving each photo’s **original aspect ratio**
- Rotating photos only when it helps them fit better
- Outputting **print-ready 4×6 images at 300 DPI**

Drop in your photos, run the script, upload the collages to your print service. Done.

---

## 🖼 What it does

- Creates **4×6 inch collages** (landscape orientation)
- Places **4 photos per collage** in a 2×2 grid
- Preserves original aspect ratio (no cropping or stretching)
- Automatically rotates photos to better match the grid orientation
- Supports:
  - `.jpg`
  - `.jpeg`
  - `.png`
  - `.heic`
  - `.heif`
- Outputs one collage per 4 photos

If you have 300 photos, you’ll get ~75 collages.

---

## 🧰 Requirements

- Python 3.8+
- Pillow
- pillow-heif (for HEIC support)

Install dependencies:

```bash
pip install pillow pillow-heif

