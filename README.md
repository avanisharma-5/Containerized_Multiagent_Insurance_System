# Containerised Multi-Agent Insurance Assistant

A sophisticated AI-powered insurance analysis system that combines multiple intelligent agents to provide comprehensive policy analysis, document comparison, and intelligent chat assistance.

## 🚀 Features

### 🤖 Multi-Agent System
- **Chat Agent**: Interactive Q&A with insurance expertise
- **RAG Agent**: Document analysis with vector search
- **Comparison Agent**: Side-by-side policy comparison
- **Web Search Agent**: Real-time insurance information retrieval

### 📄 Document Processing
- **PDF Upload & Analysis**: Extract and analyze insurance documents
- **Vector Storage**: ChromaDB for efficient document retrieval
- **Smart Chunking**: Optimized text segmentation for better context

### 🔄 RAG + Web Search Fallback
- **Primary**: Retrieval-Augmented Generation from uploaded documents
- **Fallback**: SerpAPI web search when document info insufficient
- **Intelligent Switching**: Automatic selection based on content availability

### 🎨 Modern UI/UX
- **Streamlit Frontend**: Clean, intuitive interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Light Blue Theme**: Professional, attractive color scheme
- **Real-time Updates**: Live processing status

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend     │    │    Backend     │    │  AI Services   │
│  (Streamlit)   │◄──►│   (FastAPI)    │◄──►│  (Groq/SerpAPI)│
│                 │    │                 │    │                 │
│ • Chat UI      │    │ • CrewAI       │    │ • LLM Models   │
│ • File Upload   │    │ • RAG System   │    │ • Web Search   │
│ • Results      │    │ • Vector DB     │    │ • Embeddings   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🧠 AI Models Used
- **Groq Llama 3.1**: Fast, efficient language processing
- **Sentence Transformers**: High-quality document embeddings
- **ChromaDB**: Vector database for semantic search
- **SerpAPI**: Real-time web search integration

## 🛠️ Technology Stack

### Frontend
- **Streamlit 1.29.0**: Web application framework
- **Requests 2.31.0**: HTTP client for API communication
- **Custom CSS**: Modern, responsive styling

### Backend
- **FastAPI 0.104.1**: High-performance API framework
- **Uvicorn**: ASGI server for FastAPI
- **CrewAI 0.51.0**: Multi-agent orchestration
- **LangChain**: LLM integration and RAG pipeline

### AI/ML
- **ChromaDB 0.4.18**: Vector database
- **Sentence Transformers 2.2.2**: Document embeddings
- **Transformers 4.36.0**: HuggingFace model integration
- **PyPDF**: PDF document processing

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (for containerized deployment)
- Git

### Local Development Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/avanis55/insurance-assistant.git
   cd insurance-assistant
   ```

2. **Environment Variables**
   ```bash
   # Create backend/.env file
   GROQ_API_KEY=your_groq_api_key
   SERPAPI_API_KEY=your_serpapi_key
   HF_API_TOKEN=your_huggingface_token
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Services**
   ```bash
   # Backend
   cd backend
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload

   # Frontend (new terminal)
   cd frontend
   streamlit run app.py --server.port=8501
   ```

5. **Access Application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000

## 🐳 Docker Deployment

### Build & Run Locally

1. **Build Docker Image**
   ```bash
   docker build -t insurance-assistant .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name insurance-app \
     -p 8501:8501 \
     -p 8000:8000 \
     -e GROQ_API_KEY="your_key" \
     -e SERPAPI_API_KEY="your_key" \
     -e HF_API_TOKEN="your_token" \
     insurance-assistant
   ```

## ☁️ AWS EC2 + Docker Hub Deployment

### Architecture Overview
```
GitHub ──► Docker Hub ──► EC2 Instance ──► Your Browser
   │           │               │                │
   │           │               │                │
Push Code   Build Image    Pull & Run     Access App
```

### Step-by-Step Deployment

#### 1. AWS EC2 Setup
```bash
# Launch Ubuntu 22.04 LTS instance
# Instance type: t2.micro (free tier)
# Security Group: Custom TCP 8501, 8000 from 0.0.0.0/0
```

#### 2. Docker Hub Repository
1. Create account at [hub.docker.com](https://hub.docker.com)
2. Create repository: `insurance-assistant`

#### 3. GitHub Actions CI/CD

**Required Secrets in GitHub Repository:**
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password/token
- `EC2_HOST`: EC2 public IP address
- `EC2_USERNAME`: SSH username (ubuntu)
- `EC2_SSH_KEY`: Private SSH key content
- `GROQ_API_KEY`: Groq API key
- `SERPAPI_API_KEY`: SerpAPI key
- `HF_API_TOKEN`: HuggingFace token

**Automated Workflow:**
1. **Test**: Validates code and imports
2. **Build**: Creates Docker image
3. **Push**: Uploads to Docker Hub
4. **Deploy**: Updates EC2 container

#### 4. Deployment Commands

**Manual Deployment (if needed):**
```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Pull and run
docker pull avanis55/insurance-assistant:latest
docker stop insurance-app || true
docker rm insurance-app || true
docker run -d \
  --name insurance-app \
  -p 8501:8501 \
  -p 8000:8000 \
  --restart unless-stopped \
  -e GROQ_API_KEY="your_key" \
  -e SERPAPI_API_KEY="your_key" \
  -e HF_API_TOKEN="your_token" \
  avanis55/insurance-assistant:latest
```

#### 5. Access Application
- **Frontend**: http://your-ec2-ip:8501
- **Backend API**: http://your-ec2-ip:8000

## 📚 API Documentation

### Backend Endpoints

#### Chat & Workflow
- `POST /workflow/run-inline` - Process chat with PDF
- `POST /workflow/run` - Process chat without PDF

#### Policy Comparison
- `POST /comparison/run` - Compare two insurance policies

#### Health Check
- `GET /` - API status and version

### Request Examples

#### Chat with PDF
```python
import requests

files = {
    'file': ('policy.pdf', open('policy.pdf', 'rb'), 'application/pdf')
}
data = {
    'question': 'What is the coverage limit?',
    'generate_image': False
}

response = requests.post(
    'http://localhost:8000/workflow/run-inline',
    files=files,
    data=data
)
```

#### Policy Comparison
```python
files = {
    'pdf_a': ('policy1.pdf', open('policy1.pdf', 'rb')),
    'pdf_b': ('policy2.pdf', open('policy2.pdf', 'rb'))
}

response = requests.post(
    'http://localhost:8000/comparison/run',
    files=files
)
```

## 🎯 Features in Detail

### 📖 Document Analysis (RAG)
1. **Upload PDF**: User uploads insurance document
2. **Text Extraction**: PyPDF extracts content
3. **Chunking**: Text split into 800-character chunks
4. **Embedding**: Convert chunks to vector representations
5. **Storage**: Store in ChromaDB for fast retrieval
6. **Query Processing**: Find relevant chunks for user questions

### 🤝 Agent Collaboration
- **Planner Agent**: Analyzes user intent and plans response
- **Researcher Agent**: Retrieves information from documents/web
- **Writer Agent**: Formats response with proper structure
- **Reviewer Agent**: Ensures response quality and accuracy

### 🔄 Smart Fallback System
1. **Document Search**: First tries RAG from uploaded PDFs
2. **Web Search**: If insufficient info, searches internet
3. **Response Synthesis**: Combines both sources for comprehensive answer
4. **Quality Check**: Validates response relevance and accuracy

## 🎨 UI Features

### Chat Interface
- **File Upload**: Drag-and-drop PDF support
- **Question Input**: Multi-line text area with history
- **Response Display**: Formatted markdown with syntax highlighting
- **Status Indicators**: Real-time processing feedback

### Comparison Interface
- **Dual Upload**: Side-by-side PDF selection
- **Analysis Report**: Structured comparison with key differences
- **Visual Indicators**: Color-coded winner highlighting
- **Raw Data Access**: Expandable JSON view of extracted data

### Design System
- **Color Palette**: Professional blue gradient theme
- **Typography**: Clean, readable font hierarchy
- **Responsive**: Mobile-first design approach
- **Accessibility**: High contrast ratios and keyboard navigation

## 🔧 Configuration

### Hardcoded Settings
```python
# Model Configuration
GROQ_MODEL = "groq/llama-3.1-8b-instant"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HF_IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

# Storage Paths
CHROMA_DIR = "vector_store"
UPLOADS_DIR = "uploads"
CHATS_DIR = "data/chats"

# Processing Parameters
RAG_MIN_CHARS = 250
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
RETRIEVAL_K = 5
```

### Environment Variables
Only API keys need to be configured:
- `GROQ_API_KEY`: Groq LLM access
- `SERPAPI_API_KEY`: Web search access
- `HF_API_TOKEN`: HuggingFace model access

## 🐛 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check disk space
df -h

# Clean Docker system
docker system prune -a -f

# Check container logs
docker logs insurance-app
```

#### Port Access Issues
```bash
# Verify ports are open
netstat -tlnp | grep -E ':(8501|8000)'

# Test locally
curl -I http://localhost:8501
curl -I http://localhost:8000
```

#### API Key Errors
- Verify keys are correctly set in environment variables
- Check for typos in key names
- Ensure keys have proper permissions

#### Memory Issues
- Monitor container resource usage: `docker stats`
- Increase EC2 instance size if needed
- Optimize chunk size and retrieval parameters

### Debug Commands
```bash
# Container status
docker ps -a

# Resource usage
docker stats insurance-app

# Interactive debugging
docker exec -it insurance-app bash

# Log monitoring
docker logs -f insurance-app
```

## 📊 Performance Optimization

### Token Management
- **Reduced Context**: Optimized prompt lengths
- **Smart Chunking**: Efficient text segmentation
- **Selective Retrieval**: Top 5 most relevant chunks
- **Rate Limiting**: Built-in request throttling

### Caching Strategy
- **Vector Cache**: ChromaDB for fast document retrieval
- **Response Cache**: Temporary storage for repeated queries
- **Model Cache**: Pre-loaded embeddings for common terms

### Monitoring
- **Health Checks**: Automated service validation
- **Error Logging**: Comprehensive error tracking
- **Performance Metrics**: Response time monitoring

## 🔒 Security Considerations

### API Key Management
- **Environment Variables**: Never hardcode keys in code
- **GitHub Secrets**: Secure CI/CD key storage
- **Rotation**: Regular key updates recommended

### Container Security
- **Non-root User**: Optional for production
- **Minimal Base Image**: Reduced attack surface
- **Resource Limits**: Prevent resource exhaustion

### Network Security
- **HTTPS**: Enable SSL for production
- **Firewall Rules**: Restrict access as needed
- **VPC**: Isolate in private networks when possible

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where applicable
- Add docstrings for new functions
- Update documentation for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

### Documentation
- **README**: This comprehensive guide
- **API Docs**: Built-in FastAPI documentation
- **Code Comments**: Inline documentation

### Issues
- **Bug Reports**: Create GitHub issues
- **Feature Requests**: Submit with detailed requirements
- **Questions**: Use GitHub discussions

---

## 🎉 Quick Deployment Summary

1. **Clone**: `git clone https://github.com/avanis55/insurance-assistant.git`
2. **Configure**: Set up GitHub secrets and environment variables
3. **Deploy**: Push to main branch (triggers CI/CD)
4. **Access**: Open `http://your-ec2-ip:8501`

**Your Containerised Multi-Agent Insurance Assistant is ready to use! 🚀**
