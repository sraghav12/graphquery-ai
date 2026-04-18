"""
GraphQuery AI — Natural Language to Neo4j Cypher
Converts plain English questions into Cypher queries using LLM + few-shot prompting.
"""

import streamlit as st
import traceback
import time
from datetime import datetime

from config import setup_environment, get_llm

st.set_page_config(
    page_title="GraphQuery AI",
    page_icon="🔍",
    layout="centered"
)


# ── Custom CSS ──────────────────────────────────────────────────────────────

def get_custom_css(theme):
    is_dark = theme == "dark"
    bg_color      = "#0F172A"              if is_dark else "#F8FAFC"
    text_color    = "#F8FAFC"              if is_dark else "#1E293B"
    card_bg       = "rgba(30,41,59,0.5)"   if is_dark else "#FFFFFF"
    card_border   = "rgba(148,163,184,0.1)"
    btn_bg        = "rgba(30,41,59,0.8)"   if is_dark else "#FFFFFF"
    btn_hover     = "rgba(51,65,85,0.9)"   if is_dark else "#F1F5F9"
    btn_border    = "rgba(148,163,184,0.2)"

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    .stApp {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: {bg_color}; }}
    [data-testid="stToolbar"] {{ visibility: hidden !important; display: none !important; }}
    header[data-testid="stHeader"] {{ background-color: transparent !important; }}
    h1 {{
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; letter-spacing: -0.02em; white-space: nowrap;
    }}
    h2, h3, p, span {{ color: {text_color} !important; }}
    .caption-text {{
        font-size: 1rem !important; color: {text_color} !important;
        opacity: 0.9 !important; font-weight: 500 !important; margin-bottom: 0.5rem;
    }}
    .result-card {{
        background: {card_bg}; border: 1px solid {card_border};
        border-radius: 16px; padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); backdrop-filter: blur(10px);
    }}
    .status-pill {{
        display: inline-flex; align-items: center; padding: 0.5rem 1rem;
        background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2);
        color: #10B981; border-radius: 9999px; font-size: 0.875rem; font-weight: 500;
    }}
    .stTextInput>div>div>input {{
        background-color: {btn_bg}; border: 1px solid {btn_border};
        color: {text_color}; border-radius: 12px; padding: 1rem;
    }}
    .stButton button {{
        background-color: {btn_bg}; color: {text_color} !important;
        border: 1px solid {btn_border}; border-radius: 12px; transition: all 0.2s;
        height: auto !important; padding: 0.75rem 1rem !important; white-space: normal !important;
    }}
    .stButton button:hover {{
        background-color: {btn_hover}; border-color: #6366F1;
        transform: translateY(-1px); box-shadow: 0 4px 12px rgba(99,102,241,0.2);
    }}
    div[data-testid="column"] button[kind="primary"] {{
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: white !important; border: none !important; height: 3.2rem !important;
    }}
    div[data-testid="stDataFrame"] {{
        background-color: {card_bg}; border-radius: 12px;
        padding: 1rem; border: 1px solid {card_border};
    }}
    section[data-testid="stSidebar"] {{ display: none; }}
    </style>
    """


# ── Session State ────────────────────────────────────────────────────────────

def init_session_state():
    for key, default in [("query_history", []), ("chain", None), ("graph", None), ("theme", "light")]:
        if key not in st.session_state:
            st.session_state[key] = default


# ── Database Connection ───────────────────────────────────────────────────────

@st.cache_resource
def initialize_connection():
    try:
        from langchain_neo4j import Neo4jGraph
        from src.query_chain import create_qa_chain

        neo4j_uri, neo4j_username, neo4j_password, _ = setup_environment()
        llm = get_llm()

        graph = Neo4jGraph(url=neo4j_uri, username=neo4j_username, password=neo4j_password)
        chain = create_qa_chain(graph, llm)
        return graph, chain
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
        traceback.print_exc()
        return None, None


# ── Query Execution ───────────────────────────────────────────────────────────

def execute_query(question: str):
    chain = st.session_state.chain
    if not chain:
        st.error("Not connected to database.")
        return None, 0

    try:
        start = time.time()
        result = chain.invoke({"query": question})
        elapsed = time.time() - start

        st.session_state.query_history.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "question": question,
            "result": result,
            "execution_time": elapsed,
        })
        return result, elapsed
    except Exception as e:
        st.error(f"Query failed: {str(e)}")
        traceback.print_exc()
        return None, 0


# ── Result Display ────────────────────────────────────────────────────────────

def display_result(result):
    if isinstance(result, dict) and "result" in result:
        display_result(result["result"])
    elif isinstance(result, list) and len(result) == 1 and len(result[0]) == 1:
        key = list(result[0].keys())[0]
        value = result[0][key]
        st.markdown(f"""
        <div class="result-card" style="text-align:center;">
            <p style="font-size:0.9rem;text-transform:uppercase;letter-spacing:0.05em;opacity:0.7;">{key}</p>
            <h1 style="font-size:3.5rem;margin:0;background:linear-gradient(135deg,#10B981 0%,#3B82F6 100%);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">{value}</h1>
        </div>
        """, unsafe_allow_html=True)
    elif isinstance(result, list):
        if result:
            st.dataframe(result, use_container_width=True, hide_index=True)
        else:
            st.info("No results found.")
    else:
        st.json(result)


# ── Main App ──────────────────────────────────────────────────────────────────

def main():
    init_session_state()
    st.markdown(get_custom_css(st.session_state.theme), unsafe_allow_html=True)

    # Header
    col_logo, _, col_toggle = st.columns([6, 3, 1])
    with col_logo:
        st.title("GraphQuery AI")
    with col_toggle:
        icon = "☀️" if st.session_state.theme == "dark" else "🌙"
        if st.button(icon, key="theme_toggle", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

    # Connection
    if st.session_state.chain:
        st.markdown('<div class="status-pill">Connected to Neo4j AuraDB</div>', unsafe_allow_html=True)
        st.markdown("")
        if st.session_state.graph:
            try:
                with st.expander("View Database Schema", expanded=False):
                    st.code(st.session_state.graph.schema, language="text")
            except Exception:
                pass
    else:
        if st.button("Connect Database", type="primary"):
            with st.spinner("Connecting..."):
                graph, chain = initialize_connection()
                if graph and chain:
                    st.session_state.graph = graph
                    st.session_state.chain = chain
                    st.rerun()
        return

    # Query Input
    st.markdown("### Ask your data")
    input_col, btn_col = st.columns([5, 1])
    with input_col:
        question = st.text_input(
            "Query",
            key="user_query",
            placeholder="e.g. How many actors played in The Matrix?",
            label_visibility="collapsed"
        )
    with btn_col:
        execute_btn = st.button("Run", type="primary", use_container_width=True)

    # Example chips
    st.markdown("<p class='caption-text'>Try these examples:</p>", unsafe_allow_html=True)
    examples = [
        "How many movies are there?",
        "Which actors played in Casino?",
        "How many movies has Tom Hanks acted in?",
        "List genres of Schindler's List",
        "Find movies with imdb rating higher than 8",
        "Which actors acted in more than one movie?",
    ]
    cols = st.columns(3)
    for i, q in enumerate(examples):
        with cols[i % 3]:
            st.button(q, key=f"q_{i}", use_container_width=True,
                      on_click=lambda q=q: st.session_state.update({"user_query": q}))

    # Results
    if execute_btn and question:
        with st.spinner("Querying graph..."):
            result, elapsed = execute_query(question)
            if result is not None:
                tab_res, tab_cypher, tab_trace = st.tabs(["Result", "Cypher", "Raw"])
                with tab_res:
                    st.markdown("")
                    display_result(result)
                with tab_cypher:
                    cypher = result.get("query", "N/A") if isinstance(result, dict) else "N/A"
                    st.code(cypher, language="cypher")
                with tab_trace:
                    st.json(result)
                    st.caption(f"Execution time: {elapsed:.3f}s")

    # History
    if st.session_state.query_history:
        st.markdown("---")
        st.markdown("### Recent Queries")
        for entry in reversed(st.session_state.query_history[-3:]):
            with st.expander(f"{entry['timestamp']} — {entry['question']}", expanded=False):
                st.caption(f"Latency: {entry['execution_time']:.3f}s")
                display_result(entry["result"])

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;opacity:0.5;font-size:0.8rem;'>Powered by LangChain & Neo4j</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
