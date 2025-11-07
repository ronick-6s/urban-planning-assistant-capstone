from typing import List, Dict, Tuple, Optional

# In-memory storage for users and roles for simplicity.
# In a real application, this would be stored in a database.
USERS: Dict[str, Dict] = {
    "planner1": {"roles": ["planner"], "name": "Alice"},
    "citizen1": {"roles": ["citizen"], "name": "Bob"},
    "admin1": {"roles": ["admin"], "name": "Charlie"},
}

# Define documents with their access levels and sensitive status
DOCUMENTS: Dict[str, Dict] = {
    "urban_planning_basics.txt": {"restricted": False},
    "smart_cities.txt": {"restricted": False},
    "sustainable_development.txt": {"restricted": False},
    "mixed_use_development.txt": {"restricted": False},
    "transit_oriented_development.txt": {"restricted": False},
    "urban_density.txt": {"restricted": False},
    "affordable_housing.txt": {"restricted": False},
    "complete_streets.txt": {"restricted": False},
    "climate_resilient_planning.txt": {"restricted": False},
    "climate_resilient_planning_comprehensive.txt": {"restricted": True},
    "civic_participation.txt": {"restricted": False},
    "urban_planning_history.txt": {"restricted": False},
    "urban_planning_principles.txt": {"restricted": False},
    "urban_economics_development.txt": {"restricted": True},
    "commercial_development_planning.txt": {"restricted": True},
    "public_engagement_processes.txt": {"restricted": False},
    "urban_planning_comprehensive_faq.txt": {"restricted": False},
    "urban_planning_faqs.txt": {"restricted": False},
    "urban_design_public_spaces.txt": {"restricted": False},
    "urban_density_quality_of_life.txt": {"restricted": True},
    "transit_oriented_development_comprehensive.txt": {"restricted": True},
    "land_use_zoning.txt": {"restricted": True},
    "planning_professional_practice.txt": {"restricted": True},
    "commercial_development_citizen_guide.txt": {"restricted": False},
    "commercial_space_setup_guide.txt": {"restricted": False},
}

ROLES: Dict[str, List[str]] = {
    "planner": [
        "urban_planning_basics.txt",
        "smart_cities.txt",
        "sustainable_development.txt",
        "mixed_use_development.txt",
        "transit_oriented_development.txt",
        "urban_density.txt",
        "affordable_housing.txt",
        "complete_streets.txt",
        "climate_resilient_planning.txt",
        "climate_resilient_planning_comprehensive.txt",
        "civic_participation.txt",
        "urban_planning_history.txt",
        "urban_planning_principles.txt",
        "urban_planning_comprehensive_faq.txt",
        "urban_planning_faqs.txt",
        "planning_professional_practice.txt",
        "urban_design_public_spaces.txt",
        "urban_density_quality_of_life.txt",
        "transit_oriented_development_comprehensive.txt"
    ],
    "citizen": [
        "smart_cities.txt",
        "mixed_use_development.txt",
        "complete_streets.txt",
        "affordable_housing.txt",
        "civic_participation.txt",
        "urban_planning_faqs.txt",
        "commercial_development_citizen_guide.txt",
        "commercial_space_setup_guide.txt",
        "urban_design_public_spaces.txt",
        "public_engagement_processes.txt"
    ],  # Citizens have access to public-facing information
    "admin": [
        # Admins have access to all documents through code logic
    ],  
}

def get_user(user_id: str):
    """Retrieves a user's information."""
    return USERS.get(user_id)

def has_access_to_document(user_id: str, document_source: str) -> bool:
    """
    Checks if a user has access to a specific document based on their roles.
    Admins have access to everything.
    """
    user = get_user(user_id)
    if not user:
        return False

    if "admin" in user["roles"]:
        return True
        
    # Extract the basename if a full path is provided
    if document_source:
        import os
        document_name = os.path.basename(document_source)
    else:
        return False

    for role in user["roles"]:
        if document_name in ROLES.get(role, []):
            return True
    return False

def check_document_access(user_id: str, document_source: str) -> Tuple[bool, Optional[str]]:
    """
    Checks if a user has access to a specific document and returns access status and reason.
    Returns a tuple of (has_access, reason_if_denied)
    """
    user = get_user(user_id)
    if not user:
        return False, "User not found in the system."

    if not document_source:
        return False, "Document source not specified."
        
    # Extract the basename if a full path is provided
    import os
    document_name = os.path.basename(document_source)
    
    # Admin has access to everything
    if "admin" in user["roles"]:
        return True, None
        
    # Check if user has access through their roles
    has_access = False
    for role in user["roles"]:
        if document_name in ROLES.get(role, []):
            has_access = True
            break
            
    if not has_access:
        # Check if document exists but is restricted
        if document_name in DOCUMENTS:
            if DOCUMENTS[document_name].get("restricted", False):
                return False, f"Access denied: '{document_name}' requires administrative privileges."
            else:
                return False, f"Access denied: '{document_name}' is not available for your role."
        else:
            return False, f"Access denied: Document '{document_name}' not found or requires higher permissions."
            
    return True, None

def is_restricted_document(document_source: str) -> bool:
    """Check if a document is marked as restricted regardless of user access."""
    if not document_source:
        return False
        
    import os
    document_name = os.path.basename(document_source)
    return DOCUMENTS.get(document_name, {}).get("restricted", False)

def get_accessible_documents(user_id: str) -> List[str]:
    """Get a list of all document names accessible to this user."""
    user = get_user(user_id)
    if not user:
        return []
        
    if "admin" in user["roles"]:
        return list(DOCUMENTS.keys())
        
    accessible_docs = set()
    for role in user["roles"]:
        accessible_docs.update(ROLES.get(role, []))
        
    return list(accessible_docs)
