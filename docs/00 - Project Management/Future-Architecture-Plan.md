# Future Architecture & Scale Planning

## 1. Current State & Identified Bottlenecks
As documented in the Research & Experiments phase (`docs/30 - Research & Experiments/Cross_Lingual_Embedding_Degradation.md`), the current Ecclesia-RAG pipeline is bound by three strict physical constraints:
1. **Railway Free-Tier Limit**: Hard cap of 500MB RAM.
2. **Local Network Limitations**: ISP forcibly drops Hugging Face model downloads exceeding ~280MB.
3. **Environment Compatibility**: The virtual environment uses Python 3.14 Alpha, which causes fatal `TypeError` metaclass crashes within Google's Protobuf library, blocking the use of the 0MB RAM Gemini Embeddings API.

These constraints forced the adoption of the `all-MiniLM-L6-v2` (80MB) embedding model. Because it is an English-only model, it causes **Cross-Lingual Degradation** when querying the Indonesian corpus (e.g., Alkitab TB), resulting in empty context returns for native Indonesian queries.

## 2. Strategic Roadmap for Full Multilingual Support
To achieve flawless semantic retrieval across both English (Encyclicals) and Indonesian (Alkitab) documents, the architecture must break one of the current physical constraints. The following two paths have been identified for future implementation:

### Option A: The Environment Optimization Path (Recommended for Free Tier)
This path focuses on resolving software incompatibilities to leverage external zero-RAM embedding APIs.
- **Action**: Downgrade the project's virtual environment from Python 3.14 Alpha to a stable release (Python 3.12 or 3.11).
- **Result**: This resolves the Protobuf metadata crash.
- **Implementation**: 
  1. Rebuild the `venv`.
  2. Implement `GoogleGenerativeAIEmbeddings` (specifically `models/embedding-001`).
  3. Batch the embedding ingestion script (100 chunks per request) to stay safely beneath the 1,500 Requests-Per-Day quota.
- **Benefits**: Costs $0, fully bypasses the local ISP download throttle, completely eliminates Railway RAM usage for vector generation, and provides state-of-the-art multilingual understanding.

### Option B: The Hardware Scaling Path (Production/Enterprise)
This path focuses on vertical scaling to support massive, locally-hosted multilingual open-source models, removing dependency on external APIs like Google Gemini.
- **Action**: Upgrade the Railway deployment tier (e.g., Hobby Plan or Pro Plan) to expand available RAM from 500MB to 8GB+.
- **Result**: Sufficient memory headroom to load advanced XLM-RoBERTa architectures.
- **Implementation**:
  1. Replace `all-MiniLM-L6-v2` with `paraphrase-multilingual-MiniLM-L12-v2` (471MB) or `multilingual-e5-large` (1.5GB).
  2. Perform embedding logic natively on the Railway server.
- **Benefits**: Zero rate limits, zero API dependencies, highest possible data privacy, and mathematically perfect semantic alignment for the Indonesian text corpus.

## 3. Next Steps (Action Items)
- **Immediate Task**: Complete the UTS Midterm Report utilizing the current English-optimized `L6` model to demonstrate understanding of system constraints and vocabulary alignment.
- **Post-UTS Goal**: Execute **Option A** by migrating the project to Python 3.12 and transitioning the vector store fully to Google Gemini Embeddings.
