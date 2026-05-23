# Future Architecture & Scale Planning

## 1. Current State & Identified Bottlenecks
As documented in the Research & Experiments phase (`docs/30 - Research & Experiments/Cross_Lingual_Embedding_Degradation.md`), the current Ecclesia-RAG pipeline is bound by three strict physical constraints:
1. **Railway Free-Tier Limit**: Hard cap of 500MB RAM.
2. **Local Network Limitations**: ISP forcibly drops Hugging Face model downloads exceeding ~280MB.
3. **Environment Compatibility**: The virtual environment uses Python 3.14 Alpha, which causes fatal `TypeError` metaclass crashes within Google's Protobuf library, blocking the use of the 0MB RAM Gemini Embeddings API.

These constraints forced the adoption of the `all-MiniLM-L6-v2` (80MB) embedding model. Because it is an English-only model, it causes **Cross-Lingual Degradation** when querying the Indonesian corpus (e.g., Alkitab TB), resulting in empty context returns for native Indonesian queries.

## 2. Post-UTS Production Architecture Options (For Local Church Deployment)
To make this system fully usable for the local church, it must perfectly understand Bahasa Indonesia without crashing the Railway server or hitting daily API limits. Based on our empirical testing, the following three paths are the most viable for production:

### Option A: The "Alternative Free API" Path (Easiest)
Google Gemini restricted us with a 1,000 string/day limit, but other API providers offer superior free tiers optimized for multilingual data.
- **Action**: Swap the embedding engine from local `all-MiniLM-L6-v2` to **Voyage AI** (`voyage-multilingual-2`) or **Cohere** (`embed-multilingual-v3.0`).
- **Benefits**: Voyage AI provides 50 Million tokens per month for free (the entire Alkitab is ~2M tokens). This costs $0/month, uses 0MB of Railway RAM, and provides state-of-the-art Indonesian semantic understanding.

### Option B: The "$4/Month Dedicated Server" Path (Most Robust)
The core architectural bottleneck is Railway's 500MB RAM limit, which prevents the loading of large open-source multilingual models.
- **Action**: Migrate the deployment from Railway Free Tier to a basic Cloud VPS (e.g., Hetzner or DigitalOcean) costing ~$4/month for 4GB of RAM.
- **Benefits**: 4GB of RAM is more than enough to natively run the massive `paraphrase-multilingual-MiniLM-L12-v2` offline embedding model. This creates a 100% sovereign system with zero rate limits, no API dependencies, and perfect data privacy.

### Option C: The "Hybrid Keyword Search" Path (The Engineering Route)
If the goal is to maintain $0 monthly costs and keep the lightweight English `L6` model, the system can bypass the cross-lingual vector search problem by using traditional text matching.
- **Action**: Modify the orchestration logic (`agent_logic.py`) to perform a "Hybrid Search" utilizing Supabase's native PostgreSQL Full-Text Search (BM25).
- **Benefits**: When a user queries "Apa isi Kitab Wahyu?", the vector similarity search will fail, but the BM25 keyword search will instantly locate the exact Indonesian text in the database. This requires zero extra RAM and costs $0.

## 3. Next Steps (Action Items)
- **Immediate Task**: Complete the UTS Midterm Report utilizing the current English-optimized `L6` model to demonstrate a deep understanding of Data Mining constraints, cloud limitations, and vocabulary alignment.
- **Post-UTS Goal**: Present the 3 Production Options to the church leadership to decide whether to adopt an Alternative Free API (Option A) or invest in a small $4/month server (Option B) for the final deployment.
