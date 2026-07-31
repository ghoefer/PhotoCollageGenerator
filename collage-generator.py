"""
Hello! Create print-ready 4x6 photo collages from a folder of images.

- 4 photos per collage (2x2 grid)
- Fills every quarter of the collage
- Rotates photos when that helps them fill the space better
- Crops from the center when needed
- Supports HEIC images from iPhones
- Outputs 300 DPI, print-ready JPEGs
"""

# PREREQUISITES:
# pip install pillow pillow-heif

import argparse
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

try:
    import pillow_heif
except ImportError:
    pillow_heif = None
else:
    # Enable HEIC / HEIF image support in Pillow
    pillow_heif.register_heif_opener()

# ------------------ CONFIG ------------------

# Folder containing original photos
INPUT_DIR = Path("input_images")

# Folder where collages will be saved
OUTPUT_DIR = Path("collages")

# Print resolution (300 DPI = standard photo quality)
DPI = 300

# Canvas size in inches converted to pixels
# 6x4 inches = landscape 4x6 photo
CANVAS_WIDTH = 6 * DPI   # 1800 px
CANVAS_HEIGHT = 4 * DPI  # 1200 px

# Grid layout: 2x2 = 4 photos per collage
GRID_COLS = 2
GRID_ROWS = 2

# Supported image formats
SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".heic", ".heif")
HEIC_EXTENSIONS = (".heic", ".heif")

# --------------------------------------------

def fill_image(img, target_width, target_height):
    """
    Resize and center-crop an image so it fully covers a target box.
    This avoids white space while preserving the image's aspect ratio.
    """
    scale = max(target_width / img.width, target_height / img.height)
    new_width = math.ceil(img.width * scale)
    new_height = math.ceil(img.height * scale)

    resized = img.resize((new_width, new_height), Image.LANCZOS)

    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    return resized.crop((left, top, right, bottom))


def find_images(input_dir):
    if not input_dir.exists():
        return []

    return sorted(
        [
            path
            for path in input_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ],
        key=lambda path: str(path).lower(),
    )


def open_image(img_path, temp_dir):
    if img_path.suffix.lower() not in HEIC_EXTENSIONS or pillow_heif is not None:
        return Image.open(img_path)

    sips_path = shutil.which("sips")
    if sips_path is None:
        raise RuntimeError(
            "HEIC/HEIF photos were found, but HEIC support is not available. "
            "Install the project requirements and try again."
        )

    converted_path = temp_dir / f"{img_path.stem}.jpg"
    try:
        subprocess.run(
            [sips_path, "-s", "format", "jpeg", str(img_path), "--out", str(converted_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Could not convert HEIC photo: {img_path}") from exc

    return Image.open(converted_path)


def build_collages(input_dir, output_dir, rotate_to_fill=True):
    output_dir.mkdir(parents=True, exist_ok=True)
    images = find_images(input_dir)

    if not images:
        print(f"No photos found in: {input_dir.resolve()}")
        print("Add JPG, PNG, HEIC, or HEIF photos there, then run this again.")
        return []

    heic_images = [path for path in images if path.suffix.lower() in HEIC_EXTENSIONS]
    if heic_images and pillow_heif is None:
        print("Using the Mac's built-in image converter for HEIC/HEIF photos.")

    # Calculate size of each grid cell
    cell_width = CANVAS_WIDTH // GRID_COLS
    cell_height = CANVAS_HEIGHT // GRID_ROWS

    # Determine orientation of grid cells
    cell_is_landscape = cell_width > cell_height

    # Number of collages needed (4 images per collage)
    photos_per_collage = GRID_COLS * GRID_ROWS
    num_collages = math.ceil(len(images) / photos_per_collage)
    created_files = []

    with tempfile.TemporaryDirectory(prefix="collage-temp-", dir=output_dir) as temp_dir_name:
        temp_dir = Path(temp_dir_name)

        for i in range(num_collages):
            # Create a blank white canvas
            collage = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")

            # Get the next batch of 4 images
            batch = images[i * photos_per_collage:(i + 1) * photos_per_collage]

            for idx, img_path in enumerate(batch):
                with open_image(img_path, temp_dir) as img:
                    # Apply EXIF orientation (important for phone photos)
                    img = ImageOps.exif_transpose(img)

                    # Convert to RGB for consistent output
                    if img.mode != "RGB":
                        img = img.convert("RGB")

                    # Determine image orientation
                    img_is_landscape = img.width > img.height

                    # Rotate image if its orientation mismatches the cell
                    if rotate_to_fill and img_is_landscape != cell_is_landscape:
                        img = img.rotate(90, expand=True)

                    # Resize and crop image to fill its grid cell
                    fitted = fill_image(img, cell_width, cell_height)

                # Calculate grid position
                col = idx % GRID_COLS
                row = idx // GRID_COLS

                # Center the image in its cell
                x = col * cell_width + (cell_width - fitted.width) // 2
                y = row * cell_height + (cell_height - fitted.height) // 2

                collage.paste(fitted, (x, y))

            # Save the collage as a high-quality JPEG
            output_path = output_dir / f"collage_{i+1:03}.jpg"
            collage.save(output_path, "JPEG", quality=95, dpi=(DPI, DPI))
            created_files.append(output_path)

    return created_files


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create printable 4x6 photo collages with 4 photos each."
    )
    parser.add_argument(
        "--input",
        default=INPUT_DIR,
        type=Path,
        help="Folder containing the photos to collage.",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_DIR,
        type=Path,
        help="Folder where finished collages will be saved.",
    )
    parser.add_argument(
        "--keep-orientation",
        action="store_true",
        help="Do not rotate portrait photos sideways before filling each slot.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    created_files = build_collages(
        args.input,
        args.output,
        rotate_to_fill=not args.keep_orientation,
    )

    if created_files:
        print(f"Created {len(created_files)} collage(s).")
        print(f"Each collage is {CANVAS_WIDTH}x{CANVAS_HEIGHT}px at {DPI} DPI.")
        print(f"Saved to: {args.output.resolve()}")


if __name__ == "__main__":
    main()
