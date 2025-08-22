# Job Analysis FastAPI Project

## Overview
This project is a FastAPI application designed for job analysis functionality. It provides a webhook for receiving job-related data and processes it using various services. The application is structured to follow production-grade best practices, ensuring maintainability and scalability.

## Project Structure
```
job-analysis-fastapi
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1
│   │       ├── __init__.py
│   │       ├── api.py
│   │       └── endpoints
│   │           ├── __init__.py
│   │           ├── webhooks.py
│   │           └── jobs.py
│   ├── models
│   │   ├── __init__.py
│   │   └── job.py
│   ├── schemas
│   │   ├── __init__.py
│   │   └── job.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── job_analysis.py
│   │   └── llm_service.py
│   └── utils
│       ├── __init__.py
│       └── logging.py
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_webhooks.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
└── README.md
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd job-analysis-fastapi
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   or
   uv add -r requirements.txt
   ```

4. **Environment Variables**
   Copy the `.env.example` to `.env` and fill in the required environment variables.

5. **Run the Application**
   ```bash
   uv run fastapi dev app/main.py
   ```

## Usage
- The application exposes a webhook endpoint for job analysis. You can send POST requests to the `/api/v1/webhooks` endpoint with job-related data.
- Additional endpoints for managing job data can be found under `/api/v1/jobs`.

### Webhook Security
Both incoming webhook requests and outgoing callback responses use HMAC-SHA256 signatures for security:

#### For Incoming Webhooks:
- Include `X-Webhook-Signature: sha256={hash}` header
- Hash is generated using the request payload and `WEBHOOK_SECRET`

#### For Outgoing Callbacks:
- When `async_processing=true` and a `callback_url` is provided, the service will send results to your callback URL
- The callback includes `X-Webhook-Signature` header for verification
- Use the provided `verify_callback_signature()` utility function to verify authenticity

```python
from app.utils.llm_data_postprocessing import verify_callback_signature

# At your callback endpoint
payload = request.body.decode('utf-8')  # Raw JSON string  
signature = request.headers.get('X-Webhook-Signature')
if verify_callback_signature(payload, signature, 'your-webhook-secret'):
    # Process callback safely
    data = json.loads(payload)
else:
    # Reject invalid callback
    return 401
```

## Testing
- To run the tests, use the following command:
  ```bash
  pytest
  ```


Step 1: Understand the Signature Process
Webhook signatures typically work like this:

Create your JSON payload
Generate HMAC-SHA256 hash using a secret key
Send the signature in a specific header

Step 2: Manual Preparation Methods
Option A: Using Python Script
   Create a helper script to generate the signature:

```bash
import hmac
import hashlib
import json

# Your webhook secret (get this from your application config)
WEBHOOK_SECRET = "your-webhook-secret-key"

# Your payload
payload = {
    "job_id": "test-job-123",
    "url": "https://example.com/job-posting",
    "async_processing": True,
    "callback_url": "https://your-callback-url.com/webhook"
}

# Convert to JSON string
payload_json = json.dumps(payload, separators=(',', ':'))
print(f"Payload: {payload_json}")

# Generate signature
signature = hmac.new(
    WEBHOOK_SECRET.encode('utf-8'),
    payload_json.encode('utf-8'),
    hashlib.sha256
).hexdigest()

print(f"Signature: sha256={signature}")
print(f"Full header value: sha256={signature}")
```

Option B: Using curl with OpenSSL
````bash
# Set your variables
WEBHOOK_SECRET="your-webhook-secret-key"
PAYLOAD='{"job_id":"test-job-123","url":"https://example.com/job-posting","async_processing":true,"callback_url":"https://your-callback-url.com/webhook"}'

# Generate signature
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" | sed 's/^.* //')

# Make the request
curl -X POST "http://localhost:8000/api/v1/webhooks/job-analysis" \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=$SIGNATURE" \
  -d "$PAYLOAD"
```

Step 4: Complete cURL Example
```
curl -X POST "http://localhost:8000/api/v1/webhooks/job-analysis" \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=YOUR_GENERATED_SIGNATURE" \
  -d '{
    "job_id": "test-job-123",
    "url": "https://example.com/job-posting",
    "async_processing": true,
    "callback_url": "https://your-callback-url.com/webhook"
  }'
```
## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.