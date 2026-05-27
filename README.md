# BharatStocks — Open-Source Indian Stock Market Analysis

[![CI](https://github.com/Chauhan-Mukesh/BharatStockAnalitics/actions/workflows/ci.yml/badge.svg)](https://github.com/Chauhan-Mukesh/BharatStockAnalitics/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Disclaimer:** This application is for **informational purposes only**. It is **not financial advice**. Always conduct your own research before making investment decisions.

---

## What is BharatStocks?

BharatStocks is a **free, open-source Indian stock market research and analysis platform** covering NSE and BSE listed equities. It consolidates data from multiple public sources into a single investor-focused dashboard — replacing the fragmented workflow across NSE website, BSE website, Screener, Moneycontrol, Tickertape, and more.

### Features (MVP)

| Feature | Status |
|---|---|
| Stock search (NSE + BSE) | ✅ |
| Live market quote | ✅ |
| Company overview | ✅ |
| Financial ratios (PE, PB, ROE, ROCE, D/E, margins, CAGR…) | ✅ |
| Technical indicators (RSI, MACD, SMA/EMA, BB, ATR, ADX…) | ✅ |
| Historical OHLCV charts | ✅ |
| Shareholding pattern | ✅ |
| Exchange filings (links) | ✅ |
| News with AI sentiment | ✅ |
| Risk analysis engine | ✅ |
| Peer comparison | ✅ |
| AI investment summary (local Ollama) | ✅ |
| Portfolio tracker | ✅ |
| Watchlist with alerts | ✅ |
| Android app (Kotlin + Compose) | ✅ |

---

## Repository Structure

```
BharatStockAnalitics/
├── backend-api/          # FastAPI Python backend
│   ├── app/
│   │   ├── api/v1/       # REST endpoints
│   │   ├── connectors/   # NSE, BSE, Yahoo Finance, News
│   │   ├── analytics/    # Financial ratios, technicals, risk engine
│   │   ├── ai/           # Ollama LLM client
│   │   ├── cache/        # Redis layer
│   │   ├── models/       # SQLAlchemy ORM
│   │   └── schemas/      # Pydantic schemas
│   ├── alembic/          # DB migrations
│   ├── Dockerfile
│   └── requirements.txt
│
├── workers/              # Celery async workers
│   ├── tasks/            # quotes, filings, news, metrics
│   ├── celery_app.py
│   └── Dockerfile
│
├── android-app/          # Kotlin + Jetpack Compose Android app
│   └── app/src/main/java/com/bharatstocks/
│       ├── ui/           # Compose screens & ViewModels
│       ├── data/         # Retrofit API, Repository, Models
│       └── di/           # Hilt modules
│
├── infra/                # Nginx config, Prometheus
├── tests/                # Backend unit tests
├── docs/                 # Architecture & API docs
├── docker-compose.yml    # Full stack orchestration
└── .github/workflows/    # CI/CD
```

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Android Studio (for app)

### 1. Clone & start the backend stack

```bash
git clone https://github.com/Chauhan-Mukesh/BharatStockAnalitics.git
cd BharatStockAnalitics
docker compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Ollama with Qwen2:7b (port 11434)
- FastAPI backend (port 8000 via Nginx on port 80)
- Celery worker + beat scheduler

### 2. Run DB migrations

```bash
docker compose run --rm migrations
```

### 3. Access the API

- Swagger UI: http://localhost/docs
- ReDoc: http://localhost/redoc
- Health: http://localhost/health

### 4. Open the Android app

Open `android-app/` in Android Studio, sync Gradle, and run on an emulator.
The app is pre-configured to connect to `http://10.0.2.2:8000/` (localhost from emulator).

---

## API Reference (quick)

| Endpoint | Description |
|---|---|
| `GET /api/stocks/search?q=BEL` | Search stocks |
| `GET /api/stocks/NSE/BEL/quote` | Live quote |
| `GET /api/stocks/NSE/BEL/overview` | Company overview |
| `GET /api/stocks/NSE/BEL/financials` | Ratios + statements |
| `GET /api/stocks/NSE/BEL/technicals` | Technical indicators + OHLCV |
| `GET /api/stocks/NSE/BEL/shareholding` | Shareholding pattern |
| `GET /api/stocks/NSE/BEL/filings` | Exchange filings (links) |
| `GET /api/stocks/NSE/BEL/news` | News with sentiment |
| `GET /api/stocks/NSE/BEL/risk` | Risk flags |
| `GET /api/stocks/NSE/BEL/peers` | Peer comparison |
| `GET /api/stocks/NSE/BEL/ai-summary` | AI investment summary |
| `GET /api/portfolio/{user_id}` | Portfolio summary |
| `POST /api/portfolio/{user_id}/holdings` | Add holding |
| `GET /api/watchlists/{user_id}` | Watchlists |
| `POST /api/watchlists/{user_id}` | Create watchlist |

---

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pandas numpy

# Run all tests
pytest tests/ -v
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, Uvicorn |
| Database | PostgreSQL 16 + SQLAlchemy 2 + Alembic |
| Cache | Redis 7 |
| Workers | Celery 5 + Redis broker |
| Analytics | NumPy, Pandas |
| AI | Ollama (Qwen2:7b / Mistral) |
| Connectors | httpx, BeautifulSoup4, tenacity |
| Android | Kotlin, Jetpack Compose, Hilt, Retrofit, Material 3 |
| Reverse proxy | Nginx |
| Monitoring | Prometheus + FastAPI Instrumentator |
| CI/CD | GitHub Actions |

---

## Data Sources

| Source | Used For | Access |
|---|---|---|
| NSE public API | Live quotes, shareholding, search | Free (rate-limited) |
| BSE public API | Quotes, filings, company data | Free (rate-limited) |
| Yahoo Finance | Fundamentals, financial ratios, history | Free (unofficial) |
| Google News RSS | News aggregation | Free (open) |

> **Legal note:** This app stores only document **links** — never document content — to comply with copyright. Exchange scraping is done responsibly with rate limits and delays. Always review the ToS of each data source.

---

## Configuration

Create a `.env` file in `backend-api/`:

```env
DATABASE_URL=******localhost:5432/bharatstocks
REDIS_URL=redis://localhost:6379/0
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2:7b
SECRET_KEY=your-secret-key-here
DEBUG=false
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests (`pytest tests/`)
5. Submit a pull request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Roadmap

- [ ] Phase 2: Portfolio XIRR, alerts system, advanced peer comparison
- [ ] Phase 3: AI filing summaries (PDF parsing), quarterly result analysis
- [ ] Phase 4: ETFs, mutual funds, IPO analysis, F&O data
- [ ] iOS app (Swift / Compose Multiplatform)