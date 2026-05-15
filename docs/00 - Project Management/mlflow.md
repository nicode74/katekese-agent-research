Project A: The Research & MLOps Engine (Back-End)

Objective: Develop a robust Agentic RAG pipeline for Catholic Theology with integrated MLOps tracking.
1. Core Specifications

    Pipeline: ETL (Extract, Transform, Load) for religious datasets (Alkitab, KHK, KKGK, KWI Documents).

    Logic: Hybrid LLM Orchestration using Llama 3 as a local intent router and Gemini 1.5 as the primary response synthesizer.

    Vector Database: Supabase (pgvector) for high-dimensional semantic search.

    MLOps Suite: MLflow integrated with Dagshub for remote experiment tracking and artifact versioning.

2. Technical Requirements

    Data Cleaning: Modular Python classes in src/processors/ to handle specific noise patterns from church-domain PDFs and HTML.

    Embedding Strategy: Implement text-embedding-004 with recursive character chunking (Chunk: 800, Overlap: 10%).

    Batching Logic: Asynchronous batch processing for upserting 40,000+ records to prevent API rate-limiting.

    API Layer: FastAPI serving an /ask endpoint with streaming capabilities.

3. Success Metrics (MLflow Tracking)

    Log chunk_size, embedding_model, and temperature.

    Track retrieval_latency and context_relevance.

    Store master_dataset.jsonl as an MLflow artifact.