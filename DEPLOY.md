# Web Scraper API - Deployment Guide

**Target:** Railway.app (recommended free tier)
**ETA:** 15-20 minutes
**Cost:** Free tier ($5 credit included)

---

## Prerequisites

- [ ] Railway account (https://railway.app)
- [ ] GitHub account (already have: CyberRaccoonTeam)
- [ ] Web Scraper API repo: https://github.com/CyberRaccoonTeam/web-scraper-api

---

## Step 1: Deploy to Railway

### Option A: Deploy from GitHub (Recommended)

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Find and select: `CyberRaccoonTeam/web-scraper-api`
5. Railway will auto-detect Python and start building

### Option B: Deploy via CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
cd /home/cyber/.openclaw/workspace/web-scraper-api
railway init
railway up
```

---

## Step 2: Configure Environment Variables

In Railway dashboard, add these variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `SECRET_KEY` | `your-secret-key-here` | Generate with Python: `import secrets; print(secrets.token_hex(32))` |
| `DATABASE_URL` | `sqlite:///scraper.db` | Default (Railway supports SQLite) |
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |

---

## Step 3: Verify Deployment

Railway will provide a public URL like:
```
https://web-scraper-api-production.up.railway.app
```

**Test endpoints:**

```bash
# Health check
curl https://YOUR-URL.railway.app/api/health

# Create API key
curl -X POST https://YOUR-URL.railway.app/api/keys

# Test scrape
curl -X POST https://YOUR-URL.railway.app/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## Step 4: Add Usage Tracking (Optional)

Railway has built-in metrics. For custom tracking:

1. Add `logging` to requirements.txt
2. Log each API call to stdout
3. View logs in Railway dashboard

---

## Step 5: Set Up Billing (When Ready)

**Free tier limits:**
- $5 credit/month
- 500 hours of usage
- 1GB storage

**When you need more:**
1. Add credit card in Railway settings
2. Upgrade to Hobby plan ($5/mo)
3. Set spending limits

---

## Step 6: Add Stripe for Paid Tiers (Future)

When ready to monetize:

1. Create Stripe account
2. Add Stripe API keys to Railway env vars
3. Implement payment check in `/api/scrape` endpoint
4. Create pricing tiers in Stripe

**Suggested pricing:**
- Free: 100 requests/day
- Pro ($9/mo): 5,000 requests/day
- Business ($29/mo): Unlimited

---

## Troubleshooting

### Build Fails

**Check logs in Railway dashboard.** Common issues:
- Missing `requirements.txt` → Add it
- Wrong Python version → Add `runtime.txt` with `python-3.12`
- Port not binding → Ensure Flask binds to `0.0.0.0`

### Runtime Errors

**Check Railway logs.** Common issues:
- Missing env vars → Add in Railway dashboard
- Database errors → Use SQLite or add PostgreSQL addon
- Rate limiting issues → Check `RATE_LIMIT_ENABLED` var

---

## Post-Deployment Checklist

- [ ] Deployment successful
- [ ] Health endpoint responds
- [ ] API key creation works
- [ ] Scrape endpoint works
- [ ] Rate limiting enabled
- [ ] Logs visible in Railway
- [ ] Custom domain (optional)
- [ ] HTTPS enabled (automatic on Railway)

---

## Next Steps After Deployment

1. **Create landing page** (use `/landing` route or deploy separately)
2. **Post on Hacker News** (Show HN)
3. **Post on Reddit** (r/webdev, r/SaaS, r/programming)
4. **Tweet about it** (@raccoon_builds)
5. **Monitor usage** (Railway dashboard)
6. **Add Stripe** (when ready to charge)

---

## Alternative: Self-Hosted Deployment

If you prefer to host on Z-P3-Server:

```bash
# Install gunicorn
pip install gunicorn

# Run with Cloudflare Tunnel
cd /home/cyber/.openclaw/workspace/web-scraper-api
gunicorn -w 4 -b 127.0.0.1:5556 app:app

# Expose via Cloudflare Tunnel
cloudflared tunnel --url http://localhost:5556
```

**Pros:** Free, full control
**Cons:** Your server resources, manual SSL, less reliable

---

**Ready to deploy?** Let me know which option you prefer:
1. Railway (recommended)
2. Self-hosted with Cloudflare Tunnel
3. Different platform

🦝