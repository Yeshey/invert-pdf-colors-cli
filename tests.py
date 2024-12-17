#!/usr/bin/env python3

import os
import sys
import argparse
import shutil
import tempfile
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

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


def process_embedded_image(line, img_ctr, tmp_dir, basename):
    import base64
    import re

    match = re.search(r"data:image/(\w+);base64,(.*)", line)
    if not match:
        if DEBUG:
            print(f"No match found in line: {line}")
        return line

    img_type, img_data = match.groups()
    img_file = tmp_dir / f"{basename}_{img_ctr}.{img_type}"

    if DEBUG:
        print(f"Processing image {img_ctr} of type {img_type} from line: {line}")

    with open(img_file, "wb") as f:
        f.write(base64.b64decode(img_data))

    if DEBUG:
        print(f"Image {img_ctr} saved to {img_file}")

    if trim_color:
        run_cmd(f"magick {img_file} -bordercolor '{trim_color}' -border 1 -shave 1x1 {img_file}")
        if DEBUG:
            print(f"Trimmed image {img_ctr} with color {trim_color}")

    if should_convert_image(0, img_ctr):  # Adjust for page index if needed
        run_cmd(f"magick {img_file} -channel RGB -negate {img_file}")
        if DEBUG:
            print(f"Negated image {img_ctr}")

    with open(img_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    if DEBUG:
        print(f"Re-encoded image {img_ctr} to base64")

    return f'data:image/{img_type};base64,{encoded}'

def process_page(page_file, tmp_dir):
    log = f"Processing {page_file}...\n"
    basename = Path(page_file).stem

    if DEBUG:
        print(log)

    # Convert to SVG
    svg_file = Path(tmp_dir) / f"{basename}.svg"
    run_cmd(f"unshare --user inkscape {page_file} --export-filename={svg_file} --pdf-font-strategy=substitute")

    if DEBUG:
        print(f"Converted {page_file} to {svg_file}")

    with open(svg_file) as f:
        lines = f.readlines()

    img_ctr = -1
    for i, line in enumerate(lines):
        # Replace colors
        lines[i] = replace_svg_colors(line)

        # Process images
        if "data:image" in line:
            img_ctr += 1
            lines[i] = process_embedded_image(line, img_ctr, Path(tmp_dir), basename)

def run_cmd(cmd):
    subprocess.run(cmd, shell=True, check=True)

# Replace colors in SVG
def replace_svg_colors(line):
    import re
    return re.sub(r"#([0-9a-fA-F]{6})", lambda m: f"#{replace_color(m.group(1))}", line)

# Replace color function
def replace_color(color):
    if colors_file and color in color_rules:
        return color_rules[color][1]
    else:
        inverted = 0xFFFFFF - int(color, 16)
        return f"{inverted:06x}"

# Check if image should be converted
def should_convert_image(page, image):
    if len(image_rules) > page and len(image_rules[page]) > image:
        return image_rules[page][image] != 0
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

load_color_rules()
load_image_rules()

trim_color = "white"  # Example trim color

process_page("/mnt/DataDisk/PersonalFiles/2024/Projects/Programming/invert-pdf-colors/myDear.pdf", "/tmp/")
