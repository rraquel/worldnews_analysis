#!/usr/bin/env python3
"""
Test script for international news aggregation
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.news_aggregator import NewsAggregatorAgent


def test_international_news():
    """Test international news collection from RSS feeds"""
    print("=" * 70)
    print("Testing International News Collection")
    print("=" * 70)
    print()

    # Create aggregator agent
    aggregator = NewsAggregatorAgent()

    print(f"📋 Configured {len(aggregator.rss_feeds)} international RSS feeds:")
    for source_name in aggregator.rss_feeds.keys():
        print(f"   • {source_name}")
    print()

    # Fetch only from RSS feeds (limit to 5 articles per feed for quick test)
    print("🌍 Fetching international news (this may take a moment)...")
    print()

    try:
        articles = aggregator._fetch_from_rss_feeds(days_back=3, max_articles_per_feed=5)

        print()
        print("=" * 70)
        print(f"✅ Successfully collected {len(articles)} articles from international sources")
        print("=" * 70)
        print()

        if articles:
            # Show sample articles by source
            sources = {}
            for article in articles:
                if article.source not in sources:
                    sources[article.source] = []
                sources[article.source].append(article)

            print("📰 Sample articles by source:")
            print()

            for source_name, source_articles in sorted(sources.items()):
                print(f"  {source_name} ({len(source_articles)} articles):")
                for article in source_articles[:2]:  # Show first 2 from each source
                    print(f"    • {article.title[:80]}{'...' if len(article.title) > 80 else ''}")
                    print(f"      Published: {article.published_at.strftime('%Y-%m-%d %H:%M')}")
                    print(f"      URL: {article.url[:70]}...")
                    print(f"      Sentiment: {article.sentiment_score:.2f}")
                print()

            print("=" * 70)
            print("✅ International news collection is working correctly!")
            print("=" * 70)

        else:
            print("⚠️  No articles collected. This could be due to:")
            print("   • RSS feeds being temporarily unavailable")
            print("   • Network connectivity issues")
            print("   • No recent geopolitics-related articles in feeds")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = test_international_news()
    sys.exit(0 if success else 1)
