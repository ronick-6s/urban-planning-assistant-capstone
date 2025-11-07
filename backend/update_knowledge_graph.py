"""
Enhanced Knowledge Graph Update Module
Adds comprehensive urban planning concepts and relationships to Neo4j
"""

from neo4j import GraphDatabase
from config import NEO4J_AURA_URI, NEO4J_USERNAME, NEO4J_PASSWORD
import logging

logger = logging.getLogger(__name__)

class KnowledgeGraphUpdater:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_AURA_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    def close(self):
        self.driver.close()
    
    def add_enhanced_concepts(self):
        """Add enhanced urban planning concepts and relationships"""
        
        # Enhanced Urban Planning Concepts
        concepts = [
            # Core Planning Concepts
            {"name": "Smart City", "type": "Planning_Concept", 
             "description": "Technology-enabled urban development for efficiency and sustainability"},
            {"name": "Transit-Oriented Development", "type": "Planning_Strategy",
             "description": "Dense, walkable development around public transport hubs"},
            {"name": "Green Infrastructure", "type": "Infrastructure_Type",
             "description": "Network of natural and semi-natural systems providing ecosystem services"},
            {"name": "Mixed-Use Development", "type": "Development_Type",
             "description": "Integration of residential, commercial, and office spaces"},
            {"name": "Urban Regeneration", "type": "Planning_Strategy",
             "description": "Comprehensive redevelopment of declining urban areas"},
            {"name": "Complete Streets", "type": "Transportation_Concept",
             "description": "Streets designed for all users: pedestrians, cyclists, transit, vehicles"},
            
            # Sustainability Concepts
            {"name": "Circular Economy", "type": "Economic_Model",
             "description": "Resource efficiency through reduce, reuse, recycle principles"},
            {"name": "Carbon Neutrality", "type": "Environmental_Goal",
             "description": "Net zero carbon emissions through reduction and offsetting"},
            {"name": "Resilient Infrastructure", "type": "Infrastructure_Strategy",
             "description": "Systems designed to withstand and recover from disruptions"},
            {"name": "Blue-Green Infrastructure", "type": "Infrastructure_Type",
             "description": "Integration of water and green systems for urban sustainability"},
            
            # Chennai Specific Concepts
            {"name": "Chennai Metro", "type": "Transit_System",
             "description": "Rapid transit system serving Chennai metropolitan area"},
            {"name": "Buckingham Canal", "type": "Water_Infrastructure",
             "description": "Historic waterway requiring restoration and urban integration"},
            {"name": "IT Corridor", "type": "Economic_Zone",
             "description": "Technology hub along Old Mahabalipuram Road"},
            {"name": "Marina Beach", "type": "Public_Space",
             "description": "World's second-longest urban beach and major recreation area"},
            {"name": "Chennai Port", "type": "Infrastructure",
             "description": "Major gateway port requiring sustainable expansion"},
            
            # Modern Planning Tools
            {"name": "GIS Analytics", "type": "Planning_Tool",
             "description": "Geographic information systems for spatial analysis"},
            {"name": "Digital Twin", "type": "Technology",
             "description": "Virtual replica of city systems for modeling and optimization"},
            {"name": "Participatory Planning", "type": "Planning_Method",
             "description": "Community engagement in planning decision-making"},
            {"name": "Performance Metrics", "type": "Assessment_Tool",
             "description": "Quantitative measures for evaluating planning outcomes"},
            
            # Policy Frameworks
            {"name": "New Urban Agenda", "type": "Policy_Framework",
             "description": "UN framework for sustainable urban development"},
            {"name": "SDG 11", "type": "Global_Goal",
             "description": "Sustainable Development Goal for inclusive, safe, resilient cities"},
            {"name": "Tamil Nadu Urban Policy", "type": "Regional_Policy",
             "description": "State framework for urban development and governance"},
        ]
        
        # Enhanced Relationships
        relationships = [
            # Smart City Relationships
            ("Smart City", "ENABLES", "Digital Twin"),
            ("Smart City", "REQUIRES", "GIS Analytics"),
            ("Smart City", "PROMOTES", "Participatory Planning"),
            ("Smart City", "SUPPORTS", "Performance Metrics"),
            
            # TOD Relationships
            ("Transit-Oriented Development", "INTEGRATES", "Chennai Metro"),
            ("Transit-Oriented Development", "PROMOTES", "Mixed-Use Development"),
            ("Transit-Oriented Development", "REDUCES", "Urban Sprawl"),
            ("Transit-Oriented Development", "SUPPORTS", "Complete Streets"),
            
            # Sustainability Relationships
            ("Green Infrastructure", "INCLUDES", "Blue-Green Infrastructure"),
            ("Green Infrastructure", "SUPPORTS", "Carbon Neutrality"),
            ("Green Infrastructure", "ENHANCES", "Resilient Infrastructure"),
            ("Circular Economy", "PROMOTES", "Resource Efficiency"),
            ("Circular Economy", "SUPPORTS", "Carbon Neutrality"),
            
            # Chennai Specific Relationships
            ("Chennai Metro", "CONNECTS", "IT Corridor"),
            ("Chennai Metro", "SERVES", "Marina Beach"),
            ("Buckingham Canal", "REQUIRES", "Urban Regeneration"),
            ("Buckingham Canal", "POTENTIAL_FOR", "Blue-Green Infrastructure"),
            ("IT Corridor", "BENEFITS_FROM", "Transit-Oriented Development"),
            ("Chennai Port", "NEEDS", "Resilient Infrastructure"),
            
            # Policy Integration
            ("New Urban Agenda", "PROMOTES", "Smart City"),
            ("SDG 11", "INCLUDES", "Transit-Oriented Development"),
            ("Tamil Nadu Urban Policy", "IMPLEMENTS", "New Urban Agenda"),
            ("Tamil Nadu Urban Policy", "ADDRESSES", "Chennai Metro"),
            
            # Planning Process Relationships
            ("Participatory Planning", "IMPROVES", "Community Engagement"),
            ("GIS Analytics", "SUPPORTS", "Evidence-Based Planning"),
            ("Performance Metrics", "ENABLES", "Adaptive Management"),
            ("Digital Twin", "FACILITATES", "Scenario Planning"),
        ]
        
        with self.driver.session() as session:
            # Add concepts
            for concept in concepts:
                session.run("""
                    MERGE (c:Concept {name: $name})
                    SET c.type = $type, c.description = $description
                    """, concept)
            
            # Add relationships
            for source, relation, target in relationships:
                session.run("""
                    MATCH (a:Concept {name: $source}), (b:Concept {name: $target})
                    MERGE (a)-[r:RELATIONSHIP {type: $relation}]->(b)
                    """, source=source, target=target, relation=relation)
            
            logger.info(f"Added {len(concepts)} enhanced concepts and {len(relationships)} relationships")
    
    def add_chennai_specific_data(self):
        """Add Chennai-specific urban planning data"""
        
        chennai_data = [
            # Chennai Districts
            {"name": "North Chennai", "type": "Administrative_Zone",
             "description": "Industrial and port area with heritage significance"},
            {"name": "Central Chennai", "type": "Administrative_Zone",
             "description": "Commercial and administrative heart of the city"},
            {"name": "South Chennai", "type": "Administrative_Zone",
             "description": "Residential and IT hub with modern infrastructure"},
            
            # Transportation Infrastructure
            {"name": "Chennai Central Railway", "type": "Transit_Hub",
             "description": "Major railway terminus connecting Chennai to national network"},
            {"name": "Chennai Airport", "type": "Transportation_Infrastructure",
             "description": "International gateway requiring sustainable connectivity"},
            {"name": "MTC Bus Network", "type": "Public_Transport",
             "description": "Metropolitan transport system serving Chennai region"},
            
            # Economic Zones
            {"name": "TIDEL Park", "type": "Technology_Hub",
             "description": "IT complex promoting technology-driven development"},
            {"name": "Ennore Port", "type": "Industrial_Infrastructure",
             "description": "Satellite port requiring environmental management"},
            
            # Environmental Assets
            {"name": "Adyar River", "type": "Water_Body",
             "description": "Major river requiring restoration and flood management"},
            {"name": "Cooum River", "type": "Water_Body",
             "description": "Urban river needing comprehensive rehabilitation"},
            {"name": "Pallikaranai Wetland", "type": "Ecological_Asset",
             "description": "Critical wetland ecosystem requiring protection"},
        ]
        
        with self.driver.session() as session:
            for data in chennai_data:
                session.run("""
                    MERGE (c:Chennai_Feature {name: $name})
                    SET c.type = $type, c.description = $description
                    """, data)
            
            logger.info(f"Added {len(chennai_data)} Chennai-specific features")
    
    def create_policy_framework(self):
        """Create policy framework relationships"""
        
        policy_relationships = [
            # National to Local Policy Flow
            ("National Urban Policy", "GUIDES", "Tamil Nadu Urban Policy"),
            ("Tamil Nadu Urban Policy", "IMPLEMENTS", "Chennai Development Plan"),
            ("Chennai Development Plan", "REGULATES", "Zoning Regulations"),
            
            # International to National
            ("New Urban Agenda", "INFLUENCES", "National Urban Policy"),
            ("SDG 11", "SHAPES", "National Urban Policy"),
            
            # Implementation Mechanisms
            ("Chennai Development Plan", "REQUIRES", "Environmental Impact Assessment"),
            ("Zoning Regulations", "ENABLES", "Mixed-Use Development"),
            ("Building Codes", "ENSURES", "Safety Standards"),
            
            # Governance Structure
            ("Chennai Corporation", "IMPLEMENTS", "Chennai Development Plan"),
            ("CMDA", "COORDINATES", "Metropolitan Planning"),
            ("TNPCB", "MONITORS", "Environmental Compliance"),
        ]
        
        # Policy documents
        policies = [
            {"name": "National Urban Policy", "type": "National_Framework"},
            {"name": "Chennai Development Plan", "type": "Local_Plan"},
            {"name": "Environmental Impact Assessment", "type": "Assessment_Tool"},
            {"name": "Building Codes", "type": "Regulation"},
            {"name": "Safety Standards", "type": "Compliance_Framework"},
            {"name": "Chennai Corporation", "type": "Local_Authority"},
            {"name": "CMDA", "type": "Planning_Authority"},
            {"name": "TNPCB", "type": "Regulatory_Body"},
        ]
        
        with self.driver.session() as session:
            # Add policy entities
            for policy in policies:
                session.run("""
                    MERGE (p:Policy {name: $name})
                    SET p.type = $type
                    """, policy)
            
            # Add policy relationships
            for source, relation, target in policy_relationships:
                session.run("""
                    MERGE (a {name: $source})
                    MERGE (b {name: $target})
                    MERGE (a)-[r:POLICY_RELATIONSHIP {type: $relation}]->(b)
                    """, source=source, target=target, relation=relation)
            
            logger.info(f"Created policy framework with {len(policies)} entities")

def update_knowledge_graph():
    """Main function to update the knowledge graph"""
    try:
        updater = KnowledgeGraphUpdater()
        
        logger.info("Starting knowledge graph enhancement...")
        
        # Add enhanced concepts
        updater.add_enhanced_concepts()
        
        # Add Chennai-specific data
        updater.add_chennai_specific_data()
        
        # Create policy framework
        updater.create_policy_framework()
        
        # Create cross-domain relationships
        with updater.driver.session() as session:
            # Connect planning concepts to Chennai features
            cross_relationships = [
                ("Green Infrastructure", "APPLIES_TO", "Pallikaranai Wetland"),
                ("Blue-Green Infrastructure", "RELEVANT_FOR", "Adyar River"),
                ("Urban Regeneration", "NEEDED_FOR", "Buckingham Canal"),
                ("Transit-Oriented Development", "SURROUNDS", "Chennai Metro"),
                ("Smart City", "TRANSFORMS", "Chennai"),
                ("Resilient Infrastructure", "PROTECTS", "Chennai Port"),
            ]
            
            for source, relation, target in cross_relationships:
                session.run("""
                    MATCH (a {name: $source}), (b {name: $target})
                    MERGE (a)-[r:CROSS_DOMAIN {type: $relation}]->(b)
                    """, source=source, target=target, relation=relation)
        
        updater.close()
        logger.info("Knowledge graph enhancement completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to update knowledge graph: {e}")
        raise

if __name__ == "__main__":
    update_knowledge_graph()
