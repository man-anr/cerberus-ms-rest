# Cerberus MS REST API

A Django REST Framework API service for the Cerberus security platform, providing comprehensive threat modeling and data flow diagram (DFD) management capabilities with Neo4j graph database integration.

## Overview

The Cerberus MS REST API is the backend service that powers the Cerberus security platform. It provides a robust REST API for managing threat models, data flow diagrams, security components, and threat analysis. Built with Django REST Framework and Neo4j, it offers powerful graph-based threat modeling capabilities.

## Features

### 🎯 **Core Functionality**
- **Threat Modeling**: Complete STRIDE threat analysis and management
- **Data Flow Diagrams**: Visual representation of system architecture
- **Component Management**: Process, DataStore, and ExternalEntity components
- **Trust Boundaries**: Security boundary definition and management
- **User Management**: Multi-user project collaboration
- **Bulk Operations**: Efficient bulk data synchronization

### 🔧 **Technical Features**
- **Django REST Framework**: Robust API framework with automatic documentation
- **Neo4j Integration**: Graph database for complex relationship modeling
- **OpenAPI Documentation**: Auto-generated API documentation with Swagger UI
- **CORS Support**: Cross-origin resource sharing for web applications
- **Docker Support**: Containerized deployment with health checks
- **Graph Visualization**: Cypher queries for comprehensive diagram analysis

### 🛡️ **Security Features**
- **Threat Analysis**: STRIDE methodology implementation
- **Risk Assessment**: Criticality and risk level management
- **Mitigation Tracking**: Strategy management and status tracking
- **Trust Boundary Analysis**: Security control and boundary management
- **Cross-Boundary Flow Detection**: High-risk data flow identification

## API Endpoints

### Projects
- `GET /api/projects/` - List all projects
- `POST /api/projects/` - Create new project
- `GET /api/projects/{key}/` - Get project details
- `PUT /api/projects/{key}/` - Update project
- `DELETE /api/projects/{key}/` - Delete project

### Diagrams
- `GET /api/projects/{project_key}/diagrams/` - List project diagrams
- `POST /api/projects/{project_key}/diagrams/` - Create new diagram
- `GET /api/diagrams/{key}/` - Get diagram details
- `PUT /api/diagrams/{key}/` - Update diagram
- `DELETE /api/diagrams/{key}/` - Delete diagram

### Components
- `GET /api/diagrams/{diagram_key}/components/` - List diagram components
- `POST /api/diagrams/{diagram_key}/components/` - Create component
- `GET /api/components/{key}/` - Get component details
- `PUT /api/components/{key}/` - Update component
- `DELETE /api/components/{key}/` - Delete component

### Threats
- `GET /api/diagrams/{diagram_key}/threats/` - List diagram threats
- `POST /api/diagrams/{diagram_key}/threats/` - Create threat
- `GET /api/threats/{key}/` - Get threat details
- `PUT /api/threats/{key}/` - Update threat
- `DELETE /api/threats/{key}/` - Delete threat

### Trust Boundaries
- `GET /api/diagrams/{diagram_key}/trust-boundaries/` - List trust boundaries
- `POST /api/diagrams/{diagram_key}/trust-boundaries/` - Create trust boundary
- `GET /api/trust-boundaries/{key}/` - Get trust boundary details
- `PUT /api/trust-boundaries/{key}/` - Update trust boundary
- `DELETE /api/trust-boundaries/{key}/` - Delete trust boundary

### Bulk Operations
- `POST /api/diagrams/{diagram_key}/bulk-sync/` - Bulk synchronize diagram data
- `GET /api/diagrams/{diagram_key}/export/` - Export complete diagram
- `POST /api/diagrams/{diagram_key}/import/` - Import diagram data

### Health & Documentation
- `GET /api/health/` - Health check endpoint
- `GET /api/schema/` - OpenAPI schema
- `GET /api/docs/` - Swagger UI documentation

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Neo4j database (see [cerberus-graph-db](../cerberus-graph-db) for setup)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/cerberus-ms-rest.git
cd cerberus-ms-rest
```

2. **Set up environment:**
```bash
# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
# Create .env file
cp .env.example .env
# Edit .env with your Neo4j connection details
```

4. **Run database migrations:**
```bash
python manage.py migrate
```

5. **Start the development server:**
```bash
python manage.py runserver
```

### Docker Deployment

1. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

2. **Access the API:**
- API: http://localhost:8000/api/
- Documentation: http://localhost:8000/api/docs/
- Health Check: http://localhost:8000/api/health/

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Neo4j Configuration
NEO4J_BOLT_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password1

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Neo4j Connection

The API connects to Neo4j using the following configuration:

```python
# In settings.py
NEOMODEL_NEO4J_BOLT_URL = os.getenv('NEO4J_BOLT_URL', 'bolt://localhost:7687')
NEOMODEL_NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEOMODEL_NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password1')
```

## Data Models

### Core Entities

#### Project
```python
{
  "key": "string",           # Unique project identifier
  "name": "string",          # Project name
  "user_id": "string",       # Legacy user reference
  "meta": {},                # Additional metadata
  "owner": {                 # Project owner
    "key": "string",
    "email": "string",
    "name": "string",
    "role": "string"
  },
  "members": []              # Project members
}
```

#### Diagram
```python
{
  "key": "string",           # Unique diagram identifier
  "name": "string",          # Diagram name
  "meta": {},                # Additional metadata
  "project_key": "string"    # Parent project
}
```

#### Component (DFDNode)
```python
{
  "key": "string",           # Unique component identifier
  "name": "string",          # Component name
  "description": "string",   # Component description
  "dfd_level": 0,            # DFD level (0, 1, 2, etc.)
  "zone": "string",          # Network zone
  "owner": "string",         # Component owner
  "criticality": "medium",   # "low", "medium", "high", "critical"
  "pos_x": 0.0,             # X position on canvas
  "pos_y": 0.0,             # Y position on canvas
  "width": 120.0,           # Component width
  "height": 72.0,           # Component height
  "ui": {}                  # UI properties
}
```

#### Threat
```python
{
  "key": "string",                    # Unique threat identifier
  "name": "string",                   # Threat name
  "description": "string",            # Threat description
  "threat_type": "string",            # STRIDE: "spoofing", "tampering", etc.
  "criticality": "medium",            # "low", "medium", "high", "critical"
  "status": "string",                 # "identified", "analyzed", "mitigated", "accepted"
  "impact": "string",                 # Impact description
  "likelihood": "string",             # Likelihood assessment
  "risk_level": "string",             # Overall risk level
  "mitigation_strategies": [],        # List of mitigation strategies
  "owner": "string",                  # Threat owner
  "assigned_to": "string",            # Assigned person/team
  "identified_date": "string",        # ISO date string
  "due_date": "string",               # ISO date string
  "notes": "string",                  # Additional notes
  "pos_x": 0.0,                      # X position on canvas
  "pos_y": 0.0,                      # Y position on canvas
  "width": 120.0,                    # Threat node width
  "height": 80.0                     # Threat node height
}
```

#### Trust Boundary
```python
{
  "key": "string",                    # Unique boundary identifier
  "name": "string",                   # Boundary name
  "description": "string",            # Boundary description
  "boundary_type": "string",          # "network", "process", "data", "user", "system"
  "criticality": "medium",            # "low", "medium", "high", "critical"
  "security_controls": [],            # List of security controls
  "owner": "string",                  # Boundary owner
  "notes": "string",                  # Additional notes
  "pos_x": 0.0,                      # X position on canvas
  "pos_y": 0.0,                      # Y position on canvas
  "width": 200.0,                    # Boundary width
  "height": 150.0                    # Boundary height
}
```

### Component Types

#### Process
```python
{
  # Inherits all DFDNode properties
  "tech": "string"           # Technology stack
}
```

#### External Entity
```python
{
  # Inherits all DFDNode properties
  "actor_type": "string"     # "user", "system", "service"
}
```

#### Data Store
```python
{
  # Inherits all DFDNode properties
  "store_type": "string",        # "database", "file", "cache"
  "technology": "string",        # Technology used
  "retention_days": 0,           # Data retention period
  "encryption_at_rest": true,    # Encryption status
  "backups_enabled": true,       # Backup configuration
  "rto_hours": 4.0,             # Recovery Time Objective
  "rpo_hours": 1.0              # Recovery Point Objective
}
```

## API Usage Examples

### Create a Project
```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "key": "my_security_project",
    "name": "My Security Project",
    "meta": {"description": "A comprehensive security analysis"}
  }'
```

### Create a Diagram
```bash
curl -X POST http://localhost:8000/api/projects/my_security_project/diagrams/ \
  -H "Content-Type: application/json" \
  -d '{
    "key": "dfd_v1",
    "name": "Data Flow Diagram v1",
    "meta": {"version": "1.0"}
  }'
```

### Add a Component
```bash
curl -X POST http://localhost:8000/api/diagrams/dfd_v1/components/ \
  -H "Content-Type: application/json" \
  -d '{
    "key": "web_server",
    "name": "Web Server",
    "type": "process",
    "description": "Nginx web server",
    "criticality": "high",
    "tech": "nginx",
    "pos_x": 100.0,
    "pos_y": 100.0
  }'
```

### Add a Threat
```bash
curl -X POST http://localhost:8000/api/diagrams/dfd_v1/threats/ \
  -H "Content-Type: application/json" \
  -d '{
    "key": "sql_injection",
    "name": "SQL Injection",
    "threat_type": "tampering",
    "criticality": "high",
    "status": "identified",
    "impact": "Data corruption and unauthorized access",
    "likelihood": "medium",
    "risk_level": "high",
    "mitigation_strategies": ["Input validation", "Prepared statements"],
    "owner": "security_team",
    "assigned_to": "dev_team"
  }'
```

### Bulk Synchronize Diagram
```bash
curl -X POST http://localhost:8000/api/diagrams/dfd_v1/bulk-sync/ \
  -H "Content-Type: application/json" \
  -d '{
    "components": [
      {
        "key": "web_server",
        "name": "Web Server",
        "type": "process",
        "pos_x": 100.0,
        "pos_y": 100.0
      }
    ],
    "threats": [
      {
        "key": "sql_injection",
        "name": "SQL Injection",
        "threat_type": "tampering",
        "criticality": "high"
      }
    ],
    "trust_boundaries": [
      {
        "key": "dmz_zone",
        "name": "DMZ Zone",
        "boundary_type": "network",
        "criticality": "high"
      }
    ]
  }'
```

## Cypher Queries

The API integrates with Neo4j and provides powerful graph-based threat modeling capabilities. See [cypher_queries.md](cypher_queries.md) for comprehensive query examples.

### Example: Get Complete Diagram
```cypher
MATCH (d:Diagram {key: "dfd_v1"})
OPTIONAL MATCH (d)-[:HAS_ELEMENT]->(n:DFDNode)
OPTIONAL MATCH (d)-[:HAS_THREAT]->(t:ThreatNode)
OPTIONAL MATCH (d)-[:HAS_TRUST_BOUNDARY]->(tb:TrustBoundaryNode)
RETURN d, collect(n) as components, collect(t) as threats, collect(tb) as trust_boundaries
```

### Example: Threat Analysis
```cypher
MATCH (t:ThreatNode)-[:THREATENS]->(c:DFDNode)
WHERE t.criticality = "high"
RETURN t.name, t.threat_type, collect(c.name) as affected_components
ORDER BY t.criticality DESC
```

## Development

### Project Structure
```
cerberus-ms-rest/
├── cerberus_ms_rest/          # Django project settings
│   ├── settings.py            # Configuration
│   ├── urls.py               # URL routing
│   └── wsgi.py               # WSGI application
├── dfd/                      # Main application
│   ├── models.py             # Neo4j models
│   ├── views.py              # API views
│   ├── serializers.py        # Data serializers
│   ├── urls.py               # API endpoints
│   └── exceptions.py         # Custom exceptions
├── create_complete_diagram.py # Example diagram creation
├── cypher_queries.md         # Query documentation
├── docker-compose.yaml       # Docker configuration
├── dockerfile               # Docker image
└── requirements.txt         # Python dependencies
```

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Deployment

### Production Settings

1. **Update settings.py:**
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECRET_KEY = 'your-production-secret-key'
```

2. **Use environment variables:**
```bash
export NEO4J_BOLT_URL=bolt://your-neo4j-server:7687
export NEO4J_PASSWORD=your-secure-password
```

3. **Deploy with Docker:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Health Monitoring

The API provides health check endpoints for monitoring:

- `GET /api/health/` - Basic health check
- `GET /api/health/detailed/` - Detailed system status

## Integration

### With Cerberus Platform

This API integrates with other Cerberus components:

- **cerberus-graph-db**: Neo4j database backend
- **cerberus** (Flutter): Frontend application
- **cerberus-gai-agents**: AI-powered threat analysis
- **cerberus-ms-guardrail**: Security policy enforcement

### API Clients

#### Python Client Example
```python
import requests

class CerberusAPI:
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
    
    def create_project(self, key, name):
        response = requests.post(f"{self.base_url}/projects/", json={
            "key": key,
            "name": name
        })
        return response.json()
    
    def get_diagram(self, diagram_key):
        response = requests.get(f"{self.base_url}/diagrams/{diagram_key}/")
        return response.json()
```

#### JavaScript Client Example
```javascript
class CerberusAPI {
    constructor(baseUrl = 'http://localhost:8000/api') {
        this.baseUrl = baseUrl;
    }
    
    async createProject(key, name) {
        const response = await fetch(`${this.baseUrl}/projects/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key, name })
        });
        return response.json();
    }
    
    async getDiagram(diagramKey) {
        const response = await fetch(`${this.baseUrl}/diagrams/${diagramKey}/`);
        return response.json();
    }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is part of the Cerberus security platform. Please refer to the main Cerberus repository for licensing information.

## Support

For issues and questions:
- Create an issue in this repository
- Check the Cerberus platform documentation
- Review the API documentation at `/api/docs/`

## Version History

- **v1.0.0**: Initial release
  - Django REST Framework API
  - Neo4j integration with neomodel
  - Complete threat modeling capabilities
  - Docker support
  - OpenAPI documentation
  - Bulk operations support
