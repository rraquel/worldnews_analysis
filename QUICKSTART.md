# Quick Start Guide

Get started with World News Analysis in 5 minutes!

## TL;DR

```bash
# 1. Install
pip install -r requirements.txt

# 2. Get API keys (free)
# - NewsAPI: https://newsapi.org
# - Guardian: https://open-platform.theguardian.com

# 3. Configure
cp .env.example .env
# Edit .env and add your keys

# 4. Run
python main.py
```

## What This System Does

Imagine you want to track how the media talks about "Trump and Greenland" over time:

**Without this system:**
- Manually search multiple news sites daily
- Try to remember what was said yesterday vs today
- Guess if the situation is getting better or worse
- Miss related articles from other sources

**With this system:**
- Automatically collects all relevant articles
- Groups them by topic (e.g., "Trump - Greenland - territorial")
- Tracks how the language changes: "negotiation" → "threat" → "warning"
- Predicts: "This is **escalating** with 75% confidence"
- Generates a full report with insights

## Real Example

You run:
```bash
python main.py --days 7
```

The system:
1. **Fetches** 50 articles about geopolitical events from the last 7 days
2. **Groups** them into 5 events:
   - Trump - Greenland - territorial (12 articles)
   - Ukraine - Russia - ceasefire (18 articles)
   - China - Taiwan - military (8 articles)
   - Middle East - conflict (7 articles)
   - NATO - expansion (5 articles)

3. **Analyzes** each event:
   ```
   Event: Trump - Greenland
   Rhetoric shift: neutral → negative (deteriorating)
   New keywords: "threat", "warning", "sovereignty"
   Urgency: HIGH (indicators: immediate, warning, threat)
   ```

4. **Predicts**:
   ```
   Trajectory: ESCALATING
   Confidence: 72%
   Short-term: Expect increased rhetoric and diplomatic statements
   Risk factors:
   - High urgency indicators
   - Multiple actors involved
   - Territorial dispute language
   ```

5. **Generates Report**: Detailed analysis saved to file

## Key Features in Action

### Automatic Event Detection
Articles about "Trump threatens Greenland", "Denmark responds to Trump", and "Greenland sovereignty debate" are automatically grouped together.

### Rhetoric Evolution Tracking
```
Day 1: "Trump expresses interest in Greenland"
Day 3: "Trump insists on Greenland acquisition"
Day 5: "Trump threatens to use economic leverage"
Day 7: "Denmark calls Trump's comments concerning"

Analysis: Tone shifted from neutral → negative
          Language became more aggressive
          Prediction: ESCALATING
```

### Multi-Event Comparison
```
Most negative: Ukraine - Russia (sentiment: -0.6)
Most urgent: Middle East - conflict (15 urgency indicators)
Most active: Trump - Greenland (2.4 articles/day)
```

## Use Cases

### 1. Risk Monitoring
Track specific regions or topics daily:
```bash
python main.py --mode update --days 1
```
Get alerts when rhetoric shifts toward escalation.

### 2. Research
Analyze how media framing evolved over a crisis:
```bash
python main.py --days 30 --export ukraine_analysis.txt
```

### 3. Competitive Intelligence
Monitor how different actors (countries, leaders) are portrayed in geopolitical contexts.

### 4. Trend Forecasting
Predict which events are likely to escalate vs stabilize based on linguistic patterns.

## Understanding the Output

### Event Cluster
```
EVENT: Trump - Greenland - territorial
Articles: 15
Keywords: greenland, trump, territory, sovereignty, denmark
Time: 2026-01-08 to 2026-01-15
```
↳ The system found 15 related articles about this topic

### Rhetoric Analysis
```
Tone: neutral → negative (deteriorating)
Sentiment change: -0.4 (getting more negative)
New keywords: threat, sovereignty, warning
```
↳ Language is becoming more hostile

### Prediction
```
Trajectory: ESCALATING
Confidence: 72%
Risk factors: 3
```
↳ Situation likely to intensify (72% confident)

## Common Commands

**Daily monitoring:**
```bash
# Morning check
python main.py --mode update --days 1

# Weekly overview
python main.py --days 7
```

**Deep analysis:**
```bash
# Last month
python main.py --days 30

# With custom export
python main.py --days 14 --export my_analysis.txt
```

**Quick check:**
```bash
# System status
python main.py --mode status

# Use cached data (no API calls)
python main.py --use-existing
```

## Tips

### Start Small
Begin with `--days 3` to test the system without using many API credits.

### Check Daily
Run `--mode update --days 1` each day to track evolving events.

### Adjust Sensitivity
If you get too many small clusters, increase `SIMILARITY_THRESHOLD` in `.env`.

### Customize Topics
Edit `src/agents/news_aggregator.py` to focus on specific keywords:
```python
self.search_terms = [
    'Your specific topic',
    'Another topic you care about',
]
```

## What You Get

### 1. JSON Data
Raw data for programmatic access:
- `data/raw/` - Original articles
- `data/processed/` - Clustered events
- `data/analysis/` - Predictions and analyses

### 2. Text Reports
Human-readable analysis:
```
data/analysis/analysis_report_20260115_143022.txt
```

### 3. Actionable Insights
- Which events are escalating
- Which are stabilizing
- What to monitor next

## Example Workflow

### Scenario: Monitoring International Relations

**Monday - Initial Setup:**
```bash
python main.py --days 7
```
Result: Identified 8 major events, 2 escalating

**Tuesday-Friday - Daily Updates:**
```bash
python main.py --mode update --days 1
```
Result: Tracked how those events evolved

**Friday - Weekly Report:**
```bash
python main.py --days 7 --export week1_report.txt
```
Result: Full analysis of the week's developments

**Outcome:**
- Early warning on escalating tensions
- Understanding of rhetoric patterns
- Data-driven insights for decision making

## Next Steps

1. **Run your first analysis**: `python main.py --days 3`
2. **Read the full README**: More details on features
3. **Customize**: Edit search terms and settings
4. **Automate**: Set up daily cron jobs
5. **Analyze**: Use the data for your research/monitoring

## Questions?

- **Setup issues?** See SETUP.md
- **Want more details?** See README.md
- **Technical questions?** Check the code comments

---

Ready? Run `python main.py` and start analyzing!
