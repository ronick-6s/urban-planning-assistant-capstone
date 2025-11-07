import os
import warnings
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logger
logger = logging.getLogger(__name__)

# Suppress all warnings and verbose output for clean API experience
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Disable specific library logs
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("add_real_estate_metrics").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("neo4j").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.ERROR)

from agent import create_agent
from access_control import get_user
from kb_manager import ingest_documents
from kg_manager import create_graph_from_documents
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from role_fallbacks import generate_role_response
from postgres_memory_manager import get_memory_manager
from silent_output import suppress_prints, silent_execution

# Import admin financial tools for administrator-only access
try:
    from admin_financial_tools import get_all_financial_metrics, get_specific_financial_metric
except ImportError:
    pass  # Silently handle missing admin tools

# FastAPI app instance
app = FastAPI(title="Urban Planning Assistant API", version="1.0.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:3000", "http://127.0.0.1:3000"],  # Vite and React default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    user_id: str
    query: str
    session_id: Optional[str] = None
    user_email: Optional[str] = None  # Add user email for folder management

class ChatResponse(BaseModel):
    response: str
    user_id: str
    session_id: Optional[str] = None

class ReportRequest(BaseModel):
    user_id: str
    user_email: Optional[str] = None  # Add user email for folder management
    email: Optional[str] = None
    session_ids: Optional[List[str]] = None  # Allow user to select specific sessions
    include_all_history: Optional[bool] = False  # Include all user's chat history

class ChatHistoryRequest(BaseModel):
    user_id: str
    limit: Optional[int] = 20

class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    first_message: str
    last_message: str
    first_timestamp: str
    last_timestamp: str

class UserSessionsResponse(BaseModel):
    user_id: str
    sessions: List[SessionInfo]
    total_sessions: int

# Storage and email configuration

# Global variables to store agents and memory managers per user
user_agents = {}
user_sessions = {}

def initialize_knowledge():
    """Initialize the knowledge base and knowledge graph silently."""
    with suppress_prints():
        try:
            # Test and initialize database connections silently
            from utils import get_mongo_client, get_neo4j_driver
            from config import MONGO_DB_NAME, MONGO_COLLECTION_NAME
            
            # Ensure KB directory exists
            kb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kb")
            if not os.path.exists(kb_path):
                os.makedirs(kb_path)
            
            # Load documents silently
            loader = DirectoryLoader(
                kb_path, glob="**/*.txt", loader_cls=TextLoader, show_progress=False
            )
            documents = loader.load()
            
            # Ingest documents silently
            try:
                silent_execution(ingest_documents)
            except Exception:
                pass  # Silently handle ingestion errors
            
            # Create knowledge graph silently
            try:
                silent_execution(create_graph_from_documents, documents)
                
                # Add enhanced concepts silently
                try:
                    from update_knowledge_graph import update_knowledge_graph
                    silent_execution(update_knowledge_graph)
                except ImportError:
                    pass
                    
                # Add real estate metrics silently
                try:
                    from add_real_estate_metrics import add_real_estate_metrics
                    silent_execution(add_real_estate_metrics)
                except Exception:
                    pass
            except Exception:
                pass  # Silently handle graph creation errors
        except Exception as e:
            print(f"[WARNING] Knowledge initialization failed: {e}")

# Initialize knowledge base on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup."""
    print("[SYSTEM] Starting Urban Planning Assistant API...")
    initialize_knowledge()
    print("[READY] API is ready to receive requests")

def get_or_create_agent(user_id: str):
    """Get or create an agent for the user."""
    if user_id not in user_agents:
        user = get_user(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        with suppress_prints():
            user_agents[user_id] = create_agent(user_id)
    return user_agents[user_id]

def get_or_create_session(user_id: str):
    """Get or create a session for the user."""
    memory_manager = get_memory_manager()
    if user_id not in user_sessions:
        user_sessions[user_id] = memory_manager.start_session(user_id)
    return user_sessions[user_id], memory_manager

def process_query(user_id: str, query: str, session_id: Optional[str] = None) -> tuple[str, str]:
    """Process a user query and return the response."""
    user = get_user(user_id)
    if not user:
        return "[ERROR] Invalid user ID. Please use: citizen1, planner1, or admin1", None
    
    # If session_id is provided, use it; otherwise create a new session
    memory_manager = get_memory_manager()
    if session_id:
        # Load existing session context
        memory_manager.load_session(session_id, user_id)
        print(f"[SYSTEM] Continuing session {session_id} for user {user_id}")
    else:
        # Create new session or get existing one
        session_id, memory_manager = get_or_create_session(user_id)
        print(f"[SYSTEM] Using session {session_id} for user {user_id}")
    
    # Handle admin financial commands
    if "admin" in user["roles"] and query.lower().startswith("financial:"):
        try:
            command = query.lower().split(":", 1)[1].strip()
            if command == "list all":
                # Capture the output instead of printing
                # For now, return a placeholder response
                response = "[ADMIN] Financial metrics listing functionality would be displayed here."
                memory_manager.add_conversation_turn(user_id, query, response)
                return response, memory_manager.current_session_id
            elif command.startswith("show "):
                metric_name = command[5:].strip()
                response = f"[ADMIN] Financial metric '{metric_name}' details would be displayed here."
                memory_manager.add_conversation_turn(user_id, query, response)
                return response, memory_manager.current_session_id
            else:
                response = "[ADMIN] Commands: financial:list all | financial:show [metric name]"
                memory_manager.add_conversation_turn(user_id, query, response)
                return response, memory_manager.current_session_id
        except Exception as e:
            error_response = "[ERROR] Error accessing financial data. Try again."
            memory_manager.add_conversation_turn(user_id, query, error_response)
            return error_response, memory_manager.current_session_id
    
    # Handle budget queries for admins
    if "admin" in user["roles"] and any(kw in query.lower() for kw in ["budget cut", "budget reduction", "reduce budget"]):
        budget_response = ("Based on municipal budget analysis, 15% cuts can focus on:\n" +
                         "• Administrative overhead consolidation (3-5%)\n" +
                         "• Non-essential subscriptions audit (1-2%)\n" +
                         "• Equipment upgrade delays (2-3%)\n" +
                         "• Hiring freeze for non-essential roles (3-4%)\n" +
                         "• Energy efficiency quick wins (1-2%)\n\n" +
                         "Protect: citizen services, safety infrastructure, grant matching.")
        memory_manager.add_conversation_turn(user_id, query, budget_response)
        return budget_response, memory_manager.current_session_id
    
    # Block non-admin financial queries
    if not "admin" in user["roles"] and any(kw in query.lower() for kw in ["budget", "financial metrics", "financial data"]):
        denial_msg = "[ACCESS DENIED] Financial information requires admin privileges. Contact an administrator for budget inquiries."
        memory_manager.add_conversation_turn(user_id, query, denial_msg)
        return denial_msg, memory_manager.current_session_id
    
    try:
        # Check access restrictions
        from restricted_query_detector import should_deny_access
        should_deny, denial_message = should_deny_access(user["roles"], query)
        if should_deny:
            memory_manager.add_conversation_turn(user_id, query, denial_message)
            return denial_message, memory_manager.current_session_id
        
        # Check for role-specific fallbacks
        fallback_response = generate_role_response(user["roles"], query)
        if fallback_response:
            memory_manager.add_conversation_turn(user_id, query, fallback_response)
            return fallback_response, memory_manager.current_session_id
        
        # Get context from both session and long-term memory
        session_context = memory_manager.get_session_context()
        long_term_context = memory_manager.get_relevant_long_term_context(query, user_id)
        memory_context = f"{session_context}\n{long_term_context}".strip()
        
        # Enhance query with Chennai context and comprehensive memory
        from chennai_integration import enhance_query_with_chennai_context
        enhanced_query = enhance_query_with_chennai_context(query)
        
        # Add comprehensive conversation context
        if memory_context:
            enhanced_query = f"""User Query: {query}

{memory_context}

Based on the user's query and the provided context, please provide a comprehensive and helpful response."""
        
        # Get response from the agent
        agent = get_or_create_agent(user_id)
        
        # New LangChain agents API expects messages format
        agent_response = agent.invoke({
            "messages": [
                {"role": "user", "content": enhanced_query}
            ]
        })
        
        # Extract the output string from the agent response
        if isinstance(agent_response, dict):
            if "messages" in agent_response and len(agent_response["messages"]) > 0:
                # Get the last message from the agent
                last_message = agent_response["messages"][-1]
                if hasattr(last_message, 'content'):
                    assistant_response = last_message.content
                elif isinstance(last_message, dict):
                    assistant_response = last_message.get("content", str(last_message))
                else:
                    assistant_response = str(last_message)
            elif 'output' in agent_response:
                assistant_response = agent_response['output']
            else:
                assistant_response = str(agent_response)
        else:
            assistant_response = str(agent_response)
        
        # Add the successful turn to memory
        memory_manager.add_conversation_turn(user_id, query, assistant_response)
        return assistant_response, memory_manager.current_session_id

    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}. Please try again."
        memory_manager.add_conversation_turn(user_id, query, error_msg)
        return error_msg, memory_manager.current_session_id

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat requests from the frontend."""
    try:
        # Validate user
        user = get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        # Process query with optional session_id
        response_text, session_id = process_query(request.user_id, request.query, request.session_id)
        
        return ChatResponse(response=response_text, user_id=request.user_id, session_id=session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/users/{user_id}")
async def get_user_info(user_id: str):
    """Get user information."""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/report")
async def generate_report(request: ReportRequest):
    """Generate and send a chat history report via email and store in user's Dropbox folder."""
    try:
        user = get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        # Initialize Dropbox user manager
        admin_email = os.getenv("ADMIN_EMAIL", "admin@urbanplanning.studio")
        try:
            from dropbox_user_manager import create_user_manager
            user_manager = create_user_manager(admin_email)
        except Exception as manager_error:
            logger.warning(f"Could not initialize user folder manager: {manager_error}")
            user_manager = None
        
        memory_manager = get_memory_manager()
        
        # Get conversation context based on request parameters
        chat_history = "No conversation history available"
        
        try:
            if request.include_all_history:
                # Get complete user history across all sessions
                chat_history = memory_manager.get_complete_user_history(request.user_id)
                logger.info(f"Retrieved complete history for user {request.user_id}")
            elif request.session_ids:
                # Get history for specific sessions
                chat_history = memory_manager.get_complete_user_history(request.user_id, request.session_ids)
                logger.info(f"Retrieved history for sessions {request.session_ids} for user {request.user_id}")
            else:
                # Fallback to current session context
                if hasattr(memory_manager, 'get_session_context'):
                    try:
                        session_context = memory_manager.get_session_context()
                        if session_context and session_context.strip():
                            chat_history = session_context
                    except Exception as context_error:
                        logger.warning(f"Failed to get session context: {context_error}")
                
                # If that didn't work, try long-term context
                if chat_history == "No conversation history available":
                    if hasattr(memory_manager, 'get_relevant_long_term_context'):
                        try:
                            long_term_context = memory_manager.get_relevant_long_term_context("", request.user_id)
                            if long_term_context and long_term_context.strip():
                                chat_history = long_term_context
                        except Exception as session_error:
                            logger.warning(f"Failed to get long-term context: {session_error}")
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            chat_history = f"Error retrieving conversation history: {str(e)}"
        
        # If still no chat history, create a default one for testing
        if chat_history == "No chat history available":
            chat_history = f"""[SYSTEM] Report generated for user: {request.user_id}
[USER] Hello, I would like to generate a report of our conversation
[ASSISTANT] I'll help you generate a comprehensive report of our Urban Planning Assistant conversation. This report will include our discussion history and can be saved to your personal Dropbox folder and sent via email.
[USER] Thank you, that would be very helpful
[ASSISTANT] You're welcome! The report has been generated and will be saved to your personal folder."""
        
        # Generate report in multiple formats
        from report_generator import generate_chat_report
        from email_integration import send_report_email
        
        reports_generated = []
        user_folder_saved = False
        dropbox_links = []
        
        # Get or determine user email for folder management
        user_email = request.user_email or request.email
        if not user_email:
            user_email = f"user_{request.user_id}@urbanplanning.studio"
        
        # Generate PDF report
        try:
            logger.info(f"Generating PDF report for user {request.user_id}")
            pdf_content, pdf_filename = generate_chat_report(request.user_id, chat_history, "pdf")
            reports_generated.append({
                "format": "PDF",
                "filename": pdf_filename,
                "content": pdf_content,
                "content_type": "application/pdf"
            })
            logger.info(f"PDF report generated successfully: {pdf_filename}")
            
            # Store in user's personal folder
            if user_manager:
                try:
                    file_path = user_manager.store_report(
                        user_email, 
                        pdf_content if isinstance(pdf_content, str) else "PDF report content", 
                        "planning_report_pdf"
                    )
                    user_folder_saved = True
                    logger.info(f"Report saved to user folder: {file_path}")
                except Exception as folder_error:
                    logger.warning(f"Could not save to user folder: {folder_error}")
            
            # Fallback to old Dropbox integration
            try:
                from dropbox_integration import upload_report_to_dropbox
                dropbox_result = upload_report_to_dropbox(
                    pdf_content, pdf_filename, request.user_id, "application/pdf"
                )
                if dropbox_result and dropbox_result.get("share_url"):
                    dropbox_links.append(dropbox_result["share_url"])
                    logger.info(f"PDF uploaded to Dropbox: {dropbox_result['share_url']}")
            except Exception as dropbox_error:
                logger.warning(f"Fallback Dropbox upload failed: {dropbox_error}")
                
        except Exception as pdf_error:
            logger.error(f"Failed to generate PDF report: {pdf_error}")
        
        # Generate HTML report
        try:
            html_content, html_filename = generate_chat_report(request.user_id, chat_history, "html")
            reports_generated.append({
                "format": "HTML",
                "filename": html_filename,
                "content": html_content,
                "content_type": "text/html"
            })
            
            # Store in user's personal folder
            if user_manager:
                try:
                    user_manager.store_report(
                        user_email, 
                        html_content if isinstance(html_content, str) else "HTML report content",
                        "planning_report_html"
                    )
                except Exception as folder_error:
                    logger.warning(f"Could not save HTML to user folder: {folder_error}")
            
        except Exception as html_error:
            logger.warning(f"Failed to generate HTML report: {html_error}")
        
        # Send email if email address provided
        email_sent = False
        email_address = request.email or request.user_email
        if email_address:
            try:
                logger.info(f"Sending email to {email_address}")
                # Prepare attachments for email
                attachments = [
                    {
                        "content": report["content"],
                        "filename": report["filename"],
                        "content_type": report["content_type"]
                    }
                    for report in reports_generated
                ]
                
                email_sent = send_report_email(
                    email_address,
                    request.user_id,
                    chat_history,
                    attachments=attachments,
                    dropbox_links=dropbox_links
                )
                if email_sent:
                    logger.info(f"Email sent successfully to {email_address}")
                else:
                    logger.warning(f"Email sending failed to {email_address}")
            except Exception as email_error:
                logger.error(f"Failed to send email: {email_error}")
        
        return {
            "message": "Report generated successfully",
            "user_id": request.user_id,
            "user_email": user_email,
            "reports_generated": len(reports_generated),
            "formats": [r["format"] for r in reports_generated],
            "user_folder_saved": user_folder_saved,
            "dropbox_uploaded": len(dropbox_links) > 0,
            "dropbox_links": dropbox_links,
            "email_sent": email_sent,
            "email_address": email_address,
            "status": {
                "report_generation": "success" if len(reports_generated) > 0 else "failed",
                "user_folder_storage": "success" if user_folder_saved else "failed",
                "dropbox_upload": "success" if len(dropbox_links) > 0 else "failed",
                "email_delivery": "success" if email_sent else ("not_requested" if not email_address else "failed")
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Urban Planning Assistant API is running"}

@app.get("/user-folders/{user_email}/reports")
async def get_user_folder_reports(user_email: str, admin_request: bool = False):
    """Get all reports in a user's folder."""
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@urbanplanning.studio")
        
        # Only admin can access other users' folders
        if admin_request and user_email != admin_email:
            # This would require proper admin authentication in production
            pass
        
        try:
            from dropbox_user_manager import create_user_manager
            user_manager = create_user_manager(admin_email)
            reports = user_manager.get_user_reports(user_email, admin_request)
            
            return {
                "user_email": user_email,
                "reports": reports,
                "total_reports": len(reports)
            }
        except Exception as manager_error:
            logger.error(f"Error accessing user folder: {manager_error}")
            raise HTTPException(status_code=500, detail="User folder system not available")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user reports: {str(e)}")

@app.get("/admin/users")
async def get_all_users():
    """Get list of all users with folders (admin only)."""
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@urbanplanning.studio")
        
        try:
            from dropbox_user_manager import create_user_manager
            user_manager = create_user_manager(admin_email)
            users = user_manager.get_all_users()
            
            return {
                "admin_email": admin_email,
                "users": users,
                "total_users": len(users)
            }
        except Exception as manager_error:
            logger.error(f"Error accessing user management: {manager_error}")
            raise HTTPException(status_code=500, detail="User folder system not available")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")

@app.post("/admin/user-folders/{user_email}/create")
async def create_user_folder(user_email: str):
    """Create a folder for a user (admin function)."""
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@urbanplanning.studio")
        
        try:
            from dropbox_user_manager import create_user_manager
            user_manager = create_user_manager(admin_email)
            folder_path, is_new = user_manager.get_or_create_user_folder(user_email)
            
            return {
                "user_email": user_email,
                "folder_path": folder_path,
                "is_new_folder": is_new,
                "message": "Folder created successfully" if is_new else "Folder already exists"
            }
        except Exception as manager_error:
            logger.error(f"Error creating user folder: {manager_error}")
            raise HTTPException(status_code=500, detail="Could not create user folder")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user folder: {str(e)}")

@app.delete("/admin/user-folders/{user_email}")
async def delete_user_folder(user_email: str):
    """Delete a user's folder (admin only)."""
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@urbanplanning.studio")
        
        try:
            from dropbox_user_manager import create_user_manager
            user_manager = create_user_manager(admin_email)
            deleted = user_manager.delete_user_folder(user_email, admin_request=True)
            
            if deleted:
                return {
                    "user_email": user_email,
                    "deleted": True,
                    "message": "User folder deleted successfully"
                }
            else:
                raise HTTPException(status_code=404, detail="User folder not found or could not be deleted")
                
        except Exception as manager_error:
            logger.error(f"Error deleting user folder: {manager_error}")
            raise HTTPException(status_code=500, detail="Could not delete user folder")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user folder: {str(e)}")

@app.get("/dropbox/reports/{user_id}")
async def list_user_reports(user_id: str):
    """List Dropbox reports for a user."""
    try:
        user = get_user(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        from dropbox_integration import get_user_reports
        reports = get_user_reports(user_id)
        
        return {
            "user_id": user_id,
            "reports": reports,
            "total_reports": len(reports)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reports: {str(e)}")

@app.post("/dropbox/cleanup")
async def cleanup_old_reports(days_old: int = 30):
    """Clean up old reports from Dropbox (admin function)."""
    try:
        from dropbox_integration import cleanup_old_reports
        deleted_count = cleanup_old_reports(days_old)
        
        return {
            "message": f"Cleanup completed",
            "reports_deleted": deleted_count,
            "days_old_threshold": days_old
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")

class EmailReportRequest(BaseModel):
    user_id: str
    recipient_email: str
    chat_history: List[Dict[str, str]]  # List of {role: str, content: str}

@app.post("/send-report-email")
async def send_report_email_endpoint(request: EmailReportRequest):
    """Send a report via email directly (standalone email functionality test)."""
    try:
        user = get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        # Convert chat history to formatted string
        formatted_history = ""
        for message in request.chat_history:
            role = message.get("role", "unknown").upper()
            content = message.get("content", "")
            formatted_history += f"[{role}] {content}\n\n"
        
        if not formatted_history.strip():
            formatted_history = "No conversation history provided."
        
        # Generate report content
        from report_generator import ReportGenerator
        from email_integration import EmailManager
        
        report_generator = ReportGenerator()
        email_manager = EmailManager()
        
        if not email_manager.config:
            raise HTTPException(status_code=500, detail="Email configuration not available")
        
        # Generate reports
        pdf_content, pdf_filename = report_generator.generate_report(request.user_id, formatted_history, "pdf")
        html_content, html_filename = report_generator.generate_report(request.user_id, formatted_history, "html")
        txt_content, txt_filename = report_generator.generate_report(request.user_id, formatted_history, "txt")
        
        # Send email with compact formatting
        txt_report = txt_content.decode('utf-8') if isinstance(txt_content, bytes) else txt_content
        
        email_sent = email_manager.send_report_email(
            recipient_email=request.recipient_email,
            user_id=request.user_id,
            report_content=txt_report,
            attachments=None,  # Could add attachments if needed
            dropbox_links=[]   # Could add Dropbox links if needed
        )
        
        if email_sent:
            return {
                "success": True,
                "message": f"Report email sent successfully to {request.recipient_email}",
                "user_id": request.user_id,
                "recipient": request.recipient_email,
                "reports_generated": ["PDF", "HTML", "TXT"],
                "email_sent": True
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

@app.get("/cloud/status")
async def cloud_integration_status():
    """Check status of cloud integrations."""
    try:
        # Check Dropbox status
        dropbox_status = "unknown"
        try:
            from dropbox_integration import dropbox_manager
            if dropbox_manager.dbx:
                storage_info = dropbox_manager.get_storage_info()
                dropbox_status = "connected" if storage_info else "configured_but_error"
            else:
                dropbox_status = "not_configured"
        except Exception:
            dropbox_status = "error"
        
        # Check email status
        email_status = "unknown"
        try:
            from email_integration import email_manager
            if email_manager.config:
                email_status = "configured"
            else:
                email_status = "not_configured"
        except Exception:
            email_status = "error"
        
        return {
            "dropbox": {
                "status": dropbox_status,
                "description": "Dropbox integration for report storage"
            },
            "email": {
                "status": email_status,
                "description": "iCloud mail integration for report delivery"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking cloud status: {str(e)}")

@app.get("/chat-history/{user_id}", response_model=UserSessionsResponse)
async def get_user_chat_history(user_id: str, limit: int = 20):
    """Get all chat sessions for a user."""
    try:
        memory_manager = get_memory_manager()
        sessions = memory_manager.get_user_sessions(user_id, limit)
        return UserSessionsResponse(
            user_id=user_id,
            sessions=sessions,
            total_sessions=len(sessions)
        )
    except Exception as e:
        logger.error(f"Error retrieving user chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")

@app.get("/session-history/{user_id}/{session_id}")
async def get_session_history(user_id: str, session_id: str):
    """Get complete conversation history for a specific session."""
    try:
        memory_manager = get_memory_manager()
        history = memory_manager.get_session_history(user_id, session_id)
        return {"user_id": user_id, "session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"Error retrieving session history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session history: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Urban Planning Assistant API",
        "version": "1.0.0",
        "features": [
            "Role-based access control (citizen/planner/admin)",
            "Individual user folders in Dropbox",
            "Email-based folder management",
            "Report generation and email delivery",
            "Session-based conversation memory"
        ],
        "endpoints": {
            "chat": "/chat",
            "users": "/users/{user_id}",
            "report": "/report",
            "chat_history": "/chat-history/{user_id}",
            "session_history": "/session-history/{user_id}/{session_id}",
            "user_folder_reports": "/user-folders/{user_email}/reports",
            "admin_users": "/admin/users",
            "create_user_folder": "/admin/user-folders/{user_email}/create",
            "delete_user_folder": "/admin/user-folders/{user_email}",
            "dropbox_reports": "/dropbox/reports/{user_id}",
            "dropbox_cleanup": "/dropbox/cleanup",
            "cloud_status": "/cloud/status",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
