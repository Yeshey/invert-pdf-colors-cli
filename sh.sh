#!/bin/bash

input_svg="input_0003.svg"

# First, list all IDs and filter for images more carefully
image_ids=$(inkscape --query-all "$input_svg" | grep -i "image" | awk '{print $1}')

# Check if any image IDs were found
if [ -z "$image_ids" ]; then
    echo "No image IDs found in the SVG"
    exit 1
fi

# Debug: print found image IDs
echo "Found image IDs: $image_ids"
