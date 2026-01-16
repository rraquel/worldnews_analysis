import os
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import requests
import feedparser
from src.models import Article
from src.utils import NLPProcessor, Translator


class NewsAggregatorAgent:
    """Agent responsible for aggregating news from various free sources"""

    def __init__(self, newsapi_key: Optional[str] = None, guardian_key: Optional[str] = None):
        self.newsapi_key = newsapi_key or os.getenv('NEWSAPI_KEY')
        self.guardian_key = guardian_key or os.getenv('GUARDIAN_API_KEY')
        self.nlp = NLPProcessor()
        self.translator = Translator()

        # Topics related to world order and geopolitics
        self.topics = [
            'geopolitics',
            'world order',
            'international relations',
            'diplomacy',
            'global security',
            'territorial dispute',
            'sanctions',
            'trade war',
            'military alliance',
            'sovereignty'
        ]

        # Key search terms for current geopolitical events
        self.search_terms = [
            'Trump Greenland',
            'Ukraine Russia',
            'China Taiwan',
            'Middle East conflict',
            'NATO expansion',
            'trade sanctions',
            'territorial dispute',
            'diplomatic crisis',
            'international summit',
            'military tension'
        ]

        # International RSS feeds (free sources from Europe, China, and global outlets)
        self.rss_feeds = {
            # European sources
            'BBC World': 'http://feeds.bbci.co.uk/news/world/rss.xml',
            'Euronews': 'https://www.euronews.com/rss',
            'Deutsche Welle': 'https://rss.dw.com/xml/rss-en-world',
            'France 24': 'https://www.france24.com/en/rss',
            'EUobserver': 'https://euobserver.com/rss',

            # Chinese/Asian sources (English versions)
            'CGTN': 'https://www.cgtn.com/subscribe/rss/section/world.xml',
            'China Daily': 'http://www.chinadaily.com.cn/rss/world_rss.xml',
            'Xinhua': 'http://www.xinhuanet.com/english/rss/worldrss.xml',

            # Middle East perspective
            'Al Jazeera': 'https://www.aljazeera.com/xml/rss/all.xml',

            # Russian perspective
            'RT World': 'https://www.rt.com/rss/news/',
        }

    def fetch_news(self, days_back: int = 7, max_articles: int = 100) -> List[Article]:
        """Fetch news articles from all available sources"""
        articles = []

        # Calculate distribution of articles across sources
        num_sources = 2 + len(self.rss_feeds)  # NewsAPI + Guardian + RSS feeds
        articles_per_source = max_articles // num_sources

        print("🔍 Fetching news from NewsAPI...")
        if self.newsapi_key:
            articles.extend(self._fetch_from_newsapi(days_back, articles_per_source))
        else:
            print("⚠️  NewsAPI key not found. Skipping NewsAPI.")

        print("🔍 Fetching news from Guardian API...")
        if self.guardian_key:
            articles.extend(self._fetch_from_guardian(days_back, articles_per_source))
        else:
            print("⚠️  Guardian API key not found. Skipping Guardian.")

        print(f"🌍 Fetching international news from {len(self.rss_feeds)} RSS feeds...")
        articles.extend(self._fetch_from_rss_feeds(days_back, articles_per_source))

        # Remove duplicates based on URL
        unique_articles = self._deduplicate_articles(articles)

        # Generate embeddings for articles
        print(f"📊 Generating embeddings for {len(unique_articles)} articles...")
        self._add_embeddings(unique_articles)

        print(f"✅ Collected {len(unique_articles)} unique articles")
        return unique_articles

    def _fetch_from_newsapi(self, days_back: int, max_articles: int) -> List[Article]:
        """Fetch articles from NewsAPI"""
        if not self.newsapi_key:
            return []

        articles = []
        base_url = "https://newsapi.org/v2/everything"

        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        for term in self.search_terms[:5]:  # Limit to avoid rate limits
            try:
                params = {
                    'q': term,
                    'from': from_date,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 20,
                    'apiKey': self.newsapi_key
                }

                response = requests.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get('status') == 'ok':
                    for item in data.get('articles', []):
                        article = self._parse_newsapi_article(item)
                        if article:
                            articles.append(article)

                if len(articles) >= max_articles:
                    break

            except Exception as e:
                print(f"  Error fetching from NewsAPI for '{term}': {e}")
                continue

        return articles[:max_articles]

    def _parse_newsapi_article(self, item: dict) -> Optional[Article]:
        """Parse NewsAPI article format"""
        try:
            # Generate unique ID
            article_id = hashlib.md5(
                f"{item.get('url', '')}".encode()
            ).hexdigest()

            # Parse published date
            published_str = item.get('publishedAt', '')
            published_at = datetime.fromisoformat(published_str.replace('Z', '+00:00'))

            # Extract keywords
            title = item.get('title', '')
            description = item.get('description', '')
            content = f"{title} {description}"
            keywords = self.nlp.extract_keywords(content)

            # Sentiment analysis
            sentiment = self.nlp.analyze_sentiment_simple(content)

            return Article(
                id=article_id,
                title=title,
                subtitle=None,
                description=description,
                url=item.get('url', ''),
                source=item.get('source', {}).get('name', 'NewsAPI'),
                author=item.get('author'),
                published_at=published_at,
                content_snippet=item.get('content'),
                keywords=keywords,
                sentiment_score=sentiment
            )

        except Exception as e:
            print(f"  Error parsing article: {e}")
            return None

    def _fetch_from_guardian(self, days_back: int, max_articles: int) -> List[Article]:
        """Fetch articles from Guardian API"""
        if not self.guardian_key:
            return []

        articles = []
        base_url = "https://content.guardianapis.com/search"

        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        try:
            params = {
                'q': 'geopolitics OR "international relations" OR diplomacy',
                'from-date': from_date,
                'page-size': min(50, max_articles),
                'show-fields': 'headline,trailText,byline,bodyText',
                'api-key': self.guardian_key
            }

            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('response', {}).get('status') == 'ok':
                for item in data['response'].get('results', []):
                    article = self._parse_guardian_article(item)
                    if article:
                        articles.append(article)

        except Exception as e:
            print(f"  Error fetching from Guardian API: {e}")

        return articles[:max_articles]

    def _parse_guardian_article(self, item: dict) -> Optional[Article]:
        """Parse Guardian API article format"""
        try:
            article_id = hashlib.md5(
                f"{item.get('webUrl', '')}".encode()
            ).hexdigest()

            published_at = datetime.fromisoformat(
                item.get('webPublicationDate', '').replace('Z', '+00:00')
            )

            fields = item.get('fields', {})
            title = fields.get('headline', item.get('webTitle', ''))
            description = fields.get('trailText', '')

            content = f"{title} {description}"
            keywords = self.nlp.extract_keywords(content)
            sentiment = self.nlp.analyze_sentiment_simple(content)

            return Article(
                id=article_id,
                title=title,
                subtitle=None,
                description=description,
                url=item.get('webUrl', ''),
                source='The Guardian',
                author=fields.get('byline'),
                published_at=published_at,
                content_snippet=fields.get('bodyText', '')[:500],
                keywords=keywords,
                sentiment_score=sentiment
            )

        except Exception as e:
            print(f"  Error parsing Guardian article: {e}")
            return None

    def _deduplicate_articles(self, articles: List[Article]) -> List[Article]:
        """Remove duplicate articles based on URL and title similarity"""
        seen_urls = set()
        unique_articles = []

        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        return unique_articles

    def _add_embeddings(self, articles: List[Article]) -> None:
        """Add embeddings to articles"""
        texts = []
        for article in articles:
            text = f"{article.title} {article.description or ''}"
            texts.append(text)

        if texts:
            embeddings = self.nlp.get_embeddings_batch(texts)
            for article, embedding in zip(articles, embeddings):
                article.embedding = embedding

    def _fetch_from_rss_feeds(self, days_back: int, max_articles_per_feed: int = 10) -> List[Article]:
        """Fetch articles from international RSS feeds"""
        articles = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        for source_name, feed_url in self.rss_feeds.items():
            try:
                print(f"  Fetching from {source_name}...")
                feed = feedparser.parse(feed_url)

                if not feed.entries:
                    print(f"    No entries found for {source_name}")
                    continue

                feed_articles = 0
                for entry in feed.entries[:max_articles_per_feed]:
                    try:
                        article = self._parse_rss_article(entry, source_name)
                        if article and article.published_at >= cutoff_date:
                            articles.append(article)
                            feed_articles += 1
                    except Exception as e:
                        print(f"    Error parsing entry from {source_name}: {e}")
                        continue

                print(f"    ✓ Collected {feed_articles} articles from {source_name}")

            except Exception as e:
                print(f"    Error fetching from {source_name}: {e}")
                continue

        return articles

    def _parse_rss_article(self, entry: Dict, source_name: str) -> Optional[Article]:
        """Parse RSS feed entry into Article object"""
        try:
            # Generate unique ID
            url = entry.get('link', entry.get('id', ''))
            article_id = hashlib.md5(url.encode()).hexdigest()

            # Extract title and description
            title = entry.get('title', '')
            description = entry.get('summary', entry.get('description', ''))

            # Clean HTML tags from description if present
            if description:
                import re
                description = re.sub(r'<[^>]+>', '', description)
                description = description[:500]  # Limit length

            # Translate if needed
            if title and not self.translator.is_english(title):
                print(f"    Translating from {source_name}...")
                title = self.translator.translate_to_english(title)
                if description:
                    description = self.translator.translate_to_english(description)

            # Parse published date
            published_at = None
            if 'published_parsed' in entry and entry.published_parsed:
                from time import mktime
                published_at = datetime.fromtimestamp(mktime(entry.published_parsed))
            elif 'updated_parsed' in entry and entry.updated_parsed:
                from time import mktime
                published_at = datetime.fromtimestamp(mktime(entry.updated_parsed))
            else:
                # Default to current time if no date available
                published_at = datetime.now()

            # Extract content
            content = f"{title} {description}"

            # Check if article is relevant to geopolitics
            if not self._is_geopolitics_related(content):
                return None

            # Extract keywords and sentiment
            keywords = self.nlp.extract_keywords(content)
            sentiment = self.nlp.analyze_sentiment_simple(content)

            # Get author if available
            author = entry.get('author', None)

            return Article(
                id=article_id,
                title=title,
                subtitle=None,
                description=description,
                url=url,
                source=source_name,
                author=author,
                published_at=published_at,
                content_snippet=description[:300] if description else None,
                keywords=keywords,
                sentiment_score=sentiment
            )

        except Exception as e:
            print(f"    Error parsing RSS article: {e}")
            return None

    def _is_geopolitics_related(self, text: str) -> bool:
        """Check if article content is related to geopolitics"""
        if not text:
            return False

        text_lower = text.lower()

        # Check if any topic keywords are present
        geopolitics_keywords = [
            'geopolit', 'diplomatic', 'diplomacy', 'international',
            'foreign policy', 'summit', 'treaty', 'alliance',
            'sanctions', 'trade war', 'military', 'defense',
            'territory', 'border', 'conflict', 'war', 'peace',
            'united nations', 'nato', 'security council',
            'president', 'prime minister', 'government',
            'election', 'democracy', 'authoritarian',
            'china', 'russia', 'usa', 'europe', 'ukraine',
            'taiwan', 'middle east', 'israel', 'iran'
        ]

        return any(keyword in text_lower for keyword in geopolitics_keywords)
