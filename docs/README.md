# 🤖 Code Buddy MCP

**Intelligent workflow management for developers via Model Context Protocol (MCP)**

A production-ready MCP server that provides Claude with access to 117 curated coding workflows, 730 executable tasks, and 343 reusable skills. Uses semantic search to find the right workflow for any development task.

---

## ✨ Features

- 🔍 **Semantic Search** - Natural language queries find relevant workflows
- 📚 **117 Workflows** - Covering development, DevOps, data engineering, testing, and more
- 🎯 **730 Tasks** - Granular, executable steps for each workflow
- 🧩 **343 Skills** - Reusable patterns, best practices, and techniques
- 🚀 **Railway Ready** - One-click deployment to Railway
- 🤝 **Claude Integration** - Seamless integration with Claude Desktop
- 📊 **Usage Analytics** - Track helpful workflows and improve rankings

---

## 🚀 Quick Start

### Option 1: Use Pre-Deployed Service (Recommended)

If someone on your team has already deployed:

1. Get the Railway service URL from your team
2. Configure Claude Desktop (see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#step-5-configure-claude-desktop))
3. Restart Claude Desktop
4. Start using: "Show me workflows about API design"

### Option 2: Deploy Your Own

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/code-buddy-mcp.git
cd code-buddy-mcp

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# 5. Test locally
python -m src.server

# 6. Deploy to Railway
# See full deployment guide: DEPLOYMENT_GUIDE.md
```

---

## 📖 Documentation

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[READY_TO_USE.md](READY_TO_USE.md)** - System status and capabilities  
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Architecture and design
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

---

## 🛠️ Available Tools

When integrated with Claude Desktop, you get access to:

### `search_workflows`
Search for workflows using natural language + filters

```python
search_workflows(
    query="create a REST API endpoint",
    technologies=["Python", "FastAPI"],
    complexity="intermediate"
)
```

### `get_workflow`  
Get complete workflow content by ID

```python
get_workflow(workflow_id=42)
```

### `list_categories`
Browse all available workflow categories

```python
list_categories()
```

### `get_prerequisites`
Get prerequisite chain for a workflow

```python
get_prerequisites(workflow_id=15)
```

### `track_usage`
Track workflow usage for analytics

```python
track_usage(workflow_id=42, was_helpful=True)
```

---

## 📊 What's Inside

### Workflows (117)
- **Development** (30) - FastAPI endpoints, Git workflows, CI/CD, refactoring
- **DevOps** (15) - Kubernetes, Docker, monitoring, incident response
- **Data Engineering** (12) - ETL pipelines, Kafka, Airflow, dbt
- **Architecture** (9) - API design, caching, microservices, scalability
- **Testing** (5) - Integration testing, mocking, property-based testing
- **Security** (7) - Secret management, key rotation, incident response
- **Frontend** (12) - React components, accessibility, performance
- **Machine Learning** (10) - MLOps, model deployment, A/B testing
- **Quality Assurance** (11) - Code reviews, type checking, coverage
- **Configuration** (5) - Settings management, logging, formatters
- **Version Control** (5) - Branch strategies, merge conflicts, tagging

### Database Schema

```
┌─────────────┐
│  workflows  │  117 rows - High-level overviews
│  + embedding│  with semantic search
└──────┬──────┘
       │
       ├──────────────────┐
       │                  │
┌──────▼──────┐    ┌──────▼──────┐
│    tasks    │    │   skills    │
│  730 rows   │    │  343 rows   │
│ + embedding │    │ + embedding │
└─────────────┘    └─────────────┘

Granular, token-efficient architecture
Load only what you need!
```

---

## 🎯 Use Cases

**"I need to set up CI/CD"**  
→ Finds relevant DevOps workflows with step-by-step instructions

**"How do I handle database migrations?"**  
→ Returns data engineering workflows with best practices

**"Show me beginner Docker workflows"**  
→ Filters by complexity level and technology

**"What are the prerequisites for Kubernetes deployment?"**  
→ Shows dependency chain of required workflows

---

## 🧪 Development

### Project Structure

```
code_buddy_mcp/
├── src/
│   ├── server.py              # FastMCP server
│   ├── database/
│   │   ├── connection.py      # Database connection
│   │   └── schema_v2.sql      # PostgreSQL schema
│   ├── tools/
│   │   └── workflow_search.py # Search implementation
│   └── utils/
│       └── embeddings.py      # Cohere embeddings
├── scripts/
│   ├── import_workflows_v2.py # Import workflows
│   └── parse_workflows_v2.py  # Parse markdown
├── workflows/                  # 117 workflow files
│   ├── development/
│   ├── devops/
│   ├── data-engineering/
│   └── ... (11 categories)
├── tests/                      # Test suite
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

### Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
pytest

# With coverage
pytest --cov=src --cov-report=html
```

### Adding New Workflows

1. Create markdown file in appropriate category folder
2. Follow the workflow template structure
3. Run import script to add to database
4. Embeddings are auto-generated

See workflow files in `workflows/` for examples.

---

## 🔧 Configuration

### Environment Variables

Required in `.env` or Railway environment:

```env
# Database (Railway PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/db

# Embeddings (Cohere)
COHERE_API_KEY=your_cohere_api_key
EMBEDDING_PROVIDER=cohere
EMBEDDING_MODEL=embed-english-v3.0
EMBEDDING_DIMENSIONS=1024

# Server
MCP_SERVER_NAME=code-buddy
LOG_LEVEL=INFO
```

### Claude Desktop Configuration

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#step-5-configure-claude-desktop) for complete config.

---

## 📈 Performance

- **Search Latency:** < 200ms average
- **Database:** Railway PostgreSQL with pgvector
- **Embeddings:** Cohere embed-english-v3.0 (1024 dims)
- **Token Efficiency:** Load only relevant tasks/skills
- **Concurrent Users:** Scales with Railway resources

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

See workflow files for content contribution guidelines.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Embeddings by [Cohere](https://cohere.com)
- Database hosting by [Railway](https://railway.app)
- Inspired by the Claude MCP ecosystem

---

## 📞 Support

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions  
- **Documentation:** See `/docs` folder

---

## 🎊 Status

**Production Ready** ✅

- 117 workflows imported
- 730 tasks extracted
- 343 skills available
- All embeddings generated
- Semantic search operational
- Railway deployment tested

**Ready to help you code smarter, not harder!** 🚀
