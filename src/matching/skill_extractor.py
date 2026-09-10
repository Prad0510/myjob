import re

from src.matching.skill_dictionary import SKILLS


def extract_skills(text: str) -> list[str]:
    """
    Extract known skills from a piece of text.
    """

    found_skills = []

    text_lower = text.lower()

    for skill in SKILLS:

        # C needs special handling because
        # the letter "c" appears naturally in many sentences.
        if skill == "C":

            c_patterns = [
                r"\bc programming\b",
                r"\bc language\b",
                r"\bc/c\+\+\b",
                r"\bc developer\b",
                r"\bc programming language\b",
            ]

            if any(
                re.search(pattern, text_lower)
                for pattern in c_patterns
            ):
                found_skills.append(skill)

            continue

        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return found_skills