# Chennai Smart Agent - API Setup Guide

This guide will help you set up all the real APIs and data sources for the Chennai Smart Agent.

## 🔑 Required API Keys

### 1. OpenWeatherMap API (Weather Data) ✅ YOU HAVE THIS

**What it provides**: Real-time weather data for Chennai (temperature, humidity, wind, conditions)

**Setup Steps**:
1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Navigate to API Keys section
4. Copy your API key
5. Add to `.env` file:
   ```bash
   OPENWEATHER_API_KEY="your_api_key_here"
   ```

**Free Tier**: 60 calls/minute, 1,000,000 calls/month

---

### 2. WAQI API (Air Quality Data) ✅ YOU HAVE THIS

**What it provides**: Real-time Air Quality Index (AQI) for Chennai with PM2.5, PM10, O3, NO2 levels

**Setup Steps**:
1. Go to https://aqicn.org/data-platform/token/
2. Request a free API token
3. Verify your email
4. Copy the token
5. Add to `.env` file:
   ```bash
   WAQI_API_KEY="your_token_here"
   ```

**Free Tier**: Unlimited for non-commercial use

**API Endpoint Used**:
```
https://api.waqi.info/feed/chennai/?token=YOUR_TOKEN
```

---

### 3. TomTom Traffic API (Traffic Data) ✅ YOU HAVE THIS

**What it provides**: Real-time traffic flow, congestion levels, travel times for Chennai

**Setup Steps**:
1. Go to https://developer.tomtom.com/
2. Create a free account
3. Go to Dashboard → Your Apps
4. Create a new app
5. Copy the API Key (Consumer Key)
6. Add to `.env` file:
   ```bash
   TOMTOM_API_KEY="your_api_key_here"
   ```

**Free Tier**: 2,500 transactions/day

**APIs Used**:
- Traffic Flow API: Real-time traffic speed and congestion
- Traffic Incidents API: Accidents, road works, closures

---

## 📊 Census Data Setup ✅ YOU HAVE THIS

**What it provides**: Detailed demographic data by zone/ward

**Setup Steps**:

1. **Prepare your census dataset** in CSV or Excel format with columns like:
   ```
   zone, population, households, literacy_rate, sex_ratio, area_sqkm, etc.
   ```

2. **Expected CSV format example**:
   ```csv
   zone,population,households,literacy_rate,sex_ratio,area_sqkm
   Anna Nagar,350000,87500,95.2,995,28.5
   Adyar,280000,70000,96.8,1005,24.3
   Sholinganallur,420000,105000,88.5,980,35.7
   ...
   ```

3. **Save the file** in the `chennai_agent/data/` directory:
   ```bash
   mkdir -p chennai_agent/data
   # Copy your census file here
   ```

4. **Update the agent initialization** in `chennai_agent.py`:
   ```python
   # Add census file path
   CENSUS_FILE = "data/chennai_census_2024.csv"
   
   api = ChennaiDataAPI(census_file_path=CENSUS_FILE)
   ```

---

## 🕷️ Web Scraping Sources (No API Keys Needed)

These sources are scraped automatically when APIs are not available:

### 1. Chennai Metro Water
- **Source**: https://www.chennaimetrowater.gov.in/
- **Data**: Reservoir levels, water supply status
- **Status**: Automated scraping with fallback

### 2. Chennai Corporation
- **Source**: https://www.chennaicorporation.gov.in/
- **Data**: Zone information, civic amenities
- **Status**: Automated scraping with fallback

### 3. Chennai Metro Rail
- **Source**: https://www.chennaimetrorail.org/
- **Data**: Ridership statistics, operational status
- **Status**: Automated scraping with fallback

### 4. Property Websites (MagicBricks, 99acres)
- **Sources**: 
  - https://www.magicbricks.com/
  - https://www.99acres.com/
- **Data**: Property prices by area
- **Status**: Automated scraping (requires careful rate limiting)
- **Note**: These sites may block frequent requests. Consider adding delays.

---

## 🔧 Complete `.env` File Example

Create or update `/Users/ronick/Documents/curriculum/urban_planning_assistant/.env`:

```bash
# Existing keys
GOOGLE_API_KEY="your_google_api_key"
LANGCHAIN_API_KEY="your_langchain_key"
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_PROJECT="urban-planning-assistant"

MONGO_ATLAS_URI="your_mongodb_uri"
MONGO_DB_NAME="urban_planning_db"
MONGO_COLLECTION_NAME="documents"

NEO4J_AURA_URI="your_neo4j_uri"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your_neo4j_password"

# Chennai Agent API Keys
OPENWEATHER_API_KEY="your_openweather_key"
TOMTOM_API_KEY="your_tomtom_key"
WAQI_API_KEY="your_waqi_token"
```

---

## ✅ Testing Your Setup

### 1. Test Individual APIs

```bash
cd chennai_agent
python
```

```python
from chennai_data_apis import ChennaiDataAPI

# Initialize with census data (optional)
api = ChennaiDataAPI(census_file_path="data/census.csv")

# Test weather
weather = api.get_weather_data()
print(weather)
# Should show "source": "OpenWeatherMap API (Live)" if working

# Test air quality
aqi = api.get_air_quality()
print(aqi)
# Should show "source": "WAQI API (Live)" if working

# Test traffic
traffic = api.get_traffic_data()
print(traffic)
# Should show "source": "TomTom Traffic API (Live)" if working

# Test demographics with census
demographics = api.get_demographic_trends()
print(demographics)
# Should show "source": "Census Dataset" if CSV loaded
```

### 2. Run the Demo

```bash
python demo.py
```

Check the output for:
- ✅ "Live" status indicators
- ⚠️ Warning messages if API keys are missing
- ❌ Error messages if something is wrong

### 3. Run Full Agent

```bash
python chennai_agent.py
```

Try queries like:
```
What's the current weather in Chennai?
What is the air quality today?
What's the traffic like right now?
What is the population from census data?
```

---

## 📈 Data Source Priority

The agent uses this priority for data sources:

1. **Live APIs** (if keys configured)
   - OpenWeatherMap for weather
   - WAQI for air quality
   - TomTom for traffic

2. **Census Dataset** (if CSV provided)
   - Demographics by zone
   - Population statistics

3. **Web Scraping** (automated fallback)
   - Reservoir levels
   - Metro ridership
   - Property prices
   - Civic amenities

4. **Estimated Data** (final fallback)
   - Seasonal estimates
   - Historical averages
   - Baseline values

---

## 🚨 Troubleshooting

### Problem: API returns errors

**Solutions**:
1. Check API key is correct in `.env`
2. Verify API key is active (not expired)
3. Check free tier limits not exceeded
4. Test API directly with curl:
   ```bash
   curl "https://api.openweathermap.org/data/2.5/weather?lat=13.0827&lon=80.2707&appid=YOUR_KEY"
   ```

### Problem: Census data not loading

**Solutions**:
1. Check file path is correct
2. Verify CSV format matches expected columns
3. Check for encoding issues (use UTF-8)
4. Look for error messages in console

### Problem: Web scraping fails

**Solutions**:
1. Check internet connection
2. Websites may have changed structure
3. May be blocked by rate limiting
4. Agent automatically falls back to estimates

### Problem: "Mock Data" showing instead of live

**Solutions**:
1. Ensure API keys are in `.env` file
2. Restart the agent after adding keys
3. Check if `.env` is in correct directory
4. Verify environment variables loaded:
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()
   print(os.getenv("OPENWEATHER_API_KEY"))
   ```

---

## 📊 Monitoring API Usage

### OpenWeatherMap
- Dashboard: https://home.openweathermap.org/api_keys
- Shows: Calls made, remaining quota

### WAQI
- No dashboard for free tier
- Monitor in code with timestamps

### TomTom
- Dashboard: https://developer.tomtom.com/user/me/apps
- Shows: Transactions per day

---

## 🔄 Updating Data Sources

### To add new data sources:

1. **Add scraper** to `chennai_scrapers.py`
2. **Integrate** in `chennai_data_apis.py`
3. **Create tool** in `chennai_tools.py`
4. **Test** with demo script
5. **Document** in this guide

---

## 💡 Best Practices

1. **Rate Limiting**: Add delays between scraping requests
   ```python
   import time
   time.sleep(1)  # Wait 1 second between requests
   ```

2. **Caching**: Cache API responses for 5-10 minutes
   ```python
   from functools import lru_cache
   from datetime import datetime, timedelta
   ```

3. **Error Handling**: Always have fallbacks
   ```python
   try:
       live_data = api.fetch()
   except:
       fallback_data = estimates()
   ```

4. **API Key Security**: Never commit `.env` to git
   ```bash
   echo ".env" >> .gitignore
   ```

---

## 📞 Support & Resources

- **OpenWeatherMap Docs**: https://openweathermap.org/api
- **WAQI Docs**: https://aqicn.org/api/
- **TomTom Docs**: https://developer.tomtom.com/traffic-api/documentation
- **Census India**: https://censusindia.gov.in/

---

**Last Updated**: November 2024  
**Status**: Production Ready ✅
