"""
Real Estate Metrics Integration for Urban Planning Assistant
Adds comprehensive real estate and economic data to Neo4j knowledge graph
"""

from neo4j import GraphDatabase
from config import NEO4J_AURA_URI, NEO4J_USERNAME, NEO4J_PASSWORD
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class RealEstateMetricsManager:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_AURA_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    def close(self):
        self.driver.close()
    
    def add_real_estate_metrics(self):
        """Add comprehensive real estate metrics for Chennai"""
        
        # Chennai Real Estate Data
        real_estate_metrics = [
            # Property Types
            {"name": "Residential Property", "type": "Property_Type",
             "avg_price_sqft": 4500, "growth_rate": 8.2, "market_status": "Growing"},
            {"name": "Commercial Property", "type": "Property_Type",
             "avg_price_sqft": 7800, "growth_rate": 12.1, "market_status": "High Demand"},
            {"name": "Industrial Property", "type": "Property_Type",
             "avg_price_sqft": 2200, "growth_rate": 5.8, "market_status": "Stable"},
            {"name": "Retail Space", "type": "Property_Type",
             "avg_price_sqft": 9500, "growth_rate": 15.3, "market_status": "Expanding"},
            
            # Chennai Locality Data
            {"name": "Anna Nagar", "type": "Residential_Zone",
             "avg_price_sqft": 6200, "appreciation_rate": 9.5, "demand_level": "High"},
            {"name": "T. Nagar", "type": "Commercial_Zone",
             "avg_price_sqft": 12000, "appreciation_rate": 11.2, "demand_level": "Very High"},
            {"name": "Adyar", "type": "Premium_Residential",
             "avg_price_sqft": 8500, "appreciation_rate": 10.8, "demand_level": "High"},
            {"name": "OMR (IT Corridor)", "type": "IT_Hub",
             "avg_price_sqft": 5800, "appreciation_rate": 14.2, "demand_level": "Very High"},
            {"name": "Velachery", "type": "Residential_Zone",
             "avg_price_sqft": 5200, "appreciation_rate": 12.3, "demand_level": "High"},
            {"name": "Guindy", "type": "Mixed_Development",
             "avg_price_sqft": 6800, "appreciation_rate": 8.7, "demand_level": "Medium"},
            {"name": "Tambaram", "type": "Suburban_Residential",
             "avg_price_sqft": 3200, "appreciation_rate": 6.9, "demand_level": "Medium"},
            {"name": "Porur", "type": "Emerging_IT_Hub",
             "avg_price_sqft": 4200, "appreciation_rate": 13.1, "demand_level": "Growing"},
            
            # Infrastructure Impact Metrics
            {"name": "Metro Connectivity", "type": "Infrastructure_Factor",
             "price_impact": 18.5, "demand_boost": 25.0, "accessibility_score": 8.2},
            {"name": "IT Park Proximity", "type": "Economic_Factor",
             "price_impact": 22.3, "demand_boost": 35.0, "job_accessibility": 9.1},
            {"name": "School Proximity", "type": "Social_Factor",
             "price_impact": 12.1, "demand_boost": 15.0, "family_appeal": 8.7},
            {"name": "Hospital Access", "type": "Healthcare_Factor",
             "price_impact": 8.9, "demand_boost": 12.0, "convenience_score": 7.8},
            
            # Market Trends
            {"name": "Affordable Housing", "type": "Market_Segment",
             "growth_rate": 18.7, "government_support": "High", "demand_gap": 75000},
            {"name": "Luxury Housing", "type": "Market_Segment",
             "growth_rate": 6.2, "market_saturation": "Medium", "target_income": 2500000},
            {"name": "Co-living Spaces", "type": "Emerging_Trend",
             "growth_rate": 45.2, "target_demographic": "Young Professionals", "market_size": 12000},
            {"name": "Smart Homes", "type": "Technology_Trend",
             "adoption_rate": 23.1, "price_premium": 8.5, "future_standard": "High"},
        ]
        
        # Economic Indicators
        economic_metrics = [
            {"name": "Chennai GDP Growth", "type": "Economic_Indicator",
             "current_rate": 7.8, "projection": 8.2, "sector_contribution": "Services 65%"},
            {"name": "Employment Rate", "type": "Social_Indicator",
             "current_rate": 92.3, "trend": "Improving", "key_sectors": "IT, Manufacturing"},
            {"name": "Per Capita Income", "type": "Economic_Indicator",
             "amount": 245000, "growth_rate": 9.1, "national_rank": 3},
            {"name": "Infrastructure Investment", "type": "Development_Metric",
             "annual_budget": 15600, "allocation": "Transport 40%, Utilities 35%", "roi": 12.8},
            
            # Investment Metrics
            {"name": "FDI Inflow", "type": "Investment_Metric",
             "annual_amount": 8900, "growth_rate": 14.7, "key_sectors": "IT, Auto"},
            {"name": "Real Estate Investment", "type": "Property_Investment",
             "institutional_share": 35.2, "retail_share": 64.8, "roi_avg": 11.5},
            {"name": "Construction Activity", "type": "Development_Activity",
             "new_projects": 287, "completion_rate": 78.3, "employment": 185000},
        ]
        
        with self.driver.session() as session:
            # Add real estate metrics
            for metric in real_estate_metrics:
                session.run("""
                    MERGE (m:RealEstate_Metric {name: $name})
                    SET m += $properties
                    """, name=metric["name"], properties=metric)
            
            # Add economic metrics
            for metric in economic_metrics:
                session.run("""
                    MERGE (e:Economic_Metric {name: $name})
                    SET e += $properties
                    """, name=metric["name"], properties=metric)
            
            logger.info(f"Added {len(real_estate_metrics)} real estate metrics")
            logger.info(f"Added {len(economic_metrics)} economic metrics")
    
    def add_development_projects(self):
        """Add major development projects and their impact"""
        
        major_projects = [
            {"name": "Chennai Metro Phase 2", "type": "Transit_Project",
             "investment": 61000, "completion": "2026", "impact_radius": "5km",
             "property_impact": 25.0, "areas_affected": ["Porur", "Sholinganallur", "Madhavaram"]},
            
            {"name": "Smart Cities Mission Chennai", "type": "Urban_Development",
             "investment": 2800, "completion": "2025", "scope": "Central Chennai",
             "technology_integration": "High", "property_premium": 15.0},
            
            {"name": "Chennai Port Expansion", "type": "Infrastructure_Project",
             "investment": 12000, "completion": "2027", "job_creation": 25000,
             "industrial_impact": "High", "logistics_improvement": 35.0},
            
            {"name": "IT Corridor Extension", "type": "Economic_Development",
             "investment": 8500, "new_it_parks": 12, "job_capacity": 150000,
             "residential_demand": "Very High", "commercial_growth": 40.0},
            
            {"name": "Affordable Housing Mission", "type": "Social_Housing",
             "target_units": 75000, "investment": 18000, "beneficiaries": 300000,
             "income_group": "EWS/LIG", "subsidy_component": 40.0},
            
            {"name": "Cooum River Restoration", "type": "Environmental_Project",
             "investment": 3200, "length": "17km", "flood_reduction": 60.0,
             "property_uplift": 20.0, "green_infrastructure": "Extensive"},
        ]
        
        with self.driver.session() as session:
            for project in major_projects:
                session.run("""
                    MERGE (p:Development_Project {name: $name})
                    SET p += $properties
                    """, name=project["name"], properties=project)
            
            logger.info(f"Added {len(major_projects)} major development projects")
    
    def create_impact_relationships(self):
        """Create relationships between projects, metrics, and locations"""
        
        impact_relationships = [
            # Metro Impact on Property Values
            ("Chennai Metro Phase 2", "INCREASES", "Property Values", {"impact_percentage": 25.0}),
            ("Chennai Metro Phase 2", "IMPROVES", "Connectivity", {"accessibility_boost": 40.0}),
            ("Chennai Metro Phase 2", "BENEFITS", "Porur", {"price_appreciation": 15.0}),
            ("Chennai Metro Phase 2", "BENEFITS", "Sholinganallur", {"price_appreciation": 20.0}),
            
            # IT Corridor Impact
            ("IT Corridor Extension", "DRIVES", "Commercial Property", {"demand_increase": 45.0}),
            ("IT Corridor Extension", "INCREASES", "Employment Rate", {"job_growth": 25.0}),
            ("IT Corridor Extension", "BENEFITS", "OMR (IT Corridor)", {"property_boost": 30.0}),
            
            # Smart City Impact
            ("Smart Cities Mission Chennai", "ENABLES", "Smart Homes", {"adoption_boost": 35.0}),
            ("Smart Cities Mission Chennai", "IMPROVES", "Infrastructure Quality", {"upgrade_score": 8.5}),
            
            # Environmental Projects
            ("Cooum River Restoration", "IMPROVES", "Environmental Quality", {"pollution_reduction": 50.0}),
            ("Cooum River Restoration", "INCREASES", "Property Values", {"uplift_percentage": 20.0}),
            
            # Housing Mission Impact
            ("Affordable Housing Mission", "ADDRESSES", "Housing Gap", {"units_provided": 75000}),
            ("Affordable Housing Mission", "BENEFITS", "Low Income Groups", {"household_coverage": 300000}),
            
            # Infrastructure Factors
            ("Metro Connectivity", "IMPACTS", "Residential Property", {"value_increase": 18.5}),
            ("IT Park Proximity", "DRIVES", "Commercial Property", {"demand_boost": 35.0}),
            ("School Proximity", "AFFECTS", "Family Housing Demand", {"preference_score": 8.7}),
        ]
        
        with self.driver.session() as session:
            for source, relation_type, target, properties in impact_relationships:
                session.run("""
                    MATCH (a {name: $source}), (b {name: $target})
                    MERGE (a)-[r:IMPACT {type: $relation_type}]->(b)
                    SET r += $properties
                    """, source=source, target=target, relation_type=relation_type, properties=properties)
            
            logger.info(f"Created {len(impact_relationships)} impact relationships")
    
    def add_market_forecasts(self):
        """Add market forecasting data"""
        
        forecasts = [
            {"name": "5-Year Property Forecast", "type": "Market_Forecast",
             "timeframe": "2024-2029", "avg_appreciation": 9.2, 
             "best_segments": ["Commercial", "IT Corridor Residential"],
             "risk_factors": ["Interest Rates", "Regulatory Changes"]},
            
            {"name": "Rental Market Outlook", "type": "Rental_Forecast",
             "yield_projection": 6.8, "demand_growth": 12.0,
             "preferred_locations": ["OMR", "Porur", "Velachery"],
             "tenant_profile": "IT Professionals, Young Families"},
            
            {"name": "Infrastructure ROI Analysis", "type": "Investment_Analysis",
             "metro_roi": 18.5, "road_infrastructure_roi": 12.3,
             "social_infrastructure_roi": 8.7, "green_infrastructure_roi": 15.2},
            
            {"name": "Emerging Trends Impact", "type": "Trend_Analysis",
             "work_from_home_impact": -5.2, "co_living_growth": 45.0,
             "sustainability_premium": 8.5, "smart_home_adoption": 23.0},
        ]
        
        with self.driver.session() as session:
            for forecast in forecasts:
                session.run("""
                    MERGE (f:Market_Forecast {name: $name})
                    SET f += $properties
                    """, name=forecast["name"], properties=forecast)
            
            logger.info(f"Added {len(forecasts)} market forecasting models")
    
    def generate_sample_transactions(self):
        """Generate sample transaction data for analysis"""
        
        # Sample transaction patterns
        transaction_types = [
            {"name": "Residential Sale", "avg_value": 5500000, "volume_monthly": 1250, "growth_rate": 8.9},
            {"name": "Commercial Lease", "avg_value": 450000, "volume_monthly": 380, "growth_rate": 12.1},
            {"name": "Industrial Transfer", "avg_value": 15000000, "volume_monthly": 45, "growth_rate": 6.2},
            {"name": "Land Development", "avg_value": 25000000, "volume_monthly": 15, "growth_rate": 18.7},
        ]
        
        with self.driver.session() as session:
            for transaction in transaction_types:
                session.run("""
                    MERGE (t:Transaction_Type {name: $name})
                    SET t += $properties
                    """, name=transaction["name"], properties=transaction)
            
            logger.info(f"Added {len(transaction_types)} transaction type patterns")

def add_real_estate_metrics():
    """Main function to add real estate metrics to knowledge graph"""
    try:
        manager = RealEstateMetricsManager()
        
        logger.info("Starting real estate metrics integration...")
        
        # Add core real estate metrics
        manager.add_real_estate_metrics()
        
        # Add development projects
        manager.add_development_projects()
        
        # Create impact relationships
        manager.create_impact_relationships()
        
        # Add market forecasts
        manager.add_market_forecasts()
        
        # Generate transaction patterns
        manager.generate_sample_transactions()
        
        # Create advanced analytics relationships
        with manager.driver.session() as session:
            # Connect economic indicators to real estate performance
            advanced_relationships = [
                ("Chennai GDP Growth", "DRIVES", "Real Estate Investment"),
                ("Employment Rate", "CORRELATES", "Residential Demand"),
                ("Per Capita Income", "INFLUENCES", "Luxury Housing"),
                ("FDI Inflow", "BOOSTS", "Commercial Property"),
                ("Infrastructure Investment", "ENHANCES", "Property Values"),
                
                # Market segment relationships
                ("Affordable Housing", "SERVES", "Low Income Groups"),
                ("Co-living Spaces", "TARGETS", "Young Professionals"),
                ("Smart Homes", "APPEALS_TO", "Tech-Savvy Buyers"),
                
                # Location-based correlations
                ("Metro Connectivity", "PREMIUM_IN", "Anna Nagar"),
                ("IT Park Proximity", "VALUABLE_FOR", "OMR (IT Corridor)"),
                ("Commercial Hub", "BENEFITS", "T. Nagar"),
            ]
            
            for source, relation, target in advanced_relationships:
                session.run("""
                    MATCH (a {name: $source}), (b {name: $target})
                    MERGE (a)-[r:MARKET_RELATIONSHIP {type: $relation}]->(b)
                    """, source=source, target=target, relation=relation)
        
        manager.close()
        logger.info("Real estate metrics integration completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to add real estate metrics: {e}")
        raise

if __name__ == "__main__":
    add_real_estate_metrics()
