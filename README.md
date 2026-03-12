# Web Scraper API

> Turn any website into structured JSON data with a single API call.

## Features

- 🔗 **URL to JSON** — Send a URL, get clean structured data
- 🔑 **API Keys** — Secure access with rate limiting
- 📊 **Usage Dashboard** — Track requests, limits, and stats
- ⚡ **Fast Extraction** — BeautifulSoup + smart selectors
- 🛡️ **Anti-Bot Evasion** — Rotating user agents, delays

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
python app.py

# Test scrape
curl -X POST http://localhost:5556/api/scrape \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://news.ycombinator.com"}'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scrape` | POST | Scrape a URL and return JSON |
| `/api/keys` | GET | List your API keys |
| `/api/keys` | POST | Generate new API key |
| `/api/usage` | GET | Get usage statistics |
| `/health` | GET | Health check |

## Pricing (Target)

| Plan | Requests/mo | Price |
|------|-------------|-------|
| Free | 100 | $0 |
| Starter | 5,000 | $9/mo |
| Pro | 50,000 | $29/mo |
| Enterprise | Unlimited | $99/mo |

## Stack

- **Backend:** Python 3.12 + Flask
- **Scraping:** BeautifulSoup4 + Requests
- **Database:** SQLite (upgradeable to PostgreSQL)
- **Rate Limiting:** Flask-Limiter

## Roadmap

- [x] MVP: Basic scrape endpoint
- [x] API key authentication
- [ ] Rate limiting per key
- [ ] Usage dashboard UI
- [ ] Custom extraction rules
- [ ] Webhook notifications
- [ ] Browser rendering (Playwright)

## Revenue Target

$300-1500/month

---

Built by 🦝 Raccoon | Part of [TheKeepersTeam](https://github.com/TheKeepersTeam)