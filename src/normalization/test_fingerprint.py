from src.normalization.fingerprint import generate_job_fingerprint


def main():

    fingerprint_1 = generate_job_fingerprint(
        "Python Backend Intern",
        "ABC Technologies",
        "https://example.com/apply",
    )

    fingerprint_2 = generate_job_fingerprint(
        "Python Backend Intern",
        "ABC Technologies",
        "https://example.com/apply",
    )

    print("Fingerprint 1:", fingerprint_1)
    print("Fingerprint 2:", fingerprint_2)

    print("Same:", fingerprint_1 == fingerprint_2)


if __name__ == "__main__":
    main()