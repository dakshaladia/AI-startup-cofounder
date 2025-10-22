# AI Startup Cofounder

An intelligent platform that helps entrepreneurs discover, evaluate, and refine startup ideas using AI-powered agents and market analysis.

## 🚀 Overview

This project provides a comprehensive AI-driven system for startup idea generation, market analysis, and business planning. It combines multiple specialized AI agents to provide end-to-end support for entrepreneurs.

## 🏗️ Architecture

The system is built with a microservices architecture using Docker containers:

- **Frontend**: Next.js web application with React components
- **Backend**: FastAPI-based API service
- **Agents**: Specialized AI agents for different tasks
- **Embeddings**: Vector search and retrieval system
- **Evaluator**: Idea scoring and novelty assessment
- **Ingestion**: Data processing pipelines

## 🤖 AI Agents

The platform includes several specialized AI agents:

- **Idea Generator**: Creates innovative startup concepts
- **Market Analyst**: Analyzes market opportunities and trends
- **PM Refiner**: Refines ideas from a product management perspective
- **Critic**: Provides critical analysis and identifies potential issues
- **Synthesizer**: Combines insights from all agents

## 🛠️ Tech Stack

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python
- **AI/ML**: OpenAI API, Local LLM support
- **Vector Search**: FAISS
- **Infrastructure**: Docker, Kubernetes, Terraform
- **Data Processing**: Custom pipelines for various data sources

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Node.js 18+

### Running the Application

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-startup-cofounder
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Web interface: http://localhost:3000
   - API documentation: http://localhost:8000/docs

## 📁 Project Structure

```
├── frontend/           # Next.js web application
│   ├── web/           # Main web app
│   └── demo/          # Demo application
├── services/          # Backend services
│   ├── agents/        # AI agent services
│   ├── backend/       # API service
│   ├── embeddings/    # Vector search service
│   ├── evaluator/     # Scoring service
│   └── ingestion/     # Data processing
├── infra/             # Infrastructure as code
│   ├── k8s/          # Kubernetes manifests
│   └── terraform/    # Terraform configurations
├── docs/             # Documentation
└── tests/            # Test suites
```

## 🔧 Development

### Running Individual Services

**Frontend Development**
```bash
cd frontend/web
npm install
npm run dev
```

**Backend Development**
```bash
cd services/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Agent Development**
```bash
cd services/agents
pip install -r requirements.txt
python orchestrator.py
```

## 📊 Features

- **Idea Generation**: AI-powered startup idea creation
- **Market Analysis**: Comprehensive market research and analysis
- **Idea Refinement**: Product management perspective on ideas
- **Critical Analysis**: Risk assessment and potential issues
- **Synthesis**: Combined insights from all agents
- **Timeline View**: Track idea evolution over time
- **Artifact Management**: Store and view generated documents

## 🔌 API Endpoints

- `GET /api/v1/ideas` - Retrieve ideas
- `POST /api/v1/ideas` - Create new idea
- `POST /api/v1/feedback` - Submit feedback
- `GET /api/v1/analytics` - Get analytics data

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests
pytest
```

## 📈 Monitoring

The application includes comprehensive logging and monitoring:

- Structured logging across all services
- Performance metrics
- Error tracking
- Analytics dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `docs/` folder
- Review the API documentation at `/docs` endpoint
