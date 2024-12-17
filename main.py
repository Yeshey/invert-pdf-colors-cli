import subprocess
import os

def invert_pdf(input_pdf: str, output_pdf: str, dpi: int = 150):
    """
    Invert the colors of a PDF using ImageMagick.

    Args:
        input_pdf (str): Path to the input PDF.
        output_pdf (str): Path to save the inverted PDF.
        dpi (int): DPI to use for image conversion. Default is 150.
    """
    try:
        if not os.path.exists(input_pdf):
            raise FileNotFoundError(f"Input PDF '{input_pdf}' not found.")
        
        # Step 1: Use ImageMagick to invert colors
        command = [
            "convert",
            "-density", str(dpi),
            input_pdf,
            "-negate",
            output_pdf
        ]
        subprocess.run(command, check=True)
        print(f"Saved inverted PDF as: {output_pdf}")
    except subprocess.CalledProcessError as e:
        print(f"ImageMagick error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_pdf = "input.pdf"  # Input PDF file
    output_pdf = "inverted_output.pdf"  # Output inverted PDF
    
    # Run the inversion
    invert_pdf(input_pdf, output_pdf)
