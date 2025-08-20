# # OCR utilities using pytesseract and pdf2image
# from PIL import Image
# import pytesseract
# import io
# from pdf2image import convert_from_path, convert_from_bytes
# import tempfile
# import os
# import numpy as np

# def pdf_to_images(pdf_bytes: bytes, dpi: int = 300):
#     """Convert PDF bytes to list of PIL Images (one per page)."""
#     return convert_from_bytes(pdf_bytes, dpi=dpi)

# def image_to_tsv(image: Image.Image):
#     """Run tesseract and return TSV result as list of dict rows."""
#     tsv = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
#     # tsv contains keys: level, page_num, block_num, par_num, line_num, word_num, left, top, width, height, conf, text
#     rows = []
#     n = len(tsv['level'])
#     for i in range(n):
#         rows.append({
#             'text': tsv['text'][i],
#             'conf': float(tsv['conf'][i]) if tsv['conf'][i].strip() != '-1' else -1.0,
#             'left': int(tsv['left'][i]),
#             'top': int(tsv['top'][i]),
#             'width': int(tsv['width'][i]),
#             'height': int(tsv['height'][i]),
#             'page_num': int(tsv['page_num'][i])
#         })
#     return rows

# def image_to_plain_text(image: Image.Image):
#     return pytesseract.image_to_string(image)



# OCR utilities using pytesseract and PyMuPDF (no poppler needed)
from PIL import Image
import pytesseract
import io
import fitz  # PyMuPDF
import numpy as np

def pdf_to_images(pdf_bytes: bytes, dpi: int = 300):
    """Convert PDF bytes to list of PIL Images (one per page) without Poppler."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        # render page as image
        mat = fitz.Matrix(dpi/72, dpi/72)  # scale for resolution
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        images.append(img)
    return images

def image_to_tsv(image: Image.Image):
    """Run tesseract and return TSV result as list of dict rows."""
    tsv = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    rows = []
    n = len(tsv['level'])
    for i in range(n):
        rows.append({
            'text': tsv['text'][i],
            'conf': float(tsv['conf'][i]) if tsv['conf'][i].strip() != '-1' else -1.0,
            'left': int(tsv['left'][i]),
            'top': int(tsv['top'][i]),
            'width': int(tsv['width'][i]),
            'height': int(tsv['height'][i]),
            'page_num': int(tsv['page_num'][i])
        })
    return rows

def image_to_plain_text(image: Image.Image):
    return pytesseract.image_to_string(image)
