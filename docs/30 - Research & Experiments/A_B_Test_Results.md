# RAG Agent A/B Test Results

This document contains automated evaluation results comparing different LLM orchestrations.

## Test Questions
1. Apa kewajiban seorang Uskup dalam memelihara iman umat menurut hukum gereja?
2. Berapa jumlah sakramen dalam Gereja Katolik?
3. Jelaskan secara singkat apa itu dosa asal berdasarkan Katekismus.

## Evaluation Matrix

| Agent | Question | Latency | Status | Answer Snippet |
| :--- | :--- | :--- | :--- | :--- |
| Gemini 2.0 Flash | Q1 | 3.09s | Failed | ERROR: 404 models/gemini-1.5-flash is not found for API version v1beta, or is not supported for generateContent. Call ModelService.ListModels to see the list of available models and their supported me... |
| Gemini 2.0 Flash | Q2 | 7.07s | Failed | ERROR: 404 models/gemini-1.5-flash is not found for API version v1beta, or is not supported for generateContent. Call ModelService.ListModels to see the list of available models and their supported me... |
| Gemini 2.0 Flash | Q3 | 2.82s | Failed | ERROR: 404 models/gemini-1.5-flash is not found for API version v1beta, or is not supported for generateContent. Call ModelService.ListModels to see the list of available models and their supported me... |
| Groq (Llama 3.3 70B) | Q1 | 2.88s | Success | Menurut konteks yang diberikan, kewajiban seorang Uskup dalam memelihara iman umat adalah untuk mempertahankan, melaksanakan, dan mengakui iman yang diturunkan dari para Rasul [1]. Selain itu, Uskup j... |
| Groq (Llama 3.3 70B) | Q2 | 2.04s | Success | Menurut konteks yang diberikan, terutama pada Katekismus No 15, disebutkan bahwa keselamatan yang dikerjakan oleh Allah melalui Yesus Kristus dalam Roh Kudus dihadirkan bagi kita melalui kegiatan-kegi... |
| Groq (Llama 3.3 70B) | Q3 | 3.05s | Success | Dosa asal adalah suatu konsep teologi Katolik yang merujuk pada dosa yang dilakukan oleh manusia pertama, Adam dan Hawa, yang menyebabkan mereka kehilangan persahabatan dengan Tuhan. Dosa asal ini mem... |
