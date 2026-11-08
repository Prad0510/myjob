import re


SKILL_ALIASES = {
    "python": ["python", "python3"],
    "java": ["java"],
    "c": [r"\bc\b", "c programming"],
    "c++": ["c++"],
    "c#": ["c#", "c sharp"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],

    "sql": ["sql"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "mongodb": ["mongodb", "mongo db"],
    "redis": ["redis"],

    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "django": ["django"],
    "spring boot": ["spring boot", "springboot"],

    "react": ["react", "reactjs", "react.js"],
    "node.js": ["node.js", "nodejs", "node js"],
    "angular": ["angular"],
    "html": ["html"],
    "css": ["css"],

    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "pytorch": ["pytorch"],
    "tensorflow": ["tensorflow"],

    "apache spark": ["apache spark", "spark"],
    "hadoop": ["hadoop"],
    "kafka": ["kafka"],
    "airflow": ["airflow", "apache airflow"],

    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],

    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "git": ["git"],
    "github": ["github"],
    "linux": ["linux", "ubuntu"],

    "rest api": ["rest api", "restful api", "restful"],
    "graphql": ["graphql"],

    "machine learning": ["machine learning"],
    "deep learning": ["deep learning"],
    "data engineering": ["data engineering"],
    "data science": ["data science"],

    "etl": ["etl", "extract transform load"],
    "elt": ["elt", "extract load transform"],

    "ci/cd": [
        "ci/cd",
        "cicd",
        "continuous integration",
        "continuous deployment",
    ],
}


ROLE_ALIASES = {
    "backend": [
        "backend",
        "back-end",
        "back end",
        "server-side",
        "server side",
        "api developer",
    ],

    "frontend": [
        "frontend",
        "front-end",
        "front end",
        "ui developer",
    ],

    "fullstack": [
        "full stack",
        "full-stack",
        "fullstack",
    ],

    "software": [
        "software engineer",
        "software developer",
        "software development",
    ],

    "data_engineering": [
        "data engineer",
        "data engineering",
        "data platform",
        "analytics engineer",
    ],

    "data_science": [
        "data scientist",
        "data science",
        "machine learning engineer",
        "ml engineer",
        "ai engineer",
    ],

    "devops": [
        "devops",
        "dev ops",
        "site reliability",
        "sre",
        "platform engineer",
    ],

    "cloud": [
        "cloud engineer",
        "cloud architect",
        "cloud infrastructure",
        "cloud platform",
    ],

    "security": [
        "security engineer",
        "cybersecurity",
        "cyber security",
        "security analyst",
        "information security",
        "grc analyst",
    ],

    "sales": [
        "sales",
        "account executive",
        "business development",
        "sales development",
    ],

    "marketing": [
        "marketing",
        "seo",
        "social media",
        "content marketing",
    ],

    "design": [
        "designer",
        "design",
        "ux",
        "ui/ux",
        "user experience",
    ],

    "operations": [
        "operations",
        "business operations",
        "people operations",
        "recruiter",
        "human resources",
        "hr ",
    ],

    "support": [
        "support engineer",
        "technical support",
        "customer support",
        "product support",
    ],
}


SENIORITY_ALIASES = {
    "intern": [
        "intern",
        "internship",
        "trainee",
    ],

    "entry": [
        "entry level",
        "entry-level",
        "graduate",
        "new grad",
        "fresher",
        "associate",
    ],

    "junior": [
        "junior",
        "jr",
    ],

    "mid": [
        "mid level",
        "mid-level",
        "midlevel",
    ],

    "senior": [
        "senior",
        "sr",
    ],

    "staff": [
        "staff",
    ],

    "lead": [
        "lead",
        "team lead",
        "tech lead",
    ],

    "principal": [
        "principal",
    ],

    "director": [
        "director",
    ],

    "head": [
        "head of",
    ],
}


def normalize_text(text: str) -> str:

    if not text:
        return ""

    text = text.lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def contains_skill(
    text: str,
    alias: str,
) -> bool:

    alias = alias.lower()

    if re.fullmatch(
        r"[a-z0-9+#./-]+",
        alias,
    ):

        pattern = (
            rf"(?<![a-z0-9])"
            rf"{re.escape(alias)}"
            rf"(?![a-z0-9])"
        )

        return (
            re.search(
                pattern,
                text,
            )
            is not None
        )

    return alias in text


def extract_skills(
    text: str,
) -> list[str]:

    text = normalize_text(text)

    found_skills = []

    for canonical_skill, aliases in SKILL_ALIASES.items():

        for alias in aliases:

            if contains_skill(
                text,
                alias,
            ):

                found_skills.append(
                    canonical_skill
                )

                break

    return sorted(
        set(found_skills)
    )


def extract_roles(
    title: str,
) -> list[str]:

    title = normalize_text(
        title
    )

    found_roles = []

    for role, aliases in ROLE_ALIASES.items():

        for alias in aliases:

            if alias in title:

                found_roles.append(
                    role
                )

                break

    return sorted(
        set(found_roles)
    )


def extract_seniority(
    title: str,
) -> list[str]:

    title = normalize_text(
        title
    )

    found_levels = []

    for level, aliases in SENIORITY_ALIASES.items():

        for alias in aliases:

            if alias in title:

                found_levels.append(
                    level
                )

                break

    return sorted(
        set(found_levels)
    )