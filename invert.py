#!/usr/bin/env python3

import os
import sys
import argparse
import shutil
import tempfile
import subprocess
from pathlib import Path

DEBUG = True

def run_cmd(command):
    if DEBUG:
        print(f"Running: {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stderr)
        return False
    return True

def process_page(page_file, tmp_dir):
    basename = Path(page_file).stem

    # Convert PDF page to SVG
    svg_file = tmp_dir / f"{basename}.svg"
    run_cmd(f"inkscape {page_file} --export-filename={svg_file} --pdf-font-strategy=substitute")

    # Invert the entire SVG
    inverted_svg = tmp_dir / f"{basename}_inverted.svg"
    invert_command = (
        f"inkscape {svg_file} "
        f"--batch-process "
        f"--actions=\"select-all;org.inkscape.effect.filter.Invert.noprefs;export-filename:{inverted_svg};export-do;\" "
        f"--pdf-font-strategy=substitute"
    )
    run_cmd(invert_command)

    # Convert inverted SVG back to PDF
    output_pdf = tmp_dir / f"output_{basename}.pdf"
    run_cmd(f"inkscape {inverted_svg} --export-filename={output_pdf}")

    #output_pdf = tmp_dir / f"output_{basename}.pdf"
    #run_cmd(f"pdftk {inverted_svg} output {output_pdf}")

    return output_pdf

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Invert colors in a PDF")
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("output", nargs="?", help="Output PDF file")
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output or f"{Path(input_file).stem}_inverted.pdf"

    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        shutil.copy(input_file, tmp_dir / "input.pdf")

        # Split PDF into pages
        run_cmd(f"pdftk {tmp_dir}/input.pdf burst output {tmp_dir}/page_%04d.pdf")

        # Find and process pages
        pages = sorted(tmp_dir.glob("page_*.pdf"))
        output_pages = []

        # Process pages sequentially
        for page in pages:
            output_page = process_page(page, tmp_dir)
            output_pages.append(output_page)

        # Merge inverted pages
        run_cmd(f"pdftk {' '.join(map(str, output_pages))} cat output {output_file}")
        print(f"Done! Output written to {output_file}")

if __name__ == "__main__":
    main()