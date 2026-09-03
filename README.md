# Sovereign RAG System

A self-hosted, air-gapped Retrieval-Augmented Generation (RAG) system with hybrid search capabilities. Designed for organizations with strict data sovereignty requirements.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-1.9+-red.svg)](https://qdrant.tech/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

A production-ready, self-hosted RAG system for secure document retrieval and question-answering entirely within your infrastructure—**no external API calls, no data leaving your premises**.

### Key Benefits

- 🔒 **Data Sovereignty**: All data stays on-premises
- 🚫 **Zero External Calls**: Complete network isolation
- 💰 **Cost Effective**: No ongoing API costs
- 🧠 **High Quality**: Open-weight models matching cloud AI capabilities
- 📄 **Multi-Format**: Supports PDF, DOCX, and TXT documents

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Hybrid Search** | Combines semantic (dense) and keyword (sparse) search using BGE-M3 |
| **Reciprocal Rank Fusion** | Intelligent result merging for optimal retrieval |
| **Source Citations** | Every answer includes references to source documents |
| **Self-Hosted LLM** | Qwen3-8B via Ollama—no API keys required |
| **Network Isolation** | Built-in verification of zero external calls |

## 🏗️ Architecture

```
User Interface (Next.js/React/API Clients)
           ↓ HTTP/REST API
       FastAPI Backend
           ↓
    ┌──────┴──────┐
    ↓             ↓
BGE-M3 Model   Qdrant Vector DB
(Embeddings)   (Dense + Sparse)
    ↓             ↓
    └──────┬──────┘
           ↓
    Qwen3-8B (Ollama)
    LLM Inference
```

### Data Flow

**Document Ingestion:**
1. Extract text (PDF/DOCX/TXT)
2. Chunk into 500-character segments (50-char overlap)
3. Generate BGE-M3 embeddings (dense + sparse)
4. Store in Qdrant

**Query Execution:**
1. Generate query embeddings (dense + sparse)
2. Parallel dense and sparse search
3. Merge results using Reciprocal Rank Fusion
4. Generate answer with Qwen3-8B LLM
5. Return answer + source citations

## 🧰 Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Embeddings | BAAI/bge-m3 | Dual dense + sparse vectors, 100+ language support |
| Vector DB | Qdrant | Native hybrid search, production-ready |
| LLM | Qwen3-8B (Ollama) | Fully open-source, local inference, ~GPT-3.5 quality |
| Backend | FastAPI | High-performance async API |
| Parsing | PyPDF2, python-docx | Reliable text extraction |

## 📋 Prerequisites

- Python 3.10+
- Docker (for Qdrant)
- Ollama (for Qwen3-8B)
- 8GB+ RAM recommended
- 10GB+ free disk space

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/rag-project.git
cd rag-project
```

### 2. Python Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start Qdrant (Vector Database)

```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  --name qdrant \
  qdrant/qdrant
```

### 4. Install & Start Ollama

```bash
# Download from https://ollama.com/download
# Pull Qwen3-8B
ollama pull qwen3:8b

# Start Ollama service
ollama serve
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

**`.env.example`:**
```env
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=my_documents

EMBEDDING_MODEL=BAAI/bge-m3

OLLAMA_BASE_URL=http://localhost:11434
CHAT_MODEL=qwen3:8b

MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=.pdf,.docx,.txt

ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 6. Start Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Verify Installation

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Document RAG API",
  "version": "3.0.0"
}
```

## 📡 API Reference

### Health Check
```http
GET /
```

### Upload Document
```http
POST /upload
Content-Type: multipart/form-data

Parameters: file (PDF, DOCX, TXT)
```

Response:
```json
{
  "status": "success",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "policy.pdf",
  "total_chunks": 15
}
```

### Query
```http
POST /query
Content-Type: application/json

{
  "question": "What is the vacation policy?",
  "top_k": 3
}
```

Response:
```json
{
  "answer": "According to the employee handbook, employees receive 15 days of paid vacation per year.",
  "sources": [
    {
      "source_index": 1,
      "filename": "policy.pdf",
      "rrf_score": 0.0325,
      "content_preview": "Employees receive 15 days of paid vacation..."
    }
  ]
}
```

### List Documents
```http
GET /documents
```

### Delete Document
```http
DELETE /documents/{document_id}
```

### Network Status
```http
GET /network-status
```

## 🚀 Usage

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Upload document
with open("policy.pdf", "rb") as f:
    response = requests.post(f"{BASE_URL}/upload", files={"file": f})
    doc_id = response.json()["document_id"]

# Query
response = requests.post(
    f"{BASE_URL}/query",
    json={"question": "What is the vacation policy?", "top_k": 3}
)

print(f"Answer: {response.json()['answer']}")
print(f"Sources: {response.json()['sources']}")
```

### cURL Examples

```bash
# Upload
curl -X POST "http://localhost:8000/upload" -F "file=@test.pdf"

# Query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'

# List documents
curl http://localhost:8000/documents

# Network status
curl http://localhost:8000/network-status
```

## 🧪 Testing

```bash
cd backend

# Run full test suite
python test_suite.py

# Run specific tests
pytest tests/test_rag_service.py -v

# Test network isolation (critical)
pytest tests/test_rag_service.py::test_no_external_calls -v
```

## 📊 Performance

| Operation | Average Time |
|-----------|--------------|
| Upload (10-page PDF) | 12s |
| Query (hybrid search) | 8-12s |
| LLM Generation | 5-8s |

**Scaling:**
- 1,000 chunks: ~5MB, ~12s query time
- 10,000 chunks: ~50MB, ~13s query time
- 100,000 chunks: ~500MB, ~15s query time

## 🔧 Troubleshooting

**Qdrant Connection Failed:**
```bash
docker ps | grep qdrant
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant
```

**Ollama Connection Failed:**
```bash
curl http://localhost:11434/api/tags
ollama pull qwen3:8b
```

**Out of Memory:**
```python
# Reduce chunk size in config.py
chunk_size = 300
```

**Slow Queries:**
```python
# Use CPU mode
device = "cpu"

# Reduce retrieval
top_k = 2
```

## 🔒 Security

- ✅ Documents never leave your infrastructure
- ✅ Embeddings generated locally
- ✅ LLM inference runs locally
- ✅ No usage data sent to third parties
- ✅ Built-in network isolation verification

### Recommended Practices

- Run on air-gapped network
- Add JWT/API key authentication
- Enable rate limiting
- Implement logging and monitoring
- Regular Qdrant snapshots

## 🗺️ Roadmap

**Completed:**
- ✅ Document upload (PDF, DOCX, TXT)
- ✅ Hybrid search with RRF
- ✅ Qwen3-8B LLM integration
- ✅ Network isolation verification
- ✅ Production FastAPI backend

**Planned:**
- Streaming responses
- OCR for scanned documents
- Semantic chunking
- Metadata filtering
- Cross-encoder re-ranking
- Web UI (Next.js/React)
- Docker Compose setup
- Kubernetes Helm chart

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/jatin26garg/rag-project/issues)
- **Documentation**: [Project Wiki](https://github.com/jatin26garg/rag-project/wiki)

---

Built with ❤️ for data sovereignty
