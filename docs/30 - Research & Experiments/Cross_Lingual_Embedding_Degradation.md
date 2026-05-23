# Analysis of Cross-Lingual Embedding Degradation in Resource-Constrained RAG Pipelines

## 1. Architectural Constraints & Trade-Offs
During the deployment of the Ecclesia-RAG pipeline to the cloud environment (Railway), two significant infrastructure constraints were encountered:
1. **Cloud Memory Limits:** The free-tier container was strictly limited to 500MB of RAM.
2. **ISP Bandwidth Throttling:** Local ISP routing actively dropped large model downloads (specifically Hugging Face `.safetensors` files exceeding ~280MB).

Initially, the architecture was designed to utilize `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (471MB), which provides robust cross-lingual semantic mapping. However, loading this model alongside the FastAPI server caused immediate Out-Of-Memory (OOM) crashes on the 500MB server, and local caching failed due to the ISP limit.

To bypass these hard constraints, a strategic downgrade was executed: the embedding model was switched to **`sentence-transformers/all-MiniLM-L6-v2`** (80MB). This lightweight model easily satisfied the memory ceiling while avoiding local ISP limits.

## 2. The Cross-Lingual Degradation Phenomenon
While the `all-MiniLM-L6-v2` model successfully restored system stability and achieved a 100% vector ingestion rate into the Supabase pgvector database, a critical **Data Mining phenomenon** was observed during retrieval testing.

### Observation A: High-Precision English Retrieval
When the orchestrator was queried with an English semantic prompt (`"Who is Jesus?"`), the model flawlessly retrieved the top-K relevant chunks from the English subset of the corpus (e.g., *Papal Encyclicals*). The cosine similarity was high, and the LLM synthesizer successfully generated a deeply theological, cited response.

### Observation B: Semantic Misalignment on Indonesian Queries
When queried with an Indonesian semantic prompt (`"Apa yang terjadi di Kitab Wahyu?"` or translated English queries against the Indonesian corpus), the RAG pipeline returned **zero relevant results**, prompting the LLM to output a "Context is Empty" refusal.

### Root Cause Analysis
The `all-MiniLM-L6-v2` model is mathematically bounded to an **English-only vocabulary space**. It completely lacks the multi-dimensional mapping required to associate Indonesian tokens (e.g., "Wahyu") with their English semantic equivalents (e.g., "Revelation"). 
When reading the Indonesian corpus (e.g., *Alkitab TB*), the model maps the Indonesian tokens to mathematically isolated or disjointed clusters within the 384-dimensional vector space. Consequently, during a Cosine Similarity search, the distance between the query vector and the correct Indonesian document vector falls well below the Supabase `match_threshold`, resulting in empty context arrays.

## 3. Academic Conclusion
This deployment perfectly demonstrates a core Data Mining principle in modern NLP architectures: **Vocabulary Alignment**. 

Optimizing a RAG system for pure infrastructure performance (RAM and bandwidth) by selecting a monolingual embedding model guarantees systemic failure when applied to a bilingual or cross-lingual text corpus. The mathematical degradation of vector space cohesion across unmapped languages proves that embedding selection must prioritize linguistic architecture over raw size when handling diverse datasets. 

For the purposes of this RAG demonstration, maximum accuracy is achieved by querying the system using English prompts directed at the English-language documents (e.g., Catholic Encyclicals), perfectly showcasing the theoretical limits of the `L6` model.
