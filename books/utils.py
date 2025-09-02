""" Utilities for books app. """
import re

OPERATOR_RE = re.compile(
    r'\b(intitle|inauthor|inpublisher|subject|isbn|lccn|oclc):',
    re.I
    )


def _genres():
    return [
        ("Sci-Fi", "science fiction"),
        ("Mystery", "mystery"),
        ("Non-Fiction", "nonfiction"),
        ("Fantasy", "fantasy"),
        ("Horror", "horror"),
        ("Romance", "romance"),
        ("Thriller", "thriller"),
        ("Biography", "biography"),
        ("Self-Help", "self-help"),
        ("Children", "children"),
        ("Cookbooks", "cookbooks"),
        ("Graphic Novels", "graphic novels"),
        ("Poetry", "poetry"),
        ("Classics", "classics"),
        ("Comics", "comics"),
        ("Business", "business"),
        ("Science", "science"),
        ("History", "history"),
        ("Travel", "travel"),
        ("Sports", "sports"),
        ("Memoir", "memoir"),
        ("Religion", "religion"),
        ("Spirituality", "spirituality"),
        ("Technology", "technology"),
    ]


def build_q(
    q_raw, field,
    _title_unused="",
    _author_unused="",
    _subject_unused=""
):
    """
    Build a Google Books 'q' using a single dropdown field.
    - If user already typed an operator,
    pass it through unchanged.
    - Else apply the dropdown operator
    (intitle/inauthor/subject)
    or leave as-is for 'all'.
    * Unused parameters are ignored.
    """
    q_raw = (q_raw or "").strip()
    field = (field or "all").strip().lower()

    if not q_raw:
        return ""

    # pass-through if user already used an operator
    if OPERATOR_RE.search(q_raw):
        return q_raw

    # apply operator based on dropdown
    if field == "title":
        return f"intitle:{q_raw}"
    if field == "author":
        return f"inauthor:{q_raw}"
    if field == "subject":
        return f"subject:{q_raw}"
    return q_raw  # field == "all"
