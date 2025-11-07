# Urban Planning Assistant - Prompts Guide

This guide provides comprehensive example prompts and queries for different user roles in the Urban Planning Assistant system. Each role has access to different levels of information and tools.

## [ACCESS] User Roles Overview

- **[USER] Citizens (citizen1)**: Public information, transportation, basic planning concepts
- **[DEVELOPMENT] Planners (planner1)**: Technical documents, zoning, professional planning tools
- **[ADMIN] Administrators (admin1)**: Financial data, strategic planning, complete system access

---

## [USER] Citizen Prompts (citizen1)

### Transportation & Mobility
```
"What are the best MTC bus routes from T. Nagar to Marina Beach?"
"How is the Chennai Metro connectivity to the airport?"
"What are the current traffic conditions on Mount Road?"
"Are there any bicycle sharing programs in Chennai?"
"What time does the last Metro train run from Central to Airport?"
```

### Environmental Information
```
"What's the current air quality in Chennai today?"
"How hot is it in Chennai right now?"
"What are the pollution levels in Anna Nagar area?"
"Is today a good day for outdoor activities based on weather?"
"What's the humidity level and weather forecast for tomorrow?"
```

### Government Services & Civic Information
```
"How do I apply for a building permit in Chennai?"
"What are the public libraries available in Chennai?"
"Where can I pay my property tax in Chennai?"
"What are the emergency helpline numbers for Chennai?"
"How do I register for voter ID in Chennai?"
```

### Community Development & Housing
```
"What is affordable housing and how does it work?"
"What are the benefits of mixed-use development?"
"How does public transportation benefit communities?"
"What makes a neighborhood walkable and safe?"
"What are green building practices for homes?"
```

### Urban Planning Basics
```
"What is urban planning and why is it important?"
"How do cities decide where to build parks?"
"What is zoning and how does it affect my neighborhood?"
"Why are some areas designated as residential vs commercial?"
"How do cities plan for population growth?"
```

### Restricted Query Examples (What Citizens Cannot Access)
```
"Show me the city budget details" 
→ Response: [ACCESS DENIED] Financial information requires admin privileges. Contact an administrator for budget inquiries.

"What are the internal audit findings?"
→ Response: [ACCESS DENIED] Internal administrative documents require elevated privileges.

"How much profit do contractors make on city projects?"
→ Response: [ACCESS DENIED] Detailed financial metrics require administrative access.

"What are the political considerations behind zoning decisions?"
→ Response: [ACCESS DENIED] This is a technical planning topic that requires planner privileges. Please contact a planning professional for assistance.

"Show me the city's debt and financial obligations"
→ Response: [ACCESS DENIED] Financial information requires admin privileges. For general budget information, contact your city council representative.
```

---

## [DEVELOPMENT] Urban Planner Prompts (planner1)

### Land Use & Zoning
```
"What are the current zoning regulations for IT corridors in Chennai?"
"How do I calculate Floor Area Ratio (FAR) for a mixed-use development?"
"What are the setback requirements for high-rise buildings in Chennai?"
"What is the process for rezoning land from residential to commercial?"
"How do Transfer of Development Rights (TDR) work in Chennai?"
```

### Housing Policy & Development
```
"What are the current slum rehabilitation policies in Chennai?"
"How does the Pradhan Mantri Awas Yojana apply to Chennai projects?"
"What are the density norms for affordable housing projects?"
"How do public-private partnerships work in housing development?"
"What are the parking requirements for residential developments?"
```

### Transportation Planning
```
"What is the methodology for conducting traffic impact assessments?"
"How do we plan bus rapid transit (BRT) corridors?"
"What are the design standards for pedestrian infrastructure?"
"How do we integrate different modes of transport in TOD projects?"
"What are the parking policy recommendations for Chennai CBD?"
```

### Infrastructure & Utilities
```
"How do we plan water supply networks for new developments?"
"What are the stormwater management requirements for urban projects?"
"How do we calculate sewage treatment capacity for residential areas?"
"What are the guidelines for underground utility corridors?"
"How do we plan electrical grid expansion for IT parks?"
```

### Environmental Planning
```
"What are the Environmental Impact Assessment requirements for large projects?"
"How do we implement sustainable drainage systems (SuDS)?"
"What are the tree preservation norms during development?"
"How do we calculate carbon footprint of urban developments?"
"What are the coastal regulation zone restrictions in Chennai?"
```

### Professional Methodologies
```
"How do we conduct participatory planning exercises with communities?"
"What are the best practices for master plan preparation?"
"How do we use GIS for spatial analysis in urban planning?"
"What metrics do we use to measure urban sustainability?"
"How do we integrate climate resilience in city planning?"
```

### Technical Planning (Restricted from Citizens)
```
"What are the detailed zoning variance approval procedures?"
→ Planner: Complete technical procedures and regulatory requirements
→ Citizen: [ACCESS RESTRICTED] This is a technical planning topic that requires planner privileges. Please contact a planning professional for assistance.

"How do we calculate development impact fees?"
→ Planner: Technical methodology and calculation frameworks
→ Citizen: [ACCESS RESTRICTED] Technical planning processes require professional guidance.

"What are the environmental impact assessment methodologies?"
→ Planner: Detailed EIA procedures and regulatory compliance
→ Citizen: [ACCESS RESTRICTED] Professional environmental assessment requires certified planners.

"Explain the subdivision approval process in detail"
→ Planner: Complete regulatory process and technical requirements
→ Citizen: [ACCESS RESTRICTED] Subdivision processes require planner or legal expertise.
```

---

## [ADMIN] Administrator Prompts (admin1)

### Financial Analysis & Budget Planning
```
"Show me the current municipal budget allocation for infrastructure"
"What are the revenue projections from property tax in Chennai?"
"How can we reduce administrative costs by 15% while maintaining services?"
"What is the ROI analysis for the proposed Metro Phase 2 project?"
"financial:list all"
"financial:show infrastructure_budget"
"What are the detailed departmental expenditures for the current fiscal year?"
"Analyze the cost-benefit ratio of outsourcing vs in-house service delivery"
```

### Strategic Planning & Policy Development
```
"What are the long-term demographic projections for Chennai by 2040?"
"How do we prioritize infrastructure investments across different zones?"
"What is the economic impact of the IT corridor development?"
"How do we measure the effectiveness of current urban policies?"
"What are the funding mechanisms for smart city initiatives?"
"Provide confidential feasibility analysis for the proposed waterfront development"
"What are the political economy considerations for rezoning sensitive areas?"
"Show internal risk assessments for major infrastructure projects"
```

### Municipal Finance & Revenue (Admin-Only Access)
```
"What are the classified budget allocations for administrative operations?"
"Show me the detailed breakdown of tender awards over 50 crores"
"What are the debt restructuring options for Chennai Corporation?"
"Analyze the financial impact of property tax exemptions for IT companies"
"What are the undisclosed revenue streams from land monetization?"
"Provide audit findings on departmental budget variances"
"Show contractor payment delays and their financial implications"
```

### Executive Decision Support (Restricted Content)
```
"What are the confidential legal risks in the proposed slum rehabilitation project?"
"Analyze political feasibility of implementing congestion pricing"
"What are the internal performance ratings of department heads?"
"Show sensitive demographic data for electoral ward redistricting"
"What are the classified security assessments for public infrastructure?"
"Provide confidential stakeholder analysis for major policy changes"
"What are the undisclosed environmental impact concerns?"
```

### Inter-governmental Coordination (Sensitive Information)
```
"What are the confidential negotiations with state government on fund allocation?"
"Show internal correspondence on central government scheme implementations"
"What are the political sensitivities around metropolitan governance restructuring?"
"Provide classified briefings on inter-municipal disputes"
"What are the undisclosed terms of public-private partnership agreements?"
"Show sensitive diplomatic considerations for international city partnerships"
```

### Crisis Management & Internal Operations (Admin-Restricted)
```
"What are the classified emergency response protocols for civil unrest?"
"Show internal assessment of departmental corruption risks"
"What are the confidential contingency budgets for crisis management?"
"Provide sensitive intelligence on potential infrastructure threats"
"What are the undisclosed backup plans for essential service failures?"
"Show internal staff performance issues and disciplinary actions"
"What are the classified vendor blacklist and security concerns?"
```

### Access Control Demonstration Examples
```
"Show me all financial metrics and budget data" 
→ Admin: Full detailed financial dashboard
→ Citizen: [ACCESS DENIED] Financial information requires admin privileges

"What are the internal audit findings for this year?"
→ Admin: Complete audit reports with recommendations
→ Citizen: [ACCESS DENIED] Internal audits are confidential administrative documents

"Provide breakdown of all departmental expenditures"
→ Admin: Detailed line-item budget analysis
→ Citizen: [ACCESS DENIED] Detailed budget data requires administrative access

"What are the political considerations for the new zoning policy?"
→ Admin: Strategic analysis including stakeholder politics
→ Citizen: General information about zoning policies without political analysis
```

---

## [CITY] Chennai-Specific Queries (All Roles)

### Real-Time Data Integration
```
"What's the current weather and how does it affect transport?"
"Are there any traffic disruptions on ECR due to weather?"
"What are the air quality levels near schools today?"
"Is public transport running normally during monsoon?"
"What's the current status of Chennai Metro services?"
```

### Government Services Integration
```
"What are the latest announcements from Chennai District Administration?"
"Are there any new citizen service centers opening?"
"What government schemes are currently accepting applications?"
"How do I contact the Chennai Corporation for complaints?"
"What are the current development projects in my area?"
```

### Cultural & Tourism Information
```
"What are the major cultural events happening in Chennai this month?"
"How do tourists usually travel from airport to Marina Beach?"
"What are the heritage sites that need special planning consideration?"
"How do religious festivals impact traffic planning in Chennai?"
"What are the traditional markets that need infrastructure support?"
```

---

## [SECURITY] Access Control Demonstration

### Role-Based Response Examples

#### Financial Queries
**Query**: "What is the city's annual infrastructure budget?"

**👤 Citizen Response:**
```
[ACCESS DENIED] Financial information requires admin privileges. Contact an administrator for budget inquiries.
```

**📐 Planner Response:**
```
[ACCESS DENIED] Detailed financial data requires administrative privileges. For project planning purposes, contact the finance department.
```

**🗂️ Admin Response:**
```
Chennai Corporation's annual infrastructure budget for FY 2025-26 is ₹8,450 crores, allocated across:
- Transportation: ₹3,200 crores (38%)
- Water & Sanitation: ₹2,100 crores (25%)
- Roads & Bridges: ₹1,800 crores (21%)
- Digital Infrastructure: ₹800 crores (9%)
- Green Infrastructure: ₹550 crores (7%)

[Detailed budget breakdown and variance analysis available...]
```

#### Technical Planning Queries
**Query**: "How do I apply for a zoning variance?"

**👤 Citizen Response:**
```
[ACCESS RESTRICTED] This is a technical planning topic that requires planner privileges. Please contact a planning professional for assistance.

For general guidance:
- Contact your local planning department
- Consider hiring a planning consultant
- Review publicly available zoning information on the city website
```

**📐 Planner Response:**
```
Zoning variance application process in Chennai:

1. **Pre-Application Consultation**
   - Site analysis and zoning review
   - Preliminary feasibility assessment
   - Stakeholder identification

2. **Application Preparation**
   - Form submission with required documents
   - Site plans and architectural drawings
   - Justification narrative

[Complete technical procedure continues...]
```

**🗂️ Admin Response:**
```
[Same as planner response, plus strategic considerations and approval statistics]
```

#### Internal Operations Queries
**Query**: "What are the performance issues in the public works department?"

**👤 Citizen Response:**
```
[ACCESS DENIED] Internal administrative information requires elevated privileges. For general service feedback, use the citizen portal or contact customer service.
```

**📐 Planner Response:**
```
[ACCESS DENIED] Internal personnel matters require administrative access. For project coordination issues, contact the department directly.
```

**🗂️ Admin Response:**
```
Public Works Department Performance Analysis (Confidential):

Current Issues:
- 23% delay in road maintenance projects
- Budget overruns in 4 major infrastructure contracts
- Staff shortage of 15% in technical positions
- Equipment utilization at 67% efficiency

[Detailed remedial actions and personnel recommendations...]
```

### Multi-Context Queries
```
"Considering the current weather conditions and traffic, what's the best route from Velachery to OMR IT parks, and how does this relate to TOD planning principles?"

"How do the current air quality levels in different Chennai zones influence residential development strategies and public health planning?"

"What are the financial implications of expanding public transport to reduce traffic congestion, and how do we measure success?"
```

### Comparative Analysis
```
"Compare Chennai's transportation planning with Bangalore's approach"
"How does Chennai's housing policy differ from Mumbai's slum rehabilitation?"
"What can we learn from Singapore's water management for Chennai?"
```

### Scenario Planning
```
"If Chennai's population grows by 30% in the next 10 years, how should we adapt our infrastructure?"
"What would be the impact of implementing congestion pricing in Chennai CBD?"
"How would sea level rise affect Chennai's coastal development plans?"
```

---

## [READY] Tips for Effective Prompts

### 1. Be Specific About Context
- Include location details (specific Chennai areas/zones)
- Mention timeframes (current, 5-year plan, long-term)
- Specify scale (neighborhood, city-wide, metropolitan)

### 2. Leverage Role-Specific Access
- Citizens: Focus on immediate, practical needs
- Planners: Ask for technical methodologies and professional standards
- Administrators: Request strategic insights and financial analysis

### 3. Use Follow-up Questions
- Build on previous responses for deeper understanding
- Ask for implementation details
- Request specific examples or case studies

### 4. Combine Live Data with Planning
- Ask how current conditions affect planning decisions
- Request real-time data to inform policy recommendations
- Integrate weather, traffic, and demographic data in queries

### 5. Memory-Enhanced Conversations
- Reference previous discussions in the same session
- Build complex understanding through sequential queries
- Let the system remember your specific interests and context

---

## [SUCCESS] System Capabilities Summary

The Urban Planning Assistant can handle:
- **Live Chennai Data**: Weather, traffic, air quality, government updates
- **Technical Planning**: Zoning, regulations, methodologies, standards
- **Financial Analysis**: Budgets, ROI, revenue projections (admin only)
- **Multi-modal Responses**: Text, data analysis, policy recommendations
- **Memory Integration**: Contextual conversations building on previous exchanges
- **Role-based Security**: Appropriate information access for each user type

**Start exploring**: Choose your role and begin with any query from this guide!
