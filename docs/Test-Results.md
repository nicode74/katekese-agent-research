# Test Results - May 22, 2026

## Execution Summary
- **Date**: Friday, May 22, 2026
- **Environment**: Linux (Python 3.14.5)
- **Virtual Env**: `venv_rag`
- **Total Tests**: 9
- **Passed**: 9
- **Failed**: 0
- **Skipped**: 0

## Details

### Unit Tests
- `test/test_chunker.py`: 3/3 Passed. Verifies text splitting logic.
- `test/test_retriever.py`: 3/3 Passed (Mocked). Verifies retrieval interface and top-k logic.

### Integration Tests (API)
- `test/test_api_blackbox.py`: 3/3 Passed.
    - Verified `/health` endpoint.
    - Verified `/chat` endpoint with SSE (Server-Sent Events) streaming.
    - Verified validation for missing message payloads (422 error).

## Environment Notes
The project was tested on Python 3.14. A compatibility issue with `protobuf` and Python 3.14's metaclass implementation was encountered and resolved by upgrading to `protobuf>=5.0.0` (specifically `7.35.0`).

### Requirements Status
All dependencies from `requirements.txt` are installed in `venv_rag`.

### Known Issues/Warnings
- **Supabase**: During API startup, a warning was issued regarding missing Supabase credentials. Real RAG functionality requiring remote vector search will require these credentials in the `.env` file.

## How to run tests
```bash
./venv_rag/bin/pytest test/
```
