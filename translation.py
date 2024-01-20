import gettext
from pathlib import Path

t = gettext.translation(
    domain="mb_bot", localedir=Path(__file__).resolve().parent / "src" / "locales", fallback=False, languages=["ru", "en"]
)
