# Photo Collage Generator

A simple Python tool that turns a folder of photos into print-ready 4x6 collages with 4 photos per print.

Each finished collage is:

- 4x6 inches, landscape
- 300 DPI
- 1800 x 1200 pixels
- A 2x2 grid with 4 equal photo slots
- Fills every slot with no white space
- Rotates portrait photos sideways when that fills the slot better
- Crops from the center when needed
- Saved as a high-quality JPEG

## How to use it with Codex

1. Add or upload the photos you want to use.
2. Tell Codex: "make the collages."
3. Codex will run the generator and show you where the finished collage files are.

The project folders are:

- `input_images` - put your original photos here
- `collages` - finished 4x6 collage images appear here

Supported photo formats:

- `.jpg`
- `.jpeg`
- `.png`
- `.heic`
- `.heif`

On a Mac, HEIC/HEIF files can be converted with the built-in image tools. Installing `pillow-heif` is still recommended for the most direct HEIC support.

If a Live Photo downloads as an MP4/MOV video, ask Codex to extract a still frame first. The generator uses that extracted still image in the collage.

## How it works

The script takes your photos in filename order and groups them in sets of 4. Each group becomes one printable 4x6 image.

For example:

- 4 photos makes 1 collage
- 8 photos makes 2 collages
- 10 photos makes 3 collages, with blank space in the last one

## Setup

Install the image libraries:

```bash
pip install -r requirements.txt
```

## Run it yourself

```bash
python collage-generator.py
```

By default, it reads photos from `input_images` and saves collages to `collages`.

You can also choose different folders:

```bash
python collage-generator.py --input /path/to/photos --output /path/to/collages
```

If you do not want portrait photos rotated sideways, add:

```bash
python collage-generator.py --keep-orientation
```
