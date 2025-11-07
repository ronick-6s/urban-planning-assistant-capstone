"""
Chennai Data APIs
Fetches live and real-time data for Chennai city
Integrates: OpenWeather API, TomTom Traffic API, WAQI API, Census Data, Web Scraping
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
from chennai_config import *
from chennai_scrapers import (
    ChennaiMetroWaterScraper,
    ChennaiPropertyScraper,
    ChennaiCorporationScraper,
    ChennaiMetroScraper,
    CensusDataLoader
)

class ChennaiDataAPI:
    """Handles live data fetching for Chennai with real APIs and web scraping"""
    
    def __init__(self, census_file_path: Optional[str] = None):
        # API Keys
        self.openweather_key = OPENWEATHER_API_KEY
        self.tomtom_key = TOMTOM_API_KEY
        self.waqi_key = WAQI_API_KEY
        self.chennai_coords = CHENNAI_BOUNDS["center"]
        
        # Initialize scrapers
        self.water_scraper = ChennaiMetroWaterScraper()
        self.property_scraper = ChennaiPropertyScraper()
        self.corp_scraper = ChennaiCorporationScraper()
        self.metro_scraper = ChennaiMetroScraper()
        
        # Initialize census data loader
        self.census_loader = None
        if census_file_path:
            self.census_loader = CensusDataLoader(census_file_path)
            self.census_loader.load_census_data()
    
    def get_weather_data(self) -> Dict:
        """
        Fetch current weather data for Chennai using OpenWeatherMap API
        """
        if not self.openweather_key:
            print("[WARNING]  No OpenWeather API key - using mock data")
            return self._get_mock_weather()
        
        try:
            url = f"{API_ENDPOINTS['weather']}weather"
            params = {
                "lat": self.chennai_coords["lat"],
                "lon": self.chennai_coords["lon"],
                "appid": self.openweather_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "temperature_celsius": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity_percent": data["main"]["humidity"],
                "pressure_hpa": data["main"]["pressure"],
                "weather_condition": data["weather"][0]["description"],
                "wind_speed_mps": round(data["wind"]["speed"], 1),
                "visibility_m": data.get("visibility", "N/A"),
                "timestamp": datetime.now().isoformat(),
                "source": "OpenWeatherMap API (Live)",
                "status": "live"
            }
        except Exception as e:
            print(f"[ERROR] Error fetching weather data: {e}")
            return self._get_mock_weather()
    
    def _get_mock_weather(self) -> Dict:
        """Mock weather data when API is unavailable"""
        return {
            "temperature_celsius": 32,
            "feels_like": 35,
            "humidity_percent": 75,
            "pressure_hpa": 1010,
            "weather_condition": "partly cloudy",
            "wind_speed_mps": 4.5,
            "visibility_m": 6000,
            "timestamp": datetime.now().isoformat(),
            "source": "Mock Data",
            "status": "estimated"
        }
    
    def get_air_quality(self) -> Dict:
        """
        Fetch air quality index for Chennai using WAQI API
        """
        if not self.waqi_key:
            print("[WARNING]  No WAQI API key - using mock data")
            return self._get_mock_air_quality()
        
        try:
            # WAQI API URL format
            url = f"https://api.waqi.info/feed/chennai/"
            params = {"token": self.waqi_key}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                aqi_data = data["data"]
                iaqi = aqi_data.get("iaqi", {})
                
                return {
                    "aqi": aqi_data["aqi"],
                    "quality_level": self._get_aqi_level(aqi_data["aqi"]),
                    "pm25": iaqi.get("pm25", {}).get("v", None),
                    "pm10": iaqi.get("pm10", {}).get("v", None),
                    "o3": iaqi.get("o3", {}).get("v", None),
                    "no2": iaqi.get("no2", {}).get("v", None),
                    "station": aqi_data.get("city", {}).get("name", "Chennai"),
                    "timestamp": datetime.now().isoformat(),
                    "source": "WAQI API (Live)",
                    "status": "live"
                }
            else:
                return self._get_mock_air_quality()
                
        except Exception as e:
            print(f"[ERROR] Error fetching air quality: {e}")
            return self._get_mock_air_quality()
    
    def _get_mock_air_quality(self) -> Dict:
        """Mock air quality data"""
        return {
            "aqi": 112,
            "quality_level": "Moderate",
            "pm25": 45,
            "pm10": 85,
            "o3": None,
            "no2": None,
            "station": "Chennai (Estimated)",
            "timestamp": datetime.now().isoformat(),
            "source": "Mock Data",
            "status": "estimated"
        }
    
    def _get_aqi_level(self, aqi: int) -> str:
        """Convert AQI to quality level"""
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
    
    def get_traffic_data(self, area: str = "Central Chennai") -> Dict:
        """
        Get traffic data for specific area using TomTom Traffic API
        """
        if not self.tomtom_key:
            print("[WARNING]  No TomTom API key - using estimated data")
            return self._get_mock_traffic(area)
        
        try:
            # TomTom Traffic Flow API
            url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
            params = {
                "key": self.tomtom_key,
                "point": f"{self.chennai_coords['lat']},{self.chennai_coords['lon']}",
                "unit": "KMPH"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            flow_data = data.get("flowSegmentData", {})
            current_speed = flow_data.get("currentSpeed", 25)
            free_flow_speed = flow_data.get("freeFlowSpeed", 50)
            
            # Calculate congestion level
            if current_speed >= free_flow_speed * 0.8:
                congestion = "Light"
            elif current_speed >= free_flow_speed * 0.5:
                congestion = "Moderate"
            else:
                congestion = "Heavy"
            
            return {
                "area": area,
                "congestion_level": congestion,
                "current_speed_kmph": current_speed,
                "free_flow_speed_kmph": free_flow_speed,
                "delay_factor": round((free_flow_speed - current_speed) / free_flow_speed, 2),
                "peak_hours": ["8:00-10:00", "17:00-20:00"],
                "timestamp": datetime.now().isoformat(),
                "source": "TomTom Traffic API (Live)",
                "status": "live"
            }
        
        except Exception as e:
            print(f"[ERROR] Error fetching traffic data: {e}")
            return self._get_mock_traffic(area)
    
    def _get_mock_traffic(self, area: str) -> Dict:
        """Mock traffic data"""
        return {
            "area": area,
            "congestion_level": "Moderate",
            "current_speed_kmph": 25,
            "free_flow_speed_kmph": 50,
            "delay_factor": 0.5,
            "peak_hours": ["8:00-10:00", "17:00-20:00"],
            "timestamp": datetime.now().isoformat(),
            "source": "Estimated Data",
            "status": "estimated"
        }
    
    def get_metro_status(self) -> Dict:
        """Get Chennai Metro operational status - scraped data + static info"""
        # Try to scrape ridership data
        scraped_data = self.metro_scraper.get_ridership_data()
        
        return {
            "operational": True,
            "lines": [
                {
                    "name": "Blue Line",
                    "status": "Operational",
                    "frequency_minutes": 7,
                    "stations": 32,
                    "route": "Chennai Airport - Wimco Nagar"
                },
                {
                    "name": "Green Line",
                    "status": "Operational",
                    "frequency_minutes": 8,
                    "stations": 22,
                    "route": "St. Thomas Mount - CMBT"
                }
            ],
            "total_daily_passengers": scraped_data.get("daily_average", 250000),
            "growth_rate": scraped_data.get("growth_rate", 8.5),
            "timestamp": datetime.now().isoformat(),
            "source": scraped_data.get("source", "Estimated")
        }
    
    def get_water_supply_status(self) -> Dict:
        """Get water supply status - combines CMWSSB scraping + static data"""
        # Try to scrape reservoir levels from CMWSSB official website
        reservoir_data = self.water_scraper.get_reservoir_levels()
        
        # Get ongoing water projects from CMWSSB
        projects_data = self.water_scraper.get_water_projects()
        
        # Get CMWSSB complaint and service information
        complaint_info = self.water_scraper.get_complaint_info()
        
        return {
            "total_supply_mld": 850,
            "sources": {
                "desalination": 250,  # Nemmeli + Minjur plants
                "krishna_water": 480,
                "ground_water": 120
            },
            "reservoir_levels": reservoir_data.get("reservoirs", {
                "Red Hills": "65%",
                "Chembarambakkam": "58%",
                "Poondi": "72%",
                "Cholavaram": "45%"
            }),
            "ongoing_projects": projects_data.get("projects", [])[:3],  # Top 3 projects
            "complaint_hotline": complaint_info.get("complaint_cell", "044-4567 4567"),
            "online_services": {
                "complaints": complaint_info.get("online_complaints"),
                "water_tanker": complaint_info.get("water_tanker_booking"),
                "bill_payment": complaint_info.get("water_tax_payment"),
                "new_connection": complaint_info.get("new_connections")
            },
            "timestamp": datetime.now().isoformat(),
            "source": reservoir_data.get("source", "CMWSSB Official Website"),
            "status": reservoir_data.get("status", "estimated")
        }
    
    def get_property_trends(self, zone: str = "Mid-High") -> Dict:
        """
        Get property market trends - combines scraping + baseline data
        """
        zones_data = CHENNAI_REAL_ESTATE_ZONES.get(zone, CHENNAI_REAL_ESTATE_ZONES["Mid"])
        
        # Try to scrape live data for first area in zone
        scraped_data = None
        if zones_data["areas"]:
            scraped_data = self.property_scraper.scrape_magicbricks(zones_data["areas"][0])
        
        # Use scraped data if available, otherwise baseline
        if scraped_data and "avg_price_lakhs" in scraped_data:
            avg_price = int(scraped_data["avg_price_lakhs"] * 100000 / 1000)  # Convert lakhs to per sqft
            source = scraped_data["source"]
            status = "scraped"
        else:
            avg_price = zones_data["avg_price_per_sqft_inr"]
            source = "Market Analysis (Baseline)"
            status = "estimated"
        
        return {
            "zone": zone,
            "areas": zones_data["areas"],
            "avg_price_per_sqft_inr": avg_price,
            "trend": "Rising",
            "yoy_appreciation": 8.5,
            "demand_level": "High",
            "inventory_months": 11,
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "status": status
        }
    
    def get_demographic_trends(self, zone: str = None) -> Dict:
        """
        Get demographic data - uses census dataset if available
        """
        # Try to use census data first
        if self.census_loader and self.census_loader.data is not None:
            if zone:
                census_data = self.census_loader.get_zone_demographics(zone)
                if census_data:
                    return census_data
            else:
                census_data = self.census_loader.get_total_demographics()
                if census_data:
                    # Add calculated fields
                    census_data["growth_rate_annual"] = 1.5
                    census_data["workforce_participation"] = 48.5
                    census_data["age_distribution"] = {
                        "0-14": 18,
                        "15-59": 70,
                        "60+": 12
                    }
                    return census_data
        
        # Fallback to estimated data
        base_population = CHENNAI_DEMOGRAPHICS["population"]
        years_since_2011 = 2024 - 2011
        current_population = int(base_population * (1.015 ** years_since_2011))
        
        return {
            "total_population": current_population,
            "estimated_year": 2024,
            "growth_rate_annual": 1.5,
            "density_per_sqkm": int(current_population / 426.51),
            "literacy_rate": 92.5,
            "age_distribution": {
                "0-14": 18,
                "15-59": 70,
                "60+": 12
            },
            "workforce_participation": 48.5,
            "timestamp": datetime.now().isoformat(),
            "source": "Census + Projections",
            "status": "estimated"
        }
    
    def get_infrastructure_status(self) -> Dict:
        """Get current infrastructure metrics"""
        return {
            "transportation": {
                "metro_coverage_km": 54.05,
                "bus_routes": 729,
                "daily_bus_passengers": 3500000
            },
            "utilities": {
                "water_supply_mld": CHENNAI_INFRASTRUCTURE["water_supply_mld"],
                "sewage_treatment_mld": CHENNAI_INFRASTRUCTURE["sewage_treatment_mld"],
                "solid_waste_tons_per_day": CHENNAI_INFRASTRUCTURE["solid_waste_tons_per_day"]
            },
            "civic_amenities": {
                "major_hospitals": 12,
                "schools": 1000,
                "parks": 270
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_economic_indicators(self) -> Dict:
        """Get economic indicators for Chennai"""
        return {
            "gdp_billion_usd": 78.6,
            "gdp_per_capita_usd": 14800,
            "major_industries": CHENNAI_ECONOMY["major_sectors"],
            "employment_rate": 94.5,
            "major_employers": ["TCS", "Infosys", "Ford", "Hyundai", "Apollo Hospitals"],
            "industrial_zones": len(CHENNAI_ECONOMY["industrial_parks"]),
            "it_sez_count": len(CHENNAI_ECONOMY["it_parks"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_environmental_data(self) -> Dict:
        """Get environmental and green cover data"""
        return {
            "green_cover_percent": 15,
            "wetlands_count": len(CHENNAI_ENVIRONMENT["wetlands"]),
            "coastline_km": CHENNAI_ENVIRONMENT["coastline_km"],
            "major_rivers": CHENNAI_ENVIRONMENT["rivers"],
            "water_bodies": CHENNAI_ENVIRONMENT["reservoirs"],
            "tree_cover_sqkm": 64,
            "mangrove_cover_hectares": 175,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_zone_specific_data(self, zone_name: str) -> Dict:
        """Get comprehensive data for a specific zone"""
        if zone_name not in CHENNAI_ZONES:
            return {"error": f"Zone '{zone_name}' not found"}
        
        # Mock zone-specific data
        zone_index = CHENNAI_ZONES.index(zone_name)
        base_pop = CHENNAI_DEMOGRAPHICS["population"] / 15
        
        return {
            "zone_name": zone_name,
            "population_estimate": int(base_pop * (0.8 + (zone_index * 0.03))),
            "area_sqkm": 426.51 / 15,
            "key_landmarks": self._get_zone_landmarks(zone_name),
            "connectivity": self._get_zone_connectivity(zone_name),
            "amenities": self._get_zone_amenities(zone_name),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_zone_landmarks(self, zone: str) -> List[str]:
        """Get major landmarks for zone"""
        landmarks_map = {
            "Teynampet": ["Marina Beach", "Santhome Cathedral", "T. Nagar"],
            "Anna Nagar": ["Anna Tower", "Shri Nagar Park", "Anna Nagar Tower Park"],
            "Adyar": ["Adyar River", "Theosophical Society", "Elliot's Beach"],
            "Sholinganallur": ["IT Corridor", "Sholinganallur Lake", "Tech Parks"],
            # Add more as needed
        }
        return landmarks_map.get(zone, ["Local landmarks"])
    
    def _get_zone_connectivity(self, zone: str) -> Dict:
        """Get connectivity information for zone"""
        return {
            "metro_stations": 2,
            "bus_routes": 25,
            "major_roads": ["GST Road", "OMR", "ECR"],
            "nearest_railway": "Chennai Central"
        }
    
    def _get_zone_amenities(self, zone: str) -> Dict:
        """Get amenities in the zone"""
        return {
            "hospitals": 3,
            "schools": 45,
            "parks": 12,
            "shopping_centers": 5,
            "restaurants": 150
        }


class ChennaiSpatialAnalyzer:
    """Analyze spatial relationships in Chennai"""
    
    def __init__(self):
        self.zones = CHENNAI_ZONES
        self.districts = CHENNAI_DISTRICTS
        self.transport = CHENNAI_TRANSPORT
    
    def get_zone_relationships(self, zone: str) -> Dict:
        """Get spatial relationships for a zone"""
        return {
            "zone": zone,
            "adjacent_zones": self._get_adjacent_zones(zone),
            "district_category": self._get_district_category(zone),
            "transport_connectivity": self._get_transport_connectivity(zone),
            "distance_to_center_km": self._estimate_distance_to_center(zone)
        }
    
    def _get_adjacent_zones(self, zone: str) -> List[str]:
        """Get adjacent zones (simplified)"""
        if zone not in self.zones:
            return []
        
        index = self.zones.index(zone)
        adjacent = []
        if index > 0:
            adjacent.append(self.zones[index - 1])
        if index < len(self.zones) - 1:
            adjacent.append(self.zones[index + 1])
        
        return adjacent
    
    def _get_district_category(self, zone: str) -> str:
        """Categorize zone into broader district"""
        for district, areas in self.districts.items():
            if zone in areas:
                return district
        return "Other Chennai"
    
    def _get_transport_connectivity(self, zone: str) -> Dict:
        """Get transport connectivity score"""
        return {
            "metro_access": True if zone in ["Anna Nagar", "Teynampet", "Sholinganallur"] else False,
            "bus_connectivity": "High",
            "road_connectivity": "Good",
            "nearest_airport_km": 15
        }
    
    def _estimate_distance_to_center(self, zone: str) -> float:
        """Estimate distance to city center"""
        # Simplified calculation
        center_zones = ["Teynampet", "Anna Nagar"]
        if zone in center_zones:
            return 2.0
        elif zone in ["Adyar", "Kodambakkam"]:
            return 5.0
        elif zone in ["Sholinganallur", "Ambattur"]:
            return 15.0
        else:
            return 10.0
    
    def get_corridor_analysis(self, corridor: str = "OMR") -> Dict:
        """Analyze a specific corridor"""
        corridor_data = {
            "OMR": {
                "full_name": "Old Mahabalipuram Road",
                "length_km": 45,
                "key_areas": ["Perungudi", "Thoraipakkam", "Sholinganallur", "Kelambakkam"],
                "development_type": "IT Corridor",
                "major_companies": 200,
                "employment": 500000,
                "avg_property_price_growth_yoy": 12
            },
            "ECR": {
                "full_name": "East Coast Road",
                "length_km": 70,
                "key_areas": ["Thiruvanmiyur", "Neelankarai", "Palavakkam", "Mahabalipuram"],
                "development_type": "Residential & Tourism",
                "resorts": 50,
                "beach_access": True,
                "avg_property_price_growth_yoy": 10
            },
            "GST": {
                "full_name": "Grand Southern Trunk Road",
                "length_km": 30,
                "key_areas": ["Guindy", "Chrompet", "Tambaram", "Vandalur"],
                "development_type": "Mixed Industrial & Residential",
                "industrial_units": 500,
                "avg_property_price_growth_yoy": 7
            }
        }
        
        return corridor_data.get(corridor, {"error": "Corridor not found"})
