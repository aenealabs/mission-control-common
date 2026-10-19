"""Wire the shared suite pieces into one app: static files, templates, and template globals.

    templates = Jinja2Templates(directory=PACKAGE_DIR / "templates")
    install(app, templates, "App Portfolio", fallback=suite.apps)

Then, in the app's base template:
    <head> ... {% include "mission_control/head.html" %} <link app.css> <script app.js> </head>
    <header class="appbar"> ... {% include "mission_control/suite_menu.html" %} ...

The app's own templates are searched first, so an app can still override a shared template.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, FileSystemLoader

from mission_control.launcher import suite_apps

PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_PATH = "/suite-static"  # add to the app's public paths so the sign-in page is styled


def install(app: FastAPI, templates: Jinja2Templates, current: str,
            fallback: list[tuple[str, str]] | None = None,
            suite_name: str = "Mission Control") -> None:
    from mission_control import __version__

    app.mount(STATIC_PATH, StaticFiles(directory=PACKAGE_DIR / "static"), name="suite_static")
    templates.env.loader = ChoiceLoader([templates.env.loader,
                                         FileSystemLoader(PACKAGE_DIR / "templates")])
    templates.env.globals.update(suite_name=suite_name, suite_version=__version__,
                                 suite_apps=suite_apps(current, fallback))
