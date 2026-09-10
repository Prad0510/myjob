from src.matching.skill_categories import SKILL_CATEGORIES


def categorize_skills(skills: list[str]) -> dict:
    """
    Place candidate skills into their respective categories.
    """

    categorized = {
        category: []
        for category in SKILL_CATEGORIES
    }

    skill_lookup = {
        skill.lower(): skill
        for skill in skills
    }

    for category, category_skills in SKILL_CATEGORIES.items():

        for skill in category_skills:

            if skill.lower() in skill_lookup:

                categorized[category].append(
                    skill_lookup[skill.lower()]
                )

    return categorized