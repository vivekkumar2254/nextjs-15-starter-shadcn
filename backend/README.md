# SuccessFactors WebDriver Backend

A Selenium-based scraper for SuccessFactors login automation. Handles the complete login flow including company entry page.

## Setup

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment** (for standalone script):
   Edit `.env` with your credentials:

   ```bash
   SF_COMPANY_ID=your_company_id
   SF_USERNAME=your_username
   SF_PASSWORD=your_password
   ```

## Usage

### Standalone Script

Run the scraper:

```bash
python main.py
```

### FastAPI Service

Run the API server:

```bash
python api.py
```

The API will be available at `http://localhost:8000`

#### Endpoints

- `GET /` - API information
- `POST /permission-groups` - Extract permission groups data
- `POST /roles-data` - Extract roles data with permissions (supports pagination)

#### API Usage Example

```bash
# Get permission groups
curl -X POST "http://localhost:8000/permission-groups" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password",
    "company_name": "your_company_id"
  }'

# Get roles data
curl -X POST "http://localhost:8000/roles-data" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password",
    "company_name": "your_company_id",
    "page": 1,
    "page_size": 50
  }'
```

## Configuration

| Variable | Description |
|----------|-------------|
| `SF_COMPANY_ID` | SuccessFactors Company ID (required) |
| `SF_USERNAME` | Your username (required) |
| `SF_PASSWORD` | Your password (required) |
| `HEADLESS` | Run in headless mode (default: False) |
| `IMPLICIT_WAIT` | Element wait timeout in seconds (default: 10) |
| `PAGE_LOAD_TIMEOUT` | Page load timeout in seconds (default: 30) |

## Features

- Automatic company entry page handling
- Robust element detection with multiple selectors
- Screenshot capture for debugging
- Comprehensive error handling and logging
- Context manager support for easy cleanup
