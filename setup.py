import os
from pathlib import Path
from sklearn.datasets import fetch_20newsgroups
import re

def clean_text(text):
    """Clean document text"""
    # Remove headers
    text = re.sub(r'^.*?\\n\\n', '', text, count=1, flags=re.DOTALL)
    # Remove email headers
    text = re.sub(r'^(From|Subject|Organization|Lines|NNTP-Posting-Host):.*$', '', text, flags=re.MULTILINE)
    # Remove extra whitespace
    text = re.sub(r'\\s+', ' ', text)
    return text.strip().lower()

def main():
    print("Downloading 20 Newsgroups dataset...")
    
    # Create directories
    docs_dir = Path("data/docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    cache_dir = Path("data/cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Fetch dataset (subset for manageable size)
    dataset = fetch_20newsgroups(
        subset='train',
        remove=('headers', 'footers', 'quotes'),
        categories=None  # All 20 categories
    )
    
    print(f"Processing {len(dataset.data)} documents...")
    
    # Save documents
    for idx, (text, target) in enumerate(zip(dataset.data[:1000], dataset.target[:1000])):
        category = dataset.target_names[target]
        
        # Clean text
        cleaned = clean_text(text)
        
        if len(cleaned) < 50:  # Skip very short docs
            continue
        
        # Save to file
        filename = f"doc_{idx:04d}_{category.replace('.', '_')}.txt"
        filepath = docs_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
    
    print(f"✓ Saved {len(list(docs_dir.glob('*.txt')))} documents to {docs_dir}")
    print("\\nNext steps:")
    print("1. Run: python -m src.embedder  (to generate embeddings)")
    print("2. Run: streamlit run src/streamlit_app.py  (to start UI)")

if __name__ == "__main__":
    main()