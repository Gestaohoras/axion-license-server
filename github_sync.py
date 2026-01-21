import requests
import base64
import json

GITHUB_TOKEN = "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"
OWNER = "Gestaohoras"
REPO = "axion-licenses"
BRANCH = "main"
LICENSES_PATH = "licenses"


def _headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }


def upsert_license_json(license_key: str, data: dict):
    filename = f"{LICENSES_PATH}/{license_key}.json"
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{filename}"

    r = requests.get(url, headers=_headers())
    sha = None

    if r.status_code == 200:
        sha = r.json().get("sha")

    content = base64.b64encode(
        json.dumps(data, indent=2).encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": f"update license {license_key}",
        "content": content,
        "branch": BRANCH
    }

    if sha:
        payload["sha"] = sha

    res = requests.put(url, headers=_headers(), json=payload)

    if res.status_code not in (200, 201):
        raise RuntimeError(f"GitHub error: {res.text}")
