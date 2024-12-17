#!/usr/bin/env python3

import os
import sys
import argparse
import shutil
import tempfile
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

# Modify this function to accept arguments and process a page
def process_page_wrapper(args):
    page_file, tmp_dir = args
    return process_page(page_file, tmp_dir)

DEBUG = True

# Globals
pagenumbers = False
colors_file = ""
trim_color = ""
images_file = ""
input_file = ""
output_file = ""
color_rules = {}
color_order = []
image_rules = []

# Parse command-line arguments
def parse_args():
    global pagenumbers, colors_file, trim_color, images_file, input_file, output_file

    parser = argparse.ArgumentParser(
        description="Invert colors in a PDF, including embedded images and optional rules."
    )
    parser.add_argument("-pn", action="store_true", help="Add page numbers")
    parser.add_argument("-c", metavar="<color file>", help="Color rule file")
    parser.add_argument("-i", metavar="<image rule file>", help="Image rule file")
    parser.add_argument("-it", metavar="<color>", help="Trim color (e.g., '#000000')")
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("output", nargs="?", help="Output PDF file")

    args = parser.parse_args()
    pagenumbers = args.pn
    colors_file = args.c or ""
    trim_color = args.it or ""
    images_file = args.i or ""
    input_file = args.input
    output_file = args.output or f"{Path(args.input).stem}_inverted.pdf"

    if not Path(input_file).exists():
        sys.exit(f"Error: Input file '{input_file}' does not exist.")

# Helper: Run shell commands
def run_cmd(command):
    if DEBUG:
        print(f"Running: {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stderr)
        return False
    return True

# Read and process color rules
def load_color_rules():
    if not colors_file:
        return
    if not Path(colors_file).exists():
        print(f"Warning: Color file '{colors_file}' not found. Inverting all colors.")
        return

    with open(colors_file) as f:
        for line in f:
            parts = line.strip().split()
            fuzz, src, dst = int(parts[0]), parts[1][1:], parts[2][1:]
            color_rules[src] = (fuzz, dst)
            color_order.append(src)

# Replace color function
def replace_color(color):
    if colors_file and color in color_rules:
        return color_rules[color][1]
    else:
        inverted = 0xFFFFFF - int(color, 16)
        return f"{inverted:06x}"

# Read and process image rules
def load_image_rules():
    global image_rules
    if not images_file:
        return

    if not Path(images_file).exists():
        print(f"Warning: Image rule file '{images_file}' not found.")
        return

    with open(images_file) as f:
        image_rules = [[int(x) if x.isdigit() else 1 for x in line.split()] for line in f]

# Check if image should be converted
def should_convert_image(page, image):
    if len(image_rules) > page and len(image_rules[page]) > image:
        return image_rules[page][image] != 0
    return True

# Process individual PDF pages
def process_page(page_file, tmp_dir):
    log = f"Processing {page_file}...\n"
    basename = Path(page_file).stem

    # Convert to SVG
    svg_file = tmp_dir / f"{basename}.svg"
    run_cmd(f"unshare --user inkscape {page_file} --export-filename={svg_file} --pdf-font-strategy=substitute --export-plain-svg")
    shutil.copy(svg_file, "/mnt/DataDisk/PersonalFiles/2024/Projects/Programming/invert-pdf-colors/")

    print("ok1")

    with open(svg_file) as f:
        lines = f.readlines()

    print("ok2")

    img_ctr = -1
    for i, line in enumerate(lines):
        # Replace colors
        lines[i] = replace_svg_colors(line)

        # Process images
        if "data:image" in line:
            print("ok4")
            img_ctr += 1
            thing = process_embedded_image(line, img_ctr, tmp_dir, basename)
            print("thing:")
            print(thing)
            lines[i] = thing
            print("ok5")
    print("ok6")

    # Add page numbers
    if pagenumbers:
        lines = add_page_numbers(lines, basename)

    # Write inverted SVG
    inverted_svg = tmp_dir / f"{basename}_inv.svg"
    with open(inverted_svg, "w") as f:
        f.writelines(lines)

    shutil.copy(inverted_svg, "/mnt/DataDisk/PersonalFiles/2024/Projects/Programming/invert-pdf-colors/")

    # Convert back to PDF
    output_pdf = tmp_dir / f"output_{basename}.pdf"
    run_cmd(f"unshare --user inkscape {inverted_svg} --export-filename={output_pdf}")

    return output_pdf

# Replace colors in SVG
def replace_svg_colors(line):
    import re
    return re.sub(r"#([0-9a-fA-F]{6})", lambda m: f"#{replace_color(m.group(1))}", line)

def process_embedded_image(line, img_ctr, tmp_dir, basename):
    import base64
    import re

    # Match embedded base64 images in SVG
    match = re.search(r'data:image/(\w+);base64,([^"]+)', line)
    if not match:
        if DEBUG:
            print(f"No match found in line: {line}")
        return line

    img_type, img_data = match.groups()
    img_file = tmp_dir / f"{basename}_{img_ctr}.{img_type}"
    intermediate_file = tmp_dir / f"{basename}_{img_ctr}_processed.png"

    if DEBUG:
        print(f"Processing image {img_ctr} of type {img_type} from line.")

    # Decode and save the base64 image
    with open(img_file, "wb") as f:
        f.write(base64.b64decode(img_data))

    if DEBUG:
        print(f"Image {img_ctr} saved to {img_file}")

    # Flatten transparency and save to an intermediate file
    #run_cmd(f"magick {img_file} -background white -alpha remove -alpha off PNG32:{intermediate_file}")
    #if DEBUG:
    #    print(f"Flattened transparency for image {img_ctr}")

    # Trim and negate the image, if needed
    if trim_color:
        run_cmd(f"magick {intermediate_file} -bordercolor '{trim_color}' -border 1 -shave 1x1 {intermediate_file}")
        if DEBUG:
            print(f"Trimmed image {img_ctr} with color {trim_color}")

    if should_convert_image(0, img_ctr):
        run_cmd(f"magick {intermediate_file} -channel RGB -negate {intermediate_file}")
        if DEBUG:
            print(f"Negated image {img_ctr}")

    # Re-encode the processed image to base64
    with open(intermediate_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    if DEBUG:
        print(f"Re-encoded image {img_ctr} to base64")

    # Replace the existing line with the correctly formatted xlink:href attribute
    updated_line = re.sub(
        r'data:image/(\w+);base64,([^"]+)',
        f'xlink:href="data:image/{img_type};base64,{encoded}"',
        line
    )

    if DEBUG:
        print(f"Updated line for image {img_ctr}: {updated_line.strip()}")

    return updated_line

# Add page numbers
def add_page_numbers(lines, basename):
    for i, line in enumerate(lines):
        if "</svg>" in line:
            lines.insert(i, f'<text x="50%" y="95%" text-anchor="middle" fill="#888888">{basename}</text>\n')
            break
    return lines

def main():
    parse_args()
    load_color_rules()
    load_image_rules()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        shutil.copy(input_file, tmp_dir / "input.pdf")

        # Split PDF into pages
        run_cmd(f"pdftk {tmp_dir}/input.pdf burst output {tmp_dir}/page_%04d.pdf")

        pages = sorted(tmp_dir.glob("page_*.pdf"))
        output_pages = []

        # Prepare arguments for parallel processing
        args_list = [(page, tmp_dir) for page in pages]

        # Use ProcessPoolExecutor without lambda
        with ProcessPoolExecutor() as executor:
            results = executor.map(process_page_wrapper, args_list)
            output_pages.extend(results)

        # Merge pages
        run_cmd(f"pdftk {' '.join(map(str, output_pages))} cat output {output_file}")
        print(f"Done! Output written to {output_file}")

if __name__ == "__main__":
    main()
