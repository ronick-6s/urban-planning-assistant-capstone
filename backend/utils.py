from pymongo import MongoClient
from neo4j import GraphDatabase
from config import MONGO_ATLAS_URI, NEO4J_AURA_URI, NEO4J_USERNAME, NEO4J_PASSWORD

def get_mongo_client():
    """Returns a MongoDB client."""
    client = MongoClient(MONGO_ATLAS_URI)
    return client

def get_neo4j_driver():
    """Returns a Neo4j driver."""
    driver = GraphDatabase.driver(NEO4J_AURA_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    return driver

def query_document_full_content(driver, source):
    """
    Retrieves the full content of a document by its source.
    Handles chunked documents by reassembling all chunks.
    
    Args:
        driver: Neo4j driver instance
        source: The source identifier of the document
        
    Returns:
        The full document content as string
    """
    with driver.session() as session:
        # First check if document has content directly (small document)
        result = session.run(
            """
            MATCH (d:Document {source: $source})
            RETURN d.content AS content, 
                  EXISTS((d)-[:HAS_CHUNK]->()) AS has_chunks
            """,
            source=source
        ).single()
        
        if result and result["content"] is not None:
            # Document content is stored directly
            return result["content"]
        
        elif result and result["has_chunks"]:
            # Document is chunked, retrieve and assemble all chunks
            chunks_result = session.run(
                """
                MATCH (d:Document {source: $source})-[:HAS_CHUNK]->(c:DocumentChunk)
                RETURN c.content AS content, c.chunk_index AS index, c.total_chunks AS total
                ORDER BY c.chunk_index
                """,
                source=source
            ).values()
            
            if chunks_result:
                # Get total chunks from first result
                total_chunks = chunks_result[0][2]
                # Assemble chunks in correct order
                chunks = [None] * total_chunks
                for content, index, _ in chunks_result:
                    chunks[index] = content
                
                return "".join([c for c in chunks if c is not None])
    
    # Document not found or has no content
    return "Document content not available."

def search_document_chunks(driver, search_term):
    """
    Searches for documents containing the search term in either
    document content or document chunks.
    
    Args:
        driver: Neo4j driver instance
        search_term: The term to search for
        
    Returns:
        A list of document sources and matching content
    """
    results = []
    with driver.session() as session:
        # Search in direct document content (for smaller documents)
        direct_results = session.run(
            """
            MATCH (d:Document)
            WHERE d.content CONTAINS $search_term
            RETURN d.source AS source, 
                  d.content_preview AS preview,
                  'direct' AS match_type
            """,
            search_term=search_term
        )
        
        for record in direct_results:
            results.append({
                "source": record["source"],
                "preview": record["preview"],
                "match_type": record["match_type"]
            })
        
        # Search in document chunks (for larger documents)
        chunk_results = session.run(
            """
            MATCH (d:Document)-[:HAS_CHUNK]->(c:DocumentChunk)
            WHERE c.content CONTAINS $search_term
            RETURN d.source AS source, 
                  d.content_preview AS preview,
                  'chunk' AS match_type,
                  c.chunk_index AS chunk_index
            """,
            search_term=search_term
        )
        
        for record in chunk_results:
            results.append({
                "source": record["source"],
                "preview": record["preview"],
                "match_type": record["match_type"],
                "chunk_index": record["chunk_index"]
            })
    
    return results
