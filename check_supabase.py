import os
import urllib.request
import json
from pathlib import Path

env_path = Path(".env")
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k] = v.strip()

url = os.environ.get("SUPABASE_URL").rstrip('/') + "/rest/v1/documents?select=id&limit=10"
key = os.environ.get("SUPABASE_SERVICE_KEY")

req = urllib.request.Request(url, headers={
    "apikey": key,
    "Authorization": f"Bearer {key}"
})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"Number of documents in Supabase (limit 10): {len(data)}")
except Exception as e:
    print(f"Error: {e}")
