# invert-pdf-colors-cli

The point of this script is to invert all the colors of curves objects images and background of a given pdf while preserving the text, the curves' data, etc.

There are [several tools](https://gist.github.com/douglasmiranda/9c19f23c4570a7b7e02137791880ab43) for pdf conversion to svg for its manipulation, mupdf and inkscape aren't able to draw some images, and pdf2svg converts everything to raster which is not desirable. 

## Usage

If you have a flakes enabled nix installation you can run it with `nix run github:Yeshey/invert-pdf-colors -- input.pdf output.pdf`

Otherwise, please install these packages:
- imagemagick
- inkscape
- pdftk
- poppler_utils 
- python3

And run with `python3 -u py.py input.pdf output.pdf`

> [!WARNING]  
> Confirm all images are present in the final pdf, check [known-issues](#known-issues)
> 
> If it didn't work correctly, the best alternative to my knowledge are online pdf inverters like: https://www.pdfconvertonline.com/invert-pdf/
>
> You can try something like `nix-shell -p ghostscript --command "gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -q -o output.pdf file.pdf"` ([from my techNotes](https://github.com/Yeshey/TechNotes?tab=readme-ov-file#1123-compress)) to compress your pdf if it's too big for the site 🤷

There is also (https://github.com/keotl/invert-pdf) but it converts to raster as well, but allows bigger files.

## Acknowledgements

Script based of of this [ruby script from this answer](https://superuser.com/a/911387).

## Known-Issues

- Some imgs might be missing, this is dependent on inkscape, see [issues](https://github.com/Yeshey/invert-pdf-colors-cli/issues/1#issue-2745659588)
- It substitutes all missing fonts for the closest font, so if there are some fonts missing it might look a bit different, we should add fonts with nix, or maybe add an option to draw missing fonts instead of substituting them.

