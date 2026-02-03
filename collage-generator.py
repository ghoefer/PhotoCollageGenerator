"""
Hello! Create print-ready 4x6 photo collages from a folder of images.

- 4 photos per collage (2x2 grid)
- Preserves original aspect ratio
- Rotates photos only when it helps them fit better
- Supports HEIC images from iPhones
- Outputs 300 DPI, print-ready JPEGs
"""

# PREREQUISITES:
# pip install pillow pillow-heif

from PIL import Image, ImageOps
import pillow_heif
import os
import math

# Enable HEIC / HEIF image support in Pillow
pillow_heif.register_heif_opener()

# ------------------ CONFIG ------------------

# Folder containing original photos
INPUT_DIR = "input_images"

# Folder where collages will be saved
OUTPUT_DIR = "collages"

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

# --------------------------------------------

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load and sort input images
images = [
    os.path.join(INPUT_DIR, f)
    for f in sorted(os.listdir(INPUT_DIR))
    if f.lower().endswith(SUPPORTED_EXTENSIONS)
]

def fit_image(img, target_width, target_height):
    """
    Resize an image to fit within a target box
    while preserving its aspect ratio.
    No cropping, no distortion.
    """
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        # Image is wider than target
        new_width = target_width
        new_height = int(target_width / img_ratio)
    else:
        # Image is taller than target
        new_height = target_height
        new_width = int(target_height * img_ratio)

    return img.resize((new_width, new_height), Image.LANCZOS)

# Calculate size of each grid cell
cell_width = CANVAS_WIDTH // GRID_COLS
cell_height = CANVAS_HEIGHT // GRID_ROWS

# Determine orientation of grid cells
cell_is_landscape = cell_width > cell_height

# Number of collages needed (4 images per collage)
num_collages = math.ceil(len(images) / 4)

for i in range(num_collages):
    # Create a blank white canvas
    collage = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")

    # Get the next batch of 4 images
    batch = images[i * 4:(i + 1) * 4]

    for idx, img_path in enumerate(batch):
        img = Image.open(img_path)

        # Apply EXIF orientation (important for phone photos)
        img = ImageOps.exif_transpose(img)

        # Convert to RGB for consistent output
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Determine image orientation
        img_is_landscape = img.width > img.height

        # Rotate image if its orientation mismatches the cell
        if img_is_landscape != cell_is_landscape:
            img = img.rotate(90, expand=True)

        # Resize image to fit its grid cell
        fitted = fit_image(img, cell_width, cell_height)

        # Calculate grid position
        col = idx % GRID_COLS
        row = idx // GRID_COLS

        # Center the image in its cell
        x = col * cell_width + (cell_width - fitted.width) // 2
        y = row * cell_height + (cell_height - fitted.height) // 2

        collage.paste(fitted, (x, y))

    # Save the collage as a high-quality JPEG
    output_path = os.path.join(OUTPUT_DIR, f"collage_{i+1:03}.jpg")
    collage.save(output_path, "JPEG", quality=95, dpi=(DPI, DPI))

# Debug / confirmation output
print(collage.size)  # Expected: (1800, 1200)
print(f"Created {num_collages} collages.")
