# Omnicore AI

**Omnicore AI** is a boiler-plate SaaS platform for Voice AI agents, powered by **Vapi.ai**, **FastAPI**, **React**, and **Google Sheets**. It provides a robust foundation for building intelligent voice assistants that can handle calls, store leads, and send notifications.

## Features

*   **Voice AI Integration**: Seamless connection with Vapi.ai for handling inbound/outbound calls.
*   **Smart Tools**:
    *   `send_telegram_message`: Real-time notifications to Admin via Telegram.
    *   `add_to_google_sheets`: Automatically saves lead data (Name, Phone, Notes) to Google Sheets.
*   **Admin Dashboard**: React-based UI (Shadcn/UI) to view leads, logs, and manage configuration.
*   **Infrastructure Ready**:
    *   Dockerized (Frontend + Backend + Nginx + Certbot).
    *   CI/CD pipelines (GitHub Actions, Pre-commit).
    *   Production-ready logging (JSON logs, Telegram Alerts).
*   **Security**: Signature verification for Vapi webhooks (`x-vapi-secret`).

---

## Prerequisites

*   Python 3.11+
*   Node.js 18+
*   Poetry (Python dependency manager)
*   Docker & Docker Compose (for production)
*   Ngrok (for local development)

---

## Quick Start (Local Development)

### 1. Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/omnicore-ai.git
    cd omnicore-ai
    ```

2.  **Install dependencies:**
    ```bash
    poetry install
    ```

3.  **Configure Environment:**
    Copy `.env` and fill in your keys (Vapi, OpenAI, Telegram, Google).
    ```bash
    cp .env.example .env
    # Edit .env with your real API keys
    ```

4.  **Validate Setup:**
    Run the pre-flight check script to ensure all connections work.
    ```bash
    poetry run validate
    ```

5.  **Run Backend:**
    ```bash
    poetry run uvicorn app.main:app --reload
    ```
    Backend will be available at `http://localhost:8000`.

### 2. Frontend Setup

1.  **Navigate to frontend:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Run Dev Server:**
    ```bash
    npm run dev
    ```
    Frontend will be available at `http://localhost:5173`.

### 3. Expose to Internet (Ngrok)

To receive Vapi webhooks locally, you need a public URL.

```bash
ngrok http 8000
```
Update `VAPI_SERVER_URL` in your `.env` with the https address (e.g., `https://xyz.ngrok-free.app`).

---

## Production Deployment (Docker)

The project includes a production-ready `docker-compose` setup with Nginx and SSL (Certbot).

1.  **Prepare Production Config:**
    ```bash
    cp .env.prod.example .env.prod
    # Edit .env.prod
    ```

2.  **Build Frontend:**
    ```bash
    cd frontend
    npm run build
    cd ..
    ```

3.  **Start Services:**
    ```bash
    docker compose -f docker-compose.prod.yml up --build -d
    ```

4.  **Setup SSL (Certbot):**
    Run certbot to issue an SSL certificate for your domain.
    ```bash
    docker compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path /var/www/certbot -d your-domain.com
    ```
    *After obtaining the certificate, verify the SSL paths in `nginx/nginx.conf` are uncommented and restart Nginx.*

---

## Vapi Setup

1.  **Create Assistant:**
    Use the `scripts/create_assistant.py` (if available) or create manually in Vapi Dashboard.
2.  **Server URL:**
    Set the Server URL in Vapi to: `https://your-domain.com/vapi/inbound` (or `/vapi/tool` for function calls if using Server Tools mode).
3.  **Secret Token:**
    Ensure `VAPI_SECRET_TOKEN` in your `.env` matches the secret set in Vapi Dashboard -> Provider -> Custom LLM / Server URL.

---

## Validation & Testing

*   **Run Unit Tests:**
    ```bash
    poetry run pytest
    ```
*   **Validate Environment:**
    ```bash
    poetry run validate
    ```
*   **Linting:**
    ```bash
    poetry run ruff check .
    ```

---

## Project Structure

```
├── app/
│   ├── adapters/      # External API wrappers (Telegram, Google Sheets)
│   ├── api/           # Vapi Webhook Handlers
│   ├── core/          # Config, Logger, Security
│   ├── handlers/      # Route logic
│   └── main.py        # FastAPI entrypoint
├── config/            # YAML configs & Knowledge Base
├── frontend/          # React Admin Panel
├── nginx/             # Nginx reverse proxy config
├── scripts/           # Utility scripts (validate, setup)
└── tests/             # Pytest suite
```

## Troubleshooting

*   **Vapi calls failing?** Check `VAPI_SECRET_TOKEN` headers and ensure your server URL is reachable.
*   **Google Sheets error?** Ensure `GOOGLE_CREDENTIALS_JSON` service account has `Editor` access to the spreadsheet.
*   **Frontend 404 on API?** Check Nginx/Vite proxy settings. Request `/v1/leads` should map to Backend `/v1/leads`.