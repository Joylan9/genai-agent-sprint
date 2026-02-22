import json
from app.api_app import app

def generate_openapi():
    openapi_schema = app.openapi()
    with open("frontend-handoff/openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print("✅ openapi.json generated in frontend-handoff/")

if __name__ == "__main__":
    import os
    if not os.path.exists("frontend-handoff"):
        os.makedirs("frontend-handoff")
    generate_openapi()
