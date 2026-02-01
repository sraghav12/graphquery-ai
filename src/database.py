"""
Database utilities for Neo4j connection and data management
"""

from langchain_neo4j import Neo4jGraph
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jDatabase:
    """Wrapper class for Neo4j database operations"""
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize Neo4j database connection
        
        Args:
            uri: Neo4j connection URI
            username: Database username
            password: Database password
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.graph: Optional[Neo4jGraph] = None
    
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.graph = Neo4jGraph(
                url=self.uri,
                username=self.username,
                password=self.password
            )
            # Test connection
            self.graph.query("RETURN 1 AS ok")
            logger.info("Successfully connected to Neo4j database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            return False
    
    def load_movie_data(self) -> bool:
        """
        Load sample movie data into the database
        
        Returns:
            True if data loaded successfully, False otherwise
        """
        if not self.graph:
            logger.error("Database not connected")
            return False
        
        movie_query = """
        LOAD CSV WITH HEADERS FROM
        'https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv' as row
        
        MERGE(m:Movie{id:row.movieId})
        SET m.released = date(row.released),
            m.title = row.title,
            m.imdbRating = toFloat(row.imdbRating)
        FOREACH (director in split(row.director, '|') | 
            MERGE (p:Person {name:trim(director)})
            MERGE (p)-[:DIRECTED]->(m))
        FOREACH (actor in split(row.actors, '|') | 
            MERGE (p:Person {name:trim(actor)})
            MERGE (p)-[:ACTED_IN]->(m))
        FOREACH (genre in split(row.genres, '|') | 
            MERGE (g:Genre {name:trim(genre)})
            MERGE (m)-[:IN_GENRE]->(g))
        """
        
        try:
            self.graph.query(movie_query)
            logger.info("Successfully loaded movie data")
            return True
        except Exception as e:
            logger.error(f"Failed to load movie data: {str(e)}")
            return False
    
    def get_schema(self) -> str:
        """
        Get database schema
        
        Returns:
            Schema as string
        """
        if not self.graph:
            return "Database not connected"
        
        self.graph.refresh_schema()
        return self.graph.schema
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with database stats
        """
        if not self.graph:
            return {}
        
        try:
            stats = {}
            
            # Count movies
            result = self.graph.query("MATCH (m:Movie) RETURN count(m) AS count")
            stats['movies'] = result[0]['count'] if result else 0
            
            # Count actors
            result = self.graph.query("MATCH (p:Person)-[:ACTED_IN]->(:Movie) RETURN count(DISTINCT p) AS count")
            stats['actors'] = result[0]['count'] if result else 0
            
            # Count directors
            result = self.graph.query("MATCH (p:Person)-[:DIRECTED]->(:Movie) RETURN count(DISTINCT p) AS count")
            stats['directors'] = result[0]['count'] if result else 0
            
            # Count genres
            result = self.graph.query("MATCH (g:Genre) RETURN count(g) AS count")
            stats['genres'] = result[0]['count'] if result else 0
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {}
    
    def execute_query(self, query: str) -> list:
        """
        Execute a Cypher query
        
        Args:
            query: Cypher query string
            
        Returns:
            Query results as list
        """
        if not self.graph:
            logger.error("Database not connected")
            return []
        
        try:
            return self.graph.query(query)
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.graph:
            # Neo4jGraph doesn't have explicit close, but we can clear the reference
            self.graph = None
            logger.info("Database connection closed")