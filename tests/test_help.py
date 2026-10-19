import pytest
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

from mission_control import ReferenceSection, install, install_help
from mission_control.help import render_markdown

BASE = ('<nav>{% include "mission_control/help_button.html" %}</nav>'
        '<main>{% block content %}{% endblock %}</main>')
GUIDE = """# Licenses

How licenses work.

## Spare seats

Seats above the peak.

## Spare seats

A repeated heading gets its own anchor.

<script>alert(1)</script>
"""


def make(tmp_path, monkeypatch, page_help=None, reference=True):
    monkeypatch.setenv("MISSION_CONTROL_APPS", "Backlog Pilot=http://bp.example, App Portfolio=/")
    (tmp_path / "base.html").write_text(BASE)
    (tmp_path / "screen.html").write_text('{% extends "base.html" %}')
    docs = tmp_path / "help"
    docs.mkdir()
    (docs / "01-overview.md").write_text("# Overview\n\nWhat it is for.\n")
    (docs / "02-licenses.md").write_text(GUIDE)
    app = FastAPI()
    templates = Jinja2Templates(directory=tmp_path)
    install(app, templates, "App Portfolio")

    def render(request: Request, name: str, **context) -> HTMLResponse:
        return templates.TemplateResponse(request, name, {"nav": name, **context})

    install_help(app, templates, render, docs, page_help=page_help or {},
                 reference=(lambda: [ReferenceSection("Thresholds", [("Near capacity", "95%")])])
                 if reference else None)

    @app.get("/screen")
    def screen(request: Request):
        return render(request, "screen.html")

    return TestClient(app)


def test_markdown_gets_anchors_and_never_renders_raw_html():
    title, html, sections = render_markdown(GUIDE)
    assert title == "Licenses"
    assert sections == [("spare-seats", "Spare seats"), ("spare-seats-2", "Spare seats")]
    assert '<h2 id="spare-seats">' in html and "<script>" not in html and "&lt;script&gt;" in html


def test_help_pages_reference_and_suite_guide(tmp_path, monkeypatch):
    client = make(tmp_path, monkeypatch)
    index = client.get("/help").text
    assert "What it is for." in index and 'href="/help/licenses"' in index
    assert "Seats above the peak." in client.get("/help/licenses").text
    ref = client.get("/help/reference").text
    assert "Near capacity" in ref and "95%" in ref
    suite = client.get("/help/mission-control").text
    assert "How Mission Control works" in suite and "http://bp.example/help" in suite
    assert client.get("/help/nope").status_code == 404


def test_help_button_opens_the_section_for_the_screen(tmp_path, monkeypatch):
    client = make(tmp_path, monkeypatch, page_help={"screen.html": "licenses#spare-seats"})
    assert 'href="/help/licenses#spare-seats"' in client.get("/screen").text


def test_a_help_link_to_a_missing_section_fails_at_startup(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="not a help section"):
        make(tmp_path, monkeypatch, page_help={"screen.html": "licenses#no-such-heading"})


def test_reference_is_optional(tmp_path, monkeypatch):
    client = make(tmp_path, monkeypatch, reference=False)
    assert client.get("/help/reference").status_code == 404
    assert "Rules and settings reference" not in client.get("/help").text


def test_suite_guide_puts_the_apps_after_its_intro(tmp_path, monkeypatch):
    html = make(tmp_path, monkeypatch).get("/help/mission-control").text
    intro = html.index("Mission Control is a set of small tools")
    assert intro < html.index('id="the-apps"') < html.index('id="the-same-rules-in-every-app"')
