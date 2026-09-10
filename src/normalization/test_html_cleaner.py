from src.normalization.html_cleaner import clean_html


def main():

    html = """
    <div>
        <h2>About the Company</h2>
        <p>We are building great products.</p>

        <h3>Requirements</h3>
        <ul>
            <li>Python</li>
            <li>SQL</li>
            <li>FastAPI</li>
        </ul>
    </div>
    """

    cleaned_text = clean_html(html)

    print(cleaned_text)


if __name__ == "__main__":
    main()