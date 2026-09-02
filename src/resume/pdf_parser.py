import pymupdf


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF resume.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text as a single string.
    """

    document = pymupdf.open(pdf_path)

    pages = []

    for page in document:
        text = page.get_text()
        pages.append(text)

    document.close()

    return "\n".join(pages)