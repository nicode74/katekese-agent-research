# RAG Agent A/B Test Results

This document contains automated evaluation results comparing different LLM orchestrations.

## Test Questions
1. Apa kewajiban seorang Uskup dalam memelihara iman umat menurut hukum gereja?
2. Berapa jumlah sakramen dalam Gereja Katolik?
3. Jelaskan secara singkat apa itu dosa asal berdasarkan Katekismus.

## Evaluation Matrix

| Agent | Question | Latency | Status | Answer Snippet |
| :--- | :--- | :--- | :--- | :--- |
| Gemini 2.0 Flash | Q1 | 2.81s | Failed | ERROR: 404 models/gemini-1.5-flash is not found for API version v1beta, or is not supported for generateContent. Call ModelService.ListModels to see the list of available models and their supported me... |
| Gemini 2.0 Flash | Q2 | 0.10s | Failed | ERROR: Error embedding content: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate... |
| Gemini 2.0 Flash | Q3 | 0.10s | Failed | ERROR: Error embedding content: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate... |
| Groq (Llama 3.3 70B) | Q1 | 0.26s | Failed | ERROR: Error embedding content: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate... |
| Groq (Llama 3.3 70B) | Q2 | 0.19s | Failed | ERROR: Error embedding content: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate... |
| Groq (Llama 3.3 70B) | Q3 | 0.11s | Failed | ERROR: Error embedding content: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate... |
