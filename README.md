# World News Analysis System

A sophisticated multi-agent system for analyzing geopolitical news, tracking rhetoric evolution, and predicting event trajectories.

## Overview

This system uses AI agents to automatically:
- 📰 **Aggregate news** from multiple international sources (NewsAPI, Guardian, BBC, Euronews, Deutsche Welle, France 24, CGTN, China Daily, Xinhua, Al Jazeera, RT)
- 🌍 **Multi-language support** with automatic translation from Chinese, German, French, Russian, and other languages
- 🔗 **Cluster articles** by event using semantic similarity
- 📝 **Analyze rhetoric** and language patterns over time
- 🔮 **Predict trajectories** (escalating, de-escalating, or stable)
- 📊 **Generate reports** with insights and forecasts

Perfect for tracking geopolitical events like territorial disputes, diplomatic crises, international relations, trade tensions, and more.

## Features

### Multi-Agent Architecture
- **NewsAggregatorAgent**: Collects news from free APIs with intelligent filtering
- **EventClusteringAgent**: Groups related articles using semantic embeddings
- **RhetoricAnalyzerAgent**: Analyzes language patterns, sentiment, and tone shifts
- **PredictionAgent**: Forecasts event trajectories and identifies risk factors
- **CoordinatorAgent**: Orchestrates all agents for seamless operation

### Advanced Analysis
- Sentiment trend analysis over time
- Tone shift detection (improving/deteriorating/stable)
- Urgency indicator tracking
- Actor/entity mention tracking (countries, leaders, organizations)
- Cross-event comparison
- Risk factor identification
- Confidence scoring

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd worldnews_analysis
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API keys

Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
# Get your free API keys from:
# NewsAPI: https://newsapi.org (100 requests/day free)
# Guardian: https://open-platform.theguardian.com (unlimited free)

NEWSAPI_KEY=your_newsapi_key_here
GUARDIAN_API_KEY=your_guardian_api_key_here

# Optional settings
SIMILARITY_THRESHOLD=0.7
MIN_ARTICLES_PER_CLUSTER=2
ANALYSIS_LOOKBACK_DAYS=30
```

**Note**: You need at least one API key (NewsAPI or Guardian) for the system to work.

## Usage

### Basic Usage

Run a complete analysis of the last 7 days:
```bash
python main.py
```

### Advanced Usage

**Full analysis with custom time period:**
```bash
python main.py --mode full --days 14
```

**Update existing analysis with new articles:**
```bash
python main.py --mode update --days 1
```

**Check system status:**
```bash
python main.py --mode status
```

**Use existing data (skip fetching):**
```bash
python main.py --use-existing
```

**Export report to specific file:**
```bash
python main.py --export my_report.txt
```

### Command-line Options

```
--mode {full,update,status}   Operation mode (default: full)
--days N                       Number of days to look back (default: 7)
--use-existing                 Use existing articles instead of fetching
--export FILENAME              Export report to specified file
```

## Output

### Analysis Report

The system generates a comprehensive report including:

1. **Executive Summary**: Overview of events and articles analyzed
2. **Event-by-Event Analysis**: Detailed breakdown for each event
   - Article count and time period
   - Keywords and key phrases
   - Rhetoric analysis (tone shifts, trends)
   - Trajectory prediction (escalating/de-escalating/stable)
   - Confidence score
   - Risk factors
   - Short-term and medium-term outlooks

3. **Cross-Event Comparison**:
   - Most negative/positive events
   - Most urgent events
   - Most active (highest coverage)

### Example Output

```
EVENT: Trump - Greenland - territorial
=====================================

Articles: 15
Time Period: 2026-01-08 to 2026-01-15
Keywords: greenland, trump, territory, sovereignty, denmark

Rhetoric Analysis:
  Tone: neutral → negative
  Trend: deteriorating
  Rhetoric Evolution: The rhetoric has shifted from neutral to negative,
  indicating a deterioration in tone. Urgency indicators such as 'warning,
  threat, immediate' suggest heightened concern.

Prediction:
  Trajectory: ESCALATING
  Confidence: 72%
  Short-term Outlook: Situation likely to intensify. Expect increased
  media coverage, possible diplomatic statements, and heightened rhetoric.

  Risk Factors:
    - High level of urgency indicators suggest rapid escalation risk
    - Multiple actors involved (trump, denmark, usa), increasing complexity
    - Presence of high-risk keywords: territorial, sovereignty
```

## Data Storage

All data is stored in the `data/` directory:

```
data/
├── raw/              # Original articles (JSON)
├── processed/        # Clustered events (JSON)
└── analysis/         # Rhetoric analyses and predictions (JSON, TXT)
```

Data is timestamped and versioned, allowing historical analysis.

## How It Works

### 1. News Aggregation
- Fetches articles from **12 international news sources** via APIs and RSS feeds:
  - **English APIs**: NewsAPI, Guardian
  - **European RSS**: BBC World, Euronews, Deutsche Welle, France 24, EUobserver
  - **Chinese/Asian RSS**: CGTN, China Daily, Xinhua
  - **Middle East**: Al Jazeera
  - **Russian perspective**: RT World
- **Automatic translation** from non-English sources (Chinese, German, French, Russian, Arabic)
- Intelligent geopolitical content filtering
- Extracts title, subtitle, description, and metadata
- Generates semantic embeddings for each article
- Performs basic sentiment analysis

### 2. Event Clustering
- Uses DBSCAN clustering with cosine similarity on embeddings
- Groups articles discussing the same event
- Automatically names events based on entities and keywords
- Tracks temporal evolution of events

### 3. Rhetoric Analysis
- Analyzes sentiment trends over time
- Detects tone shifts (initial vs. current)
- Identifies urgency indicators (crisis, urgent, immediate, etc.)
- Tracks actor mentions (countries, leaders, organizations)
- Extracts key phrases and their evolution

### 4. Trajectory Prediction
- Determines if event is escalating, de-escalating, or stable
- Calculates confidence based on data quality and consistency
- Identifies risk factors and key indicators
- Generates short-term (7 days) and medium-term (30 days) outlooks
- Compares to historical patterns

## Customization

### Adding Custom Keywords

Edit `src/agents/news_aggregator.py` to add your own search terms:

```python
self.search_terms = [
    'Your custom topic',
    'Another topic',
    # ... more topics
]
```

### Adjusting Clustering Sensitivity

In your `.env` file:
```env
SIMILARITY_THRESHOLD=0.6  # Lower = more clusters (0.5-0.9)
MIN_ARTICLES_PER_CLUSTER=3  # Minimum articles per cluster
```

### Changing Analysis Period

In your `.env` file:
```env
ANALYSIS_LOOKBACK_DAYS=60  # Analyze last 60 days
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           CoordinatorAgent (Orchestrator)           │
└─────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
┌──────────────────┐ ┌────────────┐ ┌──────────────┐
│ NewsAggregator   │ │  Event     │ │  Rhetoric    │
│ Agent            │ │  Clustering│ │  Analyzer    │
│                  │ │  Agent     │ │  Agent       │
└──────────────────┘ └────────────┘ └──────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  Prediction    │
                  │  Agent         │
                  └────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  Reports &     │
                  │  Predictions   │
                  └────────────────┘
```

## Use Cases

- **Geopolitical Analysis**: Track international conflicts and tensions
- **Risk Assessment**: Identify escalating situations early
- **Trend Forecasting**: Predict where events are heading
- **Media Monitoring**: Understand how events are being framed
- **Research**: Study rhetoric evolution in real-time

## Example Scenarios

### Scenario 1: Monitoring a Developing Crisis
```bash
# Initial analysis
python main.py --days 7

# Daily updates
python main.py --mode update --days 1
```

### Scenario 2: Deep Historical Analysis
```bash
# Analyze last 30 days
python main.py --days 30 --export historical_analysis.txt
```

### Scenario 3: Quick Status Check
```bash
# Check system and recent data
python main.py --mode status
python main.py --use-existing
```

## Limitations

- **API Rate Limits**: Free APIs have request limits (NewsAPI: 100/day)
- **Translation Quality**: Auto-translation may not capture nuances in some languages
- **Simple Predictions**: Based on rhetoric analysis, not political expertise
- **Free APIs**: Limited to freely available article information (no full text)
- **RSS Feed Coverage**: RSS feeds provide less article detail than full APIs

## Future Enhancements

Potential improvements:
- Additional news sources (Reuters API, Associated Press, etc.)
- Enhanced translation with context awareness
- Interactive web dashboard
- Historical pattern database
- Integration with academic datasets
- Real-time monitoring mode
- Email/Slack alerts for escalating events
- Multi-language sentiment analysis (currently English-based after translation)

## Troubleshooting

### "No articles collected"
- Check your API keys in `.env`
- Verify internet connection
- Check API quota limits

### "Not enough articles to cluster"
- Increase `--days` parameter
- Lower `SIMILARITY_THRESHOLD` in `.env`
- Lower `MIN_ARTICLES_PER_CLUSTER` in `.env`

### "Module not found" errors
- Run `pip install -r requirements.txt`
- Ensure you're in the correct directory

## Contributing

Contributions are welcome! Areas for improvement:
- Additional news sources
- Better NLP models
- Improved prediction algorithms
- Visualization tools
- Web interface

## License

[Add your license here]

## Disclaimer

This system is for informational and research purposes only. Predictions are based on linguistic analysis and should not be used as the sole basis for important decisions. Always consult multiple sources and expert analysis for critical geopolitical assessments.

## Contact

[Add your contact information]

---

Built with ❤️ using Python, sentence-transformers, and scikit-learn.
