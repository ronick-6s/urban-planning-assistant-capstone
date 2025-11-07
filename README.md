# Urban Planning Assistant

A sophisticated AI assistant designed for urban planning professionals, administrators, and citizens in Chennai. This system leverages advanced memory management with PostgreSQL 18 and pgvector, live Chennai data integration, role-based access control, and email-based personal cloud storage to provide contextual urban planning assistance.

## SYSTEM Quick Start

1. **Start PostgreSQL**: `pg_ctl -D /Users/ronick/.homebrew/var/postgresql@18 start`
2. **Start Backend**: `cd backend && python3 main.py`
3. **Start Frontend**: `cd frontend && npm run dev` (in new terminal)
4. **Access Application**: Open browser to `http://localhost:5173`
5. **Choose your role**: Citizen, Planner, or Administrator
6. **Enter your email**: Get your personal cloud storage folder
7. **Start planning**: All responses include Chennai context and live data

### Example First Queries
- **Citizens**: "What are the MTC bus routes from Anna Nagar to Marina Beach?"
- **Planners**: "What are the zoning regulations for mixed-use development in Chennai?"
- **Administrators**: "Show me Chennai's budget forecast and infrastructure costs"

## SUCCESS System Features

### MEMORY Advanced Memory Management
- **PostgreSQL 18 with pgvector**: Production-grade vector similarity search (~100x faster)
- **Conversational Memory**: Remembers entire conversation history with context
- **Semantic Search**: Finds relevant past conversations using vector embeddings
- **Session Management**: Maintains context across user sessions
- **HNSW Indexing**: Optimized for fast similarity queries at scale

### CLOUD Personal Storage System
- **Email-Based Folders**: Each user gets a private Dropbox folder based on their email
- **Automatic Report Storage**: All consultation reports saved to user's personal folder
- **Admin Access Control**: Only the user and admin can access individual folders
- **Secure File Sharing**: Private folder links with restricted access
- **Report Generation**: PDF, HTML, and text formats automatically stored and emailed

### GOVERNMENT Chennai Live Data Integration
- **Live Weather**: Current Chennai temperature, humidity, and conditions
- **Air Quality**: Real-time AQI and PM2.5 levels  
- **Traffic Data**: Current traffic conditions and route optimization
- **Government Services**: Live Chennai District Administration information
- **Public Transport**: MTC bus routes, Chennai Metro connectivity
- **Demographic Data**: Population, economic indicators, and city statistics

### ACCESS Role-Based Access Control
- **Citizens**: Public information, transportation, basic planning concepts
- **Planners**: Technical documents, zoning laws, development guidelines
- **Administrators**: Complete access including financial data and strategic information

### INTERFACE Modern Web Application
- **React TypeScript Frontend**: Modern, responsive user interface
- **FastAPI Backend**: High-performance Python API with automatic documentation
- **Dark/Light Theme**: Professional theme system with user preference storage
- **Session History**: Browse and resume previous conversations
- **Real-time Chat**: Instant responses with typing indicators
- **Report Dialog**: Generate comprehensive planning reports with one click

### INFO Hybrid Knowledge System
- **Knowledge Base**: Document retrieval from planning guides and policies
- **Knowledge Graph**: Relationship mapping between urban planning concepts
- **Chennai Integration**: 20+ specialized tools for Chennai-specific queries

## MEMORY Memory Management (PostgreSQL 18)

### Database Schema
```sql
-- Enhanced with pgvector for production performance
CREATE TABLE conversation_memory (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    user_query TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    embedding vector(384) NOT NULL,  -- pgvector for fast similarity search
    timestamp TIMESTAMP WITHOUT TIME ZONE
);

-- High-performance HNSW index
CREATE INDEX conversation_memory_embedding_idx 
ON conversation_memory USING hnsw (embedding vector_cosine_ops);
```

### Memory Features
- **Persistent Storage**: All conversations stored in PostgreSQL
- **Context Retrieval**: Relevant past conversations enhance responses
- **User Isolation**: Each user's conversations remain separate
- **Semantic Similarity**: Vector embeddings enable contextual memory recall
- **Performance Optimized**: pgvector provides enterprise-grade search speed

## CLOUD Personal Cloud Storage

### Email-Based User Folders
- **Individual Private Folders**: Each user email gets a unique Dropbox folder
- **Automatic Creation**: Folders created automatically on first use
- **Access Control**: Only the user and admin have access
- **Report Storage**: All consultation reports automatically saved to user's folder
- **File Organization**: Reports organized by date and type within user folders

### Folder Structure(Sample)
```
/UrbanPlanningReports/
├── users/
│   ├── john_at_email_com/
│   │   ├── planning_report_20241107_143022.pdf
│   │   ├── planning_report_20241107_143022.html
│   │   └── welcome_report_20241107_143022.txt
│   ├── jane_planner_at_city_gov/
│   │   ├── planning_report_20241107_150033.pdf
│   │   └── zoning_analysis_20241107_150134.html
│   └── admin_at_urbanplanning_studio/
└── users_registry.json
```

### Cloud Features
- **Automatic Report Generation**: PDF, HTML, and text formats
- **Email Delivery**: Reports emailed to user's address with Dropbox links
- **Admin Dashboard**: Admin can view all user folders and manage access
- **Secure Sharing**: Private folder links with restricted access permissions
- **File Retention**: Configurable retention policies for storage management

### API Endpoints for Cloud Management
```
POST /chat                                    # Chat with user_email parameter
POST /report                                  # Generate reports to user folder
GET /user-folders/{email}/reports            # List user's reports
GET /admin/users                             # List all users (admin only)
POST /admin/user-folders/{email}/create     # Create user folder (admin)
DELETE /admin/user-folders/{email}          # Delete user folder (admin)
```

### PostgreSQL Management Commands
```bash
# Start PostgreSQL
pg_ctl -D /Users/ronick/.homebrew/var/postgresql@18 start

# Stop PostgreSQL  
pg_ctl -D /Users/ronick/.homebrew/var/postgresql@18 stop

# Check Status
pg_ctl -D /Users/ronick/.homebrew/var/postgresql@18 status

# Connect to Database
psql -d urban_planning_db
```

## CITY Chennai Smart Agent

### 20 Specialized Tools Available

#### WEATHER Live API Integration (5 tools)
1. **Weather Data**: Real-time temperature, humidity, conditions
2. **Air Quality**: Live AQI, PM2.5, pollution levels
3. **Traffic Conditions**: Current traffic data and route optimization
4. **Economic Indicators**: GDP, employment, business statistics
5. **Population Analytics**: Demographics and growth projections

#### GOVERNMENT Government Website Integration (8 tools)
6. **District Administration**: Official Chennai government information
7. **Civic Services**: Public services, amenities, and facilities
8. **Tourism Information**: Cultural sites, attractions, events
9. **Transportation Hub**: Comprehensive Chennai transport data
10. **Business Directory**: Economic zones, industrial areas
11. **Educational Institutions**: Schools, colleges, research centers
12. **Healthcare Facilities**: Hospitals, clinics, medical services
13. **Emergency Services**: Helplines, disaster management, safety

#### MAP Analytics & Spatial Tools (7 tools)
14. **Spatial Analysis**: Geographic data processing and mapping
15. **Route Optimization**: Best path calculation for transportation
16. **Demographic Analysis**: Population distribution and trends
17. **Economic Modeling**: Financial forecasting and budget analysis
18. **Infrastructure Assessment**: Utility networks and capacity planning
19. **Development Tracking**: Project monitoring and progress updates
20. **Performance Metrics**: KPI tracking and system benchmarks

### Government Integration
- **Direct Data Access**: Live scraping from Chennai District Administration website
- **Official Information**: Authenticated government data and announcements
- **Real-time Updates**: Current notifications, schemes, and programs

## ACCESS Role-Based Access

### USER Citizens
- Public transportation information and route planning
- Basic urban planning concepts and community development
- Government services, civic amenities, and public facilities
- Environmental data (weather, air quality) and safety information
- Personal cloud folder for storing consultation reports

### DEVELOPMENT Urban Planners
- All citizen-level information plus:
- Technical planning documents, zoning regulations, and development codes
- Professional planning methodologies and best practices
- Infrastructure planning, housing policy, and land use management
- Advanced report generation and analysis tools

### ADMIN Administrators  
- All citizen and planner information plus:
- Financial data, budget analysis, and administrative metrics
- Strategic planning documents and policy development
- User management and cloud storage administration
- Special commands: `financial:list all`, `financial:show [metric]`
- Access to all user folders and system administration tools

## SYSTEM Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+ and npm
- PostgreSQL 18 with pgvector extension
- Dropbox Developer Account (for cloud storage)
- Homebrew (for macOS dependencies)

### Installation Steps
```bash
# 1. Install PostgreSQL 18 and pgvector
brew install postgresql@18 pgvector

# 2. Start PostgreSQL
pg_ctl -D /Users/ronick/.homebrew/var/postgresql@18 start

# 3. Create database
createdb urban_planning_db

# 4. Enable pgvector extension
psql -d urban_planning_db -c "CREATE EXTENSION vector;"

# 5. Setup Backend
cd backend
pip3 install -r requirements.txt

# 6. Setup Frontend
cd ../frontend
npm install

# 7. Configure Environment
# Copy .env.example to .env and fill in your API keys:
# - Dropbox credentials
# - iCloud email settings
# - API keys for weather, traffic, etc.

# 8. Run the application
# Terminal 1 (Backend):
cd backend && python3 main.py

# Terminal 2 (Frontend):
cd frontend && npm run dev
```

### Environment Configuration
Create a `.env` file in the backend directory with:
```bash
# Dropbox Configuration
DROPBOX_CLIENT_ID=your_dropbox_app_key
DROPBOX_CLIENT_SECRET=your_dropbox_app_secret  
DROPBOX_ACCESS_TOKEN=your_access_token
DROPBOX_REFRESH_TOKEN=your_refresh_token
ADMIN_EMAIL=your_admin_email@domain.com

# iCloud Email (for report delivery)
ICLOUD_EMAIL=your_email@icloud.com
ICLOUD_APP_PASSWORD=your_app_specific_password

# API Keys
GOOGLE_API_KEY=your_google_api_key
OPENWEATHER_API_KEY=your_openweather_key
TOMTOM_API_KEY=your_tomtom_key
```

### User Access
The system uses role-based access without traditional login:
- **Citizens**: Basic public information access
- **Planners**: Enhanced technical access  
- **Administrators**: Full system access including user management

## DEVELOPMENT System Architecture

**Frontend Components:**
- **React TypeScript**: Modern component-based UI with type safety
- **Session Management**: Browse and resume conversation history
- **Email Integration**: User folder assignment and validation
- **Report Generation**: One-click comprehensive report creation

**Backend Components:**
- **FastAPI Framework**: High-performance async Python API
- **User Folder Manager**: Email-based Dropbox folder creation and management
- **Memory System**: PostgreSQL 18 with pgvector for enterprise performance  
- **Access Control**: Role-based permissions and content filtering
- **Knowledge Base**: MongoDB with hybrid retrieval (RAG)
- **Knowledge Graph**: Neo4j for relationship mapping
- **Chennai Integration**: 20 specialized tools for local data

**Cloud Integration:**
- **Dropbox API**: Personal folder management with OAuth2 refresh tokens
- **iCloud SMTP**: Email delivery for reports and notifications

**External Integrations:**
- **OpenWeather API**: Real-time weather data
- **World Air Quality Index**: Pollution monitoring
- **TomTom Traffic API**: Route optimization
- **Chennai Government**: Official district administration data

### Data Flow
1. **User Access** → Email validation → Personal folder creation → Role selection
2. **User Input** → Role validation → Query enhancement → Memory context retrieval
3. **Agent Processing** → Tool selection → Data gathering → Chennai integration
4. **Response Generation** → Context application → Memory storage → Report generation
5. **Output Delivery** → Clean formatting → Cloud storage → Email delivery

### Frontend Architecture
```
src/
├── App.tsx              # Main application component
├── VogueApp.css         # Theme system and styling
├── components/          # Reusable UI components
├── types/               # TypeScript type definitions
└── utils/               # Helper functions and utilities
```

### Backend Architecture
```
backend/
├── main.py                    # FastAPI application entry point
├── dropbox_user_manager.py    # Email-based folder management
├── enhanced_dropbox_client.py # Dropbox API with token refresh
├── postgres_memory_manager.py # Memory system with pgvector
├── access_control.py          # Role-based permissions
├── chennai_agent/             # 20 Chennai-specific tools
├── kb_manager.py              # Knowledge base operations
└── config.py                  # System configuration
```

## MAP Database Management

### PostgreSQL Configuration
- **Database**: urban_planning_db
- **Host**: localhost (127.0.0.1)
- **Port**: 5432
- **Extensions**: pgvector for vector operations

### Memory Table Structure
- **Conversations**: User queries and assistant responses with session tracking
- **Vector Embeddings**: 384-dimensional vectors for similarity search
- **Session Management**: User sessions and conversation history
- **Performance**: HNSW indexing for sub-linear search complexity

### Cloud Storage Management
- **User Registry**: JSON file tracking all user folders and metadata
- **Automatic Cleanup**: Configurable retention policies for old reports
- **Access Logs**: Admin visibility into folder access and usage patterns

### Backup and Maintenance
```bash
# Backup database
pg_dump urban_planning_db > backup_$(date +%Y%m%d).sql

# Restore database  
psql urban_planning_db < backup_20241105.sql

# Check database size
psql -d urban_planning_db -c "SELECT pg_size_pretty(pg_database_size('urban_planning_db'));"
```

### INFO Usage Flow
```
1. User opens web application (http://localhost:5173)
2. Selects role: Citizen / Planner / Administrator
3. Enters email address for personal folder creation
4. System creates private Dropbox folder automatically
5. User begins conversation with context-aware AI assistant
6. All responses include live Chennai data and local context
7. Reports generated on demand, saved to personal folder
8. Admin can manage all users and folders through API endpoints
```

---

*For detailed prompt examples and query patterns, see [PROMPTS_GUIDE.md](PROMPTS_GUIDE.md)*