"""
Resume Renamer — adds today's date to the last page of the PDF,
then saves it with a date-stamped filename.
"""

import io
import glob
from datetime import datetime
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

import config


def _create_date_overlay(width: float, height: float, date_text: str) -> bytes:
    """
    Create a transparent PDF page with the date text at the bottom-right corner.
    Returns the PDF as bytes.
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))

    # Style: small, grey text at bottom-right
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.35, 0.35, 0.35)  # dark grey

    # Position: bottom-right, with some margin
    x = width - 50 - c.stringWidth(date_text, "Helvetica", 9)
    y = 25  # 25 points from bottom

    c.drawString(x, y, date_text)
    c.save()

    packet.seek(0)
    return packet


def add_date_to_pdf(source_pdf: Path, output_pdf: Path) -> Path:
    """
    Read the source PDF, add today's date to the bottom of the last page,
    and save to output_pdf. Returns the output path.
    """
    reader = PdfReader(str(source_pdf))
    writer = PdfWriter()

    total_pages = len(reader.pages)
    today = datetime.now().strftime("%d %b %Y")
    date_text = f"Updated: {today}"

    for i, page in enumerate(reader.pages):
        if i == total_pages - 1:
            # Add date overlay to the last page
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)

            overlay_stream = _create_date_overlay(page_width, page_height, date_text)
            overlay_reader = PdfReader(overlay_stream)
            overlay_page = overlay_reader.pages[0]

            page.merge_page(overlay_page)

        writer.add_page(page)

    with open(str(output_pdf), "wb") as f:
        writer.write(f)

    return output_pdf


def rename_resume() -> Path:
    """
    Add today's date to the CV and save with a date-stamped filename.
    Returns the Path to the new file.
    """
    if not config.BASE_RESUME.exists():
        raise FileNotFoundError(
            f"Base resume not found at: {config.BASE_RESUME}\n"
            f"Please place your resume as '{config.BASE_RESUME.name}' in:\n"
            f"  {config.PROJECT_DIR}"
        )

    today = datetime.now().strftime("%d_%b_%Y")
    new_name = config.RESUME_NAME_PATTERN.format(date=today)
    new_path = config.PROJECT_DIR / new_name

    # Add date to PDF and save
    add_date_to_pdf(config.BASE_RESUME, new_path)

    print(f"✅ Resume created with date stamp: {new_name}")
    print(f"   (Date 'Updated: {datetime.now().strftime('%d %b %Y')}' added to last page)")
    return new_path


def cleanup_old_resumes(keep_latest: int = 3) -> None:
    """
    Delete old date-stamped resume copies, keeping the N most recent.
    """
    pattern = str(config.PROJECT_DIR / "Abhay_Resume_*.pdf")
    files = sorted(glob.glob(pattern), key=lambda f: Path(f).stat().st_mtime, reverse=True)

    for old_file in files[keep_latest:]:
        Path(old_file).unlink()
        print(f"🗑️  Cleaned up old resume: {Path(old_file).name}")


if __name__ == "__main__":
    path = rename_resume()
    print(f"Created: {path}")
    cleanup_old_resumes()
