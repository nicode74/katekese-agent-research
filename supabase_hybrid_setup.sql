-- 1. Create a GIN index for simple text matching on the content column
CREATE INDEX IF NOT EXISTS documents_content_fts_idx ON documents USING GIN (to_tsvector('simple', content));

-- 2. Create a hybrid search function using Reciprocal Rank Fusion (RRF)
CREATE OR REPLACE FUNCTION match_documents_hybrid (
  query_text TEXT,
  query_embedding VECTOR(384),
  match_count INT DEFAULT 5,
  filter JSONB DEFAULT '{}',
  rrf_k INT DEFAULT 60
) RETURNS TABLE (
  id UUID,
  content TEXT,
  metadata JSONB,
  similarity FLOAT,
  fts_rank FLOAT,
  rrf_score FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  WITH fts_results AS (
    SELECT 
      documents.id,
      ts_rank_cd(to_tsvector('simple', documents.content), plainto_tsquery('simple', query_text))::float as fts_rank,
      ROW_NUMBER() OVER (ORDER BY ts_rank_cd(to_tsvector('simple', documents.content), plainto_tsquery('simple', query_text)) DESC) as rank
    FROM documents
    WHERE to_tsvector('simple', documents.content) @@ plainto_tsquery('simple', query_text)
      AND documents.metadata @> filter
    LIMIT match_count * 2
  ),
  vector_results AS (
    SELECT 
      documents.id,
      (1 - (documents.embedding <=> query_embedding))::float as similarity,
      ROW_NUMBER() OVER (ORDER BY documents.embedding <=> query_embedding ASC) as rank
    FROM documents
    WHERE documents.metadata @> filter
    LIMIT match_count * 2
  )
  SELECT 
    d.id,
    d.content,
    d.metadata,
    COALESCE(v.similarity, 0.0)::FLOAT as similarity,
    COALESCE(f.fts_rank, 0.0)::FLOAT as fts_rank,
    (
      COALESCE(1.0 / (rrf_k + f.rank), 0.0) + 
      COALESCE(1.0 / (rrf_k + v.rank), 0.0)
    )::FLOAT as rrf_score
  FROM documents d
  LEFT JOIN fts_results f ON d.id = f.id
  LEFT JOIN vector_results v ON d.id = v.id
  WHERE f.id IS NOT NULL OR v.id IS NOT NULL
  ORDER BY rrf_score DESC
  LIMIT match_count;
END;
$$;
