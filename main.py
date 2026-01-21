from fastapi import FastAPI
from pydantic import BaseModel
import json
from datetime import datetime

app = FastAPI()

LICENSE_FILE = "licenses.json"

class LicensePayload(BaseModel):
    license: str
    hwid: str

def load_licenses():
    with open(LICENSE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_licenses(data):
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@app.post("/license/check")
def check_license(payload: LicensePayload):
    licenses = load_licenses()

    lic = licenses.get(payload.license)
    if not lic:
        return {"status": "invalid"}

    if lic["status"] != "active":
        return {"status": "revoked"}

    if lic.get("expires"):
        if datetime.fromisoformat(lic["expires"]) < datetime.utcnow():
            return {"status": "expired"}

    # 🔐 bind automático do HWID na primeira ativação
    if not lic.get("hwid"):
        lic["hwid"] = payload.hwid
        save_licenses(licenses)
        return {"status": "bound"}

    if lic["hwid"] != payload.hwid:
        return {"status": "hwid"}

    return {"status": "ok"}
