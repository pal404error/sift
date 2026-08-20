from __future__ import annotations

import uvicorn

from llm_search.api import app
from llm_search.config import get_settings


def main() -> None:
    s = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level=s.log_level.lower())


if __name__ == "__main__":
    main()
