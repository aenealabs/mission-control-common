from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

from mission_control import STATIC_PATH, __version__, install, suite_apps

APPS = ("Backlog Pilot=http://bp.example/, Leadership Pilot=http://lp.example, "
        "Custom Tool=http://ct.example")


def test_launcher_marks_the_current_app(monkeypatch):
    monkeypatch.setenv("MISSION_CONTROL_APPS", APPS)
    apps = suite_apps("Leadership Pilot")
    assert [a.name for a in apps] == ["Backlog Pilot", "Leadership Pilot", "Custom Tool"]
    assert apps[0].url == "http://bp.example" and apps[1].url == "/" and apps[1].current
    assert apps[2].icon == "apps" and apps[2].purpose == ""  # unknown apps still listed


def test_launcher_falls_back_to_per_app_links(monkeypatch):
    monkeypatch.delenv("MISSION_CONTROL_APPS", raising=False)
    apps = suite_apps("Leadership Pilot", [("Backlog Pilot", "http://bp.example/"), ("X", "")])
    assert [(a.name, a.url) for a in apps] == [("Leadership Pilot", "/"),
                                               ("Backlog Pilot", "http://bp.example")]


def make_app(tmp_path, monkeypatch, override=False, apps=APPS):
    monkeypatch.setenv("MISSION_CONTROL_APPS", apps)
    (tmp_path / "page.html").write_text(
        '<head>{% include "mission_control/head.html" %}</head>'
        '<header>{% include "mission_control/suite_menu.html" %}</header>')
    if override:
        (tmp_path / "mission_control").mkdir()
        (tmp_path / "mission_control" / "suite_menu.html").write_text("app's own menu")
    app = FastAPI()
    templates = Jinja2Templates(directory=tmp_path)
    install(app, templates, "Leadership Pilot")

    @app.get("/")
    def page(request: Request):
        return templates.TemplateResponse(request, "page.html")

    return TestClient(app)


def test_install_serves_shared_files_and_renders_the_menu(tmp_path, monkeypatch):
    client = make_app(tmp_path, monkeypatch)
    for f in ("suite.css", "suite.js"):
        assert client.get(f"{STATIC_PATH}/{f}").status_code == 200
    html = client.get("/").text
    assert f"{STATIC_PATH}/suite.css?v={__version__}" in html
    assert 'class="suite-menu"' in html and "Mission Control" in html
    assert 'aria-current=page' in html and "http://ct.example" in html


def test_an_app_can_override_a_shared_template(tmp_path, monkeypatch):
    assert "app's own menu" in make_app(tmp_path, monkeypatch, override=True).get("/").text


def test_one_app_alone_shows_no_menu(tmp_path, monkeypatch):
    html = make_app(tmp_path, monkeypatch, apps="").get("/").text
    assert 'class="suite-menu"' not in html and "Leadership Pilot" in html
