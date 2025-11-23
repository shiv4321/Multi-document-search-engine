"""
FastAPI backend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from .search_engine import SearchEngine

app = FastAPI(title="Multi-Document Search API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search engine
search_engine = None

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResponse(BaseModel):
    results: List[dict]

@app.on_event("startup")
async def startup_event():
    """Build search index on startup"""
    global search_engine
    search_engine = SearchEngine()
    search_engine.build_index()

@app.get("/")
async def root():
    return {
        "message": "Multi-Document Search API",
        "endpoints": {
            "/search": "POST - Search documents",
            "/docs": "API documentation"
        }
    }

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Search documents"""
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = search_engine.search(request.query, request.top_k)
    
    return {"results": results}

@app.get("/document/{doc_id}")
async def get_document(doc_id: str):
    """Get full document text"""
    if search_engine is None:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    text = search_engine.get_document(doc_id)
    
    if not text:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"doc_id": doc_id, "text": text}