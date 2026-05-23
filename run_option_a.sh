#!/bin/bash
./env311/bin/pip install langchain-google-genai python-dotenv requests
./env311/bin/python src/indexer/upload_gemini_batched.py
