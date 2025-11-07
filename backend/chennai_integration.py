"""
Chennai Smart Agent Integration
Integrates Chennai-specific tools into the main Urban Planning Assistant
"""

import os
import sys
import importlib.util
from typing import List

# Add Chennai agent path
chennai_path = os.path.join(os.path.dirname(__file__), 'chennai_agent')
if chennai_path not in sys.path:
    sys.path.insert(0, chennai_path)

sys.path.insert(0, '/Users/ronick/Documents/curriculum/urban_planning_assistant/chennai_agent')

def get_chennai_tools():
    """
    Import and return Chennai-specific tools.
    Returns empty list if Chennai agent is not available.
    """
    try:
        # Change to the chennai_agent directory to handle relative imports
        current_dir = os.getcwd()
        chennai_dir = os.path.join(os.path.dirname(__file__), 'chennai_agent')
        os.chdir(chennai_dir)
        
        # Import Chennai tools
        import importlib.util
        spec = importlib.util.spec_from_file_location("chennai_tools", os.path.join(chennai_dir, "chennai_tools.py"))
        chennai_tools_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(chennai_tools_module)
        
        # Change back to original directory
        os.chdir(current_dir)
        
        chennai_tools = chennai_tools_module.CHENNAI_TOOLS
        # Chennai Smart Agent loaded quietly
        return chennai_tools
        
    except ImportError as e:
        if 'current_dir' in locals():
            os.chdir(current_dir)
        print(f"! Chennai Smart Agent not available: {e}")
        print("  Continuing with standard urban planning tools only")
        return []
    except Exception as e:
        if 'current_dir' in locals():
            os.chdir(current_dir)
        print(f"! Error loading Chennai Smart Agent: {e}")
        print("  Continuing with standard urban planning tools only")  
        return []

def is_chennai_query(query: str) -> bool:
    """
    Check if a query is specifically about Chennai.
    """
    chennai_keywords = [
        'chennai', 'madras', 'tamil nadu', 'tn',
        'adyar', 'anna nagar', 't nagar', 'mylapore', 'velachery',
        'tambaram', 'chrompet', 'guindy', 'egmore', 'central',
        'marina beach', 'cooum', 'buckingham canal', 'nungambakkam',
        'kodambakkam', 'besant nagar', 'sholinganallur', 'omr',
        'it corridor', 'ecr', 'east coast road', 'gst road',
        'mount road', 'anna salai', 'cathedral road'
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in chennai_keywords)

def get_chennai_context() -> str:
    """
    Get Chennai context information for the assistant.
    """
    return """
Chennai Smart Agent Integration Active:
- Real-time weather and air quality data
- Live traffic conditions via TomTom API
- Census demographics and spatial analysis
- Property market insights and real estate data
- Public transportation and infrastructure information
- Zone-wise development analysis and comparisons

The assistant can now provide Chennai-specific insights including:
• Current environmental conditions (weather, AQI)
• Live traffic and transportation data
• Demographic and census information
• Real estate market analysis
• Infrastructure and public services mapping
• Spatial analysis and neighborhood comparisons
"""

def should_use_chennai_data(query: str, user_roles: List[str]) -> bool:
    """
    Always use Chennai data to enhance any urban planning query.
    """
    # Always use Chennai data for context enhancement
    return True

def enhance_query_with_chennai_context(query: str) -> str:
    """
    Enhance any urban planning query with Chennai context and live data.
    """
    enhanced_query = f"""
{query}

MANDATORY CHENNAI DATA INTEGRATION:
You MUST actively use Chennai Smart Agent tools to fetch live data and enhance your response:

REQUIRED API CALLS (use these tools):
1. get_chennai_weather() - Fetch live OpenWeatherMap API data for environmental context
2. get_chennai_air_quality() - Fetch live WAQI API data for air quality conditions  
3. get_chennai_traffic() - Fetch live TomTom API traffic data for transportation context
4. get_chennai_demographics() - Fetch census data from Excel file for population context
5. get_chennai_property_trends() - Fetch real estate data for economic context

MANDATORY WEB SCRAPING INTEGRATION:
- Use get_chennai_water_supply() - Web scraping Chennai Metro Water Board
- Use get_chennai_metro_status() - Web scraping Chennai Metro Rail from chennaimetrorail.org
- Use get_chennai_infrastructure() - Web scraping Chennai Corporation data
- Use get_mtc_bus_routes() - Web scraping MTC bus routes from mtcbus.tn.gov.in
- Use get_chennai_government_info() - Web scraping Chennai District Administration from chennai.nic.in
- Use get_chennai_policies_and_services() - Comprehensive policy scraping and civic services analysis
- Use get_chennai_travel_planner() - Official tourism data and travel route planning
- Use get_chennai_city_operations_enhancement() - Data-driven city improvement recommendations

RESPONSE STRUCTURE REQUIRED:
1. Provide the general urban planning answer requested
2. ALWAYS call relevant Chennai tools to get live API data
3. Include actual numbers from API responses (temperature, AQI, traffic speed, population)
4. Use web scraped data for infrastructure and services context
5. Combine live data with Chennai zone information and spatial analysis

Make sure to demonstrate live API calls and web scraping in your response with actual data points.
"""
    return enhanced_query

def get_chennai_examples_by_role(roles: List[str]) -> List[str]:
    """
    Get Chennai-specific example queries based on user roles.
    """
    examples = []
    
    if "citizen" in roles:
        examples.extend([
            "What's the current weather in Chennai?",
            "How is the air quality in Anna Nagar today?",
            "What are the transportation options from T Nagar to Velachery?",
            "What amenities are available near Marina Beach?",
            "What government services are available in Chennai?",
            "How can I visit Chennai's tourist attractions?",
            "What are the emergency helplines in Chennai?",
            "How do I access welfare schemes in Chennai?"
        ])
    
    if "planner" in roles:
        examples.extend([
            "What are the demographics of Adyar zone?",
            "Compare development potential between Guindy and Sholinganallur",
            "What's the traffic pattern on OMR during peak hours?",
            "Analyze the infrastructure development in Chennai's IT Corridor",
            "What are Chennai's urban development policies?",
            "How can Chennai's transportation system be improved?",
            "What are the environmental policies for Chennai?",
            "Provide tourism development recommendations for Chennai"
        ])
    
    if "admin" in roles:
        examples.extend([
            "What are the property values across different Chennai zones?",
            "Provide environmental impact analysis for Cooum river area",
            "What's the ROI potential for development projects in Tambaram?",
            "Analyze the spatial relationship between transport hubs and real estate prices",
            "How can Chennai city operations be enhanced?",
            "What are data-driven recommendations for Chennai administration?",
            "Analyze Chennai's comprehensive policy framework",
            "Provide efficiency improvements for city governance"
        ])
    
    return examples
