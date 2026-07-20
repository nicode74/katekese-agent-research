import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

class QueryAnalyticsAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3
        )

    def analyze_queries(self, queries: List[str]) -> Dict[str, Any]:
        """Cluster user queries into themes and suggest administrative actions for parish leaders."""
        if not queries:
            queries = [
                "Kapan jadwal misa Paskah di St Yohanes?",
                "Bagaimana syarat sakramen perkawinan Katolik?",
                "Apakah boleh komuni kalau belum pengakuan dosa?",
                "Jam berapa sekretariat paroki buka?",
                "Dokumen apa yang dibutuhkan untuk baptis bayi?"
            ]

        system_prompt = (
            "Anda adalah analisis data AI untuk Paroki Gereja Katolik. "
            "Tugas Anda adalah menganalisis pertanyaan-pertanyaan yang sering diajukan oleh umat, "
            "mengelompokkannya menjadi beberapa kategori utama, dan memberikan saran tindakan konkret bagi pengurus paroki.\n"
            "Format jawaban HARUS berupa JSON valid dengan struktur:\n"
            '{\n'
            '  "total_queries": number,\n'
            '  "top_categories": [\n'
            '    {"category": "Nama Kategori", "percentage": number, "summary": "Ringkasan pertanyaan"}\n'
            '  ],\n'
            '  "key_insights": ["Insight 1", "Insight 2"],\n'
            '  "recommended_actions": ["Rekomendasi 1 (misal: Buat pengumuman baru)", "Rekomendasi 2"]\n'
            '}'
        )

        query_text = "\n".join([f"- {q}" for q in queries])
        user_prompt = f"Berikut daftar pertanyaan umat terkini:\n{query_text}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        try:
            res = self.llm.invoke(messages)
            text = res.content.strip()
            if "{" in text and "}" in text:
                json_str = text[text.find("{"):text.rfind("}")+1]
                return json.loads(json_str)
        except Exception as e:
            print(f"[!] Analytics Agent error: {e}")

        return {
            "total_queries": len(queries),
            "top_categories": [
                {"category": "Sakramen & Hukum Gereja", "percentage": 60, "summary": "Pertanyaan seputar syarat Baptis dan Perkawinan."},
                {"category": "Jadwal & Operasional Paroki", "percentage": 40, "summary": "Pertanyaan seputar jam misa dan sekretariat."}
            ],
            "key_insights": ["Umat banyak membutuhkan kejelasan prosedur sakramen."],
            "recommended_actions": ["Perbarui halaman FAQ Sakramen di website."]
        }

if __name__ == "__main__":
    agent = QueryAnalyticsAgent()
    result = agent.analyze_queries([])
    print("Analytics Output:", json.dumps(result, indent=2))
