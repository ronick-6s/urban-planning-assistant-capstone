"""
Planner Topic Detection Module
Determines if a query is about topics that require planner privileges
"""

import re
from typing import List

# Keywords that indicate planner-specific topics
PLANNER_KEYWORDS = [
    # Technical planning terms
    "zoning", "ordinance", "subdivision", "variance", "setback", "floor area ratio",
    "density bonus", "conditional use", "special permit", "site plan", "plat",
    "easement", "right of way", "eminent domain", "land use designation",
    
    # Professional planning processes
    "master plan", "comprehensive plan", "general plan", "strategic plan",
    "environmental impact", "traffic impact", "fiscal impact", "planning commission",
    "zoning board", "design review", "public hearing", "entitlement",
    
    # Technical regulations
    "building code", "fire code", "accessibility standards", "parking requirements",
    "landscaping requirements", "signage regulations", "historic preservation",
    "overlay district", "planned unit development", "mixed use zoning",
    
    # Infrastructure planning
    "utility planning", "infrastructure capacity", "capital improvement",
    "transportation planning", "transit oriented development", "complete streets",
    "stormwater management", "sewer capacity", "water system planning",
    
    # Economic development tools
    "tax increment financing", "redevelopment agency", "enterprise zone",
    "opportunity zone", "development agreement", "public private partnership",
    "economic impact analysis", "feasibility study", "market analysis",
    
    # Advanced planning concepts
    "growth boundary", "carrying capacity", "build out analysis",
    "demographic projection", "land supply analysis", "housing element",
    "circulation element", "open space element", "safety element"
]

# Phrases that indicate planner-specific topics
PLANNER_PHRASES = [
    "planning commission approval",
    "zoning code amendment",
    "environmental review process",
    "development impact fees",
    "affordable housing requirements",
    "parking demand analysis",
    "traffic level of service",
    "general plan amendment",
    "specific plan development",
    "design guidelines compliance",
    "subdivision map approval",
    "conditional use permit",
    "variance application process",
    "historic designation process",
    "environmental impact report",
    "negative declaration",
    "categorical exemption",
    "development agreement negotiation",
    "inclusionary housing policy",
    "growth management strategy"
]

def is_planner_topic(query: str) -> bool:
    """
    Determine if a query is about topics that require planner privileges.
    
    Args:
        query (str): The user's query
        
    Returns:
        bool: True if the query is about planner-specific topics, False otherwise
    """
    if not query:
        return False
    
    # Convert to lowercase for case-insensitive matching
    query_lower = query.lower()
    
    # Check for exact phrase matches first (higher confidence)
    for phrase in PLANNER_PHRASES:
        if phrase.lower() in query_lower:
            return True
    
    # Check for keyword matches
    keyword_count = 0
    for keyword in PLANNER_KEYWORDS:
        if keyword.lower() in query_lower:
            keyword_count += 1
    
    # If multiple planning keywords are found, it's likely a planner topic
    if keyword_count >= 2:
        return True
    
    # Check for single critical keywords that almost always indicate planner topics
    critical_keywords = [
        "zoning", "ordinance", "variance", "conditional use", "planning commission",
        "environmental impact", "subdivision", "entitlement", "general plan"
    ]
    
    for keyword in critical_keywords:
        if keyword.lower() in query_lower:
            return True
    
    # Check for regulatory language patterns
    regulatory_patterns = [
        r"code\s+section",
        r"municipal\s+code",
        r"planning\s+regulation",
        r"development\s+standard",
        r"regulatory\s+requirement",
        r"permit\s+process",
        r"approval\s+process",
        r"compliance\s+with"
    ]
    
    for pattern in regulatory_patterns:
        if re.search(pattern, query_lower):
            return True
    
    return False

def get_planner_topic_explanation() -> str:
    """
    Get an explanation of what topics require planner privileges.
    
    Returns:
        str: Explanation text for citizens about restricted topics
    """
    return """
    This topic involves technical planning processes, regulations, or professional 
    procedures that require specialized knowledge and training. These topics are 
    typically handled by certified urban planners, land use attorneys, or other 
    planning professionals.
    
    For assistance with planning applications, zoning questions, or development 
    processes, please contact your local planning department or consult with a 
    qualified planning professional.
    """

def suggest_alternative_resources(query: str) -> List[str]:
    """
    Suggest alternative resources for citizens on planner topics.
    
    Args:
        query (str): The original query
        
    Returns:
        List[str]: List of suggested alternative resources
    """
    suggestions = [
        "Contact your local planning department for official guidance",
        "Consult the city's official website for planning resources",
        "Attend public planning commission meetings to learn about the process",
        "Consider hiring a planning consultant for complex projects",
        "Review publicly available planning documents and studies"
    ]
    
    # Add specific suggestions based on query content
    query_lower = query.lower()
    
    if "zoning" in query_lower:
        suggestions.insert(0, "Check your property's zoning on the city's online zoning map")
    
    if "permit" in query_lower:
        suggestions.insert(0, "Visit the planning department's permit counter for application guidance")
    
    if "variance" in query_lower or "conditional use" in query_lower:
        suggestions.insert(0, "Consider consulting with a land use attorney for complex applications")
    
    return suggestions[:5]  # Limit to 5 suggestions
