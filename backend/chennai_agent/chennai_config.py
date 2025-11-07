"""
Chennai Smart Agent Configuration
Handles configuration and API endpoints for Chennai city data
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Chennai Geographic Boundaries
CHENNAI_BOUNDS = {
    "north": 13.2846,
    "south": 12.7749,
    "east": 80.3463,
    "west": 80.0812,
    "center": {
        "lat": 13.0827,
        "lon": 80.2707
    }
}

# Administrative Zones in Chennai (15 zones)
CHENNAI_ZONES = [
    "Thiruvottiyur", "Manali", "Madhavaram", "Tondiarpet", "Royapuram",
    "Thiru. Vi. Ka. Nagar", "Ambattur", "Anna Nagar", "Teynampet", "Kodambakkam",
    "Valasaravakkam", "Alandur", "Adyar", "Perungudi", "Sholinganallur"
]

# Major Districts/Areas
CHENNAI_DISTRICTS = {
    "Central Chennai": ["George Town", "Parry's Corner", "Sowcarpet", "Broadway"],
    "North Chennai": ["Thiruvottiyur", "Manali", "Ennore", "Madhavaram"],
    "South Chennai": ["Adyar", "Velachery", "Tambaram", "Pallikaranai"],
    "West Chennai": ["Porur", "Koyambedu", "Vadapalani", "K.K. Nagar"],
    "OMR Corridor": ["Perungudi", "Sholinganallur", "Thoraipakkam", "Kelambakkam"],
    "IT Corridor": ["Guindy", "Taramani", "Siruseri", "Kazhipattur"]
}

# Transportation Systems
CHENNAI_TRANSPORT = {
    "metro": {
        "lines": ["Blue Line", "Green Line"],
        "stations": 54,
        "total_length_km": 54.05
    },
    "suburban_rail": {
        "lines": ["Chennai Beach-Tambaram", "Chennai Beach-Velachery", "Chennai Central-Arakkonam"],
        "stations": 28
    },
    "bus": {
        "routes": 729,
        "buses": 3411,
        "daily_passengers": 3500000
    },
    "mrts": {
        "length_km": 19.664,
        "stations": 18
    }
}

# API Endpoints for Live Data (These would be replaced with actual APIs)
API_ENDPOINTS = {
    "census": "https://api.censusindia.gov.in/",
    "weather": "https://api.openweathermap.org/data/2.5/",
    "traffic": "https://api.tomtom.com/traffic/",
    "air_quality": "https://api.waqi.info/feed/here/?token=db1387fa05881cc7eb7b87072201536ad467d35d",
    "property": "https://api.magicbricks.com/",  # Example
    "water": "https://www.chennaimetrowater.gov.in/",  # Would need API
}

# API Keys (from environment)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY", "")
WAQI_API_KEY = os.getenv("WAQI_API_KEY", "")

# Chennai Metropolitan Development Authority (CMDA) Areas
CMDA_AREAS = {
    "Chennai Corporation": 426.51,  # sq km
    "Added Areas": 721.62,  # sq km
    "Total CMA": 1189.0  # sq km
}

# Demographics (2011 Census - as baseline)
CHENNAI_DEMOGRAPHICS = {
    "population": 4646732,  # 2011 census
    "density_per_sqkm": 26903,
    "literacy_rate": 90.33,
    "sex_ratio": 989,  # females per 1000 males
    "households": 1255686,
    "slum_population": 820000,
    "slum_percentage": 17.65
}

# Economic Indicators
CHENNAI_ECONOMY = {
    "gdp_billion_usd": 78.6,  # 2020 estimate
    "major_sectors": ["Automobiles", "IT Services", "Healthcare", "Manufacturing"],
    "industrial_parks": ["Ambattur", "Guindy", "Madhavaram"],
    "it_parks": ["Tidel Park", "ELCOT SEZ", "DLF IT Park", "RMZ Millenia"]
}

# Infrastructure
CHENNAI_INFRASTRUCTURE = {
    "water_supply_mld": 830,  # Million Liters per Day
    "sewage_treatment_mld": 714,
    "solid_waste_tons_per_day": 5000,
    "hospitals": 12,  # Major hospitals
    "schools": 1000,  # Approximate
    "parks": 270
}

# Environmental Data
CHENNAI_ENVIRONMENT = {
    "coastline_km": 19,
    "wetlands": ["Pallikaranai Marshland", "Ennore Creek", "Adyar Poonga"],
    "rivers": ["Cooum", "Adyar", "Kosasthalaiyar"],
    "reservoirs": ["Red Hills Lake", "Chembarambakkam Lake", "Poondi Reservoir", "Cholavaram Lake"]
}

# Real Estate Zones (Approximate pricing - would need live API)
CHENNAI_REAL_ESTATE_ZONES = {
    "Premium": {
        "areas": ["Boat Club", "Poes Garden", "Nungambakkam", "Alwarpet"],
        "avg_price_per_sqft_inr": 12000
    },
    "High": {
        "areas": ["Anna Nagar", "T. Nagar", "Adyar", "Mylapore"],
        "avg_price_per_sqft_inr": 8000
    },
    "Mid-High": {
        "areas": ["Velachery", "Porur", "OMR Areas", "ECR"],
        "avg_price_per_sqft_inr": 6000
    },
    "Mid": {
        "areas": ["Chromepet", "Tambaram", "Ambattur", "Avadi"],
        "avg_price_per_sqft_inr": 4500
    },
    "Emerging": {
        "areas": ["Kelambakkam", "Maraimalai Nagar", "Chengalpattu"],
        "avg_price_per_sqft_inr": 3500
    }
}
