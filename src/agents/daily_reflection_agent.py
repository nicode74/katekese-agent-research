import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

class DailyReflectionAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7
        )
        self.supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
        self.supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("SUPABASE_KEY", ""))

    def generate_reflection(self, date_str: str = None) -> dict:
        """Generate a Catholic daily pastoral reflection for a given date."""
        if not date_str:
            date_str = datetime.today().strftime('%Y-%m-%d')
            
        system_prompt = (
            "Anda adalah seorang Imam Katolik yang bijaksana dan penuh kasih. "
            "Tugas Anda adalah menulis Renungan Harian Katolik yang menyentuh hati, inspiratif, dan berakar pada Injil.\n"
            "Format jawaban Anda HARUS berupa objek JSON valid dengan field berikut:\n"
            '{\n'
            '  "judul": "Judul Renungan yang menarik",\n'
            '  "ayat_referensi": "Referensi Kitab Suci (misal: Yohanes 14:1-6)",\n'
            '  "isi": "Isi renungan 3-4 paragraf pendek yang mendalam dan relevan untuk kehidupan sehari-hari.",\n'
            '  "tanggal": "YYYY-MM-DD"\n'
            '}'
        )
        
        user_prompt = f"Buatkan Renungan Harian Katolik untuk tanggal {date_str}."
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            res = self.llm.invoke(messages)
            text = res.content.strip()
            
            # Extract JSON substring
            if "{" in text and "}" in text:
                json_str = text[text.find("{"):text.rfind("}")+1]
                data = json.loads(json_str)
                data["tanggal"] = date_str
                return data
        except Exception as e:
            print(f"[!] Reflection Generation Error: {e}")
            
        # Fallback default reflection
        return {
            "judul": "Berjalan Dalam Terang Kristus",
            "ayat_referensi": "Yohanes 8:12",
            "isi": "Kristus adalah terang dunia. Barangsiapa mengikut Dia, ia tidak akan berjalan dalam kegelapan, melainkan ia akan mempunyai terang hidup. Mari kita senantiasa membuka hati bagi bimbingan Roh Kudus dalam setiap langkah hidup kita hari ini.",
            "tanggal": date_str
        }

    def save_to_supabase(self, reflection_data: dict) -> bool:
        """Save generated reflection directly to Supabase renungan table."""
        if not self.supabase_url or not self.supabase_key:
            print("[!] Supabase credentials not found. Cannot save reflection.")
            return False

        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

        url = f"{self.supabase_url}/rest/v1/renungan"
        
        try:
            res = requests.post(url, headers=headers, json=reflection_data)
            if res.status_code in [200, 201]:
                print(f"[✓] Daily reflection for {reflection_data.get('tanggal')} saved to Supabase successfully!")
                return True
            else:
                print(f"[!] Supabase POST error ({res.status_code}): {res.text}")
        except Exception as e:
            print(f"[!] Error posting reflection to Supabase: {e}")

        return False

    def run_daily_job(self, date_str: str = None) -> dict:
        """Run full reflection pipeline: generate and save to database."""
        reflection = self.generate_reflection(date_str)
        saved = self.save_to_supabase(reflection)
        reflection["saved_to_db"] = saved
        return reflection

if __name__ == "__main__":
    agent = DailyReflectionAgent()
    result = agent.run_daily_job()
    print("Reflection Output:", json.dumps(result, indent=2))
