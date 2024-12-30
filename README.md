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
> Confirm images and formatting in the resulting pdf, check [known-issues](#known-issues)
> 
> If it didn't work correctly, the best alternative to my knowledge are online pdf inverters like: https://www.pdfconvertonline.com/invert-pdf/
>
> You can try something like `nix-shell -p ghostscript --command "gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -q -o output.pdf file.pdf"` ([from my techNotes](https://github.com/Yeshey/TechNotes?tab=readme-ov-file#1123-compress)) to compress your pdf if it's too big for the site 🤷

There is also (https://github.com/keotl/invert-pdf) but it converts to raster as well, but allows bigger files.

## Acknowledgements

Script based of of this [ruby script from this answer](https://superuser.com/a/911387).

## Known-Issues

- All hyperlinks will be lost
- Some fonts might not be found and will be converted to paths (actually most of them seem to not be found), we should add fonts with nix, or maybe add an option to substitute missing fonts instead of drawing them.
- Some imgs might be missing, this is dependent on inkscape, see [issues](https://github.com/Yeshey/invert-pdf-colors-cli/issues/1#issue-2745659588)
- Always adds a white background to make sure there is not a transparent background, we should somehow check if there is an object serving as background already.
