# International News Sources - Implementation Summary

## Overview

Added comprehensive international news aggregation with automatic translation capabilities to provide a broader global perspective on geopolitical events.

## New Features

### 1. Multi-Source RSS Feed Integration

Added **10 international RSS feeds** covering diverse geographic regions and perspectives:

#### European Sources
- **BBC World**: Global news from UK perspective
- **Euronews**: Pan-European multilingual news network
- **Deutsche Welle**: German international broadcaster
- **France 24**: French international news channel
- **EUobserver**: European Union political news

#### Chinese/Asian Sources
- **CGTN** (China Global Television Network): Chinese state media, international English service
- **China Daily**: Official English-language daily newspaper
- **Xinhua**: Chinese state news agency, English service

#### Other Perspectives
- **Al Jazeera**: Middle Eastern perspective on world events
- **RT World**: Russian perspective on international affairs

### 2. Automatic Translation

Implemented translation capability using **deep-translator** library:

- **Auto-detection**: Automatically detects non-English content
- **Free translation**: Uses Google Translate API (free tier) via deep-translator
- **Supported languages**: Chinese (Simplified/Traditional), German, French, Russian, Arabic, and 100+ other languages
- **Fallback handling**: Returns original text if translation fails

**Implementation**: `/src/utils/translator.py`

### 3. Intelligent Content Filtering

Added geopolitical relevance filtering:

- Filters articles based on geopolitical keywords
- Ensures only relevant content is processed
- Reduces noise from general news
- Keywords include: diplomacy, international relations, sanctions, territorial disputes, military, etc.

### 4. Enhanced News Aggregation

Modified **NewsAggregatorAgent** (`/src/agents/news_aggregator.py`) to:

- Fetch from RSS feeds in addition to NewsAPI and Guardian
- Parse RSS entries into standardized Article format
- Clean HTML from RSS descriptions
- Handle various date formats from different feeds
- Distribute article collection across all sources proportionally

## Technical Details

### Dependencies Added

```txt
feedparser>=6.0.10      # RSS feed parsing
deep-translator>=1.11.4  # Translation service
```

### New Modules

1. **`src/utils/translator.py`**: Translation utility class
   - `translate_to_english(text, source_lang='auto')`: Translate text to English
   - `detect_language(text)`: Detect language of text
   - `is_english(text)`: Check if text is in English

2. **`test_international_news.py`**: Test script for international news collection

### Modified Files

1. **`src/agents/news_aggregator.py`**:
   - Added `rss_feeds` dictionary with 10 international sources
   - Added `_fetch_from_rss_feeds()` method
   - Added `_parse_rss_article()` method
   - Added `_is_geopolitics_related()` filtering method
   - Modified `fetch_news()` to include RSS feeds

2. **`requirements.txt`**: Added feedparser and deep-translator

3. **`README.md`**: Updated documentation to reflect new capabilities

4. **`.env.example`**: Added documentation about RSS feeds

5. **`src/utils/__init__.py`**: Exported Translator class

## Usage

### No Additional Configuration Required

The RSS feeds work out of the box with **no API keys needed**. Simply run:

```bash
python main.py
```

The system will automatically:
1. Fetch from NewsAPI and Guardian (if keys provided)
2. Fetch from all 10 RSS feeds
3. Translate non-English content to English
4. Filter for geopolitics-relevant articles
5. Deduplicate and cluster events
6. Perform rhetoric analysis and predictions

### Testing International News Collection

Run the test script to verify RSS feed collection:

```bash
python test_international_news.py
```

This will fetch articles from all international sources and display a summary.

## Benefits

### 1. Broader Geographic Coverage

- **European perspective**: BBC, Euronews, Deutsche Welle, France 24
- **Chinese perspective**: CGTN, China Daily, Xinhua
- **Middle Eastern perspective**: Al Jazeera
- **Russian perspective**: RT World
- **Western perspective**: NewsAPI, Guardian (existing)

### 2. Diverse Narratives

Different sources report the same events with different framing, allowing the system to:
- Detect narrative differences across regions
- Identify bias and propaganda patterns
- Compare rhetoric across state-controlled vs. independent media
- Understand how events are portrayed in different countries

### 3. Language Diversity

Articles in Chinese, German, French, Russian, and other languages are automatically translated, providing access to:
- Regional news not available in English
- Original source reporting before Western translation/interpretation
- Cultural context in how events are framed

### 4. More Data Points

- **Before**: ~100-150 articles from 2 sources
- **After**: ~200-400+ articles from 12 sources
- Better clustering and event detection
- More robust sentiment and trend analysis

## Example: How a Topic is Covered Differently

For example, a territorial dispute might be covered as:

- **BBC/Guardian**: Focus on diplomatic implications, international law
- **Xinhua/CGTN**: Emphasize historical claims, sovereignty rights
- **RT**: Highlight Western hypocrisy, geopolitical maneuvering
- **Al Jazeera**: Regional impact, local perspectives
- **Deutsche Welle/France 24**: EU interests, multilateral responses

The system can now:
1. Cluster all these articles into one event
2. Analyze how rhetoric differs across sources
3. Identify where narratives diverge
4. Detect coordinated messaging or information campaigns

## Limitations

1. **RSS Feed Quality**: RSS feeds provide less detail than full APIs (title + summary only)
2. **Translation Accuracy**: Auto-translation may miss cultural nuances or idioms
3. **Rate Limiting**: Google Translate free tier has limits (though quite generous)
4. **State Media Bias**: Some sources (CGTN, Xinhua, RT) are state-controlled and should be analyzed with that context
5. **Network Reliability**: RSS feeds can be slower or temporarily unavailable

## Future Enhancements

Potential improvements:
- Add more regional sources (African, South American, Southeast Asian)
- Implement premium translation APIs (DeepL) for better quality
- Add source credibility scoring
- Detect coordinated narratives across state media
- Multi-language sentiment analysis (analyze before translation)
- Add regional news aggregators (Asia Times, Africa News, etc.)

## Troubleshooting

### "No articles from RSS feeds"

Check:
- Network connectivity
- RSS feed URLs (some may change)
- Firewall/proxy blocking RSS requests

### "Translation not working"

Check:
- Network connectivity to Google services
- Rate limits (wait a few minutes)
- Language detection accuracy

### "Too many/few articles"

Adjust in code:
- `max_articles_per_feed` parameter in `_fetch_from_rss_feeds()`
- `days_back` parameter to control time range
- `_is_geopolitics_related()` keywords to broaden/narrow filtering

## Summary

This implementation provides a **truly global perspective** on geopolitical news by:

✅ Adding 10 international RSS feeds (Europe, China, Middle East, Russia)
✅ Implementing automatic translation from 100+ languages
✅ Filtering for geopolitical relevance
✅ Maintaining the existing multi-agent architecture
✅ Requiring no additional API keys or configuration
✅ Providing broader, more diverse news coverage for better analysis

The system can now answer: **"How is this event being broadcasted internationally?"** by comparing coverage across Western, Chinese, Russian, Middle Eastern, and European sources.
