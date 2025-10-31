# Tehisintellekt.ee Info API
A FastAPI application that crawls the tehisintellekt.ee website with Scrapy web crawler and uses OpenAI's GPT-4o-mini to answer questions based on the collected information

### Content Overview
- Installation & Setup
- How It Works
- Chosen Packages
- TODOs Before Production
- CI/CD GitHub Actions
- Azure Deploy
- API Endpoints
- Configuration
- Project Structure
- Development (tests)


## Installation & Setup
Below are described steps for set up. Steps 2, 3, 4, 5, 6 can be avoided if Docker is used

### Prerequisites
System/Host machine dependencies. Although, with Docker no need to install Postgres and python as Docker implements own
- **Python 3.11** or higher (for manual launching e.g. without Docker)
- **PostgreSQL** database (for manual launching e.g. without Docker)
- **OpenAI API** key
- **Docker** only for docker image launch

### 1. Clone the repository
```bash
git clone tehisintellekt-web-chat-api
cd tehisintellekt-web-chat-api
```
### 2. Configure environment variables
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
OPENAI_API_KEY=sk-your-openai-api-key-here
```
### 3. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up the database
Ensure your PostgreSQL server is running and the database exists. The application will automatically create the required tables on startup. Install PostgreSQL from [the official website](https://www.postgresql.org/download/)

### 6. Start the server
```bash
uvicorn app.main:app --reload
```

### Or instead use Docker
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```
Launch Docker:
```bash
sudo docker-compose up --build # on Windows: docker-compose up
```


## How It Works
Below is described the workflow of application

### 1. **Startup & Crawling**
When the application starts, it automatically:
- Launches a Scrapy crawler e.g. spider (`text_spider.py`) in a subprocess by initialising `crawler_service.py`
- Crawls all pages on `tehisintellekt.ee` (configurable domain) by following links found by crawler for specified domain 
- Extracts and cleans text (from HTML tags, CSS properties and JavaScript code)
- Stores the cleaned content in a PostgreSQL through SQLAlchemy ORM class `page_crud.py`
- The crawler enforces a 190,000-character limit to stay safely below the 200,000-character threshold
- Initializes tables in connected database
- Creates the database schema if it does not exist
- Starts **uvicorn** server on `http://localhost:8000`

### 2. **Question Answering Flow**
When a user submits a question via the `/ask` endpoint:
- The question is validated for length (5-1000 characters)
- All crawled pages and their content are fetched from the database, if no pages are saved, a 500 error is returned
- The question and all pages content are sent to OpenAI's GPT-4o-mini model with structured output parsing
- **Response**: Returns a JSON object with:
   - The original question
   - The AI-generated answer
   - List of source URLs used
   - Token usage statistics (input/output)
   
   
## Chosen packages
Below is table of libraries that project is using
| Package | Purpose | Why Chosen |
|---------|---------|------------|
| **FastAPI** | Web framework | Required by tehisintellekt |
| **Scrapy** | Web crawling | Configurable. Functional. Concurrent. Built-in HTTP client |
| **uvicorn** | Web Server | ACGI, handles asynchronous event loops for requests |
| **SQLAlchemy** | Database ORM | Database-agnostic, type-safe/injection-safe queries, excellent migration support |
| **PostgreSQL** | Database | ACID compliance, supports multiple types (e.g. JSON) |
| **OpenAI** | AI/LLM | Effective use of OpenAI API, structured answer |
| **Pydantic** | Data validation | Automatic validation, serialization, and required by FastAPI |
| **python-dotenv** | Configuration | Secure environment variable management |
| **pytest** | Unit Tests | Configurable test environment. Common choice |


## TODOS before the production
There are certain steps that should be done before production so application would be stable and completed
- **Health check**: create script or use 3rd parties to continuously check if server is alive and notify about failures or delayed responses via email (SMTP) or phone number
- **Add JWT authentication**: web security fundamental. Can be also used for http request rate-limit
- **Set API limits**: make sure there are limits set up for OpenAI and/or create manager to track and block suspicious activity to avoid high bills
- **SSL, HTTPs**: add SSL certificate (for example in nginx with certbot), must-have
- **nginx**: reliable server for request handling and easy configuration. Also must-have for SSL
- **Logs**: add logs to capture bugs/errors and save them in log files
- **Enhance crawler**: add scheduler to have up-to-date page content, for example every 24 hours. handle users who submit questions while crawling is in progress
- **Adjust response**: if API is used inside messenger (like browser popups with messenger like support) the usual ChatGPT response could be too overwhelming to read
- **Caching**: Add caching to reduce server load


## CI/CD GitHub Actions
This setup ensures a continuous integration and deployment flow: all branches are tested before merging, and the production environment is updated automatically and safely whenever the main branch changes

- **Secrets**: add secrets (OpenAI API key, SSH private key, server credentials) in **GitHub Secrets**. These will be accessed during workflow execution through environment variables
- **Configure Script**: create a workflow file called `.github/workflows/deploy.yml` that defines automated steps for testing and deployment
  - On **feature branches**, the workflow should **only run tests** (using `pytest`) to verify that new code changes don’t break the application. Every new feature should go through a pull request and team review before merging
  - On **main branch**, after successful tests, it should **deploy automatically** to the production server via SSH. The script will:
    - Connect to the remote server using the SSH key stored in secrets
    - Pull the latest code from the repository
    - Rebuild and restart the Docker containers
    - Load required environment variables (e.g., `OPENAI_API_KEY`, `DATABASE_URL`) from GitHub secrets into the `.env` file


## Azure Deploy
To deploy Web Chat API backend application these steps could be performed:
- Push Docker image to AZR (Azure Container Registry)
- Use Azure database for Postgres
- Add load balancer with horizontal expansion (for current application it is almost meaningless, except it would grow into larger one)


## API Endpoints

### `GET /health`
Health check endpoint
```json
{
  "status": "healthy"
}
```

### `GET /source_info`
Returns all crawled pages and their content
```json
{
  "https://tehisintellekt.ee/": "Page content...",
  "https://tehisintellekt.ee/about": "About page content..."
}
```

### `POST /ask`
Ask a question based on crawled content

**Request Body:**
```json
{
  "question": "What services does the company offer?"
}
```

**Response:**
```json
{
  "question": "What services does the company offer?",
  "answer": "Based on the website, the company offers...",
  "sources": [
    "https://tehisintellekt.ee/services",
    "https://tehisintellekt.ee/"
  ],
  "usage": {
    "input_tokens": 1250,
    "output_tokens": 87
  }
}
```

**Error Responses:**
- `400 Bad Request` - Question validation failed (too short/long or empty)
- `500 Internal Server Error` - No information available or processing error



## Configuration
Edit `app/config.py` to customize:

```python
DOMAIN = 'tehisintellekt.ee'  # Website to crawl, should be target domain 
MAX_QUESTION_LENGTH = 1000    # Maximum question length
MIN_QUESTION_LENGTH = 5       # Minimum question length
MAX_CONTENT_SIZE = 190000     # Maximum total content size (characters)
CHATGPT_MODEL = "gpt-4o-mini" # OpenAI model to use
```

Crawler settings in `crawler/text_spider.py`:
```python
custom_settings = {
    "DEPTH_LIMIT": 0,      # Unlimited depth
    "DOWNLOAD_DELAY": 0.5,  # 0.5 seconds between requests
}
```
and in `crawler/settings.py`:
```python
BOT_NAME = 'crawler'
SPIDER_MODULES = ['crawler']
NEWSPIDER_MODULE = 'crawler'
LOG_ENABLED = True 
```

## Project Structure

```
.
├── app/
│   ├── api/routes/        # API route definitions
│   ├── db/                # Database models and connection
│   ├── dtos/              # Data transfer objects (Pydantic models)
│   ├── cruds/             # Database CRUD 
│   ├── services/          # Business logic layer
│   ├── config.py          # Application configuration
│   └── main.py            # FastAPI application entry point
├── crawler/
│   ├── text_spider.py     # Scrapy spider for web crawling
│   └── settings.py        # Scrapy configuration
├── tests/                 # Test files
├── .env                   # Environment variables (create this)
└── requirements.txt       # Python dependencies
```


## Development

### Running tests
```bash
pytest
```

### Code structure
- **Services Layer**: Business logic (validation, OpenAI integration, crawling). It is designed for `app_service.py` to contain main business logic and make decision, e.g. middleware/bridge between user request and app functionality. It is easier to handle errors from dependencies (database, OpenAI)  and structure detailed output to back to user.
- **CRUD Layer**: Database operations
- **DTOs**: Request/response models.
- **API Routes**: HTTP endpoint handlers e.g. controller
- **tests**: For unit testing of services
- **Crawler**: Scrapy web crawler default project


