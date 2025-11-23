"""
Streamlit UI for search engine - DEBUG VERSION
"""
import streamlit as st
from pathlib import Path
import sys
import time
import traceback

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

st.write("✅ Step 1: Imports successful")

try:
    from src.search_engine import SearchEngine
    st.write("✅ Step 2: SearchEngine imported")
except Exception as e:
    st.error(f"❌ Step 2 FAILED: Cannot import SearchEngine")
    st.error(f"Error: {e}")
    st.code(traceback.format_exc())
    st.stop()

# Page config
st.set_page_config(
    page_title="Multi-Document Search Engine",
    page_icon="🔍",
    layout="wide"
)

st.write("✅ Step 3: Page config set")

# Initialize
@st.cache_resource
def load_search_engine():
    """Load and cache search engine"""
    st.write("🔄 Loading search engine...")
    
    # Check if data exists
    data_path = Path("data/docs")
    st.write(f"Checking for data at: {data_path.absolute()}")
    
    if not data_path.exists():
        st.error(f"❌ Data not found at: {data_path.absolute()}")
        st.info("Please run: python setup.py")
        st.stop()
    
    doc_count = len(list(data_path.glob("*.txt")))
    st.write(f"✅ Found {doc_count} documents")
    
    if doc_count == 0:
        st.error("❌ No .txt files in data/docs/")
        st.info("Please run: python setup.py")
        st.stop()
    
    try:
        engine = SearchEngine()
        st.write("✅ SearchEngine created")
        
        engine.build_index()
        st.write("✅ Index built successfully")
        
        return engine
    except Exception as e:
        st.error(f"❌ Error during initialization: {e}")
        st.code(traceback.format_exc())
        st.stop()

# Main app
def main():
    st.title("🔍 Multi-Document Search Engine")
    st.markdown("Semantic search over 20 Newsgroups dataset using AI embeddings")
    
    st.write("✅ Step 4: Starting main app")
    
    # Load engine
    try:
        search_engine = load_search_engine()
        st.write("✅ Step 5: Search engine loaded successfully!")
    except Exception as e:
        st.error(f"❌ Error loading search engine: {e}")
        st.code(traceback.format_exc())
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
    
    # Search
    if search_button and query:
        with st.spinner("Searching..."):
            try:
                start_time = time.time()
                results = search_engine.search(query, top_k)
                search_time = time.time() - start_time
                
                st.success(f"Found {len(results)} results in {search_time:.2f}s")
                
                # Display results
                for i, result in enumerate(results, 1):
                    with st.expander(f"**{i}. {result['doc_id']}** (Score: {result['score']:.3f})", expanded=(i<=3)):
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
                        
                        # Full text
                        if st.button(f"Show full text", key=f"show_{result['doc_id']}"):
                            full_text = search_engine.get_document(result['doc_id'])
                            st.text_area("Full Document", full_text, height=300)
            except Exception as e:
                st.error(f"❌ Search failed: {e}")
                st.code(traceback.format_exc())
    
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