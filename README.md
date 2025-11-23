<<<<<<< HEAD
`# Multi-Document Embedding Search Engine

## Overview
A semantic search engine built with caching, vector embeddings, and a clean API. Searches 20 Newsgroups dataset using sentence transformers.

## Features
- ✅ Embedding generation with sentence-transformers
- ✅ SQLite-based caching (no recomputation)
- ✅ FAISS vector search
- ✅ FastAPI backend
- ✅ Streamlit UI
- ✅ Ranking explanations with keyword overlap

## Installation

\`\`\`bash
# Clone repository
git clone <your-repo-url>
cd multi-doc-search-engine

# Install dependencies
pip install -r requirements.txt

# Download and prepare data
python setup.py
\`\`\`

## How It Works

### 1. Caching System
- Uses SQLite to store document embeddings
- Each document has a SHA256 hash
- If document unchanged → reuse cached embedding
- If document changes → regenerate embedding
- Cache schema: doc_id, embedding (blob), hash, updated_at

### 2. Embedding Generation
- Model: sentence-transformers/all-MiniLM-L6-v2
- Generates 384-dim vectors
- Batch processing for efficiency
- Run: \`python -m src.embedder\`

### 3. Vector Search
- FAISS IndexFlatIP (inner product)
- Normalized embeddings for cosine similarity
- Returns top-k most similar documents

## Usage

### Run Streamlit UI (Recommended)
\`\`\`bash
streamlit run src/streamlit_app.py
\`\`\`
Then open http://localhost:8501

### Run FastAPI (Alternative)
\`\`\`bash
uvicorn src.api:app --reload
\`\`\`
API docs at http://localhost:8000/docs

### API Example
\`\`\`bash
curl -X POST "http://localhost:8000/search" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "quantum physics basics", "top_k": 5}'
\`\`\`

## Folder Structure
\`\`\`
multi-doc-search-engine/
├── src/
│   ├── embedder.py          # Embedding generation
│   ├── cache_manager.py     # SQLite caching
│   ├── search_engine.py     # FAISS vector search
│   ├── api.py               # FastAPI endpoints
│   └── streamlit_app.py     # UI (main entry)
├── data/
│   ├── docs/                # 20 Newsgroups texts
│   └── cache/               # embeddings.db
├── requirements.txt
├── README.md
└── setup.py
\`\`\`

## Design Choices

1. **sentence-transformers over OpenAI**: Free, local, fast
2. **SQLite for cache**: Simple, reliable, no external DB
3. **FAISS IndexFlatIP**: Exact search, no approximation
4. **Streamlit**: Easy deployment to Streamlit Cloud
5. **Modular design**: Each component is independent

## Deployment (Streamlit Cloud)

1. Push code to GitHub (exclude data/ in .gitignore)
2. Go to share.streamlit.io
3. Connect your repo
4. Set main file: \`src/streamlit_app.py\`
5. Deploy!

Note: First run will download data and generate embeddings (~2 min)

## Performance
- 1000 documents embedded in ~30 seconds
- Search query: <50ms
- Cache hit: 0ms (instant)
- Memory: ~100MB for 1000 docs`,
=======
# Multi-document-search-engine
Search across multiple documents with ease fast!!!
>>>>>>> f3d3e308b4415621db1e512c71780d2c246314b4
