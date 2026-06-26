# Agentic Contract RAG AI

An Agentic Retrieval-Augmented Generation (RAG) system that extracts structured information from legal contracts using semantic search, vector embeddings, and a Large Language Model (LLM).

---

## Overview

This project processes legal contract PDFs and converts unstructured content into structured JSON that conforms to a predefined JSON Schema.

The pipeline performs:

* PDF text extraction
* Table extraction
* Semantic document chunking
* Dense vector embedding generation
* FAISS-based semantic retrieval
* Schema-driven information extraction using an LLM
* JSON Schema validation
* Structured JSON output generation

---

## Architecture

```text
                   Contract PDF
                        │
                        ▼
                 PDF Text Extraction
                        │
                        ▼
                 Table Extraction
                        │
                        ▼
                Document Builder
                        │
                        ▼
               Semantic Chunking
                        │
                        ▼
              BGE Text Embeddings
                        │
                        ▼
               FAISS Vector Store
                        │
                        ▼
             Semantic Retrieval
                        │
                        ▼
               Context Builder
                        │
                        ▼
          Prompt Construction
                        │
                        ▼
      Groq (Llama 3.3 70B Versatile)
                        │
                        ▼
             Extraction Agent
                        │
                        ▼
              Validator Agent
                        │
                        ▼
             Structured JSON Output
```

---

## Features

* Semantic chunking for legal contracts
* PDF and table extraction
* Dense vector embeddings using Sentence Transformers
* FAISS-based semantic retrieval
* Schema-guided information extraction
* JSON Schema validation
* Modular Agent-based architecture
* Configurable LLM backend
* Structured JSON output

---

## Tech Stack

### Language

* Python 3.11+

### AI & LLM

* Groq API
* Llama 3.3 70B Versatile

### Embeddings

* BAAI/bge-small-en-v1.5
* Sentence Transformers

### Vector Search

* FAISS

### Document Processing

* pdfplumber
* Camelot

### Validation

* JSON Schema (Draft 2020-12)
* jsonschema

### CLI & Utilities

* Typer
* python-dotenv
* NumPy
* Rich Logging

---

## Project Structure

```text
app/
├── agents/
├── chunking/
├── embeddings/
├── ingestion/
├── llm/
├── prompts/
├── retrieval/
├── schemas/
├── utils/
└── vectorstore/

run.py
requirements.txt
README.md
PROMPTS.md
LICENSE
```

---

## Installation

```bash
git clone <repository-url>

cd contract-rag-ai

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## Running the Project

```bash
python run.py \
--pdf "data/contracts/Track1_Sample_Contract.pdf" \
--schema "data/schema/Track1_Extraction_Schema.json"
```

The generated output will be saved as:

```text
data/output/output.json
```

---

## Repository Notes

The following files are intentionally **not included** in this repository:

* Sample contract PDF(s) supplied as part of the coding challenge
* Challenge-provided JSON extraction schema
* Local environment files (`.env`)
* Generated output files
* Local vector database

These files are excluded to avoid redistributing challenge materials and local artifacts.

---

## Current Capabilities

* Contract text extraction
* Table extraction
* Semantic chunking
* Semantic retrieval
* Schema-driven extraction
* JSON validation
* Structured JSON generation

---

## Future Improvements

* Hybrid semantic + keyword retrieval
* Cross-encoder reranking
* Multi-document processing
* Persistent vector database
* REST API
* Web interface

---

## Author

**Siddhesh Nikumb**

Bachelor of Computer Engineering

Cloud • DevOps • AI Engineering
