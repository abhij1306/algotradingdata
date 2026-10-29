"""render.py <pdf> <out_dir> <page,page,...> [scale]: pages (1-based) as PNG."""
import sys
from pathlib import Path
import pypdfium2 as pdfium
pdf, out, pages = sys.argv[1], Path(sys.argv[2]), [int(p) for p in sys.argv[3].split(",")]
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
out.mkdir(parents=True, exist_ok=True)
doc = pdfium.PdfDocument(pdf)
for p in pages:
    img = doc[p - 1].render(scale=scale).to_pil()
    target = out / f"{Path(pdf).stem}_p{p}.png"
    img.save(target)
    print(target, img.size)
