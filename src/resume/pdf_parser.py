import pymupdf


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF as plain text.

    The extracted blocks are sorted according to their
    physical position on the page.
    """

    document = pymupdf.open(pdf_path)

    all_blocks = []

    for page_number, page in enumerate(document):

        page_blocks = page.get_text("blocks")

        for block in page_blocks:
            x0, y0, x1, y1, text = block[:5]

            text = text.strip()

            if not text:
                continue

            all_blocks.append(
                {
                    "page": page_number + 1,
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1,
                    "text": text,
                }
            )

    document.close()

    # Sort according to physical position on the page.
    #
    # First:
    #   page number
    #
    # Then:
    #   vertical position (top -> bottom)
    #
    # Finally:
    #   horizontal position (left -> right)
    all_blocks.sort(
        key=lambda block: (
            block["page"],
            block["y0"],
            block["x0"],
        )
    )

    return "\n".join(
        block["text"]
        for block in all_blocks
    )


def extract_text_blocks_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text blocks from a PDF while preserving
    their page position and layout information.

    Returns:
        A list of dictionaries containing:

        page
        x0
        y0
        x1
        y1
        text
    """

    document = pymupdf.open(pdf_path)

    blocks = []

    for page_number, page in enumerate(document):

        page_blocks = page.get_text("blocks")

        for block in page_blocks:

            x0, y0, x1, y1, text = block[:5]

            text = text.strip()

            if not text:
                continue

            blocks.append(
                {
                    "page": page_number + 1,
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1,
                    "text": text,
                }
            )

    document.close()

    # Sort blocks according to their physical position.
    blocks.sort(
        key=lambda block: (
            block["page"],
            block["y0"],
            block["x0"],
        )
    )

    return blocks
