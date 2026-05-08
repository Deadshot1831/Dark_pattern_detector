from bs4 import BeautifulSoup, Comment

STRIP_TAGS = ("script", "style", "noscript", "template", "svg")


def parse(html: str) -> BeautifulSoup:
    """Parse HTML and remove non-visible noise (scripts, styles, comments)."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(STRIP_TAGS):
        tag.decompose()
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()
    return soup


def visible_text(soup: BeautifulSoup) -> str:
    """Whitespace-collapsed visible text from a parsed soup."""
    raw = soup.get_text(separator=" ", strip=True)
    return " ".join(raw.split())
