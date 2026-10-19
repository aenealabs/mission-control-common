"""Mission Control: what every app in the suite shares (launcher, suite menu, help, base styles)."""

from mission_control.help import ReferenceSection, install_help
from mission_control.launcher import KNOWN, SuiteApp, suite_apps
from mission_control.web import STATIC_PATH, install

__version__ = "0.3.0"
__all__ = ["KNOWN", "STATIC_PATH", "ReferenceSection", "SuiteApp", "__version__", "install",
           "install_help", "suite_apps"]
