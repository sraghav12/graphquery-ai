"""
Query chain creation and management for Neo4j Cypher QA
"""

from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from typing import Any


def get_few_shot_examples():
    """
    Returns carefully crafted few-shot examples from the notebook
    """
    return [
        {
            "question": "How many artists are there?",
            "query": "MATCH (a:Person)-[:ACTED_IN]->(:Movie) RETURN count(DISTINCT a) AS actors",
        },
        {
            "question": "Which actors played in the movie Casino?",
            "query": "MATCH (m:Movie {{title: 'Casino'}})<-[:ACTED_IN]-(a:Person) RETURN a.name AS actor",
        },
        {
            "question": "How many movies has Tom Hanks acted in?",
            "query": "MATCH (a:Person {{name: 'Tom Hanks'}})-[:ACTED_IN]->(m:Movie) RETURN count(m) AS movies",
        },
        {
            "question": "List all the genres of the movie Schindler's List",
            "query": "MATCH (m:Movie {{title: 'Schindler\\'s List'}})-[:IN_GENRE]->(g:Genre) RETURN g.name AS genre",
        },
        {
            "question": "Which actors have worked in movies from both the comedy and action genres?",
            "query": "MATCH (a:Person)-[:ACTED_IN]->(:Movie)-[:IN_GENRE]->(g1:Genre), (a)-[:ACTED_IN]->(:Movie)-[:IN_GENRE]->(g2:Genre) WHERE g1.name = 'Comedy' AND g2.name = 'Action' RETURN DISTINCT a.name AS actor",
        },
        {
            "question": "Which actors acted in more than one movie?",
            "query": "MATCH (a:Person)-[:ACTED_IN]->(m:Movie) WITH a, count(DISTINCT m) AS movies WHERE movies > 1 RETURN a.name AS actor, movies AS count"
        },
        {
            "question": "Find movies with imdb rating higher than 8",
            "query": "MATCH (m:Movie) WHERE m.imdbRating > 8.0 RETURN m.title AS title, m.imdbRating AS rating"
        },
        {
            "question": "List top 3 movies by rating",
            "query": "MATCH (m:Movie) RETURN m.title AS title, m.imdbRating AS rating ORDER BY m.imdbRating DESC LIMIT 3"
        }
    ]


def create_cypher_prompt():
    """
    Creates a few-shot prompt template matching the notebook
    """
    examples = get_few_shot_examples()
    
    example_prompt = PromptTemplate.from_template(
        "User input: {question}\nCypher query: {query}"
    )
    
    prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix=(
            "Task: Generate a Cypher statement to query a Neo4j graph database.\n"
            "Instructions:\n"
            "- Use only the provided schema.\n"
            "- Do not include any explanations or extra text.\n"
            "- Do not wrap the query in quotes or backticks.\n"
            "- Output ONLY the Cypher statement.\n\n"
            "Schema:\n{schema}\n"
        ),
        suffix="User input: {question}\nCypher query:",
        input_variables=["schema", "question"],
    )
    
    return prompt


def create_qa_chain(graph: Any, llm: Any, verbose: bool = True):
    """
    Creates a GraphCypherQAChain with custom prompting
    """
    # Refresh schema
    graph.refresh_schema()
    
    prompt = create_cypher_prompt()
    
    chain = GraphCypherQAChain.from_llm(
        graph=graph,
        llm=llm,
        validate_cypher=True,
        return_direct=True,  # Set to True as per notebook
        allow_dangerous_requests=True,
        verbose=verbose,
        cypher_llm_kwargs={
            "prompt": prompt,
            "stop": ["\n\n", "```"],
        },
    )
    
    return chain


def add_custom_examples(new_examples: list) -> list:
    """
    Allows dynamic addition of new examples for improved performance
    
    Args:
        new_examples: List of dicts with 'question' and 'query' keys
        
    Returns:
        Combined list of examples
    """
    base_examples = get_few_shot_examples()
    return base_examples + new_examples