# Synthetic Indian Number Plate Generator

A Python-based tool to generate synthetic Indian vehicle number plates for OCR training. It creates realistic plate images with varying backgrounds, noise, and perspective transformations.

## Features

- **Standard Plates**: Generates standard state-based plates (e.g., `MH 01 AB 1234`).
- **Bharat Series**: Supports the new Bharat Series format (e.g., `21 BH 1234 XX`).
- **Augmentations**: Adds noise, blur, lighting effects, and perspective transforms.
- **Backgrounds**: Superimposes plates onto random background images (or synthetic noise).
- **IND Feature**: simulate High Security Registration Plate (HSRP) features like "IND" text and Chakra.
- **Formats**: Exports annotations in CSV and JSON formats (compatible with typical OCR pipelines).

## Installation

This project uses `uv` for dependency management.

```bash
# Clone the repository
git clone <repo_url>
cd indian_plate_generator

# Install dependencies (or let uv handle it via `uv run`)
uv pip install pillow opencv-python numpy tqdm
```

## Usage

Run the generator using the CLI script:

```bash
# Generate 1000 plates into ./dataset
uv run --with pillow --with opencv-python --with numpy --with tqdm generate_dataset.py --count 1000 --output dataset

# Use custom backgrounds
uv run ... generate_dataset.py --count 5000 --backgrounds /path/to/background_images

# Disable augmentations (clean plates)
uv run ... generate_dataset.py --no-augment
```

## Configuration

You can customize the generator by editing `indian_plate_generator/config.py`:
- **States**: Add or remove state codes.
- **Dimensions**: Change plate aspect ratios.
- **Colors**: Adjust text/background colors.

To use a custom font, place the `.ttf` file in the project directory or update `FONT_SEARCH_PATHS` in `config.py`.

## Output Structure

The output directory will contain:
- `images/`: Contains `train`, `val`, `test` subdirectories with generated images.
- `annotations/`: Contains CSV files for each split and a master `labels.json`.
- `labels.json`: Full dataset metadata.

## Annotation Format (CSV)

```csv
filename,text,code,xmin,ymin,xmax,ymax,width,height
train_000000_MH02AB1234.jpg,MH 02 AB 1234,MH02AB1234,50,120,450,220,500,500
```
