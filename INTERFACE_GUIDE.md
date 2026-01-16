# Global Conflict Analysis Interface

An interactive web interface for analyzing global conflicts and emerging threats that could affect world order.

## Features

### 🌍 Topic Selection
- **20 Predefined Global Conflict Topics** covering:
  - Active conflicts (Ukraine-Russia, Israel-Palestine, Yemen, Syria, etc.)
  - Territorial disputes (China-Taiwan, Kashmir, South China Sea, etc.)
  - Nuclear proliferation (Iran, North Korea)
  - Emerging threats (Cyber warfare, Space militarization, Climate security, AI weapons)
  - Economic conflicts (US-China tech war)
  - Political instability (Venezuela, Myanmar, Ethiopia)

- **Flexible Filtering**:
  - By risk level (Critical, High, Medium, Low)
  - By category (Active Conflict, Territorial Dispute, Proliferation, etc.)
  - Select multiple topics or analyze all discovered events

### 📊 Analysis Depth
Choose from three analysis levels:

1. **Quick Overview**
   - 3 days of data
   - Up to 50 articles
   - Basic clustering and sentiment analysis
   - Fast results (~30 seconds)

2. **Standard Analysis** (Recommended)
   - 7 days of data
   - Up to 150 articles
   - Full rhetoric analysis with topic modeling
   - Trajectory predictions
   - Cross-event analysis
   - Typical runtime: 1-2 minutes

3. **Deep Analysis**
   - 14 days of data
   - Up to 300 articles
   - Comprehensive analysis with historical comparison
   - Advanced topic modeling
   - Detailed visualizations
   - Runtime: 2-5 minutes

### 📈 Visualizations

The interface provides rich visualizations including:

1. **Rhetoric Timeline**
   - Sentiment evolution over time
   - Tone shift indicators
   - Article frequency distribution
   - Urgency markers

2. **Sentiment Heatmap**
   - Cross-event sentiment comparison
   - Temporal patterns
   - Color-coded intensity

3. **Prediction Dashboard**
   - Trajectory distribution (escalating/stable/de-escalating)
   - Confidence scores by event
   - Risk factor analysis

4. **Topic Visualization**
   - Key topics per event with relevance scores
   - Temporal trends (increasing/decreasing/stable)
   - Representative keywords

5. **Actor Network**
   - Key actors mentioned
   - Frequency of mentions
   - Visual ranking

### 🏷️ Topic Modeling

Advanced topic modeling using BERTopic:
- Automatic discovery of sub-themes within each conflict
- Temporal analysis showing how topics evolve
- Coherence scoring for topic quality
- Sample articles for each topic
- Cross-cluster theme comparison

### 📝 Comprehensive Reports

Each analysis includes:
- **Executive Summary**: Overall statistics and key findings
- **Event-by-Event Analysis**:
  - Rhetoric evolution narrative
  - Tone shift analysis (initial → current)
  - Urgency indicators
  - Actor identification
  - Topic breakdown
- **Trajectory Predictions**:
  - Escalating/stable/de-escalating classification
  - Confidence scores
  - Key indicators
  - Short-term (7-day) outlook
  - Medium-term (30-day) outlook
  - Risk factors
- **Article Listings**: Access to source articles

### 💾 Export Options

- **Text Report**: Human-readable comprehensive report
- **JSON Export**: Structured data for further analysis

## Getting Started

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (copy `.env.example` to `.env`):
```bash
cp .env.example .env
```

3. Add your API keys to `.env`:
```
NEWSAPI_KEY=your_newsapi_key_here
GUARDIAN_API_KEY=your_guardian_key_here
```

### Launching the Interface

Run the Streamlit app:
```bash
streamlit run app.py
```

The interface will open in your default web browser at `http://localhost:8501`

### Using the Interface

1. **Configure Analysis**:
   - Select analysis depth in the sidebar (Quick/Standard/Deep)
   - Choose topic selection mode:
     - Select specific predefined topics
     - Or analyze all discovered events

2. **Filter Topics** (if using predefined topics):
   - Filter by risk level or category
   - Check boxes for topics of interest
   - View topic details (description, risk level, category)

3. **Run Analysis**:
   - Click "Run Analysis" button
   - Wait for progress bar to complete
   - Analysis time varies by depth level

4. **Explore Results**:
   - View summary statistics
   - Examine prediction dashboard
   - Check sentiment heatmap
   - Dive into individual events with tabs:
     - Rhetoric Timeline
     - Topics
     - Actors
     - Report
     - Articles

5. **Export Results**:
   - Download text report
   - Export JSON data for further processing

## Architecture

### Components

```
app.py                          # Streamlit web interface
│
├── src/config/
│   └── conflict_topics.py     # 20 predefined global topics + configurations
│
├── src/agents/                 # Analysis agents (existing)
│   ├── coordinator.py
│   ├── news_aggregator.py
│   ├── event_clustering.py
│   ├── rhetoric_analyzer.py
│   └── prediction_agent.py
│
├── src/utils/
│   ├── topic_modeling.py      # BERTopic integration (NEW)
│   ├── visualizations.py      # Matplotlib visualizations (NEW)
│   ├── storage.py             # Data persistence
│   ├── nlp_utils.py
│   └── translator.py
│
└── src/models/
    └── article.py             # Data models
```

### Data Flow

1. **Topic Selection** → Filter and select conflict topics
2. **News Aggregation** → Fetch articles from 12+ international sources
3. **Event Clustering** → Group related articles using DBSCAN
4. **Rhetoric Analysis** → Analyze sentiment, tone, urgency
5. **Topic Modeling** → Extract sub-themes using BERTopic
6. **Prediction** → Forecast trajectory and risk
7. **Visualization** → Create charts and graphs
8. **Presentation** → Interactive web interface

## Predefined Topics

### Critical Risk
- 🔴 Russia-Ukraine War
- 🔴 Israel-Palestine Conflict

### High Risk
- 🟠 China-Taiwan Tensions
- 🟠 Iran Nuclear Program
- 🟠 North Korea Nuclear Threat
- 🟠 India-Pakistan Kashmir Dispute
- 🟠 Yemen Civil War
- 🟠 US-China Technology Competition
- 🟠 Cyber Warfare and Espionage

### Medium Risk
- 🟡 South China Sea Disputes
- 🟡 Syria Conflict
- 🟡 Ethiopia-Tigray Conflict
- 🟡 Sahel Region Terrorism
- 🟡 Arctic Resource Competition
- 🟡 Venezuela Political Crisis
- 🟡 Myanmar Military Coup
- 🟡 Space Militarization
- 🟡 Climate Change and Security
- 🟡 AI and Autonomous Weapons

### Low Risk
- 🟢 Western Balkans Tensions

## Tips for Best Results

1. **Start with Standard Analysis**: Provides the best balance of depth and speed
2. **Select Related Topics**: Choose topics in the same region or category for better comparison
3. **Use Filters**: Narrow down to high-risk topics for most critical insights
4. **Review Visualizations First**: Get overview before diving into detailed reports
5. **Export Data**: Save results for historical comparison
6. **Check Regularly**: Run analyses periodically to track evolution

## Technical Details

### Topic Modeling
- **Method**: BERTopic (automatic topic discovery)
- **Fallback**: LDA if BERTopic unavailable
- **Features**:
  - Semantic clustering of articles
  - Temporal trend analysis
  - Coherence scoring
  - Cross-cluster theme identification

### Visualizations
- **Library**: Matplotlib with customizable styles
- **Chart Types**:
  - Line plots (sentiment over time)
  - Histograms (article frequency)
  - Heatmaps (cross-event sentiment)
  - Pie charts (trajectory distribution)
  - Horizontal bar charts (confidence, actors, topics)
- **Export**: PNG format at 300 DPI

### Analysis Depth Configurations

| Feature | Quick | Standard | Deep |
|---------|-------|----------|------|
| Days of data | 3 | 7 | 14 |
| Max articles | 50 | 150 | 300 |
| Similarity threshold | 0.7 | 0.6 | 0.5 |
| Topic modeling | ❌ | ✅ | ✅ |
| Predictions | ❌ | ✅ | ✅ |
| Cross-analysis | ❌ | ✅ | ✅ |
| Historical comparison | ❌ | ❌ | ✅ |

## Troubleshooting

### No articles found
- Check API keys in `.env`
- Try different topics or longer time range
- Verify internet connection

### Analysis too slow
- Use Quick depth for faster results
- Select fewer topics
- Check system resources

### Visualizations not showing
- Ensure matplotlib is installed
- Check for errors in console
- Try refreshing the page

### Topic modeling not working
- BERTopic requires sufficient articles (5+)
- Install BERTopic: `pip install bertopic`
- Fallback to LDA is automatic

## Future Enhancements

Potential additions:
- Real-time monitoring and alerts
- Historical trend comparison
- Interactive network graphs
- PDF report generation
- Email notifications
- Custom topic creation
- Multi-language interface
- Advanced filtering options

## Support

For issues or questions:
1. Check this guide
2. Review console logs
3. Verify dependencies are installed
4. Ensure API keys are configured

## Credits

Built on top of the existing worldnews_analysis multi-agent system with new components:
- Interactive Streamlit interface
- 20 predefined global conflict topics
- BERTopic integration for topic modeling
- Matplotlib visualization suite
- Configurable analysis depth
