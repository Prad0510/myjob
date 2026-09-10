from bs4 import BeautifulSoup


def clean_html(html: str) -> str:
    """
    Convert HTML content into clean plain text.
    """

    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text(
        separator="\n",
        strip=True
    )

    return text