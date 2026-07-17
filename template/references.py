"""Single source of truth for the book's references.

Chapters cite a work with `[@key]` in their markdown; `build.py` resolves each
key against `REFERENCES`, renders an author-year citation linked to the entry,
and appends a per-chapter References section listing exactly the works that
chapter cites. A citation whose key is missing here fails the build loudly.

Every entry should be verified against the actual paper (arXiv listing, venue
page) before it lands — a wrong citation is worse than no citation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

KEY_PATTERN = re.compile(r"^[a-z][a-z0-9]*$")
ARXIV_ID_PATTERN = re.compile(r"^\d{4}\.\d{4,5}$")


@dataclass(frozen=True)
class Reference:
    """One cited work.

    `authors` holds one "Lastname, F. M." string per author, in the paper's
    order; a corporate author (e.g. "DeepMind") is a single comma-free string.
    `truncated` marks an author list that is deliberately cut short (papers with
    dozens or hundreds of authors) and renders as "et al.". Exactly one of
    `arxiv` (a bare id like "1706.03762") and `url` may be set; both empty means
    the entry renders with no link.
    """

    key: str
    authors: tuple[str, ...]
    truncated: bool
    year: int
    title: str
    venue: str
    arxiv: str
    url: str

    def __post_init__(self) -> None:
        assert KEY_PATTERN.match(self.key), f"Bad reference key: {self.key!r}."
        assert self.authors, f"Reference '{self.key}' has no authors."
        assert all(a.strip() for a in self.authors), f"Empty author in '{self.key}'."
        assert 1900 < self.year <= 2100, f"Implausible year in '{self.key}'."
        assert self.title and not self.title.endswith(
            "."
        ), f"Title of '{self.key}' must be non-empty and carry no trailing period."
        assert self.venue, f"Reference '{self.key}' has no venue."
        assert not (
            self.arxiv and self.url
        ), f"Reference '{self.key}' sets both arxiv and url; pick one."
        if self.arxiv:
            assert ARXIV_ID_PATTERN.match(
                self.arxiv
            ), f"Bad arXiv id in '{self.key}': {self.arxiv!r}."

    def first_author_family(self) -> str:
        """Return the first author's family name (the part before the comma)."""
        first = self.authors[0]
        return first.split(",")[0].strip() if "," in first else first

    def in_text_label(self) -> str:
        """Return the author-year label, e.g. "Vaswani et al., 2017"."""
        family = self.first_author_family()
        if self.truncated or len(self.authors) >= 3:
            return f"{family} et al., {self.year}"
        if len(self.authors) == 2:
            second = self.authors[1]
            second_family = second.split(",")[0].strip() if "," in second else second
            return f"{family} & {second_family}, {self.year}"
        return f"{family}, {self.year}"

    def link(self) -> str:
        """Return the entry's URL, or "" when it has none."""
        if self.arxiv:
            return f"https://arxiv.org/abs/{self.arxiv}"
        return self.url


# One worked example so a drafter has a pattern to copy. Add verified entries as
# chapters cite them, and delete this one once real references land. Every entry
# must be checked against the actual paper before it ships.
_ENTRIES: tuple[Reference, ...] = (
    Reference(
        key="vaswani2017",
        authors=(
            "Vaswani, A.",
            "Shazeer, N.",
            "Parmar, N.",
            "Uszkoreit, J.",
            "Jones, L.",
            "Gomez, A. N.",
            "Kaiser, L.",
            "Polosukhin, I.",
        ),
        truncated=False,
        year=2017,
        title="Attention Is All You Need",
        venue="NeurIPS",
        arxiv="1706.03762",
        url="",
    ),
)


def _build_index(entries: tuple[Reference, ...]) -> dict[str, Reference]:
    """Index entries by key, failing loudly on duplicates."""
    index: dict[str, Reference] = {}
    for entry in entries:
        assert entry.key not in index, f"Duplicate reference key: {entry.key}."
        index[entry.key] = entry
    return index


REFERENCES: dict[str, Reference] = _build_index(_ENTRIES)
