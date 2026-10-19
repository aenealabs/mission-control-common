"""Mission Control app launcher: one list of suite apps, the same in every app.

Set MISSION_CONTROL_APPS to the same value everywhere, for example
  Backlog Pilot=https://backlog.example.com, Leadership Pilot=https://lp.example.com,
  PLM Insight=https://plm.example.com, Support Pilot=https://support.example.com
Each app marks itself as current. Adding an app means adding it to this one setting; no
code changes in the others. Without the setting, the app's older per-app links are used.
"""

import os
from dataclasses import dataclass

KNOWN = {  # icon and one-line purpose for apps in the suite
    "Backlog Pilot": ("assignment", "Requests to traced, prioritized backlog"),
    "Leadership Pilot": ("record_voice_over", "Listening tour, status, weekly update"),
    "PLM Insight": ("fact_check", "Engineering data quality and ECO analytics"),
    "Support Pilot": ("support_agent", "Cited answers and recurring problems"),
    "App Portfolio": ("apps", "Application rationalization and licenses"),
}


@dataclass(frozen=True)
class SuiteApp:
    name: str
    url: str
    icon: str
    purpose: str
    current: bool


def suite_apps(current: str, fallback: list[tuple[str, str]] | None = None) -> list[SuiteApp]:
    raw = os.getenv("MISSION_CONTROL_APPS", "").strip()
    pairs = []
    if raw:
        for entry in raw.replace("\n", ",").split(","):
            name, _, url = entry.partition("=")
            if name.strip() and url.strip():
                pairs.append((name.strip(), url.strip().rstrip("/")))
    else:
        pairs = [(n, u.rstrip("/")) for n, u in (fallback or []) if u]
    if current not in [n for n, _ in pairs]:
        pairs.insert(0, (current, ""))
    return [SuiteApp(n, "/" if n == current else u, *KNOWN.get(n, ("apps", "")), n == current)
            for n, u in pairs]
