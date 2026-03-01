import json
import sys
from pathlib import Path

from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=backend_dir / ".env")
sys.path.insert(0, str(backend_dir))

from app.main import app  # noqa: E402


def main() -> None:
    print(json.dumps(app.openapi()))


if __name__ == "__main__":
    main()
