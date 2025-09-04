""" Utilities for books app. """
import re
from html import unescape

OPERATOR_RE = re.compile(
    r'\b(intitle|inauthor|inpublisher|subject|isbn|lccn|oclc):',
    re.I
    )


def meta_description_from_volume(book: dict, max_len: int = 155) -> str:
    """
    Normalize, sanitize and slice book description
    to create meta description tag
    """
    text = book.get("description") or ""

    # Normalize and sanitize
    text = unescape(text)                      # decode entities
    text = re.sub(r"<[^>]+>", "", text)        # strip tags if any
    text = re.sub(r"\s+", " ", text).strip()   # collapse whitespace

    if not text:
        title = book.get("title") or "Untitled"
        authors = book.get("authors") or []
        text = f"{title} — by {authors}." if authors else f"{title}."

    if len(text) <= max_len:
        return text

    # Soft wrap on a nice boundary near max_len
    slice_ = text[: max_len + 20]
    # prefer a sentence end, then em dash, semicolon, colon, comma, then space
    candidates = [". ", " — ", "; ", ": ", ", ", " "]
    idx = max((slice_.rfind(c) for c in candidates), default=-1)
    cut = slice_[:idx] if idx > 0 else text[:max_len]
    cut = re.sub(r"[.,:;—\s]+$", "", cut)
    return cut + "…"


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
