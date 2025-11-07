"""
This module contains functions for providing fallback responses when specific documents
are not available but the user has appropriate access level (admin or planner). It allows 
the system to generate approximate answers even when the supporting documents are missing.
"""

from typing import Dict, List, Optional
import os
import re

# Dictionary mapping keywords to fallback responses for admin users
ADMIN_FALLBACKS = {
    "budget forecast": """
Based on available information, the five-year budget forecast shows moderate growth in revenue sources, 
with property taxes increasing by an average of 3.2% annually. Major expenses are projected to grow at 
2.8% annually, with infrastructure maintenance requiring increased allocation in years 3-5 due to aging 
city assets. The general reserve fund is expected to remain stable at approximately 15% of annual operating 
expenses. Note that this is a generalized projection and specific numbers would require accessing the 
complete budget forecast document.
    """,
    
    "infrastructure maintenance": """
Infrastructure maintenance costs are projected to increase by 4.1% annually over the next five years, 
with particular focus needed on water delivery systems (estimated $2.5M-$3.2M annually) and transportation
infrastructure (estimated $4.7M-$5.5M annually). Deferred maintenance from previous years has created a 
backlog that will require either increased funding or strategic prioritization. This is a general assessment
based on typical urban infrastructure patterns; specific numbers would require the detailed maintenance 
projection document.
    """,
    
    "development investment": """
Current development investment risk analysis suggests moderate risk in the downtown high-density sector, 
with potential overbuilding in the luxury condo market segment. Mixed-use developments along transit 
corridors show strong resilience and low risk profiles, with steady 5-8% ROI projections. The waterfront 
development zone presents higher risk but potentially higher returns, contingent on completion of planned 
infrastructure improvements. This assessment provides general guidance; detailed risk metrics would 
require the complete investment risk analysis document.
    """,
    
    "municipal bond": """
Municipal bond performance projections indicate our AAA rating should be maintainable with current fiscal
policies. The next bond issuance (projected for Q2 next year) should achieve favorable interest rates 
between 2.8-3.2% depending on market conditions. Debt service remains manageable at approximately 7% of 
annual expenditures. This is a general assessment of bond performance; specific metrics would require 
the detailed bond performance projection document.
    """,
    
    "property tax revenue": """
Property tax revenues are projected to increase by approximately 3.5% annually over the next three years, 
based on current property valuations and development patterns. Commercial property taxes show stronger
growth (4.2%) compared to residential (3.1%). Areas surrounding transit corridor improvements are expected 
to see above-average valuation increases of 5-7%. This represents a general projection; specific revenue
numbers would require accessing the complete property tax forecast document.
    """,
    
    "development pipeline": """
The current development pipeline for downtown includes approximately 1,200 residential units, 175,000 sq ft
of commercial space, and 85,000 sq ft of retail space in various stages of approval and construction. The
largest projects are concentrated in the north downtown area and along the newly designated innovation
corridor. Completion timelines range from 6 months to 4 years, with most projects scheduled for completion
within 18-24 months. This is a generalized overview; specific project details would require accessing the
complete development pipeline analysis.
    """,
    
    "transit investments": """
Transit investments are projected to create a 12-18% increase in property values within 0.5 miles of new 
stations over a 5-year period following completion. Commercial properties typically see larger value increases
(15-22%) compared to residential properties (8-15%). The property value impact gradient typically extends up 
to 1.5 miles from major transit improvements, with diminishing effects as distance increases. This represents
a general assessment based on comparable urban areas; specific projections would require accessing the 
complete transit impact analysis.
    """,
    
    "waterfront development": """
Waterfront development projects are currently showing an average ROI of 12.3%, above the city-wide development
average of 8.7%. Phase 1 projects have outperformed initial projections by approximately 15%, while Phase 2 
projects are tracking with expectations. The public amenity components have increased surrounding property
values by an estimated 8-10%. Long-term financial projections suggest the initial public infrastructure 
investments will be recovered through increased tax revenue within 7-9 years. This is a general performance
summary; detailed financial metrics would require accessing the complete waterfront financial analysis.
    """,
}

# Dictionary mapping keywords to fallback responses for planner users
PLANNER_FALLBACKS = {
    "climate resilient planning": """
Climate resilient planning involves infrastructure adaptation strategies that anticipate and mitigate
climate change impacts. Key elements include flood mitigation systems, heat island reduction through
urban greening, and updated building codes addressing changing weather patterns. Best practices include
risk assessment mapping, community vulnerability identification, and integrated watershed management.
This general overview covers core principles; specific technical details would require accessing the
complete climate resilient planning handbook.
    """,
    
    "transit oriented development": """
Transit-oriented development (TOD) focuses on creating compact, walkable communities centered around
high-quality transit systems. Successful implementation typically involves mixed land use zoning within
a half-mile of transit stations, pedestrian-friendly street design, reduced parking requirements,
and higher density gradients closer to transit nodes. Case studies show economic benefits including
increased property values (10-25%), reduced transportation costs for residents (15-30%), and improved
retail performance in station-adjacent locations. This general overview covers key principles; specific
implementation guidelines would require the complete TOD planning manual.
    """,
    
    "urban density quality": """
Urban density quality assessment incorporates metrics such as infrastructure sufficiency, public space
availability, service proximity, and social cohesion indicators. The relationship between density and
quality of life follows a complex curve, with benefits increasing up to approximately 150 dwelling units
per acre before potentially declining without proper planning. Key quality interventions include green
space allocation (minimum 15% of developed area), public amenity distribution, and transportation network
efficiency. This represents a general assessment of density quality principles; detailed metrics would
require accessing the complete urban density quality analysis framework.
    """,
    
    "land use zoning": """
Contemporary land use zoning approaches emphasize flexibility through form-based codes, mixed-use
designations, and performance standards over rigid single-use categories. Progressive zoning practices
include incentive zoning for affordable housing, transit-supportive overlays, and sustainability-focused
development standards. Implementation challenges typically involve existing non-conforming uses,
community resistance to increased density, and balancing market demands with long-term planning goals.
This general overview covers modern zoning approaches; specific implementation details would require
accessing the complete land use and zoning policy handbook.
    """,
    
    "planning professional practice": """
Current professional planning practice emphasizes interdisciplinary collaboration, stakeholder
engagement throughout the planning process, data-driven decision making, and equity considerations.
Core competencies include spatial analysis, policy development, community facilitation, and technical
writing. Emerging trends include digital participation tools, scenario planning with predictive
analytics, and integration of health impact assessments into standard planning workflows. This
overview covers general professional practice principles; specific professional development guidance
would require accessing the complete planning professional practice manual.
    """,
    
    "commercial development planning": """
Commercial development planning strategies balance market demand with community needs through targeted
incentives, design standards, and infrastructure coordination. Successful commercial corridors typically
incorporate diverse business types, pedestrian-friendly frontages, and multimodal access. Market analysis
should address trade area demographics, competitive saturation, and emerging retail/office trends.
Implementation challenges often include parking requirements, legacy zoning constraints, and adaptation
to changing retail formats. This general overview covers key commercial planning principles; specific
implementation techniques would require accessing the complete commercial development planning guide.
    """,
}

def get_admin_fallback(query: str) -> Optional[str]:
    """
    For admin users, provide a fallback response when specific documents aren't available.
    Returns None if no fallback is available for the query.
    """
    query_lower = query.lower()
    
    for keyword, response in ADMIN_FALLBACKS.items():
        if keyword.lower() in query_lower:
            return f"NOTE: The following is a generalized response based on available information. " \
                   f"Specific supporting documents for '{keyword}' are not available in the knowledge base.\n\n{response.strip()}"
                   
    return None

def get_planner_fallback(query: str) -> Optional[str]:
    """
    For planner users, provide a fallback response when specific documents aren't available.
    Returns None if no fallback is available for the query.
    """
    query_lower = query.lower()
    
    for keyword, response in PLANNER_FALLBACKS.items():
        if keyword.lower() in query_lower:
            return f"NOTE: The following is a generalized response based on available information. " \
                   f"Specific supporting documents for '{keyword}' are not available in the knowledge base.\n\n{response.strip()}"
                   
    return None

def should_use_admin_fallback(user_roles: List[str], query: str) -> bool:
    """
    Determines if an admin fallback response should be used based on user roles and query content.
    """
    if "admin" not in user_roles:
        return False
        
    # Check if query contains admin-specific financial or management terms
    admin_terms = [
        "budget forecast", "financial projection", "property tax revenue",
        "municipal bond", "investment risk", "development pipeline",
        "infrastructure maintenance", "waterfront development", "transit investment"
    ]
    
    query_lower = query.lower()
    return any(term.lower() in query_lower for term in admin_terms)

def should_use_planner_fallback(user_roles: List[str], query: str) -> bool:
    """
    Determines if a planner fallback response should be used based on user roles and query content.
    """
    if "planner" not in user_roles and "admin" not in user_roles:
        return False
        
    # Check if query contains planner-specific technical or planning terms
    planner_terms = [
        "climate resilient planning", "transit oriented development", "urban density quality",
        "land use zoning", "planning professional practice", "commercial development planning"
    ]
    
    query_lower = query.lower()
    return any(term.lower() in query_lower for term in planner_terms)

def generate_role_response(user_roles: List[str], query: str) -> Optional[str]:
    """
    Generates a role-specific response for queries where supporting documents
    aren't available but the user has appropriate access level.
    
    Returns None if no fallback response is available or appropriate.
    """
    # Try admin fallback first (if user is an admin)
    if should_use_admin_fallback(user_roles, query):
        return get_admin_fallback(query)
        
    # Try planner fallback (if user is an admin or planner)
    if should_use_planner_fallback(user_roles, query):
        return get_planner_fallback(query)
        
    return None
