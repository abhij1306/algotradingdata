"""sheet.py <pdf> <out.png> <first> <last>: a contact sheet of pages first..last (1-based)."""
import sys
import pypdfium2 as pdfium
from PIL import Image, ImageDraw
pdf, out, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
doc = pdfium.PdfDocument(pdf)
imgs = [doc[i - 1].render(scale=0.3).to_pil() for i in range(a, min(b, len(doc)) + 1)]
w = max(i.width for i in imgs); h = max(i.height for i in imgs); cols = 4
sheet = Image.new("RGB", (w * cols, h * ((len(imgs) + cols - 1) // cols)), "white")
for n, im in enumerate(imgs):
    x, y = (n % cols) * w, (n // cols) * h
    sheet.paste(im, (x, y)); ImageDraw.Draw(sheet).text((x + 5, y + 5), f"p{a + n}", fill="red")
sheet.save(out); print(out, sheet.size)
