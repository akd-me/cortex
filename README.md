## License

Cortex is licensed under the Apache License 2.0 with the Commons Clause restriction.
This means you can use, modify, and self-host Cortex for free for personal or internal purposes.

Commercial use — including offering Cortex as a hosted service, selling access to it,
or integrating it into a paid product — requires a commercial license from DEV.


# Cortex Context Manager

A Docker-based application that stores context information locally and exposes a Model Context Protocol (MCP) server for integration with AI development tools like Cursor and Claude Desktop.

## Goal: "Bring Your Own Context"

Cortex provides the following capabilities:
- Local storage and management of context information in a Docker container
- Advanced search functionality with multiple search modes
- Project-based organization of context items
- MCP server integration for AI development tools
- Complete data control with persistent Docker volumes

## Architecture

```
cortex/
├── app/                    # FastAPI backend
│   ├── models/            # Pydantic models (LanceDB-based)
│   ├── routes/            # API endpoints (enhanced with semantic search)
│   ├── services/          # Business logic (LanceDB + embeddings)
│   ├── database/          # LanceDB connection & management
│   ├── servers/           # MCP server implementation
│   ├── middleware/        # CORS and other middleware
│   ├── helpers/           # Utility functions
│   ├── exceptions/        # Custom exceptions
│   ├── assets/            # Frontend build assets
│   └── main.py           # FastAPI application
├── akd.dev.fe/           # Vue.js frontend
│   ├── src/
│   │   ├── components/   # Vue components (Header, Sidebar)
│   │   ├── views/        # Page views (Dashboard, Contexts, Projects, Settings)
│   │   ├── router/       # Vue Router config
│   │   ├── stores/       # Pinia state management
│   │   ├── types/        # TypeScript type definitions
│   │   └── styles/       # Global CSS styles
│   ├── dist/             # Built frontend assets
│   └── package.json      # Frontend dependencies
├── scripts/              # Development scripts
│   └── docker-dev.sh     # Docker development script
├── docker-compose.dev.yml # Docker Compose configuration
├── Dockerfile.dev        # Docker development image
└── requirements.txt      # Python dependencies
```

## Features

### Core Functionality
- **Vector Database Storage**: LanceDB vector database with embeddings stored in persistent Docker volumes
- **Context Management**: Full CRUD operations for context items with automatic embedding generation
- **Project Organization**: Hierarchical organization of contexts by projects
- **Advanced Search**: Multiple search modes including semantic, keyword, and hybrid search
- **Semantic Search**: AI-powered vector similarity search using sentence-transformers
- **Tag System**: Flexible categorization system for context items
- **Data Persistence**: All data persists across container restarts

### Advanced Search Capabilities
- **Semantic Search**: Meaning-based context discovery using AI embeddings (384-dimensional vectors)
- **Keyword Search**: Traditional text-based search through titles and content
- **Hybrid Search**: Intelligent combination of semantic and keyword search with configurable weights
- **Search Modes**: Flexible selection between semantic, keyword, or hybrid search approaches
- **Advanced Filtering**: Filter results by project, content type, tags, and active status
- **Performance Optimization**: Sub-second search results with detailed execution time tracking

### MCP Server
- **FastMCP Integration**: Modern MCP server implementation using the FastMCP framework
- **HTTP Protocol Support**: Full HTTP communication protocol compatibility
- **Comprehensive Tool Set**: Seven MCP tools for complete context management:
  - `store_context` - Store new context information with metadata
  - `retrieve_context` - Retrieve specific context items by ID
  - `search_context` - Advanced search through stored context with filtering
  - `list_contexts` - List all context items with pagination support
  - `delete_context` - Remove context items from storage
  - `create_project` - Create new projects for organization
  - `list_projects` - List all projects with pagination support
- **MCP Resources**: Exposes context and project data as MCP resources
- **Integrated Architecture**: MCP server runs on the same port as the main application (`/mcp`)

### Web Interface
- **Modern Vue.js 3 Application**: Built with TypeScript and Vite for optimal performance
- **Responsive Design**: Clean, professional interface optimized for all devices
- **Comprehensive Views**: Four main application views:
  - **Dashboard**: Overview of stored contexts and system statistics
  - **Context Items**: Complete context item management interface
  - **Projects**: Project organization and management tools
  - **Settings**: Application configuration and MCP client setup
- **State Management**: Pinia for efficient reactive state management
- **Modular Architecture**: Well-structured component system (Header, Sidebar, etc.)

## Tech Stack

### Backend
- **FastAPI** - Modern, high-performance Python web framework
- **LanceDB** - Vector database optimized for embeddings and semantic search
- **Sentence Transformers** - AI embeddings generation using all-MiniLM-L6-v2 model
- **PyTorch** - Deep learning framework for embedding computations
- **Pandas** - Data manipulation and analysis library
- **Uvicorn** - High-performance ASGI server
- **FastMCP** - Model Context Protocol server framework

### Frontend
- **Vue.js 3** - Progressive JavaScript framework with Composition API
- **TypeScript** - Type-safe JavaScript development
- **Vite** - Fast build tool and development server
- **Pinia** - Modern state management solution

### Infrastructure
- **Docker** - Application containerization
- **Docker Compose** - Multi-container orchestration
- **Persistent Volumes** - Reliable data persistence

## Prerequisites

- **Docker** 20.10 or higher
- **Docker Compose** 2.0 or higher
- **Node.js** 20.19+ or 22.12+ (for frontend development)
- **pnpm** (recommended) or npm (for frontend development)
- **Python** 3.8+ (for local development)
- **PyTorch** (automatically installed via requirements.txt)
- **Sentence Transformers** (automatically installed via requirements.txt)

## Quick Start

### Docker Development (Recommended)

The easiest way to get started is with Docker:

```bash
# Clone the repository
git clone <repository-url>
cd cortex

# Start everything with Docker
./scripts/docker-dev.sh
```

This process will:
1. Build the Vue.js frontend using `pnpm build-only`
2. Copy frontend assets to the FastAPI `app/assets/` directory
3. Build and start the containerized application
4. Serve the application on http://localhost:8000
5. Provide MCP server access at http://localhost:8000/mcp

### Manual Docker Setup

```bash
# Build frontend
cd akd.dev.fe
pnpm install
pnpm build-only
cd ..

# Copy frontend assets to FastAPI
rm -rf app/assets && mkdir -p app/assets
cp -r akd.dev.fe/dist/* app/assets/

# Start with Docker Compose
docker-compose -f docker-compose.dev.yml up --build
```

### View Logs and Manage

```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes (⚠️ This will delete all data)
docker-compose -f docker-compose.dev.yml down -v
```

## MCP Client Configuration

### Cursor IDE

Add to your Cursor MCP configuration:

```json
{
  "mcpServers": {
    "cortex": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

### Claude Desktop

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cortex": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

### Important Notes

- **MCP Server HTTP Endpoint**: The server runs as an HTTP endpoint at `http://127.0.0.1:8000/mcp`
- **Docker Networking**: Ensure Docker is running and the container is accessible on port 8000
- **Database Persistence**: Data is stored in the Docker volume `cortex_data`
- **Server Requirements**: The Cortex application must be running for MCP clients to connect

## API Endpoints

### Context Items
- `POST /api/context/items` - Create context item with automatic embedding generation
- `GET /api/context/items` - List context items with pagination
- `GET /api/context/items/{id}` - Get specific context item
- `PUT /api/context/items/{id}` - Update context item (regenerates embeddings if content changed)
- `DELETE /api/context/items/{id}` - Soft delete context item
- `POST /api/context/items/search` - Enhanced search with semantic, keyword, and hybrid modes
- `GET /api/context/items/semantic-search` - Semantic vector similarity search
- `GET /api/context/items/keyword-search` - Traditional keyword search
- `GET /api/context/items/hybrid-search` - Combined semantic + keyword search

### Projects
- `POST /api/context/projects` - Create project
- `GET /api/context/projects` - List projects with pagination
- `GET /api/context/projects/{id}` - Get specific project
- `PUT /api/context/projects/{id}` - Update project
- `DELETE /api/context/projects/{id}` - Delete project

### MCP Server Integration
- `POST /mcp` - Main MCP server endpoint (JSON-RPC 2.0)
- `GET /mcp/health` - MCP server health check
- `GET /api/mcp/info` - MCP server information and configuration

### Data Management
- `GET /api/data/export` - Export all context data
- `POST /api/data/import` - Import context data
- `POST /api/data/wipe` - Wipe all data (development only)
- `GET /api/data/info` - Database information and statistics

### Health & Stats
- `GET /health` - Application health status
- `GET /api/context/stats` - Context statistics with embedding information

### Frontend Routes
- `GET /` - Dashboard view
- `GET /contexts` - Context management view
- `GET /projects` - Project management view
- `GET /settings` - Application settings

## Data Storage

### Docker Volume
- **Location**: Docker volume `cortex_data`
- **Type**: LanceDB vector database stored at `/data/lancedb/`
- **Embeddings**: 384-dimensional vectors generated using all-MiniLM-L6-v2 model
- **Persistence**: All data persists across container restarts
- **Backup**: Volume can be backed up using standard Docker volume commands

### Context Item Structure
```json
{
  "id": 1,
  "title": "Example Context",
  "content": "Context content here...",
  "content_type": "text",
  "tags": ["tag1", "tag2"],
  "extra_metadata": {},
  "source": "manual",
  "project_id": "my-project",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "vector": [0.1, 0.2, 0.3, ...] // 384-dimensional embedding
}
```

## User Interface

### Dashboard (`/`)
- Comprehensive overview of stored contexts and system statistics
- Quick access to recently created items
- MCP server status and health monitoring
- Application information and system metrics

### Context Items (`/contexts`)
- Complete context item management interface
- Rich content editing and management capabilities
- Tag assignment and management system
- Project association and organization
- Content type filtering and search

### Projects (`/projects`)
- Project creation and management tools
- Project-specific context viewing and organization
- Project statistics and metadata display
- Project settings and configuration options

### Settings (`/settings`)
- Application configuration and preferences
- MCP server settings and status monitoring
- Database management and maintenance tools
- Connection guides for Cursor and Claude Desktop integration

## Security & Privacy

- **Local-First Architecture**: All data stored locally in Docker volumes
- **No Cloud Synchronization**: Complete data control and privacy
- **Container Isolation**: Application runs in isolated Docker container environment
- **Local-Only MCP Server**: Server accessible only from localhost for security
- **Persistent Storage**: All data persists across container restarts

## Development

### Frontend Development

```bash
# Install dependencies
cd akd.dev.fe
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build
```

### Backend Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run FastAPI server
cd app
python main.py
```

### Docker Development

```bash
# Rebuild and restart containers
docker-compose -f docker-compose.dev.yml up --build

# View container logs
docker-compose -f docker-compose.dev.yml logs -f cortex

# Access container shell
docker-compose -f docker-compose.dev.yml exec cortex bash
```

## Production Deployment

### Docker Production Build

```bash
# Build frontend
cd akd.dev.fe && pnpm build && cd ..

# Copy assets to FastAPI
rm -rf app/assets && mkdir -p app/assets
cp -r akd.dev.fe/dist/* app/assets/

# Build production image
docker build -f Dockerfile.dev -t cortex:latest .

# Run production container
docker run -d \
  --name cortex \
  -p 8000:8000 \
  -v cortex_data:/data \
  cortex:latest
```

### Docker Compose Production

Create a `docker-compose.prod.yml`:

```yaml
version: '3.8'
services:
  cortex:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - HOST=0.0.0.0
      - PORT=8000
    volumes:
      - cortex_data:/data
    restart: unless-stopped

volumes:
  cortex_data:
    driver: local
```

## Roadmap

- [x] Core context storage system
- [x] MCP server implementation
- [x] Vue.js frontend interface
- [x] Docker containerization
- [x] **Vector database migration (LanceDB)**
- [x] **Semantic search with embeddings**
- [x] **Hybrid search (semantic + keyword)**
- [x] **Advanced search with filters**
- [x] **Data export/import functionality**
- [ ] Context templates
- [ ] Bulk operations
- [ ] Markdown editor improvements
- [ ] Database encryption
- [ ] Plugin system
- [ ] Custom MCP tools
- [ ] Multi-user support

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the built-in help system
- **MCP Protocol**: See [MCP Specification](https://spec.modelcontextprotocol.io/)

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker-compose -f docker-compose.dev.yml logs

# Rebuild containers
docker-compose -f docker-compose.dev.yml up --build --force-recreate
```

**MCP client can't connect:**
- Ensure Cortex is running: `docker-compose -f docker-compose.dev.yml ps`
- Check if port 8000 is accessible: `curl http://localhost:8000/health`
- Verify MCP endpoint: `curl http://localhost:8000/mcp/health`

**Data persistence issues:**
```bash
# Check volume exists
docker volume ls | grep cortex

# Inspect volume
docker volume inspect cortex_cortex_data

# Backup volume
docker run --rm -v cortex_cortex_data:/data -v $(pwd):/backup alpine tar czf /backup/cortex-backup.tar.gz -C /data .
```

**Embedding Model Issues:**
- Initial startup may require additional time for sentence-transformers model download (~80MB)
- Model is cached in Docker volume for faster subsequent starts
- If embeddings fail, check Docker logs for model download errors

---

**Happy context managing!**