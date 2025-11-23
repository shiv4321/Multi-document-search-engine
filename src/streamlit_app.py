"""
Streamlit UI for search engine
"""
import streamlit as st

# Page config MUST be first!
st.set_page_config(
    page_title="Multi-Document Search Engine",
    page_icon="🔍",
    layout="wide"
)

from pathlib import Path
import sys
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.search_engine import SearchEngine

# Auto-download data if missing
def setup_data():
    """Download data if not exists"""
    docs_dir = Path("data/docs")
    if not docs_dir.exists() or len(list(docs_dir.glob("*.txt"))) == 0:
        st.info("📥 First run detected! Downloading dataset... (~30 seconds)")
        
        import subprocess
        result = subprocess.run([sys.executable, "setup.py"], capture_output=True, text=True)
        
        if result.returncode != 0:
            st.error(f"Failed to download data: {result.stderr}")
            st.stop()
        
        st.success("✅ Dataset downloaded!")

# Initialize
@st.cache_resource
def load_search_engine():
    """Load and cache search engine"""
    setup_data()
    
    with st.spinner("🔄 Building search index... This takes ~1 minute on first run."):
        engine = SearchEngine()
        engine.build_index()
    
    return engine

# Main app
def main():
    st.title("🔍 Multi-Document Search Engine")
    st.markdown("Semantic search over 20 Newsgroups dataset using AI embeddings")
    
    # Load engine
    try:
        search_engine = load_search_engine()
        st.success("✅ Search engine ready!")
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        top_k = st.slider("Number of results", 1, 20, 5)
        
        st.markdown("---")
        st.markdown("### About")
        st.info("""
        This search engine uses:
        - **sentence-transformers** for embeddings
        - **FAISS** for vector search
        - **SQLite** for caching
        
        Features:
        ✅ Semantic similarity search
        ✅ Keyword overlap analysis
        ✅ Smart caching (no recomputation)
        """)
    
    # Search interface
    query = st.text_input(
        "Enter your search query:",
        placeholder="e.g., quantum physics, baseball statistics, computer graphics..."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    # Initialize session state for showing full text
    if 'show_full' not in st.session_state:
        st.session_state.show_full = set()
    
    # Search
    if search_button and query:
        with st.spinner("Searching..."):
            start_time = time.time()
            results = search_engine.search(query, top_k)
            search_time = time.time() - start_time
        
        st.success(f"Found {len(results)} results in {search_time:.2f}s")
        
        # Display results
        for i, result in enumerate(results, 1):
            doc_id = result['doc_id']
            
            with st.expander(f"**{i}. {doc_id}** (Score: {result['score']:.3f})", expanded=(i<=3)):
                st.markdown(f"**Preview:** {result['preview']}")
                
                st.markdown("---")
                st.markdown("**📊 Ranking Explanation:**")
                
                exp = result['explanation']
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Semantic Similarity", f"{exp['semantic_similarity']:.3f}")
                col2.metric("Keyword Overlap", f"{exp['overlap_ratio']*100:.0f}%")
                col3.metric("Document Length", f"{exp['doc_length']} words")
                
                if exp['keyword_overlap']:
                    st.markdown(f"**Overlapping keywords:** {', '.join(exp['keyword_overlap'])}")
                
                # Full text toggle button
                button_label = "Hide full text" if doc_id in st.session_state.show_full else "Show full text"
                
                if st.button(button_label, key=f"btn_{doc_id}"):
                    if doc_id in st.session_state.show_full:
                        st.session_state.show_full.remove(doc_id)
                    else:
                        st.session_state.show_full.add(doc_id)
                    st.rerun()
                
                # Display full text if toggled on
                if doc_id in st.session_state.show_full:
                    full_text = search_engine.get_document(doc_id)
                    st.text_area("Full Document", full_text, height=300, key=f"text_{doc_id}")
    
    elif search_button:
        st.warning("Please enter a search query")
    
    # Example queries
    st.markdown("---")
    st.markdown("### 💡 Example Queries")
    examples = [
        "quantum physics basics",
        "baseball statistics",
        "computer graphics rendering",
        "space exploration",
        "gun control debate"
    ]
    
    cols = st.columns(len(examples))
    for col, example in zip(cols, examples):
        if col.button(example, key=f"ex_{example}"):
            st.rerun()

if __name__ == "__main__":
    main()
