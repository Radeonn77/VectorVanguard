# 🛡️ VectorVanguard

**Offline-first, post-exam AI evidence investigation system.**

## 📌 Overview

VectorVanguard analyzes **static examination evidence** (images, CCTV snapshots, scanned IDs, OCR text, AI-generated scene descriptions, and metadata) collected *after* an exam — not live proctoring. It turns this evidence into a searchable knowledge base that administrators can query in natural language.

**Stack:** Computer Vision + OCR + Local Vision AI + Embeddings + Vector Search + SQL Search + RAG + LLM Reasoning — all running locally.

## 🎯 Problem Statement

Cloud-based proctoring raises privacy, cost, and connectivity concerns, and makes historical evidence hard to search. VectorVanguard instead acts as an **investigation assistant**, answering questions like:

- "Show evidence associated with student ID 1023."
- "Find evidence containing a mobile phone near an examination desk."
- "Which evidence belongs to session EXAM-2026-001?"

It retrieves relevant evidence and generates grounded answers via a local LLM — it does not make automated misconduct decisions.

## 🧠 Core Concept — RAG

```
User Question → LangGraph Router → [SQL Search | Vector Search] → Relevant Evidence → Local Ollama LLM → Evidence-Grounded Answer
```

- **SQL Search** — exact retrieval for IDs, timestamps, sessions, seat numbers.
- **Vector Search** — semantic retrieval for visual descriptions, objects, and behaviors.
- **LLM Reasoning** — synthesizes retrieved evidence into a natural-language answer.

## 🏗️ Architecture

**1. Ingestion:** Raw evidence → OpenCV preprocessing → Tesseract OCR + Ollama Vision Model → combined text → LangChain chunking → Ollama embeddings → PostgreSQL + pgvector.

**2. Query:** User question → LangGraph router picks SQL and/or vector search → evidence retrieved → passed to local LLM → grounded answer with evidence IDs (e.g. `EV-00124`).

**Key principle:** the LLM never invents evidence — it only reasons over what's retrieved.

## 🔐 Privacy-First

All processing — vision, OCR, embeddings, LLM reasoning, storage — stays local. No evidence leaves the environment, no external API calls, no internet dependency.

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React.js |
| Backend | FastAPI |
| Orchestration | LangGraph |
| RAG Framework | LangChain |
| Local AI (LLM/Vision/Embeddings) | Ollama |
| Computer Vision | OpenCV |
| OCR | Tesseract |
| Database | PostgreSQL |
| Vector Search | pgvector |
| Runtime | Python 3.12 |

## 🚀 Roadmap

- **Phase 0** — Workspace & environment setup
- **Phase 1** — Database & Ollama infrastructure
- **Phase 2** — Vision & OCR pipeline
- **Phase 3** — Embeddings & RAG storage
- **Phase 4** — LangGraph intelligence layer
- **Phase 5** — FastAPI backend
- **Phase 6** — React frontend

## ⚠️ Scope & Responsible AI

VectorVanguard is **not** intended to:

- ❌ Automatically accuse students of cheating
- ❌ Replace examination authorities or make disciplinary decisions
- ❌ Perform continuous biometric surveillance
- ❌ Guarantee that observed behavior constitutes misconduct

All AI output is investigative assistance, with final decisions left to human review.

## 👥 Team

**Project:** Offline AI Exam Proctoring Assistant
**Author:** Ankit Kumar Pradhan

## 📌 Status

🚧 Under active development.

---

*Process locally. Retrieve intelligently. Explain with evidence.*