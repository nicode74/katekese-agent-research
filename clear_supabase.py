import os
import urllib.request
from pathlib import Path

env_path = Path(".env")
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k] = v.strip()

url = os.environ.get("SUPABASE_URL").rstrip('/') + "/rest/v1/documents?id=gt.0"
key = os.environ.get("SUPABASE_SERVICE_KEY")

req = urllib.request.Request(url, method="DELETE", headers={
    "apikey": key,
    "Authorization": f"Bearer {key}"
})
with urllib.request.urlopen(req) as resp:
    print(resp.read().decode('utf-8'))
