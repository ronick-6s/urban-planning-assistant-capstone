from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.graphs import Neo4jGraph
from langchain_core.documents import Document

import os
import time
from typing import List, Dict, Any

from config import MODEL_NAME, EMBEDDING_MODEL, MONGO_DB_NAME, MONGO_COLLECTION_NAME, VERBOSE_OUTPUT
from utils import get_mongo_client, get_neo4j_driver, query_document_full_content, search_document_chunks
from access_control import check_document_access, get_user, is_restricted_document, get_accessible_documents
from planner_topics import is_planner_topic

def get_rag_chain(user_id: str):
    """
    Creates a RAG chain that combines retrieval from both the vector store
    and the knowledge graph.
    """
    # Get user information for access control
    user = get_user(user_id)
    user_roles = user.get("roles", []) if user else []
    is_admin = "admin" in user_roles
    
    # MongoDB Retrieval
    if VERBOSE_OUTPUT:
        print("\n=== Setting up RAG pipeline ===")
        print("Initializing MongoDB connection...")
    client = get_mongo_client()
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    
    
    # Verify MongoDB collection has documents
    try:
        doc_count = collection.count_documents({})
        if VERBOSE_OUTPUT:
            print(f"MongoDB collection contains {doc_count} documents")
        
        # Show a sample document to verify content
        if doc_count > 0:
            sample_doc = collection.find_one({})
            if VERBOSE_OUTPUT:
                print(f"Sample document fields: {list(sample_doc.keys())}")
            
            # Show a preview of the text content
            if 'text' in sample_doc:
                text_preview = sample_doc['text'][:100] + "..." if len(sample_doc['text']) > 100 else sample_doc['text']
                if VERBOSE_OUTPUT:
                    print(f"Sample text: {text_preview}")
    except Exception as e:
        if VERBOSE_OUTPUT:
            print(f"Error checking MongoDB documents: {e}")
    
    if VERBOSE_OUTPUT:
        print("Initializing embedding model...")
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)
    
    if VERBOSE_OUTPUT:
        print("Setting up MongoDB vector store...")
    vector_store = MongoDBAtlasVectorSearch(
        collection=collection, embedding=embeddings
    )
    
    # Neo4j Setup - Import config directly
    if VERBOSE_OUTPUT:
        print("Initializing Neo4j connection...")
    from config import NEO4J_AURA_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    graph = Neo4jGraph(
        url=NEO4J_AURA_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD
    )
    
    # Verify Neo4j has nodes
    try:
        result = graph.query("MATCH (n) RETURN count(n) as count")
        if result and VERBOSE_OUTPUT:
            print(f"Neo4j graph contains {result[0]['count']} nodes")
    except Exception as e:
        if VERBOSE_OUTPUT:
            print(f"Error checking Neo4j nodes: {e}")
    
    if VERBOSE_OUTPUT:
        print("RAG pipeline initialized successfully")
        print("=====================================")
    
    # Define retrieval function
    def retrieve_docs(query: str) -> List[Document]:
        if VERBOSE_OUTPUT:
            print(f"\n=== Processing query: {query} ===")
        
        # Check if the user is a citizen asking about planner-specific topics
        if "citizen" in user_roles and is_planner_topic(query):
            print("Citizen asking about planner-specific topic. Access restricted.")
            return [Document(
                page_content="[ACCESS RESTRICTED: This is a technical planning topic that requires planner privileges. Please contact a planning professional for assistance.]",
                metadata={"retrieval_method": "access_denied", "reason": "This topic requires planner privileges"}
            )]
        
        # Initialize lists for documents with different access levels
        kg_docs = []
        access_denied_docs = []
        
        # Preprocess the query to handle common variations and related terms
        processed_query = query.lower()
        
        # Map common question variations to keywords more likely to match our content
        query_expansions = {
            "get involved": ["civic participation", "public engagement", "community involvement", "participation"],
            "participate": ["civic participation", "public engagement", "community involvement", "citizen engagement"],
            "urban planning": ["city planning", "urban design", "community development", "planning process"],
            "local planning": ["city planning", "urban planning", "municipal planning", "community planning"],
            "initiatives": ["programs", "projects", "development", "plans", "engagement"],
            "housing": ["affordable housing", "residential development", "housing policy", "homes"],
            "transportation": ["transit", "mobility", "complete streets", "transportation planning"],
            "sustainability": ["sustainable development", "green infrastructure", "climate resilience"],
            "development": ["urban development", "construction", "growth", "redevelopment"],
            "community": ["neighborhood", "local", "public", "residents"],
            "budget cut": ["municipal budget", "budget reduction", "budget planning", "fiscal management", "cost efficiency"],
            "trim budget": ["municipal budget", "budget reduction", "fiscal management", "cost saving", "budget efficiency"],
            "reduce expenses": ["municipal budget", "cost cutting", "financial planning", "budget management", "efficiency"],
            "financial": ["budget", "municipal finance", "fiscal planning", "economic impact", "revenue", "funding"]
        }
        
        # Analyze query for keywords
        keywords = []
        for word in processed_query.split():
            if len(word) > 3:  # Only consider words longer than 3 characters
                keywords.append(word)
        
        # Expand the query with related terms
        expanded_queries = [processed_query]
        
        # Add individual keywords from the query
        expanded_queries.extend(keywords)
        
        # Add expanded terms based on keywords in the query
        for key, expansions in query_expansions.items():
            if key in processed_query:
                expanded_queries.extend(expansions)
        
        # Add some specific expanded queries for common questions
        if "get involved" in processed_query or "how can i" in processed_query and "local planning" in processed_query:
            expanded_queries.extend(["civic participation", "public participation", "community engagement", 
                                    "public involvement", "citizen participation", "community input", 
                                    "stakeholder engagement", "planning process"])
                
        if VERBOSE_OUTPUT:
            print(f"Expanded search terms: {expanded_queries}")
        
        # 1. Vector Store Retrieval with metadata
        vector_docs = []
        try:
            if VERBOSE_OUTPUT:
                print("Attempting vector search with expanded terms...")
            # Try each expanded query until we get results
            for expanded_query in expanded_queries:
                if VERBOSE_OUTPUT:
                    print(f"  Trying term: '{expanded_query}'")
                try:
                    results = vector_store.similarity_search_with_score(expanded_query, k=3)
                    if results:
                        print(f"  ✓ Found {len(results)} results with '{expanded_query}'")
                        # Print sample results for debugging
                        for i, (doc, score) in enumerate(results[:2]):
                            source = doc.metadata.get("source", "unknown")
                            preview = doc.page_content[:50] + "..." if len(doc.page_content) > 50 else doc.page_content
                            if VERBOSE_OUTPUT:
                                print(f"    Result {i+1}: {os.path.basename(source)} (score: {score:.4f})")
                                print(f"    Preview: {preview}")
                        vector_docs.extend(results)
                        # Don't break - collect results from multiple terms
                except Exception as e:
                    print(f"  ✗ Error with term '{expanded_query}': {e}")
            
            # Deduplicate results
            seen_content = set()
            unique_vector_docs = []
            for doc, score in vector_docs:
                content_hash = hash(doc.page_content[:100])  # Hash the first 100 chars as a simple deduplication
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    unique_vector_docs.append((doc, score))
            
            vector_docs = unique_vector_docs
            if VERBOSE_OUTPUT:
                print(f"Total unique vector results: {len(vector_docs)}")
            
            # If we still have no results, try one more approach with a more lenient search
            if not vector_docs:
                # Try a keyword-based approach with higher k
                if VERBOSE_OUTPUT:
                    print("No results found with expanded terms, trying direct keyword search with higher k...")
                key_terms = " ".join([term for term in expanded_queries if len(term.split()) == 1])
                vector_docs = vector_store.similarity_search_with_score(key_terms, k=7)
                if VERBOSE_OUTPUT:
                    print(f"Retrieved {len(vector_docs)} documents using keyword search: '{key_terms}'")
                
        except Exception as e:
            if VERBOSE_OUTPUT:
                print(f"Vector store retrieval error: {e}")
            print("Continuing with empty vector results")
            vector_docs = []
        
        # Apply access control to vector results
        filtered_vector_docs = []
        access_denied_docs = []
        
        for doc, score in vector_docs:
            source = doc.metadata.get("source", "")
            has_access, reason = check_document_access(user_id, source)
            
            if has_access:
                # Add the score to metadata for hybrid ranking later
                doc.metadata["vector_score"] = score
                doc.metadata["retrieval_method"] = "vector"
                filtered_vector_docs.append(doc)
            elif is_restricted_document(source):
                # For restricted documents, create a special access denied document
                access_denied_docs.append(Document(
                    page_content=f"[ACCESS RESTRICTED] You don't have permission to access this document.",
                    metadata={
                        "source": source,
                        "vector_score": score,
                        "retrieval_method": "access_denied",
                        "reason": reason,
                        "is_restricted": True
                    }
                ))
        
        if VERBOSE_OUTPUT:
            print(f"After access control: {len(filtered_vector_docs)} vector documents, {len(access_denied_docs)} restricted")
        
        # 2. Direct Knowledge Graph Query - find relevant concepts without fulltext index
        if VERBOSE_OUTPUT:
            print("Executing Neo4j knowledge graph queries...")
        
        # Query for each expanded term
        kg_docs = []
        for expanded_query in expanded_queries:
            if VERBOSE_OUTPUT:
                print(f"  Trying graph query with term: '{expanded_query}'")
            
            # Direct document content search with CONTAINS - now also searches document chunks
            concept_query = """
            // Search in regular document content for small documents
            MATCH (node:Document)
            WHERE node.content CONTAINS $query
            WITH node, 0.8 as graph_score
            RETURN node.content as content, 
                  null as name, 
                  node.source as source,
                  graph_score,
                  false as is_chunk
            LIMIT 2
            
            UNION
            
            // Search in document chunks for large documents
            MATCH (d:Document)-[:HAS_CHUNK]->(c:DocumentChunk)
            WHERE c.content CONTAINS $query
            WITH d, c, 0.8 as graph_score
            RETURN c.content as content, 
                  null as name, 
                  d.source as source,
                  graph_score,
                  true as is_chunk
            LIMIT 3
            
            UNION
            
            // Search in concepts
            MATCH (node:Concept)
            WHERE node.name CONTAINS $query
            WITH node, 0.9 as graph_score
            RETURN null as content, 
                  node.name as name, 
                  null as source,
                  graph_score,
                  false as is_chunk
            LIMIT 2
            """
            
            try:
                # Execute direct search
                kg_results = graph.query(concept_query, params={"query": expanded_query})
                if VERBOSE_OUTPUT:
                    print(f"  ✓ Direct search found {len(kg_results)} results with '{expanded_query}'")
                
                # Print sample results
                if VERBOSE_OUTPUT:
                    for i, result in enumerate(kg_results[:2]):
                        content_type = "Document" if result.get("content") else "Concept"
                        content_preview = result.get("content", result.get("name", ""))
                        if content_preview and len(content_preview) > 50:
                            content_preview = content_preview[:50] + "..."
                        print(f"    Result {i+1}: {content_type} - {content_preview}")
                
                for result in kg_results:
                    source = result.get("source", "unknown")
                    has_access, reason = check_document_access(user_id, source)
                    if has_access:
                        content = result.get("content", result.get("name", ""))
                        is_chunk = result.get("is_chunk", False)
                        
                        if content:  # Ensure we have content
                            # For chunks, try to get the full document content when possible
                            full_content = None
                            if is_chunk and source:
                                try:
                                    neo4j_driver = get_neo4j_driver()
                                    full_content = query_document_full_content(neo4j_driver, source)
                                    if full_content and full_content != "Document content not available.":
                                        content = full_content
                                        print(f"    Retrieved full document content for chunked document: {source}")
                                except Exception as e:
                                    print(f"    Error retrieving full content: {e}")
                            
                            kg_docs.append(Document(
                                page_content=content,
                                metadata={
                                    "source": source,
                                    "graph_score": result.get("graph_score", 0.5),
                                    "retrieval_method": "graph_direct",
                                    "query_term": expanded_query,
                                    "is_chunk": is_chunk
                                }
                            ))
            except Exception as e:
                print(f"  ✗ Error with direct graph search for '{expanded_query}': {e}")
        
        # 3. Concept-based traversal search - only run once with original query
        if VERBOSE_OUTPUT:
            print("Executing concept-based traversal search...")
        
        # More flexible concept-based traversal
        concept_traversal_query = """
        // Find concepts relevant to the query
        MATCH (c:Concept)
        WHERE toLower(c.name) CONTAINS toLower($query)
        
        // Find documents that mention these concepts
        MATCH (c)<-[:MENTIONS]-(d:Document)
        
        // Return the results with relevance score
        RETURN d.content as content, 
               d.source as source, 
               c.name as concept,
               1.0 as relevance
        LIMIT 5
        
        UNION
        
        // Try to find documents directly matching the query
        MATCH (d:Document)
        WHERE toLower(d.content) CONTAINS toLower($query)
        RETURN d.content as content, 
               d.source as source, 
               'direct_match' as concept,
               0.9 as relevance
        LIMIT 3
        """
        
        try:
            # Execute concept traversal search with the original query
            relation_results = graph.query(concept_traversal_query, params={"query": query})
            if VERBOSE_OUTPUT:
                print(f"  ✓ Concept traversal search found {len(relation_results)} results")
            
            # Print sample results
            for i, result in enumerate(relation_results[:2]):
                source = result.get("source", "unknown source")
                concept = result.get("concept", "unknown concept")
                content_preview = result.get("content", "")[:50] + "..." if result.get("content") else ""
                if VERBOSE_OUTPUT:
                    print(f"    Result {i+1}: Source={os.path.basename(source)}, Concept={concept}")
                    print(f"    Preview: {content_preview}")
                
            # Check if we need to get full content for any chunked documents
            neo4j_driver = get_neo4j_driver()
            for i, result in enumerate(relation_results):
                if "content" in result and result.get("source"):
                    try:
                        # Try to get full document content for any results that might be chunks
                        source = result.get("source")
                        full_content = query_document_full_content(neo4j_driver, source)
                        if full_content and full_content != "Document content not available." and len(full_content) > len(result.get("content", "")):
                            print(f"    Retrieved full content for document: {os.path.basename(source)}")
                            result["content"] = full_content
                            result["is_full_content"] = True
                    except Exception as e:
                        print(f"    Error checking for full content: {e}")
            
            for result in relation_results:
                source = result.get("source", "unknown")
                has_access, reason = check_document_access(user_id, source)
                if has_access:
                    concept = result.get("concept", "unknown concept")
                    content = result.get("content", "")
                    if content:  # Ensure we have content
                        # Add concept information to the content
                        if concept != "direct_match":
                            content = f"{content}\n[Related to concept: {concept}]"
                        
                        kg_docs.append(Document(
                            page_content=content,
                            metadata={
                                "source": source,
                                "concept": concept,
                                "relevance": result.get("relevance", 1),
                                "retrieval_method": "graph_traversal"
                            }
                        ))
        except Exception as e:
            if VERBOSE_OUTPUT:
                print(f"  ✗ Error with concept traversal search: {e}")
        
        # 4. Additional related concepts search
        related_concepts_query = """
        // Find concepts in the same categories as concepts matching the query
        MATCH (c1:Concept)-[:BELONGS_TO]->(cat:Category)<-[:BELONGS_TO]-(c2:Concept)
        WHERE toLower(c1.name) CONTAINS toLower($query)
          AND c1 <> c2
        
        // Find documents mentioning the related concepts
        MATCH (c2)-[:MENTIONED_IN]->(d:Document)
        
        // Return the documents with relevance scores
        RETURN d.content as content, 
               d.source as source, 
               c1.name as original_concept,
               c2.name as related_concept,
               0.7 as relevance
        LIMIT 5
        """
        
        try:
            # Only execute if we have few results so far
            if len(kg_docs) < 3:
                print("  Executing related concepts search for additional results...")
                related_results = graph.query(related_concepts_query, params={"query": query})
                print(f"  ✓ Related concepts search found {len(related_results)} results")
                
                for result in related_results:
                    source = result.get("source", "unknown")
                    has_access, reason = check_document_access(user_id, source)
                    if has_access:
                        original_concept = result.get("original_concept", "")
                        related_concept = result.get("related_concept", "")
                        content = result.get("content", "")
                        if content:  # Ensure we have content
                            content = f"{content}\n[Related concepts: {original_concept} → {related_concept}]"
                            kg_docs.append(Document(
                                page_content=content,
                                metadata={
                                    "source": source,
                                    "original_concept": original_concept,
                                    "related_concept": related_concept,
                                    "relevance": result.get("relevance", 0.7),
                                    "retrieval_method": "related_concepts"
                                }
                            ))
        except Exception as e:
            if VERBOSE_OUTPUT:
                print(f"  ✗ Error with related concepts search: {e}")
                    
        if VERBOSE_OUTPUT:
            print(f"Retrieved {len(kg_docs)} documents from knowledge graph")
        
        # 4. Hybrid ranking and combination
        if VERBOSE_OUTPUT:
            print("\n=== Combining and ranking results ===")
        # First, add all documents to a single list
        all_docs = filtered_vector_docs + kg_docs
        if VERBOSE_OUTPUT:
            print(f"Total documents before deduplication: {len(all_docs)}")
        
        # Remove duplicates (if any document appears in both sources)
        unique_docs = {}
        for doc in all_docs:
            # Create a content signature based on first 100 chars for deduplication
            content_signature = doc.page_content[:100].strip()
            source = doc.metadata.get('source', '')
            key = f"{source}-{hash(content_signature)}"
            
            # Prioritize vector results or higher-scoring results when duplicates exist
            if key not in unique_docs:
                unique_docs[key] = doc
            elif doc.metadata.get("retrieval_method") == "vector" and unique_docs[key].metadata.get("retrieval_method") != "vector":
                # Vector results override graph results
                unique_docs[key] = doc
            elif doc.metadata.get("retrieval_method") == unique_docs[key].metadata.get("retrieval_method"):
                # If same retrieval method, keep the one with better score
                current_score = 0
                new_score = 0
                
                # Get appropriate score based on retrieval method
                if doc.metadata.get("retrieval_method") == "vector":
                    current_score = unique_docs[key].metadata.get("vector_score", 1.0)
                    new_score = doc.metadata.get("vector_score", 1.0)
                elif doc.metadata.get("retrieval_method") == "graph_direct":
                    current_score = unique_docs[key].metadata.get("graph_score", 0.5)
                    new_score = doc.metadata.get("graph_score", 0.5)
                else:
                    current_score = unique_docs[key].metadata.get("relevance", 0.5)
                    new_score = doc.metadata.get("relevance", 0.5)
                
                # Lower scores are better for vector search, higher for graph
                if (doc.metadata.get("retrieval_method") == "vector" and new_score < current_score) or \
                   (doc.metadata.get("retrieval_method") != "vector" and new_score > current_score):
                    unique_docs[key] = doc
        
        # Rank documents by a combination of scores from different retrieval methods
        ranked_docs = list(unique_docs.values())
        
        # Custom sorting function for hybrid ranking
        def hybrid_rank(doc):
            method = doc.metadata.get("retrieval_method", "")
            
            # Base rank by method (lower is better)
            method_rank = {
                "vector": 1,
                "graph_direct": 2,
                "graph_traversal": 3,
                "related_concepts": 4
            }.get(method, 5)
            
            # Score within that method (normalized to be comparable)
            if method == "vector":
                # Lower vector scores are better (convert to 0-1 range, inverted)
                score = 1.0 - min(doc.metadata.get("vector_score", 1.0), 1.0)
            elif method == "graph_direct":
                # Higher graph scores are better (0-1 range)
                score = doc.metadata.get("graph_score", 0.5)
            else:
                # Higher relevance is better (0-1 range)
                score = doc.metadata.get("relevance", 0.5)
            
            # Return a tuple for sorting (method_rank first, then score)
            # This prioritizes method type first, then score within that method
            return (method_rank, -score)  # Negative score because we want higher scores first
        
        # Sort the documents
        ranked_docs.sort(key=hybrid_rank)
        
        # Limit to a reasonable number of documents
        ranked_docs = ranked_docs[:10]  # Adjust the limit as needed
        
        if VERBOSE_OUTPUT:
            print(f"Final retrieval: {len(ranked_docs)} unique documents")
        
        # Print document details for debugging
        if VERBOSE_OUTPUT:
            print("\n=== Retrieved Documents ===")
        for i, doc in enumerate(ranked_docs):
            method = doc.metadata.get("retrieval_method", "unknown")
            source = os.path.basename(doc.metadata.get("source", "unknown"))
            
            # Get the score based on retrieval method
            score_info = ""
            if method == "vector":
                score_info = f"vector_score: {doc.metadata.get('vector_score', 'N/A'):.4f}"
            elif method == "graph_direct":
                score_info = f"graph_score: {doc.metadata.get('graph_score', 'N/A')}"
            else:
                score_info = f"relevance: {doc.metadata.get('relevance', 'N/A')}"
                
            # Get content preview
            preview = doc.page_content[:100].replace("\n", " ") + "..." if len(doc.page_content) > 100 else doc.page_content
            
            if VERBOSE_OUTPUT:
                print(f"Document {i+1}: {source} (method: {method}, {score_info})")
                print(f"  Preview: {preview}\n")
        
        return ranked_docs
    
    template = """
    You are an urban planning assistant with expertise in city planning, zoning, community development, 
    transportation planning, and sustainable development. You help users by providing accurate, 
    comprehensive information about urban planning principles, practices, and processes.
    
    The user's role is: {user_roles}
    
    Answer the question based only on the following context. If the context contains ACCESS RESTRICTED notices,
    do not attempt to answer the question at all - instead, provide only the access restriction message. 
    Do not try to be helpful by providing related information when access is restricted.
    
    If the context doesn't contain enough information to give a complete answer, acknowledge what you don't 
    know rather than making up information. If relevant, mention specific urban planning concepts, approaches, 
    or case studies from the context.
    
    IMPORTANT ACCESS CONTROL RULES:
    1. If the user is not an administrator but is asking about administrative topics that require access to
       restricted documents, provide a brief response: "I don't have access to this information. This data 
       requires administrative privileges. Please contact an administrator for assistance."
    2. If the user is not a planner but is asking about technical planning topics that require access to
       professional planning documents, provide a brief response: "I don't have access to this information. This data 
       requires planner privileges. Please contact a planning professional for assistance."
    3. If the user is an administrator asking about administrative content, provide as much information as possible.
    4. If the user is a planner asking about technical planning content, provide as much information as possible.
    
    CONTEXT:
    {context}

    QUESTION: {question}
    
    ANSWER:
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME)
    
    def format_docs(docs):
        # Process each document and add access restriction notices
        processed_docs = []
        restricted_docs_count = 0
        
        for doc in docs:
            content = doc.page_content
            method = doc.metadata.get("retrieval_method", "")
            
            # If this is an access denied document, mark it clearly
            if method == "access_denied":
                restricted_docs_count += 1
                # Don't add individual restriction notices - we'll add a single summary notice instead
            else:
                processed_docs.append(content)
        
        # Add a summary of restrictions at the beginning if needed
        result = "\n\n".join(processed_docs)
        if restricted_docs_count > 0:
            if "citizen" in user_roles:
                restriction_notice = f"[ACCESS RESTRICTED: This information requires planner privileges. Please contact a planning professional for assistance.]"
                # For citizens, just return the restriction notice without any other content
                return restriction_notice
            else:
                restriction_notice = f"[ACCESS RESTRICTED: You don't have permission to access {restricted_docs_count} document(s) related to this topic.]"
                result = restriction_notice + "\n\n" + result
            
        return result
    
    # Create the RAG chain
    rag_chain = (
        {
            "question": RunnablePassthrough(), 
            "context": lambda query: format_docs(retrieve_docs(query)),
            "user_roles": lambda _: ", ".join(user_roles)
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain
