from src.matching.skill_weights import ROLE_SKILL_WEIGHTS


def main():

    for role, weights in ROLE_SKILL_WEIGHTS.items():

        print(f"\n{role}:")
        print("Total:", sum(weights.values()))
        print(weights)


if __name__ == "__main__":
    main()