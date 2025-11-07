from langchain_community.graphs import Neo4jGraph
from utils import get_neo4j_driver
from config import NEO4J_AURA_URI, NEO4J_USERNAME, NEO4J_PASSWORD

def get_graph():
    """Returns a Neo4j graph instance."""
    graph = Neo4jGraph(
        url=NEO4J_AURA_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD
    )
    return graph

def get_document_full_content(document_source):
    """
    Retrieve the full content of a document from the graph.
    
    Args:
        document_source (str): The source/path of the document
        
    Returns:
        str: The complete document content, or None if not found
    """
    from utils import get_neo4j_driver
    
    driver = get_neo4j_driver()
    if driver is None:
        return None
    
    try:
        with driver.session() as session:
            # Retrieve content directly from Document node
            result = session.run("""
                MATCH (d:Document {source: $source})
                RETURN d.content as content
            """, source=document_source)
            
            record = result.single()
            if record and record["content"]:
                return record["content"]
            else:
                return None
                
    except Exception as e:
        print(f"Error retrieving document content: {e}")
        return None

def create_graph_from_documents(documents):
    """
    Creates a knowledge graph from documents by extracting entities and relationships.
    This is a simplified example. A real-world implementation would use more
    sophisticated NLP techniques for entity and relationship extraction.
    
    Handles large documents by chunking them into smaller segments to avoid Neo4j
    index size limitations.
    """
    import time
    start_time = time.time()
    
    graph = get_graph()
    print("Clearing existing graph data...")
    graph.query("MATCH (n) DETACH DELETE n") # Clear the graph
    print(f"Graph cleared in {time.time() - start_time:.2f} seconds")
    
    # Define key urban planning concepts to extract
    concepts = [
        "urban design", "zoning", "land use", "transportation", "sustainability",
        "public space", "infrastructure", "housing", "community development",
        "city planning", "green space", "smart city", "urban renewal",
        "mixed-use development", "transit-oriented development", "urban density",
        "affordable housing", "complete streets", "climate resilience", 
        "walkability", "bicycle infrastructure", "public transit", "green infrastructure",
        "traffic calming", "urban heat island", "stormwater management", "economic development",
        "inclusive design", "tactical urbanism", "form-based code", "new urbanism",
        "gentrification", "urban sprawl", "placemaking", "historic preservation",
        "civic participation", "public engagement", "community involvement", "participatory planning",
        "charrettes", "public hearings", "citizen advisory", "community feedback",
        "stakeholder engagement", "public input", "grassroots planning"
    ]
    
    print(f"Creating document nodes and relationships with {len(concepts)} concepts...")
    concept_start_time = time.time()
    
    # Create document nodes with chunking for large documents
    # First, create all document parent nodes in a batch
    batch_size = 10
    doc_batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]
    
    doc_processing_start = time.time()
    print(f"Processing {len(documents)} documents in {len(doc_batches)} batches...")
    
    for batch_idx, doc_batch in enumerate(doc_batches):
        batch_start = time.time()
        # Prepare batch data
        batch_data = []
        for doc in doc_batch:
            source = doc.metadata["source"]
            content = doc.page_content
            batch_data.append({
                "source": source,
                "content_preview": content[:500] + "..." if len(content) > 500 else content,
                "content_length": len(content)
            })
        
        # Batch create document parent nodes
        batch_query = """
        UNWIND $batch as row
        MERGE (d:Document {source: row.source})
        SET d.content_preview = row.content_preview,
            d.content_length = row.content_length
        """
        graph.query(batch_query, params={"batch": batch_data})
        
        print(f"  Batch {batch_idx+1}/{len(doc_batches)} document nodes created in {time.time() - batch_start:.2f} seconds")
    
    print(f"All document parent nodes created in {time.time() - doc_processing_start:.2f} seconds")
    
    # Store all document content directly in Document nodes (no chunking)
    content_start = time.time()
    print("Storing document content (no chunking)...")
    
    for doc in documents:
        source = doc.metadata["source"]
        content = doc.page_content
        
        # Store content directly in document node (no chunking)
        graph.query(
            """
            MATCH (d:Document {source: $source})
            SET d.content = $content
            """,
            params={
                "source": source,
                "content": content
            }
        )
    
    print(f"Document content stored in {time.time() - content_start:.2f} seconds")
    
    # Process document-concept relationships
    relationships_start = time.time()
    print("Creating document-concept relationships...")
    
    for doc in documents:
        source = doc.metadata["source"]
        content = doc.page_content
        
        # Extract concepts from document and create relationships
        doc_concepts = []
        concept_data = []
        
        # Define category mapping for faster lookup
        category_map = {
            "transportation": "Mobility", "complete streets": "Mobility", 
            "public transit": "Mobility", "bicycle infrastructure": "Mobility",
            "walkability": "Mobility", "traffic calming": "Mobility",
            
            "housing": "Housing", "affordable housing": "Housing", 
            "mixed-use development": "Housing", "urban density": "Housing",
            "gentrification": "Housing",
            
            "sustainability": "Environment", "climate resilience": "Environment",
            "green infrastructure": "Environment", "urban heat island": "Environment",
            "stormwater management": "Environment",
            
            "zoning": "Land Use", "land use": "Land Use", 
            "form-based code": "Land Use", "new urbanism": "Land Use",
            "urban sprawl": "Land Use",
            
            "public space": "Public Realm", "placemaking": "Public Realm",
            "tactical urbanism": "Public Realm", "historic preservation": "Public Realm",
            
            "smart city": "Technology", "infrastructure": "Technology",
            
            "civic participation": "Public Engagement", "public engagement": "Public Engagement",
            "community involvement": "Public Engagement", "participatory planning": "Public Engagement",
            "charrettes": "Public Engagement", "public hearings": "Public Engagement",
            "citizen advisory": "Public Engagement", "community feedback": "Public Engagement",
            "stakeholder engagement": "Public Engagement", "public input": "Public Engagement",
            "grassroots planning": "Public Engagement"
        }
        
        # Process content once to find all concepts
        content_lower = content.lower()
        for concept in concepts:
            if concept.lower() in content_lower:
                doc_concepts.append(concept)
                
                # Get category with default to "General"
                category = category_map.get(concept, "General")
                
                # Add to batch data
                concept_data.append({
                    "concept": concept,
                    "source": source,
                    "category": category
                })
        
        # Batch create concepts and relationships if we found any
        if concept_data:
            graph.query(
                """
                UNWIND $batch as row
                MERGE (c:Concept {name: row.concept})
                SET c.category = row.category
                WITH c, row
                MATCH (d:Document {source: row.source})
                MERGE (d)-[:MENTIONS]->(c)
                MERGE (c)-[:MENTIONED_IN]->(d)
                WITH c, row
                MERGE (cat:Category {name: row.category})
                MERGE (c)-[:BELONGS_TO]->(cat)
                """,
                params={"batch": concept_data},
            )
        
        # Create relationships between related concepts that appear in the same document
        # Use batch processing for concept relationships
        relationship_batch = []
        for i, concept1 in enumerate(doc_concepts):
            for concept2 in doc_concepts[i+1:]:
                relationship_batch.append({
                    "concept1": concept1,
                    "concept2": concept2,
                    "source": source
                })
        
        # If we have relationships to create, use a batch query
        if relationship_batch:
            graph.query(
                """
                UNWIND $batch as row
                MATCH (c1:Concept {name: row.concept1})
                MATCH (c2:Concept {name: row.concept2})
                MERGE (c1)-[:RELATED_TO {source: row.source}]->(c2)
                """,
                params={"batch": relationship_batch},
            )
    
    relation_end_time = time.time()
    print(f"Document and concept relationships created in {relation_end_time - concept_start_time:.2f} seconds")
    
    # Create indexes for search optimization
    index_start_time = time.time()
    try:
        print("Creating indexes for search optimization...")
        # Create regular indexes instead of fulltext search
        graph.query(
            """
            CREATE INDEX document_content_preview_idx IF NOT EXISTS
            FOR (d:Document) ON (d.content_preview)
            """
        )
        graph.query(
            """
            CREATE INDEX concept_name_idx IF NOT EXISTS
            FOR (c:Concept) ON (c.name)
            """
        )
        print(f"Indexes created successfully in {time.time() - index_start_time:.2f} seconds")
    except Exception as e:
        # Index might already exist or not supported
        print(f"Note: Index creation issue: {str(e)}")
        print("Continuing without custom indexes.")

    total_time = time.time() - start_time
    print(f"Knowledge graph created successfully in Neo4j. Total time: {total_time:.2f} seconds")

def query_documents_by_concept(concept_name):
    """
    Retrieves documents that mention a specific concept.
    
    Args:
        concept_name: The name of the concept to query for
        
    Returns:
        A list of document sources and previews
    """
    graph = get_graph()
    
    result = graph.query(
        """
        MATCH (c:Concept {name: $concept_name})<-[:MENTIONS]-(d:Document)
        RETURN d.source AS source, d.content_preview AS preview
        """,
        params={"concept_name": concept_name}
    )
    
    return result

def search_documents(search_term):
    """
    Searches for documents containing the search term in document content.
    
    Args:
        search_term: The term to search for
        
    Returns:
        A list of document sources and matching content
    """
    graph = get_graph()
    
    # Search in document content
    results = graph.query(
        """
        MATCH (d:Document)
        WHERE d.content CONTAINS $search_term
        RETURN d.source AS source, 
               d.content_preview AS preview
        """,
        params={"search_term": search_term}
    )
    
    return results

if __name__ == "__main__":
    from kb_manager import ingest_documents
    from langchain_community.document_loaders import DirectoryLoader, TextLoader
    import os

    # We need to load the documents to create the graph
    kb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kb")
    loader = DirectoryLoader(
        kb_path, glob="**/*.txt", loader_cls=TextLoader, show_progress=True
    )
    documents = loader.load()
    create_graph_from_documents(documents)
