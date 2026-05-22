import os
from dotenv import load_dotenv
from supabase.client import Client, create_client

load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_key:
    print("No Supabase URL or Key")
    exit(1)

supabase = create_client(supabase_url, supabase_key)
try:
    response = supabase.table("documents").select("id", count="exact").limit(1).execute()
    print("Documents count:", response.count)
except Exception as e:
    print("Error querying supabase:", e)
