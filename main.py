import json

from src.resume.pdf_parser import extract_text_from_pdf
from src.resume.resume_parser import build_candidate_profile


def main():

    # PDF → text
    text = extract_text_from_pdf("data/raw/resume.pdf")

    # Text → CandidateProfile
    candidate = build_candidate_profile(text)

    # CandidateProfile → dictionary
    candidate_data = candidate.to_dict()

    # Save dictionary as JSON
    output_path = "data/processed/candidate_profile.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            candidate_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nCandidate profile created successfully.")
    print("Saved to:", output_path)


if __name__ == "__main__":
    main()

