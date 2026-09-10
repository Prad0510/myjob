from src.matching.final_score import calculate_final_score


def main():

    score = calculate_final_score(
        skill_score=35,
        role_score=100,
        experience_score=100
    )

    print("\n===== FINAL MATCH SCORE =====")
    print("Final score:", score, "%")


if __name__ == "__main__":
    main()