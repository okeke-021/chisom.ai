# Chisom.ai - AI Agent Builder 🚀

Transform natural language descriptions into fully functional, production-ready web applications with AI-powered code generation.

## Features ✨

- **Natural Language to Code**: Describe your app idea, get complete codebase
- **Smart Tech Stack Selection**: AI chooses optimal frameworks and tools
- **Production Ready**: Includes Docker support, configuration, and documentation
- **GitHub Integration**: Automatic repository creation and commits
- **Multi-Framework Support**: React, Vue, Next.js, FastAPI, and more
- **Code Quality**: Built-in ESLint, Prettier, and validation
- **Vector-Based Templates**: Learn from approved GitHub repositories
- **Real-time Preview**: See your app before deployment
- **Authentication & Rate Limiting**: Secure with tier-based usage

## Tech Stack 🛠️

### Core Technologies
- **Chainlit**: Interactive chat interface with full lifecycle support
- **LangChain**: AI orchestration and prompt management
- **LangGraph**: Complex workflow management
- **LangSmith**: Debugging, tracing, and monitoring
- **Codestral**: Latest Mistral AI model for code generation

### Infrastructure
- **Neon**: Serverless Postgres database
- **Redis**: Rate limiting and caching
- **Docker**: Containerization and deployment
- **GitHub API**: Repository management

### AI & ML
- **ChromaDB**: Vector storage for code templates
- **Sentence Transformers**: Code similarity search
- **Tree-sitter**: Code parsing and analysis

## Installation 🔧

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (for code quality tools)
- GitHub Personal Access Token
- Mistral AI API Key
- Neon Database

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/chisom-ai.git
cd chisom-ai
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
npm install -g eslint prettier
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Initialize database**
```bash
python -c "from database.connection import init_db; init_db()"
```

6. **Run with Docker Compose**
```bash
docker-compose up -d
```

7. **Access the application**
- Open http://localhost:8000
- Create an account and start building!

## Usage 💡

### Basic Example

1. **Describe your app**:
   ```
   Create a task management app with user authentication,
   drag-and-drop interface, and real-time collaboration
   ```

2. **AI generates**:
   - Complete React frontend
   - FastAPI backend with auth
   - PostgreSQL schema
   - Docker configuration
   - README and documentation

3. **Automatic GitHub commit**:
   - New repository created
   - All files committed
   - Ready to deploy

### Advanced Features

#### Custom Tech Stack
```
Build an e-commerce platform using Next.js, Stripe,
and MongoDB with admin dashboard
```

#### API Integration
```
Create a weather dashboard that fetches data from
OpenWeather API with charts and forecasts
```

#### Real-time Apps
```
Build a chat application with WebSockets,
message encryption, and file sharing
```

## Architecture 📐

```
chisom-ai/
├── app.py                 # Main Chainlit application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Multi-container setup
│
├── auth/
│   └── auth_service.py   # Authentication & rate limiting
│
├── database/
│   ├── models.py         # SQLAlchemy models
│   └── connection.py     # Database connection
│
├── services/
│   ├── github_service.py      # GitHub integration
│   ├── code_quality_service.py # Code analysis
│   └── vector_store_service.py # Template retrieval
│
├── agents/
│   └── app_generator_agent.py # LangGraph workflow
│
└── public/
    └── README.md         # User documentation
```

## Pricing Plans 💳

### Free Tier
- 5 requests per day
- All core features
- GitHub integration
- Community support

### Pro Plan ($29/month)
- 30 requests per day
- Priority processing
- Advanced templates
- Email support
- Custom tech stacks

## API Reference 📚

### Rate Limiting

```python
# Check current usage
GET /api/rate-limit

# Response
{
  "tier": "free",
  "used": 3,
  "limit": 5,
  "resets_at": "2026-01-22T00:00:00Z"
}
```

### Project Management

```python
# List projects
GET /api/projects

# Get project details
GET /api/projects/{project_id}

# Delete project
DELETE /api/projects/{project_id}
```

## Development 🔨

### Running Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
# Format Python code
black .

# Lint Python code
ruff check .

# Format JavaScript
npx prettier --write "**/*.{js,jsx,ts,tsx}"
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Deployment 🚀

### Docker Production

```bash
docker build -t chisom-ai:latest .
docker run -p 8000:8000 --env-file .env chisom-ai:latest
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chisom-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chisom-ai
  template:
    metadata:
      labels:
        app: chisom-ai
    spec:
      containers:
      - name: chisom-ai
        image: chisom-ai:latest
        ports:
        - containerPort: 8000
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MISTRAL_API_KEY` | Mistral AI API key | Yes |
| `GITHUB_TOKEN` | GitHub personal access token | Yes |
| `NEON_DATABASE_URL` | Neon Postgres connection string | Yes |
| `REDIS_URL` | Redis connection URL | Yes |
| `JWT_SECRET_KEY` | Secret for JWT tokens | Yes |
| `LANGSMITH_API_KEY` | LangSmith API key | Optional |

## Troubleshooting 🔍

### Common Issues

1. **Docker build fails**
   ```bash
   docker system prune -a
   docker-compose build --no-cache
   ```

2. **Database connection error**
   - Verify `DATABASE_URL` in .env
   - Check Neon database is active
   - Run migrations

3. **Rate limit not working**
   - Ensure Redis is running
   - Check `REDIS_URL` configuration

4. **GitHub API errors**
   - Verify token has repo permissions
   - Check rate limits on GitHub

## Contributing 🤝

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License 📄

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support 💬

- **Documentation**: https://docs.chisom.ai
- **Issues**: https://github.com/yourusername/chisom-ai/issues
- **Discord**: https://discord.gg/chisom-ai
- **Email**: support@chisom.ai

## Roadmap 🗺️

- [ ] Multi-language support
- [ ] VS Code extension
- [ ] Mobile app generation
- [ ] Blockchain integration
- [ ] AI model fine-tuning
- [ ] Team collaboration features
- [ ] Marketplace for templates

## Acknowledgments 🙏

- Chainlit team for the amazing framework
- LangChain community
- Mistral AI for Codestral
- All contributors and users

---

Built with ❤️ by the Chisom.ai team
