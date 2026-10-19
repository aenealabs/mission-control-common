"""Built-in Help for a suite app: its own guide pages, a reference generated from its code, and
the Mission Control suite guide, which every app serves from this package.

    install_help(app, templates, render, PACKAGE_DIR / "help",
                 reference=lambda: [...ReferenceSection...],
                 page_help={"licenses.html": "licenses", "directory.html": "directory#set-up"})

Guide pages are Markdown files named NN-slug.md (NN orders them); the first "# " line is the
title. Raw HTML in them is not rendered. `page_help` maps each screen's template to the guide
section about it; the app bar's help button opens that section.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from markdown_it import MarkdownIt
from markupsafe import Markup

SUITE_GUIDE = Path(__file__).resolve().parent / "help" / "mission-control.md"
SUITE_SLUG = "mission-control"
REFERENCE_SLUG = "reference"

_md = MarkdownIt("js-default")  # CommonMark plus tables; raw HTML is escaped, not rendered


@dataclass
class HelpPage:
    slug: str
    title: str
    html: Markup
    sections: list[tuple[str, str]]  # (anchor id, heading) for each "## " heading

    @property
    def intro(self) -> Markup:
        """Everything before the first "## " heading."""
        return Markup(str(self.html).split("<h2", 1)[0])

    @property
    def body(self) -> Markup:
        """From the first "## " heading on."""
        head, sep, rest = str(self.html).partition("<h2")
        return Markup(sep + rest)


@dataclass
class ReferenceSection:
    """A table generated from the app's code, so it cannot drift from what the app does."""
    title: str
    rows: list[tuple[str, ...]]
    columns: tuple[str, ...] = ("Rule", "How it works")
    intro: str = ""
    anchor: str = field(default="")

    def __post_init__(self):
        self.anchor = self.anchor or slugify(self.title)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def render_markdown(text: str) -> tuple[str, Markup, list[tuple[str, str]]]:
    """Title (the first "# " line), the body as HTML, and its "## " sections with anchors."""
    lines = text.strip().splitlines()
    title = lines[0].removeprefix("# ").strip() if lines and lines[0].startswith("# ") else ""
    body = "\n".join(lines[1:] if title else lines)
    tokens = _md.parse(body)
    sections, used = [], set()
    for i, tok in enumerate(tokens):
        if tok.type == "heading_open" and tok.tag in ("h2", "h3"):
            heading = tokens[i + 1].content
            anchor = base = slugify(heading)
            n = 2
            while anchor in used:
                anchor, n = f"{base}-{n}", n + 1
            used.add(anchor)
            tok.attrSet("id", anchor)
            if tok.tag == "h2":
                sections.append((anchor, heading))
    return title, Markup(_md.renderer.render(tokens, _md.options, {})), sections


def load_page(path: Path, slug: str) -> HelpPage:
    title, html, sections = render_markdown(path.read_text())
    return HelpPage(slug, title or slug.replace("-", " ").capitalize(), html, sections)


def load_pages(docs_dir: Path) -> list[HelpPage]:
    pages = []
    for path in sorted(docs_dir.glob("*.md")):
        slug = re.sub(r"^\d+-", "", path.stem)
        if slug in (SUITE_SLUG, REFERENCE_SLUG):
            raise ValueError(f"{path.name}: '{slug}' is reserved for the shared help pages")
        pages.append(load_page(path, slug))
    return pages


def install_help(app: FastAPI, templates: Jinja2Templates,
                 render: Callable[..., HTMLResponse], docs_dir: Path,
                 reference: Callable[[], list[ReferenceSection]] | None = None,
                 page_help: dict[str, str] | None = None) -> list[HelpPage]:
    """Add /help, /help/<page>, /help/reference, and /help/mission-control to the app.

    `render(request, template_name, **context)` is the app's own page renderer, so help pages
    get the same layout, signed-in user, and navigation as every other screen.
    """
    pages = load_pages(docs_dir)
    suite = load_page(SUITE_GUIDE, SUITE_SLUG)
    suite.sections.insert(0, ("the-apps", "The apps"))  # the table the template adds
    by_slug = {p.slug: p for p in pages}
    for target in (page_help or {}).values():
        slug, _, anchor = target.partition("#")
        if slug not in by_slug or (anchor and anchor not in dict(by_slug[slug].sections)):
            raise ValueError(f"page_help points at '{target}', which is not a help section")
    templates.env.globals.update(help_for=page_help or {}, help_pages=pages,
                                 help_has_reference=reference is not None)

    def show(request: Request, page: HelpPage | None, **context) -> HTMLResponse:
        return render(request, "mission_control/help.html", page=page, **context)

    @app.get("/help", response_class=HTMLResponse)
    def help_index(request: Request):
        return show(request, pages[0] if pages else suite)

    @app.get(f"/help/{SUITE_SLUG}", response_class=HTMLResponse)
    def help_suite(request: Request):
        return show(request, suite, suite_guide=True)

    if reference is not None:
        @app.get(f"/help/{REFERENCE_SLUG}", response_class=HTMLResponse)
        def help_reference(request: Request):
            return show(request, None, reference=reference())

    @app.get("/help/{slug}", response_class=HTMLResponse)
    def help_page(request: Request, slug: str):
        if slug not in by_slug:
            raise HTTPException(404, "No such help page")
        return show(request, by_slug[slug])

    return pages
