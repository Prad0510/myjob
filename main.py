from src.resume.pdf_parser import extract_text_from_pdf


def main():
    text = extract_text_from_pdf("data/raw/resume.pdf")

    print(text)


if __name__ == "__main__":
    main()