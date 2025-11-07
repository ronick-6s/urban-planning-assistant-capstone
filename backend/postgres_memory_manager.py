import os
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, ARRAY, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    Vector = None
from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

Base = declarative_base()

class ConversationMemory(Base):
    """PostgreSQL table for storing conversation embeddings with pgvector support"""
    __tablename__ = 'conversation_memory'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    user_query = Column(Text, nullable=False)
    assistant_response = Column(Text, nullable=False)
    
    # Use pgvector if available, otherwise fall back to ARRAY(Float)
    if PGVECTOR_AVAILABLE:
        embedding = Column(Vector(384), nullable=False)  # 384-dimensional vector for all-MiniLM-L6-v2
    else:
        embedding = Column(ARRAY(Float), nullable=False)  # Fallback to array of floats
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ConversationMemory(user_id='{self.user_id}', session_id='{self.session_id}', timestamp='{self.timestamp}')>"

class PostgreSQLMemoryManager:
    """
    A memory manager using PostgreSQL with vector embeddings for semantic similarity search.
    """
    
    def __init__(self):
        """Initialize the PostgreSQL connection and sentence transformer model."""
        
        # Create database connection string
        if POSTGRES_PASSWORD:
            db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        else:
            db_url = f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        
        # Initialize SQLAlchemy
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
        # Enable pgvector extension if available
        self.use_pgvector = False
        if PGVECTOR_AVAILABLE:
            self._enable_pgvector_extension()
            self.use_pgvector = True
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        
        # Create vector index for fast similarity search if using pgvector
        if self.use_pgvector:
            self._create_vector_index()
        
        # Initialize sentence transformer for embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # In-memory storage for current session
        self.session_memory: Dict[str, List[str]] = {}
        self.current_session_id: Optional[str] = None
    
    def _enable_pgvector_extension(self):
        """Enable the pgvector extension in PostgreSQL."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not enable pgvector extension: {e}")
    
    def _create_vector_index(self):
        """Create an index on the embedding column for fast similarity search."""
        try:
            with self.engine.connect() as conn:
                # Create HNSW index for fast approximate nearest neighbor search
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS conversation_memory_embedding_idx 
                    ON conversation_memory 
                    USING hnsw (embedding vector_cosine_ops)
                """))
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not create vector index: {e}")
    
    def start_session(self, user_id: str) -> str:
        """Start a new session for a user."""
        timestamp = datetime.now().isoformat()
        session_id = hashlib.md5(f"{user_id}-{timestamp}".encode()).hexdigest()[:16]
        self.current_session_id = session_id
        self.session_memory[session_id] = []
        return session_id
    
    def load_session(self, session_id: str, user_id: str):
        """Load an existing session and its context."""
        self.current_session_id = session_id
        
        # Initialize session memory if not exists
        if session_id not in self.session_memory:
            self.session_memory[session_id] = []
            
            # Load conversation history from database
            session = self.Session()
            try:
                conversations = session.query(ConversationMemory).filter(
                    ConversationMemory.session_id == session_id,
                    ConversationMemory.user_id == user_id
                ).order_by(ConversationMemory.timestamp).all()
                
                # Reconstruct session memory from database
                for conv in conversations:
                    self.session_memory[session_id].append(f"User: {conv.user_query}")
                    self.session_memory[session_id].append(f"Assistant: {conv.assistant_response}")
                    
                print(f"Loaded {len(conversations)} conversation turns for session {session_id}")
                
            except Exception as e:
                print(f"Error loading session {session_id}: {e}")
            finally:
                session.close()
    
    def add_conversation_turn(self, user_id: str, user_query: str, assistant_response: str):
        """
        Add a conversation turn to both session memory and PostgreSQL database.
        """
        if not self.current_session_id:
            self.start_session(user_id)
        
        # Add to in-memory session storage
        self.session_memory[self.current_session_id].append(f"User: {user_query}")
        self.session_memory[self.current_session_id].append(f"Assistant: {assistant_response}")
        
        # Create combined text for embedding
        combined_text = f"User query: {user_query}\nAssistant response: {assistant_response}"
        
        # Generate embedding
        embedding_vector = self.model.encode(combined_text)
        
        # Prepare embedding based on available extensions
        if PGVECTOR_AVAILABLE:
            embedding = embedding_vector.tolist()  # pgvector handles list format
        else:
            embedding = embedding_vector.tolist()  # Ensure it's a Python list for ARRAY
        
        # Store in PostgreSQL
        session = self.Session()
        try:
            memory_record = ConversationMemory(
                user_id=user_id,
                session_id=self.current_session_id,
                user_query=user_query,
                assistant_response=assistant_response,
                embedding=embedding,
                timestamp=datetime.utcnow()
            )
            session.add(memory_record)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error saving to database: {e}")
        finally:
            session.close()
    
    def get_session_context(self) -> str:
        """Return the conversation history from the current session."""
        if not self.current_session_id or not self.session_memory.get(self.current_session_id):
            return "No current session history."
        
        return "\n".join(self.session_memory[self.current_session_id])
    
    def get_relevant_long_term_context(self, user_query: str, user_id: str, limit: int = 3) -> str:
        """
        Find the most relevant past conversations using cosine similarity.
        Uses pgvector for efficient similarity search when available.
        """
        if not user_query:
            return ""
        
        # Generate embedding for the query
        query_embedding = self.model.encode(user_query)
        
        session = self.Session()
        try:
            if PGVECTOR_AVAILABLE:
                # Use pgvector for efficient similarity search
                relevant_memories = self._pgvector_similarity_search(
                    session, query_embedding, user_id, limit
                )
            else:
                # Fallback to manual similarity calculation
                relevant_memories = self._manual_similarity_search(
                    session, query_embedding, user_id, limit
                )
            
            if not relevant_memories:
                return ""
            
            # Format the results
            context_parts = ["Relevant past conversations:"]
            for memory in relevant_memories:
                context_parts.append(
                    f"- Past Q: '{memory.user_query}' (Response: '{memory.assistant_response[:80]}...')"
                )
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"Error retrieving long-term context: {e}")
            return ""
        finally:
            session.close()
    
    def _pgvector_similarity_search(self, session, query_embedding, user_id: str, limit: int):
        """Use pgvector for efficient similarity search."""
        try:
            # Convert numpy array to list for pgvector
            query_vector = query_embedding.tolist()
            
            # Use pgvector's cosine distance operator (<->)
            results = session.query(
                ConversationMemory,
                ConversationMemory.embedding.cosine_distance(query_vector).label('distance')
            ).filter(
                ConversationMemory.user_id == user_id
            ).order_by(
                ConversationMemory.embedding.cosine_distance(query_vector)
            ).limit(limit * 2).all()  # Get more results to filter by threshold
            
            # Filter by similarity threshold (distance < 0.4 means similarity > 0.6)
            relevant_memories = [
                memory for memory, distance in results 
                if distance < 0.4  # Convert distance to similarity threshold
            ][:limit]
            
            return relevant_memories
        except Exception as e:
            print(f"pgvector search failed, falling back to manual search: {e}")
            # Fall back to manual search if pgvector operations fail
            return self._manual_similarity_search(session, query_embedding, user_id, limit)
    
    def _manual_similarity_search(self, session, query_embedding, user_id: str, limit: int):
        """Fallback method using manual similarity calculation."""
        # Fetch recent memories (last 100) for the user
        recent_memories = session.query(ConversationMemory).filter(
            ConversationMemory.user_id == user_id
        ).order_by(ConversationMemory.timestamp.desc()).limit(100).all()
        
        if not recent_memories:
            return []
        
        # Calculate similarities
        similarities = []
        for memory in recent_memories:
            memory_embedding = np.array(memory.embedding)
            similarity = self._cosine_similarity(query_embedding, memory_embedding)
            similarities.append((similarity, memory))
        
        # Sort by similarity (highest first) and filter by threshold
        similarities.sort(key=lambda x: x[0], reverse=True)
        relevant_memories = [
            memory for similarity, memory in similarities[:limit] 
            if similarity > 0.6  # Similarity threshold
        ]
        
        return relevant_memories
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def get_user_memory_count(self, user_id: str) -> int:
        """Get the total number of memories for a user."""
        session = self.Session()
        try:
            count = session.query(ConversationMemory).filter(
                ConversationMemory.user_id == user_id
            ).count()
            return count
        except Exception:
            return 0
        finally:
            session.close()
    
    def cleanup_old_memories(self, days_old: int = 90):
        """Remove memories older than specified days."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        session = self.Session()
        try:
            deleted = session.query(ConversationMemory).filter(
                ConversationMemory.timestamp < cutoff_date
            ).delete()
            session.commit()
            return deleted
        except Exception as e:
            session.rollback()
            print(f"Error cleaning up old memories: {e}")
            return 0
        finally:
            session.close()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics."""
        session = self.Session()
        try:
            from sqlalchemy import func
            
            stats = {
                "pgvector_enabled": PGVECTOR_AVAILABLE,
                "total_memories": session.query(ConversationMemory).count(),
                "unique_users": session.query(ConversationMemory.user_id).distinct().count(),
                "unique_sessions": session.query(ConversationMemory.session_id).distinct().count(),
            }
            
            # Get per-user statistics
            user_stats = {}
            results = session.query(
                ConversationMemory.user_id,
                func.count(ConversationMemory.id).label('count')
            ).group_by(ConversationMemory.user_id).all()
            
            for user_id, count in results:
                user_stats[user_id] = count
            
            stats["user_memory_counts"] = user_stats
            
            return stats
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {"error": str(e)}
        finally:
            session.close()
    
    def find_similar_conversations(self, query: str, user_id: str = None, limit: int = 5, threshold: float = 0.7) -> List[Dict]:
        """
        Advanced similarity search for conversations.
        Returns detailed similarity results for analysis.
        """
        if not query:
            return []
        
        query_embedding = self.model.encode(query)
        session = self.Session()
        
        try:
            base_query = session.query(ConversationMemory)
            if user_id:
                base_query = base_query.filter(ConversationMemory.user_id == user_id)
            
            if PGVECTOR_AVAILABLE:
                # Use pgvector for efficient search
                query_vector = query_embedding.tolist()
                results = base_query.add_columns(
                    ConversationMemory.embedding.cosine_distance(query_vector).label('distance')
                ).order_by(
                    ConversationMemory.embedding.cosine_distance(query_vector)
                ).limit(limit * 2).all()
                
                similar_conversations = []
                for memory, distance in results:
                    similarity = 1 - distance  # Convert distance to similarity
                    if similarity >= threshold:
                        similar_conversations.append({
                            "memory_id": str(memory.id),
                            "user_id": memory.user_id,
                            "session_id": memory.session_id,
                            "user_query": memory.user_query,
                            "assistant_response": memory.assistant_response[:200] + "...",
                            "similarity": float(similarity),
                            "timestamp": memory.timestamp.isoformat()
                        })
                
                return similar_conversations[:limit]
            else:
                # Fallback to manual calculation
                memories = base_query.limit(200).all()  # Limit for performance
                similarities = []
                
                for memory in memories:
                    memory_embedding = np.array(memory.embedding)
                    similarity = self._cosine_similarity(query_embedding, memory_embedding)
                    if similarity >= threshold:
                        similarities.append((similarity, memory))
                
                similarities.sort(key=lambda x: x[0], reverse=True)
                
                return [{
                    "memory_id": str(memory.id),
                    "user_id": memory.user_id,
                    "session_id": memory.session_id,
                    "user_query": memory.user_query,
                    "assistant_response": memory.assistant_response[:200] + "...",
                    "similarity": float(similarity),
                    "timestamp": memory.timestamp.isoformat()
                } for similarity, memory in similarities[:limit]]
                
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []
        finally:
            session.close()
    
    def get_user_sessions(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user with summary information."""
        session = self.Session()
        try:
            from sqlalchemy import func
            
            # Get sessions with summary info
            sessions = session.query(
                ConversationMemory.session_id,
                func.count(ConversationMemory.id).label('message_count'),
                func.min(ConversationMemory.timestamp).label('first_timestamp'),
                func.max(ConversationMemory.timestamp).label('last_timestamp')
            ).filter(
                ConversationMemory.user_id == user_id
            ).group_by(
                ConversationMemory.session_id
            ).order_by(
                func.max(ConversationMemory.timestamp).desc()
            ).limit(limit).all()
            
            session_info = []
            for sess in sessions:
                # Get first and last messages for this session
                first_msg = session.query(ConversationMemory).filter(
                    ConversationMemory.user_id == user_id,
                    ConversationMemory.session_id == sess.session_id
                ).order_by(ConversationMemory.timestamp.asc()).first()
                
                last_msg = session.query(ConversationMemory).filter(
                    ConversationMemory.user_id == user_id,
                    ConversationMemory.session_id == sess.session_id
                ).order_by(ConversationMemory.timestamp.desc()).first()
                
                session_info.append({
                    "session_id": sess.session_id,
                    "message_count": sess.message_count,
                    "first_message": first_msg.user_query[:100] + "..." if first_msg else "No messages",
                    "last_message": last_msg.user_query[:100] + "..." if last_msg else "No messages",
                    "first_timestamp": sess.first_timestamp.isoformat() if sess.first_timestamp else None,
                    "last_timestamp": sess.last_timestamp.isoformat() if sess.last_timestamp else None
                })
            
            return session_info
            
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []
        finally:
            session.close()
    
    def get_session_history(self, user_id: str, session_id: str) -> str:
        """Get complete chat history for a specific session."""
        session = self.Session()
        try:
            memories = session.query(ConversationMemory).filter(
                ConversationMemory.user_id == user_id,
                ConversationMemory.session_id == session_id
            ).order_by(ConversationMemory.timestamp.asc()).all()
            
            if not memories:
                return "No conversation history found for this session."
            
            history_parts = []
            for memory in memories:
                history_parts.append(f"[USER] {memory.user_query}")
                history_parts.append(f"[ASSISTANT] {memory.assistant_response}")
            
            return "\n".join(history_parts)
            
        except Exception as e:
            print(f"Error getting session history: {e}")
            return f"Error retrieving session history: {e}"
        finally:
            session.close()
    
    def get_complete_user_history(self, user_id: str, session_ids: List[str] = None) -> str:
        """Get complete chat history for a user, optionally filtered by session IDs."""
        session = self.Session()
        try:
            query = session.query(ConversationMemory).filter(
                ConversationMemory.user_id == user_id
            )
            
            if session_ids:
                query = query.filter(ConversationMemory.session_id.in_(session_ids))
            
            memories = query.order_by(ConversationMemory.timestamp.asc()).all()
            
            if not memories:
                return "No conversation history found."
            
            # Group by session for better organization
            sessions = {}
            for memory in memories:
                if memory.session_id not in sessions:
                    sessions[memory.session_id] = []
                sessions[memory.session_id].append(memory)
            
            history_parts = []
            for session_id, session_memories in sessions.items():
                history_parts.append(f"[SYSTEM] Session: {session_id}")
                for memory in session_memories:
                    history_parts.append(f"[USER] {memory.user_query}")
                    history_parts.append(f"[ASSISTANT] {memory.assistant_response}")
                history_parts.append("")  # Empty line between sessions
            
            return "\n".join(history_parts)
            
        except Exception as e:
            print(f"Error getting complete user history: {e}")
            return f"Error retrieving user history: {e}"
        finally:
            session.close()

# Singleton instance
_memory_manager_instance = None

def get_memory_manager():
    """Get the singleton instance of the PostgreSQL memory manager."""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = PostgreSQLMemoryManager()
    return _memory_manager_instance
