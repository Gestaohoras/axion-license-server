from fastapi import FastAPI
from pydantic import BaseModel
import requests
import base64
import json
import os

app = FastAPI()

# ================= CONFIG =================
GITHUB_OWNER = "GestaoHoras"
GITHUB_REPO = "axion-licenses"
GITHUB_BRANCH = "main"
LICENSES_PATH = "licenses"
GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}
# =========================================


class LicensePayload(BaseModel):
    license: str
    hwid: str


def load_license(license_key: str):
    url = f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{LICENSES_PATH}/{license_key}.json"
    r = requests.get(url, headers=HEADERS, timeout=10)

    if r.status_code != 200:
        return None, None

    data = r.json()
    content = json.loads(
        base64.b64decode(data["content"]).decode("utf-8")
    )
    return content, data["sha"]


def save_license(license_key: str, content: dict, sha: str):
    url = f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{LICENSES_PATH}/{license_key}.json"

    payload = {
        "message": f"bind hwid {license_key}",
        "content": base64.b64encode(
            json.dumps(content, indent=2).encode()
        ).decode(),
        "sha": sha,
        "branch": GITHUB_BRANCH
    }

    r = requests.put(url, headers=HEADERS, json=payload, timeout=10)
    return r.status_code in (200, 201)


@app.post("/license/check")
def check_license(payload: LicensePayload):
    license_key = payload.license
    hwid = payload.hwid

    license_data, sha = load_license(license_key)
    if not license_data:
        return {"status": "invalid"}

    if license_data.get("status") != "active":
        return {"status": "inactive"}

    # primeira ativação → grava HWID
    if not license_data.get("hwid"):
        license_data["hwid"] = hwid
        save_license(license_key, license_data, sha)
        return {"status": "ok"}

    # HWID diferente
    if license_data["hwid"] != hwid:
        return {"status": "hwid"}

    return {"status": "ok"}
