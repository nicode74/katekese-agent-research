import pytest

# from src.indexer.retriever import Retriever

class MockRetriever:
    def __init__(self, top_k=3):
        self.top_k = top_k
        self.database = ["Dokumen KWI", "Alkitab TB", "Katekismus"]

    def retrieve(self, query):
        if not query:
            raise ValueError("Query cannot be empty")
        # Mock returning top K
        return self.database[:self.top_k]

def test_retriever_initialization():
    retriever = MockRetriever(top_k=5)
    assert retriever.top_k == 5

def test_retriever_returns_top_k():
    retriever = MockRetriever(top_k=2)
    results = retriever.retrieve("Tuhan Yesus")
    assert len(results) == 2

def test_retriever_empty_query():
    retriever = MockRetriever()
    with pytest.raises(ValueError, match="Query cannot be empty"):
        retriever.retrieve("")
