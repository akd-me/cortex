## License

Cortex is licensed under the Apache License 2.0 with the Commons Clause restriction.
This means you can use, modify, and self-host Cortex for free for personal or internal purposes.

Commercial use — including offering Cortex as a hosted service, selling access to it,
or integrating it into a paid product — requires a commercial license from DEV.


# Cortex Context Manager

A Docker-based application that stores context information locally and exposes a Model Context Protocol (MCP) server for integration with AI development tools like Cursor and Claude Desktop.

## 🎯 Goal: "Bring Your Own Context"

Cortex allows you to:
- Store and manage context information locally in a Docker container
- Search through your context items with advanced filtering
- Organize contexts by projects
- Expose context via MCP server for AI tools
- Maintain full control over your data with persistent Docker volumes

## 🏗️ Architecture

```
cortex/
├── app/                    # FastAPI backend
│   ├── models/            # SQLAlchemy & Pydantic models
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   ├── database/          # Database connection
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

## 🚀 Features

### Core Functionality
- **Docker-based Storage**: SQLite database in persistent Docker volume
- **Context Management**: Create, read, update, delete context items
- **Project Organization**: Group contexts by projects
- **Full-Text Search**: Search through titles and content
- **Tag System**: Categorize contexts with tags
- **Persistent Data**: Data survives container restarts

### MCP Server
- **FastMCP Integration**: Modern MCP server implementation using FastMCP framework
- **HTTP Support**: HTTP communication protocol
- **7 MCP Tools**:
  - `store_context` - Store new context information with metadata
  - `retrieve_context` - Get specific context by ID
  - `search_context` - Advanced search through stored context with filters
  - `list_contexts` - List all context items with pagination
  - `delete_context` - Remove context items
  - `create_project` - Create new projects for organization
  - `list_projects` - List all projects with pagination
- **MCP Resources**: Exposes context and project data as MCP resources
- **Integrated Endpoints**: MCP server runs on same port as main application (`/mcp`)

### Web Interface
- **Modern Vue.js 3 App**: Built with TypeScript and Vite
- **Responsive Design**: Clean, modern interface
- **4 Main Views**:
  - **Dashboard**: Overview of stored contexts and statistics
  - **Context Items**: Create, edit, and manage context items
  - **Projects**: Organize contexts into projects
  - **Settings**: App configuration and MCP client setup
- **State Management**: Pinia for reactive state management
- **Component Architecture**: Modular components (Header, Sidebar)

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Local database
- **Uvicorn** - ASGI server
- **FastMCP** - MCP server framework

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **Pinia** - State management

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Persistent Volumes** - Data persistence

## 📋 Prerequisites

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Node.js** 20.19+ or 22.12+ (for frontend development)
- **pnpm** (recommended) or npm (for frontend development)

## 🚀 Quick Start

### 🐳 Docker Development (Recommended)

The easiest way to get started is with Docker:

```bash
# Clone the repository
git clone <repository-url>
cd cortex

# Start everything with Docker
./scripts/docker-dev.sh
```

This will:
1. Build the Vue.js frontend with `pnpm build-only`
2. Copy frontend assets to FastAPI `app/assets/` directory
3. Build and start the containerized application
4. Serve everything on http://localhost:8000
5. Provide MCP server at http://localhost:8000/mcp

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

## 🔧 MCP Client Configuration

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

- **MCP Server runs via HTTP**: The server runs as an HTTP endpoint at `http://127.0.0.1:8000/mcp`
- **Docker networking**: Ensure Docker is running and the container is accessible on port 8000
- **Database persistence**: Data is stored in Docker volume `cortex_data`
- **Server must be running**: The Cortex application must be running for MCP clients to connect

## 📚 API Endpoints

### Context Items
- `POST /api/context/items` - Create context item
- `GET /api/context/items` - List context items with pagination
- `GET /api/context/items/{id}` - Get specific context item
- `PUT /api/context/items/{id}` - Update context item
- `DELETE /api/context/items/{id}` - Delete context item
- `POST /api/context/items/search` - Search context items with filters

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

### Health & Stats
- `GET /health` - Application health status
- `GET /api/context/stats` - Context statistics

### Frontend Routes
- `GET /` - Dashboard view
- `GET /contexts` - Context management view
- `GET /projects` - Project management view
- `GET /settings` - Application settings

## 🗃️ Data Storage

### Docker Volume
- **Location**: Docker volume `cortex_data`
- **Type**: SQLite database at `/data/context.db`
- **Persistence**: Data survives container restarts
- **Backup**: Volume can be backed up using Docker volume commands

### Context Item Structure
```json
{
  "id": 1,
  "title": "Example Context",
  "content": "Context content here...",
  "content_type": "text",
  "tags": ["tag1", "tag2"],
  "project_id": "my-project",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## 🎨 User Interface

### Dashboard (`/`)
- Overview of stored contexts and statistics
- Quick access to recent items
- MCP server status and health
- Application information

### Context Items (`/contexts`)
- Create, edit, and delete context items
- Rich content management
- Tag assignment and management
- Project association
- Content type filtering

### Projects (`/projects`)
- Create and manage projects
- View project-specific contexts
- Project statistics and metadata
- Project settings and configuration

### Settings (`/settings`)
- Application configuration
- MCP server settings and status
- Database management
- Connection guides for Cursor and Claude Desktop

## 🔐 Security & Privacy

- **Local-first**: All data stored in Docker volume
- **No cloud sync**: Complete data control
- **Container isolation**: Application runs in isolated Docker container
- **Local-only MCP server**: Only accessible from localhost
- **Persistent storage**: Data survives container restarts

## 🛠️ Development

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

## 📦 Production Deployment

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

## 🛣️ Roadmap

- [x] Core context storage system
- [x] MCP server implementation
- [x] Vue.js frontend interface
- [x] Docker containerization
- [ ] Advanced search with filters
- [ ] Data export/import functionality
- [ ] Context templates
- [ ] Bulk operations
- [ ] Markdown editor improvements
- [ ] Database encryption
- [ ] Plugin system
- [ ] Custom MCP tools
- [ ] Kubernetes deployment
- [ ] Multi-user support

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the built-in help system
- **MCP Protocol**: See [MCP Specification](https://spec.modelcontextprotocol.io/)

## 🔧 Troubleshooting

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

---

**Happy context managing! 🧠**