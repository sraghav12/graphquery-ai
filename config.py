import os
from dotenv import load_dotenv

def _get_secret(key):
    """Get a secret from st.secrets (Streamlit Cloud) or os.environ (local)."""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)

def setup_environment():
    """Load credentials and propagate to os.environ for downstream libraries."""
    load_dotenv()

    neo4j_uri = _get_secret("NEO4J_URI")
    neo4j_username = _get_secret("NEO4J_USERNAME")
    neo4j_password = _get_secret("NEO4J_PASSWORD")
    groq_api_key = _get_secret("GROQ_API_KEY")

    missing = [k for k, v in {
        "NEO4J_URI": neo4j_uri,
        "NEO4J_USERNAME": neo4j_username,
        "NEO4J_PASSWORD": neo4j_password,
        "GROQ_API_KEY": groq_api_key,
    }.items() if not v]

    if missing:
        raise ValueError(
            f"Missing credentials: {', '.join(missing)}. "
            "Set them in Streamlit secrets or a .env file."
        )

    os.environ["NEO4J_URI"] = neo4j_uri
    os.environ["NEO4J_USERNAME"] = neo4j_username
    os.environ["NEO4J_PASSWORD"] = neo4j_password
    os.environ["GROQ_API_KEY"] = groq_api_key

    return neo4j_uri, neo4j_username, neo4j_password, groq_api_key

def get_llm():
    from langchain_groq import ChatGroq
    groq_api_key = _get_secret("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    return ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")
