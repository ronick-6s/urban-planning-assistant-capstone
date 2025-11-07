# Chennai Smart City Agent 🏙️

A sophisticated AI agent with **live demographics and spatial data** for Chennai city, India. This external agent integrates with the main Urban Planning Assistant to provide real-time insights about Chennai's urban landscape.

## 🎯 Overview

The Chennai Smart Agent provides access to:
- **Live Weather & Air Quality Data**
- **Demographics & Population Statistics**
- **Real Estate Market Trends**
- **Transportation Systems (Metro, Bus, Traffic)**
- **Water Supply & Infrastructure Status**
- **Economic Indicators**
- **Environmental & Green Cover Data**
- **Zone-specific Information (15 administrative zones)**
- **Spatial Relationships & Connectivity Analysis**

## 📋 Features

### Real-Time Data Integration
- Weather API integration (OpenWeatherMap)
- Air Quality Index (World Air Quality Index)
- Traffic data (TomTom API ready)
- Mock data fallbacks when APIs unavailable

### Comprehensive Chennai Coverage
- **15 Administrative Zones**: Detailed data for each zone
- **Major Corridors**: OMR (IT), ECR (Residential/Tourism), GST (Mixed)
- **5 District Categories**: North, South, Central, West, OMR/IT Corridor
- **Transportation Networks**: Metro (2 lines, 54 stations), Bus (729 routes), Suburban Rail

### Spatial Intelligence
- Zone connectivity analysis
- Adjacent zone relationships
- Distance calculations
- Transport accessibility scores
- Corridor development analysis

## 🚀 Quick Start

### 1. Installation

```bash
cd chennai_agent
pip install -r requirements.txt
```

### 2. Environment Setup

Add to your `.env` file (optional for live APIs):

```bash
# Optional: For live weather data
OPENWEATHER_API_KEY="your_openweathermap_api_key"

# Optional: For traffic data
TOMTOM_API_KEY="your_tomtom_api_key"

# Optional: For air quality
WAQI_API_KEY="your_waqi_api_key"
```

**Note**: The agent works with mock data if API keys are not provided.

### 3. Run the Agent

```bash
python chennai_agent.py
```

## 📊 Data Categories

### 🌤️ Weather & Environment
- Current temperature, humidity, wind speed
- Air Quality Index (AQI) with PM2.5/PM10
- Green cover and tree density
- Wetlands and water bodies

### 👥 Demographics
- Total population: ~5.5 million (2024 estimate)
- Density: ~12,900 per sq km
- Age distribution
- Literacy rate: 92.5%
- Workforce participation

### 🏠 Real Estate
- 5 price zones (Premium to Emerging)
- Average prices per sq ft
- Year-over-year appreciation
- Market trends and demand levels
- Inventory analysis

### 🚇 Transportation
- **Metro**: 2 lines, 54 stations, 54.05 km network
- **Bus**: 729 routes, 3,411 buses, 3.5M daily passengers
- **Suburban Rail**: 3 major lines
- Traffic conditions by area
- Peak hour analysis

### 💧 Infrastructure
- Water supply: 830 MLD
- Sources: Desalination, Krishna Water, Ground Water
- Reservoir levels (4 major reservoirs)
- Sewage treatment capacity
- Solid waste management

### 💼 Economy
- GDP: $78.6 billion USD
- GDP per capita: $14,800
- Major sectors: Automobiles, IT, Healthcare, Manufacturing
- Employment rate: 94.5%
- Industrial and IT parks

## 🗺️ Chennai Geographic Data

### Administrative Zones (15)
1. Thiruvottiyur
2. Manali
3. Madhavaram
4. Tondiarpet
5. Royapuram
6. Thiru. Vi. Ka. Nagar
7. Ambattur
8. Anna Nagar
9. Teynampet
10. Kodambakkam
11. Valasaravakkam
12. Alandur
13. Adyar
14. Perungudi
15. Sholinganallur

### Development Corridors
- **OMR (Old Mahabalipuram Road)**: 45 km IT corridor with 500,000 employees
- **ECR (East Coast Road)**: 70 km residential & tourism corridor
- **GST (Grand Southern Trunk)**: 30 km mixed industrial & residential

## 💡 Example Queries

### Weather & Environment
```
What's the current weather in Chennai?
What is the air quality like today?
Tell me about Chennai's green cover
What are the water sources for Chennai?
```

### Demographics
```
What is the population of Chennai?
Tell me about Anna Nagar demographics
What is the population density in different zones?
How is Chennai's workforce participation?
```

### Real Estate
```
What are property prices in OMR corridor?
Which are the premium residential areas?
What is the real estate trend in South Chennai?
Compare property prices between Anna Nagar and Adyar
```

### Transportation
```
How is Chennai Metro performing?
What's the traffic like in Central Chennai?
Tell me about bus connectivity
Which zones have metro access?
How do I get around Chennai?
```

### Infrastructure & Services
```
What's the water supply status?
What is Chennai's sewage treatment capacity?
Tell me about Chennai's infrastructure
How many hospitals and schools are there?
```

### Economy
```
What is Chennai's GDP?
What are the major industries in Chennai?
Tell me about employment in Chennai
Which are the top employers?
```

### Zone-Specific
```
Tell me about Adyar zone
What are the key landmarks in Sholinganallur?
Analyze spatial connectivity of Teynampet
Which zones are adjacent to Anna Nagar?
```

### Corridor Analysis
```
Analyze the OMR corridor
Compare OMR and ECR corridors
What is the development type on ECR?
How many IT companies are on OMR?
```

## 🔧 Architecture

### File Structure
```
chennai_agent/
├── chennai_config.py          # Configuration & static data
├── chennai_data_apis.py       # API integrations & data fetchers
├── chennai_tools.py           # LangChain tools
├── chennai_agent.py           # Main agent implementation
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

### Components

**chennai_config.py**
- Geographic boundaries
- Zone definitions
- Transportation systems
- Demographics baseline
- Economic indicators
- Real estate zones

**chennai_data_apis.py**
- `ChennaiDataAPI`: Fetches live/mock data
  - Weather (OpenWeatherMap)
  - Air Quality (WAQI)
  - Demographics (Census + projections)
  - Property trends
  - Infrastructure status
  - Economic indicators
  
- `ChennaiSpatialAnalyzer`: Spatial analysis
  - Zone relationships
  - Connectivity analysis
  - Distance calculations
  - Corridor analysis

**chennai_tools.py**
- 15 LangChain tools for different data categories
- Formatted output with timestamps and sources
- Error handling and fallbacks

**chennai_agent.py**
- LangChain agent with tool calling
- Google Gemini integration
- Interactive command-line interface
- Context-aware responses

## 🔌 API Integration

### Current Integrations
- **OpenWeatherMap**: Live weather data
- **WAQI**: Air quality index
- **TomTom**: Traffic data (ready, needs API key)

### Adding New APIs

1. Add API endpoint to `chennai_config.py`:
```python
API_ENDPOINTS = {
    "your_api": "https://api.example.com/",
}
```

2. Add API key to `.env`:
```
YOUR_API_KEY="your_key_here"
```

3. Implement fetcher in `chennai_data_apis.py`:
```python
def get_your_data(self):
    # API call implementation
    pass
```

4. Create tool in `chennai_tools.py`:
```python
@tool
def get_your_data_tool() -> str:
    """Tool description"""
    data = chennai_api.get_your_data()
    return formatted_output
```

## 📈 Data Sources

### Live APIs
- OpenWeatherMap (weather)
- World Air Quality Index (AQI)
- TomTom Traffic API (ready)

### Static/Projected Data
- Census 2011 (baseline demographics)
- CMDA (Chennai Metropolitan Development Authority)
- Chennai Metro Rail Limited
- MTC (Metropolitan Transport Corporation)
- Chennai Metro Water
- Market analysis reports

### Data Update Frequency
- Weather: Real-time (when API available)
- Air Quality: Hourly updates
- Traffic: Real-time (when API configured)
- Demographics: Annual projections
- Real Estate: Quarterly estimates
- Infrastructure: Monthly status updates

## 🚦 Usage Tips

1. **Specific Questions**: Ask about specific zones or corridors for detailed insights
2. **Comparisons**: Compare multiple zones or corridors for relative analysis
3. **Trends**: Ask about year-over-year changes and growth trends
4. **Data Sources**: Responses include timestamps and data sources
5. **Multi-dimensional**: Combine different aspects (e.g., "property prices and metro access")

## 🔮 Future Enhancements

### Planned Features
- [ ] Real-time traffic integration
- [ ] Property transaction database
- [ ] Smart City IoT sensor data
- [ ] Social media sentiment analysis
- [ ] Predictive analytics for trends
- [ ] Interactive maps and visualizations
- [ ] WhatsApp/Telegram bot interface
- [ ] Voice assistant integration

### Data Expansions
- [ ] Historical trend analysis (5-10 years)
- [ ] Micro-level ward data (200+ wards)
- [ ] Building permit and construction data
- [ ] Event and festival calendar
- [ ] Public safety statistics
- [ ] Healthcare facility real-time capacity

## 🤝 Integration with Main Assistant

The Chennai Smart Agent can be integrated with the main Urban Planning Assistant:

```python
from chennai_agent.chennai_tools import CHENNAI_TOOLS

# Add Chennai tools to main agent
all_tools = MAIN_TOOLS + CHENNAI_TOOLS

# Create combined agent
agent = create_agent(user_id, tools=all_tools)
```

This allows users to:
- Ask general urban planning questions
- Get Chennai-specific live data
- Compare Chennai with other cities
- Apply Chennai data to planning concepts

## 📝 Notes

- Mock data is used when API keys are not configured
- Data is cached for reasonable periods to minimize API calls
- All monetary values in Indian Rupees (₹) unless specified
- Distances in kilometers (km)
- Area in square kilometers (sq km)
- Population density per sq km

## 🆘 Troubleshooting

**API errors**: Check API keys in `.env` file
**Import errors**: Ensure you're in the correct directory and dependencies are installed
**No data returned**: Agent falls back to mock data automatically
**Tool not found**: Check tool names in CHENNAI_TOOLS list

## 📄 License

This Chennai Smart Agent is part of the Urban Planning Assistant project.

## 👨‍💻 Author

Created as an external smart agent module for the Urban Planning Assistant system.

---

**Last Updated**: November 2024
**Chennai Data Version**: 2024
**Agent Version**: 1.0.0
