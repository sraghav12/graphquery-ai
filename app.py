"""
Natural Language to Neo4j Cypher Query Generator
A professional interface for converting natural language questions to Cypher queries
using LLM and few-shot prompting techniques.
"""

import streamlit as st
import os
from dotenv import load_dotenv
import time
from datetime import datetime
import json
import traceback

# Load environment variables
load_dotenv()

# Custom CSS Generator
def get_custom_css(theme):
    is_dark = theme == 'dark'
    
    # Colors
    bg_color = "#0F172A" if is_dark else "#F8FAFC"
    text_color = "#F8FAFC" if is_dark else "#1E293B"
    card_bg = "rgba(30, 41, 59, 0.5)" if is_dark else "#FFFFFF"
    card_border = "rgba(148, 163, 184, 0.1)"
    
    # Button Colors
    btn_bg = "rgba(30, 41, 59, 0.8)" if is_dark else "#FFFFFF"
    btn_hover = "rgba(51, 65, 85, 0.9)" if is_dark else "#F1F5F9"
    btn_text = "#F8FAFC" if is_dark else "#334155"
    btn_border = "rgba(148, 163, 184, 0.2)"
    
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    .stApp {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: {bg_color};
    }}
    
    /* Hide Streamlit Toolbar & Header Decoration */
    [data-testid="stToolbar"] {{
        visibility: hidden !important;
        display: none !important;
    }}
    
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    
    /* Elegant Header */
    h1 {{
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -0.02em;
        white-space: nowrap;
    }}
    
    h2, h3, p, span {{
        color: {text_color} !important;
    }}
    
    /* "Try these examples" Label */
    .caption-text {{
        font-size: 1rem !important;
        color: {text_color} !important; 
        opacity: 0.9 !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem;
    }}
    
    /* Clean Cards */
    .result-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        backdrop-filter: blur(10px);
    }}
    
    /* Status Bar */
    .status-pill {{
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.2);
        color: #10B981;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }}
    
    /* Input Styling */
    .stTextInput>div>div>input {{
        background-color: {btn_bg};
        border: 1px solid {btn_border};
        color: {text_color};
        border-radius: 12px;
        padding: 1rem;
    }}
    
    /* Quick Action Chips via Buttons */
    .stButton button {{
        background-color: {btn_bg};
        color: {text_color} !important;
        border: 1px solid {btn_border};
        border-radius: 12px;
        transition: all 0.2s;
        height: auto !important;
        padding: 0.75rem 1rem !important;
        white-space: normal !important;
    }}
    
    .stButton button:hover {{
        background-color: {btn_hover};
        border-color: #6366F1;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
    }}
    
    /* Primary Action Button overrides */
    div[data-testid="column"] button[kind="primary"] {{
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        height: 3.2rem !important;
    }}
    
    /* DataFrame Styling */
    div[data-testid="stDataFrame"] {{
        background-color: {card_bg};
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid {card_border};
    }}
    
    /* Hide default sidebar junk */
    section[data-testid="stSidebar"] {{
        display: none;
    }}
    </style>
    """


def init_session_state():
    """Initialize session state variables"""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'chain' not in st.session_state:
        st.session_state.chain = None
    if 'graph' not in st.session_state:
        st.session_state.graph = None

def connect_to_database():
    """Initialize database connection and chain"""
    try:
        from langchain_neo4j import Neo4jGraph
        from langchain_groq import ChatGroq
        from src.query_chain import create_qa_chain
        
        # Get credentials
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_username = os.getenv("NEO4J_USERNAME")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        groq_api_key = os.getenv("GROQ_API_KEY")

        # Fallback to secrets
        try:
            if not neo4j_uri: neo4j_uri = st.secrets.get("NEO4J_URI", "")
            if not neo4j_username: neo4j_username = st.secrets.get("NEO4J_USERNAME", "")
            if not neo4j_password: neo4j_password = st.secrets.get("NEO4J_PASSWORD", "")
            if not groq_api_key: groq_api_key = st.secrets.get("GROQ_API_KEY", "")
        except: pass
        
        if not all([neo4j_uri, neo4j_username, neo4j_password, groq_api_key]):
            st.error("Missing credentials. Please check .env or secrets.")
            return False
        
        # Connect
        graph = Neo4jGraph(
            url=neo4j_uri,
            username=neo4j_username,
            password=neo4j_password
        )
        
        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-8b-instant"
        )
        
        chain = create_qa_chain(graph, llm)
        
        st.session_state.graph = graph
        st.session_state.chain = chain
        return True
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
        traceback.print_exc()
        return False

def display_schema():
    """Display database schema in sidebar"""
    if st.session_state.graph:
        try:
            schema = st.session_state.graph.schema
            with st.expander("View Database Schema", expanded=False):
                st.code(schema, language="text")
        except: pass

def execute_query(question: str):
    """Execute natural language query and return results"""
    if not st.session_state.chain:
        st.error("Please connect to database first.")
        return None
    
    try:
        print(f"DEBUG: Executing query: {question}")
        start_time = time.time()
        result = st.session_state.chain.invoke({"query": question})
        execution_time = time.time() - start_time
        print(f"DEBUG: Result content: {result}")
        
        st.session_state.query_history.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"), # Simplified timestamp
            "question": question,
            "result": result,
            "execution_time": execution_time
        })
        
        return result, execution_time
    except Exception as e:
        print(f"DEBUG: Error: {e}")
        st.error(f"Execution failed: {str(e)}")
        traceback.print_exc()
        return None, 0

def display_smart_result(result):
    """Intelligently display results based on data shape"""
    if isinstance(result, list) and len(result) == 1 and len(result[0]) == 1:
        # Single value case (e.g. Count)
        key = list(result[0].keys())[0]
        value = result[0][key]
        st.markdown(f"""
        <div class="result-card" style="text-align: center;">
            <p style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.7;">{key}</p>
            <h1 style="font-size: 3.5rem; margin: 0; background: linear-gradient(135deg, #10B981 0%, #3B82F6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</h1>
        </div>
        """, unsafe_allow_html=True)
    elif isinstance(result, list):
        if result:
            st.dataframe(result, width="stretch", hide_index=True)
        else:
            st.info("No results found.")
    elif isinstance(result, dict) and 'result' in result:
        display_smart_result(result['result'])
    else:
        st.json(result)

def main():
    """Main application"""
    init_session_state()
    
    # Initialize theme state
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
        
    st.markdown(get_custom_css(st.session_state.theme), unsafe_allow_html=True)
    
    # --- Header Area ---
    # Use a layout to push toggle to absolute right
    col_logo, col_spacer, col_toggle = st.columns([6, 3, 1])
    
    with col_logo:
        st.title("GraphQuery AI")
    
    with col_toggle:
        toggle_icon = "☀️" if st.session_state.theme == 'dark' else "🌙"
        if st.button(toggle_icon, key="theme_toggle", use_container_width=True):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.rerun()
            
    # Connection Status
    if st.session_state.chain:
        st.markdown('<div class="status-pill">✅ Connected to Neo4j AuraDB</div>', unsafe_allow_html=True)
        st.markdown("")
        display_schema() # Moved Schema Here
    else:
        if st.button("🔌 Connect Database", type="primary"):
            with st.spinner("Connecting..."):
                if connect_to_database():
                    st.rerun()

    if not st.session_state.chain:
        return

    # --- Main Input Area ---
    st.markdown("### Ask your data")
    
    input_col, btn_col = st.columns([5, 1])
    with input_col:
        question = st.text_input(
            "Query", 
            key="user_query", # Persistent key
            placeholder="e.g. How many actors played in The Matrix?", 
            label_visibility="collapsed"
        )
            
    with btn_col:
        execute_btn = st.button("Run Query", type="primary", use_container_width=True)
    
    # --- Quick Starters (Chips) ---
    st.markdown("<p class='caption-text'>Try these examples:</p>", unsafe_allow_html=True)
    
    example_queries = [
        "How many movies are there?",
        "Which actors played in Casino?",
        "How many movies has Tom Hanks acted in?",
        "List genres of Schindler's List",
        "Find movies with imdb rating higher than 8",
        "Which actors acted in more than one movie?"
    ]
    
    def set_query(q):
        st.session_state.user_query = q
    
    # Dynamic grid for alignment
    cols = st.columns(3) # fixed 3 columns for better look
    for i, query in enumerate(example_queries):
        with cols[i % 3]:
            st.button(
                query, 
                key=f"q_{i}", 
                use_container_width=True,
                on_click=set_query,
                args=(query,)
            )
    

    # --- Results Area ---
    if execute_btn and question:
        with st.spinner("Analyzing graph..."):
            result_data = execute_query(question)
            
            if result_data:
                result, exec_time = result_data
                
                # Tabbed Interface
                tab_res, tab_code, tab_trace = st.tabs(["Visualization", "Cypher Logic", "Execution Context"])
                
                with tab_res:
                    st.markdown("")
                    display_smart_result(result)
                    
                with tab_code:
                    st.markdown("")
                    cypher = "N/A"
                    if isinstance(result, dict) and 'query' in result:
                        cypher = result['query']
                    st.code(cypher, language="cypher")
                    
                with tab_trace:
                    st.markdown("")
                    st.json(result)
                    st.caption(f"Execution time: {exec_time:.3f}s")

    # History
    if st.session_state.query_history:
        st.markdown("---")
        st.markdown("### Request History")
        for entry in reversed(st.session_state.query_history[-3:]):
            with st.expander(f"{entry['timestamp']} - {entry['question']}", expanded=False):
                st.write(f"Latency: {entry['execution_time']:.3f}s")
                if isinstance(entry['result'], dict) and 'result' in entry['result']:
                    display_smart_result(entry['result']['result'])
                else:
                    st.json(entry['result'])

    # --- Footer ---
    st.markdown("---")
    st.markdown("<div style='text-align: center; opacity: 0.5; font-size: 0.8rem;'>Powered by LangChain & Neo4j</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()