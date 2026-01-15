import os
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional
import requests
from src.models import Article
from src.utils import NLPProcessor


class NewsAggregatorAgent:
    """Agent responsible for aggregating news from various free sources"""

    def __init__(self, newsapi_key: Optional[str] = None, guardian_key: Optional[str] = None):
        self.newsapi_key = newsapi_key or os.getenv('NEWSAPI_KEY')
        self.guardian_key = guardian_key or os.getenv('GUARDIAN_API_KEY')
        self.nlp = NLPProcessor()

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

    def fetch_news(self, days_back: int = 7, max_articles: int = 100) -> List[Article]:
        """Fetch news articles from all available sources"""
        articles = []

        print("🔍 Fetching news from NewsAPI...")
        if self.newsapi_key:
            articles.extend(self._fetch_from_newsapi(days_back, max_articles // 2))
        else:
            print("⚠️  NewsAPI key not found. Skipping NewsAPI.")

        print("🔍 Fetching news from Guardian API...")
        if self.guardian_key:
            articles.extend(self._fetch_from_guardian(days_back, max_articles // 2))
        else:
            print("⚠️  Guardian API key not found. Skipping Guardian.")

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
