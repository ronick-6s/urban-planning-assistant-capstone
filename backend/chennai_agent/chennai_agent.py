"""
Chennai Smart Agent
Integrates Chennai-specific tools with the main urban planning assistant
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from chennai_tools import CHENNAI_TOOLS
from config import GOOGLE_API_KEY, MODEL_NAME


def create_chennai_agent():
    """
    Create a Chennai-specific smart agent with live data tools.
    
    Returns:
        AgentExecutor: Configured agent for Chennai queries
    """
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3,
        convert_system_message_to_human=True
    )
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Chennai Smart City Assistant with access to live demographic, 
spatial, and urban data for Chennai, India.

You have access to real-time and near-real-time data including:
- Weather and air quality
- Demographics and population statistics
- Real estate and property trends
- Transportation (Metro, Bus, Traffic)
- Water supply and infrastructure
- Economic indicators
- Environmental data
- Zone-specific information
- Spatial relationships and connectivity

GUIDELINES:
1. Always use the appropriate tool to fetch current data
2. Provide specific, data-driven answers with numbers and statistics
3. Cite your data sources (timestamp and source)
4. When users ask about specific areas, use zone_information or spatial_analysis tools
5. Compare different zones or corridors when relevant
6. Explain trends and changes over time
7. Provide context for numbers (e.g., "This is above/below average...")
8. For complex queries, combine multiple tools

CHENNAI CONTEXT:
- Chennai is the capital of Tamil Nadu with ~5.5 million population
- 15 administrative zones covering 426.51 sq km
- Major development corridors: OMR (IT), ECR (Residential/Tourism), GST (Mixed)
- Key districts: North, South, Central, West Chennai; OMR & IT Corridors
- Transportation: Metro (2 lines), extensive bus network, suburban rail

Be helpful, accurate, and provide actionable insights based on live data."""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create agent
    agent = create_tool_calling_agent(llm, CHENNAI_TOOLS, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=CHENNAI_TOOLS,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    return agent_executor


def main():
    """
    Main function to run the Chennai Smart Agent
    """
    print("=" * 80)
    print("CHENNAI SMART CITY AGENT")
    print("=" * 80)
    print("\nWelcome to the Chennai Smart City Assistant!")
    print("I have access to live demographic, spatial, and urban data for Chennai.\n")
    
    print("Available Data Categories:")
    print("  🌤️  Weather & Air Quality")
    print("  👥 Demographics & Population")
    print("  🏠 Real Estate & Property Trends")
    print("  🚇 Transportation (Metro, Bus, Traffic)")
    print("  💧 Water Supply & Infrastructure")
    print("  💼 Economic Indicators")
    print("  🌳 Environmental Data")
    print("  📍 Zone-specific Information")
    print("  🗺️  Spatial Analysis & Connectivity")
    print()
    
    print("Example Questions:")
    print("  • What's the current weather in Chennai?")
    print("  • What is the air quality like today?")
    print("  • Tell me about the demographics of Anna Nagar zone")
    print("  • What are property prices in the OMR corridor?")
    print("  • How is the Chennai Metro performing?")
    print("  • What's the water supply status?")
    print("  • Give me an economic overview of Chennai")
    print("  • Analyze the spatial connectivity of Adyar")
    print("  • Compare OMR and ECR corridors")
    print("  • Which zones have metro access?")
    print()
    
    # Create agent
    print("Initializing Chennai Smart Agent...")
    agent = create_chennai_agent()
    print("Agent ready!\n")
    
    # Interactive loop
    while True:
        query = input("\nAsk me about Chennai (or 'exit' to quit): ")
        
        if query.lower() in ['exit', 'quit', 'q']:
            print("\nThank you for using Chennai Smart City Agent!")
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
            print("Please try rephrasing your question.\n")


if __name__ == "__main__":
    main()
