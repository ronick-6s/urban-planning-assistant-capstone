"""
Integration Example: Adding Chennai Smart Agent to Main Urban Planning Assistant
This shows how to integrate Chennai-specific tools with the main agent
"""

import sys
sys.path.append('..')

from agent import create_agent
from chennai_agent.chennai_tools import CHENNAI_TOOLS
from access_control import get_user


def create_integrated_agent(user_id: str):
    """
    Create an integrated agent with both main tools and Chennai-specific tools.
    
    Args:
        user_id: User ID for access control
        
    Returns:
        AgentExecutor with combined tools
    """
    # Import main agent creation function
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from config import GOOGLE_API_KEY, MODEL_NAME
    from rag_chain import retrieve_docs
    from langchain.tools import tool
    
    # Get user for access control
    user = get_user(user_id)
    user_roles = user["roles"]
    
    # Create main RAG tool
    @tool
    def search_knowledge_base(query: str) -> str:
        """
        Search the urban planning knowledge base for relevant information.
        Use this for general urban planning concepts, policies, and best practices.
        """
        results = retrieve_docs(query, user_id)
        return results
    
    # Combine main tools with Chennai tools
    all_tools = [search_knowledge_base] + CHENNAI_TOOLS
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3,
        convert_system_message_to_human=True
    )
    
    # Create enhanced prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an Urban Planning Assistant with specialized knowledge about Chennai city.

USER ROLE: {', '.join(user_roles)}

You have access to:
1. General urban planning knowledge base (global concepts, policies, best practices)
2. Live Chennai city data (demographics, spatial data, real-time metrics)

WHEN TO USE EACH:
- Use search_knowledge_base for:
  * General urban planning concepts
  * Policy frameworks and best practices
  * Theoretical questions
  * Comparisons with other cities
  * Historical context
  
- Use Chennai-specific tools for:
  * Current Chennai data (weather, air quality, traffic)
  * Chennai demographics and population
  * Chennai real estate and property prices
  * Chennai transportation (Metro, bus, traffic)
  * Chennai infrastructure and utilities
  * Chennai zone-specific information
  * Chennai spatial analysis
  * Chennai economic indicators

APPROACH:
1. For Chennai-specific questions, ALWAYS use Chennai tools for live data
2. For general planning questions, use the knowledge base
3. For mixed questions, combine both sources
4. Always cite data sources and timestamps
5. Provide specific numbers and statistics when available

Be helpful, accurate, and provide data-driven insights."""),
        ("human", "{{input}}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create agent
    agent = create_tool_calling_agent(llm, all_tools, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=6
    )
    
    return agent_executor


def main():
    """
    Example usage of the integrated agent
    """
    print("=" * 80)
    print("INTEGRATED URBAN PLANNING ASSISTANT WITH CHENNAI DATA")
    print("=" * 80)
    print()
    
    # Login
    print("Available users: citizen1, planner1, admin1")
    user_id = input("Enter user ID: ").strip() or "planner1"
    
    # Create integrated agent
    print(f"\nInitializing integrated agent for {user_id}...")
    agent = create_integrated_agent(user_id)
    print("Agent ready!\n")
    
    print("You can now ask:")
    print("  • General urban planning questions (uses knowledge base)")
    print("  • Chennai-specific questions (uses live data)")
    print("  • Mixed questions (combines both)")
    print()
    print("Examples:")
    print("  - What are the best practices for transit-oriented development?")
    print("  - What is the current population of Chennai?")
    print("  - How can Chennai implement complete streets given its current traffic conditions?")
    print("  - Compare Chennai's real estate trends with sustainable housing principles")
    print()
    
    # Interactive loop
    while True:
        query = input("\nYour question (or 'exit' to quit): ")
        
        if query.lower() in ['exit', 'quit', 'q']:
            break
        
        if not query.strip():
            continue
        
        try:
            print("\n" + "=" * 80)
            response = agent.invoke({"input": query})
            print("\n" + "=" * 80)
            print("\nRESPONSE:")
            print(response['output'])
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
