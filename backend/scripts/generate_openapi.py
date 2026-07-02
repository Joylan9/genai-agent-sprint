import json
from pathlib import Path

from app.api_app import app


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HANDOFF_DIR = PROJECT_ROOT / "frontend-handoff"
OPENAPI_PATH = HANDOFF_DIR / "openapi.json"


def generate_openapi():
    openapi_schema = app.openapi()
    HANDOFF_DIR.mkdir(exist_ok=True)
    OPENAPI_PATH.write_text(json.dumps(openapi_schema, indent=2), encoding="utf-8")
    print(f"OpenAPI schema generated at {OPENAPI_PATH}")


if __name__ == "__main__":
    generate_openapi()
