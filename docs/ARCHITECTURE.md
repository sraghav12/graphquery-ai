# Architecture Documentation

## System Overview

The Neo4j NLP Query Generator is a sophisticated text-to-query system that leverages Large Language Models (LLMs) and graph databases to transform natural language into executable Cypher queries.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                      (Streamlit App)                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Query Chain  │  │  Database    │  │   Config     │      │
│  │   Manager    │  │   Manager    │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangChain Framework                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Few-Shot     │  │  Cypher      │  │  Validation  │      │
│  │ Prompter     │  │  Generator   │  │   Engine     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  Groq API    │  │   Neo4j      │
│ (Llama 3.1)  │  │  AuraDB      │
└──────────────┘  └──────────────┘
```

## Component Details

### 1. User Interface Layer

**Technology**: Streamlit

**Components**:
- `app.py`: Main application entry point
- Interactive query input
- Results visualization
- Query history management
- Database connection management

**Features**:
- Real-time query execution
- Performance metrics display
- Download capabilities
- Responsive design
- Dark mode support

### 2. Application Layer

#### Query Chain Manager (`src/query_chain.py`)

**Responsibilities**:
- Manages few-shot examples
- Creates and configures LangChain QA chain
- Handles prompt template construction
- Validates generated queries

**Key Functions**:
```python
- get_few_shot_examples(): Returns curated examples
- create_cypher_prompt(): Builds prompt template
- create_qa_chain(): Initializes LangChain chain
- add_custom_examples(): Extends example set
```

#### Database Manager (`src/database.py`)

**Responsibilities**:
- Neo4j connection management
- Schema extraction
- Query execution
- Data loading utilities
- Statistics gathering

**Key Functions**:
```python
- connect(): Establishes database connection
- load_movie_data(): Loads sample dataset
- get_schema(): Retrieves database schema
- get_stats(): Gathers database statistics
- execute_query(): Runs Cypher queries
```

### 3. LangChain Integration

**Framework**: LangChain

**Components**:

1. **GraphCypherQAChain**:
   - Orchestrates the query generation pipeline
   - Manages LLM interactions
   - Validates Cypher syntax
   - Returns query results

2. **Few-Shot Prompt Template**:
   - Stores example question-query pairs
   - Formats prompts for LLM
   - Provides context and constraints

3. **Validation Engine**:
   - Syntax checking
   - Schema compliance
   - Error handling

### 4. External Services

#### Groq API (LLM)

**Model**: Llama 3.1-8B-Instant

**Usage**:
- Natural language understanding
- Cypher query generation
- Pattern matching

**Configuration**:
```python
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant"
)
```

#### Neo4j AuraDB

**Database**: Graph Database

**Schema**:
```
Nodes:
- Movie {id, title, released, imdbRating}
- Person {name}
- Genre {name}

Relationships:
- (Person)-[:ACTED_IN]->(Movie)
- (Person)-[:DIRECTED]->(Movie)
- (Movie)-[:IN_GENRE]->(Genre)
```

## Data Flow

### Query Execution Flow

```
1. User Input
   │
   ▼
2. Session State Check
   │
   ▼
3. Chain Invocation
   │
   ├──▶ 4. Few-Shot Context Building
   │         │
   │         ▼
   │    5. LLM Prompt Construction
   │         │
   │         ▼
   │    6. Groq API Call
   │         │
   │         ▼
   │    7. Cypher Query Generation
   │         │
   │         ▼
   │    8. Query Validation
   │
   ▼
9. Neo4j Execution
   │
   ▼
10. Results Processing
    │
    ▼
11. UI Display
    │
    ▼
12. History Update
```

### Few-Shot Learning Process

```
User Question: "How many movies are there?"
                │
                ▼
        ┌───────────────┐
        │ Schema Info   │
        │ + Examples    │
        └───────┬───────┘
                │
                ▼
┌────────────────────────────────────┐
│ Example 1: Question + Query        │
│ Example 2: Question + Query        │
│ Example 3: Question + Query        │
│ ...                                │
│ User Question: ?                   │
│ Expected Output: Cypher query      │
└────────────────┬───────────────────┘
                 │
                 ▼
          ┌──────────┐
          │   LLM    │
          └────┬─────┘
               │
               ▼
     Generated Cypher Query
```

## Prompt Engineering

### Template Structure

```python
Prefix:
- Task description
- Constraints
- Schema information

Examples:
- Question 1 → Query 1
- Question 2 → Query 2
- ...

Suffix:
- User's question
- Expected output format
```

### Example Prompt

```
Task: Generate a Cypher statement to query a Neo4j graph database.
Instructions:
- Use only the provided schema.
- Do not include explanations.
- Output ONLY the Cypher statement.

Schema:
Node properties:
Movie {id, title, released, imdbRating}
Person {name}
Genre {name}
...

User input: How many actors are there?
Cypher query: MATCH (a:Person)-[:ACTED_IN]->(:Movie) RETURN count(DISTINCT a)

User input: <USER_QUESTION>
Cypher query:
```

## Security Considerations

### Credential Management

1. **Environment Variables**:
   - Never hardcode credentials
   - Use `.env` for local development
   - Use Streamlit Secrets for deployment

2. **API Key Protection**:
   - Rotate keys regularly
   - Monitor usage
   - Implement rate limiting

### Query Validation

1. **Cypher Injection Prevention**:
   - Validate syntax before execution
   - Use parameterized queries where possible
   - Sanitize user inputs

2. **Resource Limits**:
   - Timeout configurations
   - Result size limits
   - Query complexity checks

## Performance Optimization

### Caching Strategy

```python
@st.cache_resource
def get_database_connection():
    # Connection is cached
    return Neo4jGraph(...)

@st.cache_data
def get_schema():
    # Schema is cached
    return graph.schema
```

### Query Optimization

1. **Index Usage**:
   ```cypher
   CREATE INDEX person_name FOR (p:Person) ON (p.name)
   CREATE INDEX movie_title FOR (m:Movie) ON (m.title)
   ```

2. **Query Patterns**:
   - Use specific labels
   - Limit result sets
   - Avoid Cartesian products

### LLM Optimization

1. **Token Efficiency**:
   - Minimal examples
   - Concise prompts
   - Stop sequences to prevent verbosity

2. **Model Selection**:
   - Llama 3.1-8B for speed
   - Can upgrade to larger models for accuracy

## Scalability Considerations

### Horizontal Scaling

- Stateless application design
- Can deploy multiple instances
- Load balancer ready

### Vertical Scaling

- Increase Neo4j resources
- Upgrade LLM tier
- Optimize prompt templates

## Monitoring and Logging

### Metrics to Track

1. **Performance**:
   - Query execution time
   - LLM response time
   - Total request time

2. **Quality**:
   - Query success rate
   - Validation failures
   - User corrections

3. **Usage**:
   - Total queries
   - Unique users
   - Popular query patterns

### Logging Strategy

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Error Handling

### Error Categories

1. **Connection Errors**:
   - Database unavailable
   - API timeout
   - Network issues

2. **Query Errors**:
   - Invalid Cypher syntax
   - Schema violations
   - Execution failures

3. **Application Errors**:
   - Session state corruption
   - Resource exhaustion
   - Configuration issues

### Recovery Strategies

- Automatic retry with exponential backoff
- Graceful degradation
- User-friendly error messages
- Fallback to cached results

## Future Enhancements

### Planned Features

1. **Multi-language Support**:
   - Translate questions to Cypher
   - Support multiple graph schemas

2. **Advanced Analytics**:
   - Query pattern learning
   - Automatic example generation
   - Performance prediction

3. **Collaboration Features**:
   - Share queries
   - Team workspaces
   - Query libraries

4. **API Layer**:
   - REST API for programmatic access
   - Webhook support
   - Batch processing

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | User interface |
| Backend | Python 3.8+ | Application logic |
| LLM Framework | LangChain | Query generation |
| LLM Provider | Groq | AI inference |
| Database | Neo4j AuraDB | Graph storage |
| Deployment | Streamlit Cloud | Hosting |
| Version Control | Git/GitHub | Code management |

## Development Workflow

```
Local Development
       │
       ▼
   Git Commit
       │
       ▼
  GitHub Push
       │
       ▼
Streamlit Cloud
  Auto-Deploy
       │
       ▼
   Production
```

## Conclusion

This architecture provides a robust, scalable foundation for natural language to Cypher query generation. The modular design allows for easy extension and maintenance, while the use of proven technologies ensures reliability and performance.