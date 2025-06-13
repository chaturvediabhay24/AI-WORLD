# AI World - AI Agents Framework

A flexible and extensible AI agents framework built with FastAPI and LangChain, supporting multiple model providers and streaming responses.

## Features

- 🚀 FastAPI-based REST API
- 🔄 Real-time streaming responses
- 🔌 Pluggable model provider system
- 🗄️ PostgreSQL database for persistence
- 📝 Chat history tracking
- 🔐 API key management
- 📚 OpenAPI/Swagger documentation

## Setup Instructions

### Prerequisites

- Python 3.9+
- PostgreSQL
- Poetry (Python package manager)

### Installation

1. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-world
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration:
   # - Database credentials
   # - API keys for model providers
   ```

5. Create databases:
   ```bash
   # For development
   createdb ai_world
   
   # For testing
   createdb ai_world_test
   ```

### Running the Server

1. Development server with auto-reload:
   ```bash
   poetry run start
   ```

2. Production server:
   ```bash
   poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

## API Documentation

### Model Providers API

#### Register a Provider
```http
POST /api/v1/providers/
```
```json
{
  "name": "openai",
  "api_key": "your-api-key",
  "config": {
    "model_name": "gpt-3.5-turbo",
    "temperature": 0.7
  }
}
```

#### List Providers
```http
GET /api/v1/providers/
```

#### Get Provider Details
```http
GET /api/v1/providers/{provider_id}
```

#### Update Provider
```http
PUT /api/v1/providers/{provider_id}
```
```json
{
  "name": "openai",
  "config": {
    "model_name": "gpt-4",
    "temperature": 0.5
  }
}
```

#### Delete Provider
```http
DELETE /api/v1/providers/{provider_id}
```

### Chat API

#### Send Message
```http
POST /api/v1/chat/chat
```
```json
{
  "message": "Hello, how are you?",
  "model_provider_id": 1,
  "stream": false,
  "metadata": {
    "user_id": "123",
    "session_id": "abc"
  }
}
```

#### Stream Chat Response
```http
POST /api/v1/chat/chat/stream
```
```json
{
  "message": "Tell me a story",
  "model_provider_id": 1,
  "stream": true
}
```

#### Get Chat History
```http
GET /api/v1/chat/history/{provider_id}
```

## Development

### Project Structure
```
app/
├── api/
│   └── v1/
│       ├── chat.py      # Chat endpoints
│       └── providers.py # Provider management
├── core/
│   └── config.py        # App configuration
├── database/
│   └── base.py          # Database setup
├── models/
│   └── models.py        # SQLAlchemy models
├── schemas/
│   └── schemas.py       # Pydantic schemas
├── services/
│   ├── base.py          # Base service class
│   ├── factory.py       # Service factory
│   └── openai_service.py # OpenAI implementation
└── main.py              # Application entry
```

### Running Tests

1. Run all tests:
   ```bash
   poetry run pytest
   ```

2. Run with coverage:
   ```bash
   poetry run pytest --cov=app
   ```

3. Run specific test file:
   ```bash
   poetry run pytest tests/test_api.py
   ```

### Code Quality

1. Format code:
   ```bash
   poetry run black app/
   ```

2. Sort imports:
   ```bash
   poetry run isort app/
   ```

3. Lint code:
   ```bash
   poetry run flake8 app/
   ```

### Debugging

1. Enable debug logs in .env:
   ```
   LOG_LEVEL=DEBUG
   ```

2. Debug database queries by setting echo=True in database/base.py:
   ```python
   engine = create_async_engine(settings.get_database_url, echo=True)
   ```

3. Use FastAPI's debug mode:
   ```bash
   poetry run uvicorn app.main:app --reload --log-level debug
   ```

### Adding New Model Providers

1. Create a new service class in `app/services/`:
   ```python
   from app.services.base import BaseModelService

   class NewProviderService(BaseModelService):
       async def initialize_model(self) -> None:
           # Initialize your model
           pass

       async def generate_response(self, message: str) -> str:
           # Generate response
           pass

       async def generate_stream(self, message: str) -> AsyncGenerator[str, None]:
           # Generate streaming response
           pass
   ```

2. Register in factory:
   ```python
   ModelServiceFactory.register_service("new_provider", NewProviderService)
   ```

## Common Issues & Solutions

1. Database Connection:
   - Ensure PostgreSQL is running
   - Check database credentials in .env
   - Verify database exists: `psql -l`

2. Model Provider Errors:
   - Verify API keys in .env
   - Check provider configuration
   - Enable debug logging for detailed errors

3. Import Errors:
   - Ensure you're using Poetry's virtual environment
   - Check package versions in pyproject.toml
   - Try removing poetry.lock and reinstalling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License
