# mission-control-common

What every **Mission Control** app shares, kept in one place: the app launcher, the suite menu
in the app bar, and the Brightlayer UI base styles and behavior (theme toggle, phone menu). The
apps (Backlog Pilot, Leadership Pilot, PLM Insight, Support Pilot, App Portfolio) each install
it, pinned to a version tag, and keep only their own screens.

## Use it in an app

```toml
# pyproject.toml
dependencies = [
    "mission-control-common @ git+https://github.com/aenealabs/mission-control-common.git@v0.1.0",
]
```

```python
from mission_control import STATIC_PATH, install

templates = Jinja2Templates(directory=PACKAGE_DIR / "templates")
install(app, templates, "App Portfolio", fallback=suite.apps)
PUBLIC_PATHS = ("/static", STATIC_PATH, "/login", ...)  # the sign-in page needs the styles
```

```html
<head>
  {% include "mission_control/head.html" %}   <!-- fonts, suite.css, suite.js -->
  <link rel="stylesheet" href="{{ url_for('static', path='css/app.css') }}">
</head>
<header class="appbar"> {% include "mission_control/suite_menu.html" %} ... </header>
```

`install()` mounts the shared files at `/suite-static`, adds the shared templates after the
app's own (so an app can still override one), and sets `suite_name`, `suite_apps`, and
`suite_version` for templates. The version is added to the CSS and JS links so browsers pick
up changes after an upgrade.

## The app list

Set `MISSION_CONTROL_APPS` to the same value in every app:

```bash
MISSION_CONTROL_APPS="Backlog Pilot=http://127.0.0.1:8000, Leadership Pilot=http://127.0.0.1:8010, PLM Insight=http://127.0.0.1:8020, Support Pilot=http://127.0.0.1:8030, App Portfolio=http://127.0.0.1:8040"
```

Each app marks itself as current. An app running alone shows no menu.

## Releasing a change

1. Change, test (`pytest -q`, `ruff check .`), and bump `version` in `pyproject.toml` and
   `mission_control/__init__.py`.
2. Tag it (`git tag v0.1.1 && git push --tags`).
3. In each app, move the pin in `pyproject.toml` to the new tag and run its tests.

For local work across repos, `pip install -e ../mission-control-common` in an app's virtual
environment uses your working copy instead of the tag.

This repo is public so each app's CI can install it without credentials; the apps themselves
stay private. It holds no data, prompts, or business rules.

## Data and branding

The styles use the open-source Brightlayer UI color and theme values (BSD-3-Clause); see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). This is an independent project, not affiliated with or endorsed by Eaton.

## License

Released under the [MIT License](LICENSE). Third-party components keep their own licenses; see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
