"""
This module detects when users are asking questions that require elevated privileges
and provides appropriate access denial messages instead of generalized fallbacks.
"""

from typing import List, Dict, Optional, Tuple
import re

# Admin-only query patterns
ADMIN_QUERY_PATTERNS = [
    # Financial and budgetary
    r'\b(?:budget|financial|finance|cost|revenue|tax|bond|investment|roi|profit|expense)\b.*\b(?:forecast|projection|analysis|data|metrics|numbers)\b',
    r'\b(?:show|give|provide).*\b(?:budget|financial|finance|revenue|tax)\b',
    r'\b(?:property tax|municipal bond|infrastructure cost|development investment|budget forecast)\b',
    r'\bdo the numbers justify\b',
    r'\b(?:financial performance|market projections|budget projections)\b',
    r'\b(?:debt service|financing|funding allocation|capital improvement)\b',
    
    # Strategic planning and management
    r'\b(?:strategic|management|administrative|departmental)\b.*\b(?:planning|coordination|restructur|workflow)\b',
    r'\b(?:staff|resource|budget).*\b(?:allocation|management|cut|reduction)\b',
    r'\b(?:cm|chief minister|government).*\b(?:wants|initiative|signature)\b',
    r'\b(?:interdepartmental|cross-departmental|coordination|collaboration)\b',
    
    # Sensitive data requests
    r'\b(?:confidential|internal|restricted|sensitive|classified)\b',
    r'\b(?:show me|give me|provide).*\b(?:all|complete|detailed|comprehensive)\b.*\b(?:data|metrics|analysis|report)\b',
]

# Planner-only query patterns (technical planning)
PLANNER_QUERY_PATTERNS = [
    # Technical planning concepts
    r'\b(?:zoning|land use|tod|transit.oriented|form.based codes|mixed.use)\b.*\b(?:implementation|technical|professional|practice|comprehensive|strategy|strategies)\b',
    r'\b(?:climate resilient|comprehensive|technical)\b.*\b(?:planning|development|strategy|strategies)\b',
    r'\b(?:urban density|professional practice|commercial development)\b.*\b(?:planning|technical|analysis)\b',
    r'\b(?:development control|building bylaws|planning standards|zoning ordinance)\b',
    r'\b(?:implement|implementing).*\b(?:comprehensive|zoning|planning)\b.*\b(?:strategies|strategy|approach)\b',
    
    # Professional/technical tools and methods
    r'\b(?:spatial analysis|gis|mapping|modeling|forecasting)\b.*\b(?:technical|professional|planning)\b',
    r'\b(?:planning methodology|technical standards|professional guidelines)\b',
    r'\b(?:environmental impact|traffic study|market analysis)\b.*\b(?:technical|professional)\b',
]

# Financial/sensitive terms that should never be accessible to citizens
SENSITIVE_FINANCIAL_TERMS = [
    'budget forecast', 'financial projection', 'property tax revenue', 'municipal bond performance',
    'development investment risk', 'infrastructure maintenance cost', 'roi analysis', 'roi for',
    'debt service ratio', 'capital improvement budget', 'financing gap', 'bond performance',
    'tax revenue projection', 'financial metrics', 'budget allocation', 'cost analysis',
    'return on investment', 'profit analysis', 'financial performance', 'investment return'
]

# Technical planning terms that require planner/admin access
TECHNICAL_PLANNING_TERMS = [
    'comprehensive planning', 'zoning ordinance', 'development control rules', 'planning methodology',
    'spatial analysis', 'land use planning', 'technical standards', 'professional practice',
    'urban density analysis', 'transit oriented development technical', 'climate resilient planning comprehensive'
]

def detect_admin_query(query: str) -> bool:
    """
    Detect if a query is asking for admin-level information.
    """
    query_lower = query.lower()
    
    # Check for sensitive financial terms
    for term in SENSITIVE_FINANCIAL_TERMS:
        if term.lower() in query_lower:
            return True
    
    # Check for admin query patterns
    for pattern in ADMIN_QUERY_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            return True
    
    return False

def detect_planner_query(query: str) -> bool:
    """
    Detect if a query is asking for planner-level technical information.
    """
    query_lower = query.lower()
    
    # Check for technical planning terms
    for term in TECHNICAL_PLANNING_TERMS:
        if term.lower() in query_lower:
            return True
    
    # Check for planner query patterns
    for pattern in PLANNER_QUERY_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            return True
    
    return False

def get_access_denial_message(user_roles: List[str], query: str) -> Optional[str]:
    """
    Generate an appropriate access denial message when users ask for information
    above their permission level.
    
    Returns None if the query is appropriate for the user's role.
    """
    is_admin_query = detect_admin_query(query)
    is_planner_query = detect_planner_query(query)
    
    # If user is an admin, they have access to everything
    if "admin" in user_roles:
        return None
    
    # If user is a planner, they can access planner content but not admin content
    if "planner" in user_roles:
        if is_admin_query:
            return """[DENIED] ACCESS RESTRICTED

This query requires administrative privileges. The information you're requesting involves financial data, budget details, or strategic management information that is only available to administrative users.

As a planner, you have access to technical planning documents and professional guidance, but not to financial projections, budget data, or administrative strategic information.

Please contact your administrator if you need access to this information for official planning purposes."""
        return None
    
    # If user is a citizen, they cannot access admin or planner content
    if "citizen" in user_roles:
        if is_admin_query:
            return """[DENIED] ACCESS RESTRICTED

This query requires administrative privileges. The information you're requesting involves financial data, budget details, or strategic management information that is only available to administrative users.

As a citizen, you have access to public information about urban planning concepts, community services, and general planning principles, but not to detailed financial data or administrative information.

For questions about city services, public programs, or general planning concepts, I'm happy to help with publicly available information."""
        
        if is_planner_query:
            return """[DENIED] ACCESS RESTRICTED

This query requires professional planning privileges. The information you're requesting involves technical planning documents, professional methodologies, or detailed implementation guidance that is only available to planning professionals.

As a citizen, you have access to public information about urban planning concepts, community involvement opportunities, and general planning principles.

For questions about how planning decisions affect your community or how to participate in planning processes, I'm happy to help with publicly available information."""
    
    return None

def should_deny_access(user_roles: List[str], query: str) -> Tuple[bool, Optional[str]]:
    """
    Check if access should be denied for a query based on user role.
    
    Returns:
        (should_deny, denial_message)
    """
    denial_message = get_access_denial_message(user_roles, query)
    return (denial_message is not None, denial_message)

# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_queries = [
        ("admin", "Show me Chennai's budget forecast"),
        ("citizen", "Do the numbers justify tax breaks for this OMR project?"),
        ("citizen", "What are the principles of transit-oriented development?"),
        ("planner", "Show me Chennai's financial metrics"),
        ("citizen", "How can we implement comprehensive zoning strategies?"),
        ("planner", "What are best practices for climate resilient planning?")
    ]
    
    print("Testing Access Control:")
    print("=" * 50)
    
    for role, query in test_queries:
        user_roles = [role]
        should_deny, message = should_deny_access(user_roles, query)
        
        print(f"\nRole: {role}")
        print(f"Query: {query}")
        print(f"Access Denied: {should_deny}")
        if message:
            print(f"Message: {message[:100]}...")
        print("-" * 30)
