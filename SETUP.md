# Setup Guide

Complete setup instructions for the World News Analysis System.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection
- At least one news API key (see below)

## Step-by-Step Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `requests` - For API calls
- `sentence-transformers` - For semantic embeddings
- `scikit-learn` - For clustering
- `numpy` - For numerical operations
- `nltk` - For NLP utilities
- `newsapi-python` - NewsAPI client
- Other supporting libraries

**Note**: The first run will download the sentence-transformers model (~90MB), which may take a few minutes.

### 2. Get Free API Keys

You need at least one API key. Both are free!

#### NewsAPI (Recommended)

1. Go to https://newsapi.org
2. Click "Get API Key"
3. Sign up with your email
4. Free tier: 100 requests/day, 1 request/second
5. Copy your API key

#### Guardian API (Alternative/Additional)

1. Go to https://open-platform.theguardian.com/access/
2. Register for a developer key
3. Free tier: Unlimited requests (rate limited to 12 per second)
4. Copy your API key

### 3. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```env
NEWSAPI_KEY=abc123yourkeyhere
GUARDIAN_API_KEY=xyz789yourkeyhere

# Optional configuration
SIMILARITY_THRESHOLD=0.7
MIN_ARTICLES_PER_CLUSTER=2
ANALYSIS_LOOKBACK_DAYS=30
```

### 4. Create Data Directories

The directories should already exist, but if not:

```bash
mkdir -p data/raw data/processed data/analysis
```

### 5. Test the Installation

Check system status:

```bash
python main.py --mode status
```

You should see:
```
✅ API Configuration:
   - NewsAPI: Configured
   - Guardian API: Configured

SYSTEM STATUS
==============================================================
Storage Paths:
  raw: data/raw
  processed: data/processed
  analysis: data/analysis

Agent Status:
  news_aggregator: ready
  clusterer: ready
  rhetoric_analyzer: ready
  predictor: ready
```

### 6. Run Your First Analysis

Try a small test first:

```bash
python main.py --days 3
```

This will:
1. Fetch news from the last 3 days
2. Cluster articles into events
3. Analyze rhetoric
4. Generate predictions
5. Export a report

Expected output:
```
🚀 Starting Full News Analysis Pipeline
============================================================

📰 STEP 1: Fetching News Articles
------------------------------------------------------------
🔍 Fetching news from NewsAPI...
🔍 Fetching news from Guardian API...
📊 Generating embeddings for X articles...
✅ Collected X unique articles

🔗 STEP 2: Clustering Articles into Events
------------------------------------------------------------
📊 Clustering X articles into events...
✅ Created Y event clusters

📝 STEP 3: Analyzing Rhetoric for Each Event
------------------------------------------------------------
[Event analysis details...]

🔮 STEP 4: Generating Event Predictions
------------------------------------------------------------
[Prediction details...]

✅ Analysis Complete!
```

## Troubleshooting

### Issue: "No API keys configured"

**Solution**: Make sure you created a `.env` file with at least one API key:
```bash
cat .env  # Check if file exists and has keys
```

### Issue: "No articles collected"

**Possible causes**:
1. API keys are invalid - check your keys at the provider websites
2. API rate limit reached - wait and try again
3. No articles match search criteria - try increasing `--days`

### Issue: "Not enough articles to cluster"

**Solutions**:
- Increase time period: `python main.py --days 14`
- Lower clustering threshold in `.env`: `SIMILARITY_THRESHOLD=0.6`
- Lower minimum cluster size: `MIN_ARTICLES_PER_CLUSTER=2`

### Issue: "Module not found"

**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Model download fails

**Solution**: The sentence-transformers model will download on first run. If it fails:
```python
# Run this in Python to manually download
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

## Performance Tips

### For Faster Processing
- Use NewsAPI alone (faster than Guardian)
- Reduce `--days` parameter
- Lower `SIMILARITY_THRESHOLD` for fewer clusters

### For Better Analysis
- Use both APIs for more coverage
- Increase `--days` for more historical context
- Increase `MIN_ARTICLES_PER_CLUSTER` for higher quality clusters

## Next Steps

After successful setup:

1. **Customize search terms**: Edit `src/agents/news_aggregator.py`
2. **Adjust sensitivity**: Modify settings in `.env`
3. **Schedule regular runs**: Set up a cron job or scheduled task
4. **Explore the data**: Check `data/` directories for JSON outputs

## Recommended Workflow

### Daily Monitoring
```bash
# Morning: Get overnight news
python main.py --mode update --days 1

# Afternoon: Full analysis
python main.py --days 7 --export daily_report.txt
```

### Weekly Deep Dive
```bash
# Full 30-day analysis
python main.py --days 30 --export weekly_report.txt
```

### Custom Analysis
```bash
# Focus on specific period
python main.py --days 14 --export custom_report.txt
```

## Advanced Configuration

### Python Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Using Different Models

Edit `src/utils/nlp_utils.py` to use a different sentence-transformer model:

```python
# Faster but less accurate
self.model = SentenceTransformer('all-MiniLM-L6-v2')

# Slower but more accurate
self.model = SentenceTransformer('all-mpnet-base-v2')
```

## Getting Help

If you encounter issues:

1. Check this setup guide
2. Read the main README.md
3. Check the troubleshooting section
4. Review error messages carefully
5. Verify API keys are working at provider websites

## System Requirements

**Minimum**:
- 2GB RAM
- 1GB free disk space
- Python 3.8+
- Stable internet connection

**Recommended**:
- 4GB RAM
- 2GB free disk space
- Python 3.9+
- Fast internet connection

## Security Notes

- Never commit your `.env` file to version control
- Keep API keys private
- Regularly rotate API keys
- Monitor API usage at provider dashboards
- The `.gitignore` file is configured to protect your keys

---

You're all set! Run `python main.py` to start analyzing world news.
