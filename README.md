# GraphQuery AI

**Live Demo:** [graphquery-ai.streamlit.app](https://graphquery-aitabreadme-ov-file-agli4bhznjjcjeawqftnya.streamlit.app/)

A natural language interface for Neo4j graph databases. Ask questions in plain English — get Cypher queries generated, executed, and results returned in real time.

---

## The Problem

Graph databases are powerful but inaccessible. To query Neo4j you need to know Cypher — a specialized query language most people don't know. Even experienced developers spend time translating business questions into graph traversal patterns.

GraphQuery AI removes that barrier: you describe what you want in English, and the system generates the correct Cypher, runs it against the database, and returns structured results.

---

## How It Works

Every question goes through a four-stage pipeline:

```
User Question
      │
      ▼
┌─────────────────────┐
│   Few-Shot Prompt   │  ← Schema + curated Cypher examples injected
│   (LLM context)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Cypher Generator  │  ← Groq LLM outputs a valid Cypher statement
│   (Llama 3.1)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Neo4j AuraDB      │  ← Query executes against the live graph
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Result Display    │  ← Table, single value, or raw JSON
└─────────────────────┘
```

### Few-Shot Prompting

The LLM doesn't just receive a question — it receives the live database schema plus a curated set of question/Cypher pairs. This teaches the model the graph's structure and naming conventions before it generates anything.

```python
# Example prompt context injected before every query
{
  "question": "Which actors played in Casino?",
  "query": "MATCH (m:Movie {title: 'Casino'})<-[:ACTED_IN]-(a:Person) RETURN a.name AS actor"
}
```

This approach consistently outperforms zero-shot prompting on graph databases because relationship names and node labels are domain-specific — the model can't guess them reliably.

### Cypher Validation

Generated queries are validated before execution via `validate_cypher=True` in `GraphCypherQAChain`. Malformed queries are caught before hitting the database.

---

## Architecture

```
graphdb/
├── app.py              # Streamlit UI — connection, input, result rendering
├── config.py           # Credential loading — .env locally, st.secrets on Cloud
├── src/
│   ├── query_chain.py  # Few-shot prompt + GraphCypherQAChain setup
│   └── database.py     # Neo4jDatabase wrapper with schema + data loading
└── requirements.txt
```

**Data model** (movie dataset):
```
(Person)-[:ACTED_IN]->(Movie)
(Person)-[:DIRECTED]->(Movie)
(Movie)-[:IN_GENRE]->(Genre)

Movie  { id, title, released, imdbRating }
Person { name }
Genre  { name }
```

**Tech stack:**
| Layer | Tool |
|---|---|
| UI | Streamlit |
| LLM | Groq (`llama-3.1-8b-instant`) |
| Chain | LangChain `GraphCypherQAChain` |
| Graph database | Neo4j AuraDB |
| Prompt strategy | Few-shot with live schema injection |

---

## Local Setup

**Prerequisites:** Python 3.10+

```bash
git clone https://github.com/sraghav12/graphdb
cd graphdb
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:
```
NEO4J_URI="neo4j+s://your-instance.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your-password"
GROQ_API_KEY="your-groq-key"
```

Run:
```bash
streamlit run app.py
```

### Load Sample Data

The app uses a public movie dataset. To populate your Neo4j database, run this in the Neo4j Browser or Cypher Shell:

```cypher
LOAD CSV WITH HEADERS FROM
'https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv' AS row
MERGE (m:Movie {id: row.movieId})
SET m.released = date(row.released), m.title = row.title, m.imdbRating = toFloat(row.imdbRating)
FOREACH (director IN split(row.director, '|') |
    MERGE (p:Person {name: trim(director)}) MERGE (p)-[:DIRECTED]->(m))
FOREACH (actor IN split(row.actors, '|') |
    MERGE (p:Person {name: trim(actor)}) MERGE (p)-[:ACTED_IN]->(m))
FOREACH (genre IN split(row.genres, '|') |
    MERGE (g:Genre {name: trim(genre)}) MERGE (m)-[:IN_GENRE]->(g))
```

---

## Deploying to Streamlit Cloud

1. Push the repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → select repo, set `app.py` as entrypoint
3. Under **Advanced Settings → Secrets**, add:

```toml
NEO4J_URI = "neo4j+s://your-instance.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your-password"
GROQ_API_KEY = "your-groq-key"
```

4. Deploy. The app reads from `st.secrets` on Streamlit Cloud and from `.env` locally — no code changes between environments.

---

## Example Questions

```
How many movies are in the database?
Which actors played in Casino?
How many movies has Tom Hanks acted in?
List all genres of Schindler's List
Find movies with an IMDb rating above 8
Which actors have worked in both Comedy and Action films?
Who directed the most movies?
```

---

## Why Few-Shot Over Zero-Shot?

Zero-shot prompting ("generate Cypher for this question") fails on graph databases because:

1. **Relationship names aren't obvious** — `ACTED_IN` vs `STARRED_IN` vs `PERFORMED_IN` are all valid English but only one matches the schema
2. **Graph traversal patterns vary** — querying depth-1 vs depth-2 relationships requires different Cypher structures
3. **Property names aren't guessable** — `imdbRating` vs `rating` vs `score`

Few-shot examples act as in-context schema documentation. The LLM learns the exact vocabulary of your graph before generating anything.

To extend the system with your own domain, add examples in [`src/query_chain.py`](src/query_chain.py):

```python
{
    "question": "Find all movies released after 2000",
    "query": "MATCH (m:Movie) WHERE m.released > date('2000-01-01') RETURN m.title, m.released"
}
```
