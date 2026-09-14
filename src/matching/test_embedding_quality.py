from src.matching.semantic_matcher import calculate_semantic_score


candidate = """
Computer Engineering student skilled in Python, Java, MySQL,
Flask, Django, React, JavaScript, Machine Learning, Pandas,
NumPy and Scikit-learn. Interested in backend development,
software engineering and data engineering.
"""


strong_job = """
We are looking for a Python Backend Developer to build REST APIs
and backend services. Candidates should have experience with
Python, Flask or Django, databases and backend development.
"""


medium_job = """
We are looking for a Software Engineer to develop applications,
work with APIs, databases and cloud technologies. Experience
with programming and software development is required.
"""


poor_job = """
We are looking for a Graphic Designer to create visual designs,
branding materials, illustrations and marketing graphics.
Candidates should have experience with Adobe Photoshop,
Illustrator and visual design.
"""


strong_score = calculate_semantic_score(candidate, strong_job)
medium_score = calculate_semantic_score(candidate, medium_job)
poor_score = calculate_semantic_score(candidate, poor_job)


print("\n===== EMBEDDING QUALITY TEST =====")
print("Strong match :", strong_score)
print("Medium match :", medium_score)
print("Poor match   :", poor_score)