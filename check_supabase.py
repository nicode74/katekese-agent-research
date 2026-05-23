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

url = os.environ.get("SUPABASE_URL").rstrip('/') + "/rest/v1/documents?select=id"
key = os.environ.get("SUPABASE_SERVICE_KEY")

req = urllib.request.Request(url, headers={
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Prefer": "count=exact",
    "Range-Unit": "items",
    "Range": "0-0"
})
try:
    with urllib.request.urlopen(req) as resp:
        # The exact count is returned in the Content-Range header
        content_range = resp.getheader("Content-Range")
        count = content_range.split('/')[-1] if content_range else "Unknown"
        print(f"Total documents successfully uploaded: {count}")
except Exception as e:
    print(f"Error: {e}")
