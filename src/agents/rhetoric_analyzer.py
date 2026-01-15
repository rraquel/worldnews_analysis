from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict
import numpy as np
from src.models import Article, ArticleCluster, RhetoricAnalysis
from src.utils import NLPProcessor


class RhetoricAnalyzerAgent:
    """Agent responsible for analyzing rhetoric and language patterns over time"""

    def __init__(self, time_period_days: int = 30):
        self.time_period_days = time_period_days
        self.nlp = NLPProcessor()

    def analyze_cluster(self, cluster: ArticleCluster) -> RhetoricAnalysis:
        """Perform comprehensive rhetoric analysis on a cluster"""
        print(f"📝 Analyzing rhetoric for: {cluster.event_name}")

        # Sort articles by date
        sorted_articles = sorted(cluster.articles, key=lambda a: a.published_at)

        # Analyze sentiment trend over time
        sentiment_trend = self._analyze_sentiment_trend(sorted_articles)

        # Extract and analyze key phrases over time
        key_phrases = self._analyze_key_phrases(sorted_articles)

        # Detect tone shifts
        tone_shift = self._analyze_tone_shift(sorted_articles)

        # Find urgency indicators
        urgency_indicators = self._find_urgency_indicators(sorted_articles)

        # Track actor mentions
        actor_mentions = self._track_actor_mentions(sorted_articles)

        # Analyze linguistic features
        linguistic_features = self._analyze_linguistic_features(sorted_articles)

        # Generate narrative description
        rhetoric_evolution = self._generate_rhetoric_narrative(
            sentiment_trend,
            tone_shift,
            key_phrases,
            urgency_indicators
        )

        return RhetoricAnalysis(
            cluster_id=cluster.id,
            event_name=cluster.event_name,
            analysis_date=datetime.now(),
            time_period_days=self.time_period_days,
            sentiment_trend=sentiment_trend,
            key_phrases=key_phrases,
            tone_shift=tone_shift,
            urgency_indicators=urgency_indicators,
            actor_mentions=actor_mentions,
            linguistic_features=linguistic_features,
            rhetoric_evolution=rhetoric_evolution
        )

    def _analyze_sentiment_trend(self, articles: List[Article]) -> List[Dict[str, Any]]:
        """Analyze how sentiment changes over time"""
        trend = []

        for article in articles:
            if article.sentiment_score is not None:
                trend.append({
                    'date': article.published_at.isoformat(),
                    'sentiment_score': article.sentiment_score,
                    'title': article.title[:50]
                })

        return trend

    def _analyze_key_phrases(self, articles: List[Article]) -> List[Dict[str, Any]]:
        """Analyze key phrases and their evolution over time"""
        # Split articles into time periods
        if len(articles) < 4:
            periods = [articles]
        else:
            mid_point = len(articles) // 2
            periods = [articles[:mid_point], articles[mid_point:]]

        phrase_analysis = []

        for i, period_articles in enumerate(periods):
            # Combine all text from period
            period_text = ' '.join([
                f"{a.title} {a.description or ''}"
                for a in period_articles
            ])

            # Extract phrases
            phrases = self.nlp.extract_phrases(period_text, n_gram=2)

            period_name = 'early' if i == 0 else 'recent'

            for phrase, freq in phrases[:10]:
                phrase_analysis.append({
                    'phrase': phrase,
                    'frequency': freq,
                    'period': period_name
                })

        return phrase_analysis

    def _analyze_tone_shift(self, articles: List[Article]) -> Dict[str, Any]:
        """Detect shifts in tone between early and recent articles"""
        if len(articles) < 2:
            return {
                'initial_tone': 'neutral',
                'current_tone': 'neutral',
                'shift_magnitude': 0,
                'shift_direction': 'stable'
            }

        # Split into early and recent
        mid_point = max(1, len(articles) // 2)
        early_articles = articles[:mid_point]
        recent_articles = articles[mid_point:]

        # Compare rhetoric
        early_texts = [f"{a.title} {a.description or ''}" for a in early_articles]
        recent_texts = [f"{a.title} {a.description or ''}" for a in recent_articles]

        comparison = self.nlp.compare_rhetoric(early_texts, recent_texts)

        # Determine tone labels
        early_sentiment = np.mean([a.sentiment_score for a in early_articles if a.sentiment_score is not None])
        recent_sentiment = np.mean([a.sentiment_score for a in recent_articles if a.sentiment_score is not None])

        def sentiment_to_tone(score):
            if score < -0.3:
                return 'highly negative'
            elif score < -0.1:
                return 'negative'
            elif score < 0.1:
                return 'neutral'
            elif score < 0.3:
                return 'positive'
            else:
                return 'highly positive'

        initial_tone = sentiment_to_tone(early_sentiment)
        current_tone = sentiment_to_tone(recent_sentiment)

        # Determine shift direction
        sentiment_change = comparison['sentiment_change']
        if abs(sentiment_change) < 0.1:
            shift_direction = 'stable'
        elif sentiment_change > 0:
            shift_direction = 'improving'
        else:
            shift_direction = 'deteriorating'

        return {
            'initial_tone': initial_tone,
            'current_tone': current_tone,
            'shift_magnitude': abs(sentiment_change),
            'shift_direction': shift_direction,
            'sentiment_change': sentiment_change,
            'urgency_change': comparison['urgency_change'],
            'new_keywords': comparison['new_keywords'][:5],
            'dropped_keywords': comparison['dropped_keywords'][:5]
        }

    def _find_urgency_indicators(self, articles: List[Article]) -> List[str]:
        """Find urgency indicators across all articles"""
        all_indicators = set()

        for article in articles:
            text = f"{article.title} {article.description or ''}"
            indicators = self.nlp.detect_urgency_indicators(text)
            all_indicators.update(indicators)

        return list(all_indicators)

    def _track_actor_mentions(self, articles: List[Article]) -> Dict[str, int]:
        """Track mentions of key actors (countries, leaders, organizations)"""
        all_entities = {
            'countries': [],
            'leaders': [],
            'organizations': []
        }

        for article in articles:
            text = f"{article.title} {article.description or ''}"
            entities = self.nlp.extract_entities(text)

            for category in all_entities:
                all_entities[category].extend(entities.get(category, []))

        # Count all actors
        actor_counts = defaultdict(int)
        for category, actors in all_entities.items():
            for actor in actors:
                actor_counts[actor] += 1

        # Return sorted by frequency
        return dict(sorted(actor_counts.items(), key=lambda x: x[1], reverse=True))

    def _analyze_linguistic_features(self, articles: List[Article]) -> Dict[str, Any]:
        """Analyze various linguistic features"""
        # Title length analysis
        title_lengths = [len(a.title.split()) for a in articles]

        # Source diversity
        sources = set(a.source for a in articles)

        # Temporal distribution
        dates = [a.published_at for a in articles]
        if dates:
            time_span = (max(dates) - min(dates)).days
        else:
            time_span = 0

        return {
            'avg_title_length': np.mean(title_lengths) if title_lengths else 0,
            'source_diversity': len(sources),
            'time_span_days': time_span,
            'article_frequency': len(articles) / max(1, time_span),
            'sources': list(sources)
        }

    def _generate_rhetoric_narrative(self,
                                     sentiment_trend: List[Dict],
                                     tone_shift: Dict,
                                     key_phrases: List[Dict],
                                     urgency_indicators: List[str]) -> str:
        """Generate a narrative description of rhetoric evolution"""
        narrative_parts = []

        # Tone shift description
        shift_dir = tone_shift['shift_direction']
        if shift_dir == 'stable':
            narrative_parts.append(
                f"The rhetoric has remained relatively stable, maintaining a {tone_shift['current_tone']} tone."
            )
        elif shift_dir == 'deteriorating':
            narrative_parts.append(
                f"The rhetoric has shifted from {tone_shift['initial_tone']} to {tone_shift['current_tone']}, "
                f"indicating a deterioration in tone."
            )
        else:
            narrative_parts.append(
                f"The rhetoric has shifted from {tone_shift['initial_tone']} to {tone_shift['current_tone']}, "
                f"showing improvement."
            )

        # Urgency analysis
        if urgency_indicators:
            narrative_parts.append(
                f"Urgency indicators such as '{', '.join(urgency_indicators[:3])}' suggest heightened concern."
            )

        # Keyword evolution
        if tone_shift.get('new_keywords'):
            narrative_parts.append(
                f"New keywords emerging include: {', '.join(tone_shift['new_keywords'][:3])}."
            )

        # Sentiment trend
        if len(sentiment_trend) > 1:
            recent_sentiments = [s['sentiment_score'] for s in sentiment_trend[-5:]]
            avg_recent = np.mean(recent_sentiments)

            if avg_recent < -0.2:
                narrative_parts.append("Recent coverage has been predominantly negative.")
            elif avg_recent > 0.2:
                narrative_parts.append("Recent coverage has been predominantly positive.")

        return ' '.join(narrative_parts)

    def compare_clusters(self, clusters: List[ArticleCluster]) -> Dict[str, Any]:
        """Compare rhetoric across multiple clusters"""
        print(f"📊 Comparing rhetoric across {len(clusters)} event clusters...")

        comparisons = {
            'most_negative': None,
            'most_positive': None,
            'most_urgent': None,
            'most_active': None,
            'sentiment_summary': {}
        }

        cluster_metrics = []

        for cluster in clusters:
            avg_sentiment = np.mean([
                a.sentiment_score for a in cluster.articles
                if a.sentiment_score is not None
            ])

            # Count urgency indicators
            urgency_count = 0
            for article in cluster.articles:
                text = f"{article.title} {article.description or ''}"
                urgency_count += len(self.nlp.detect_urgency_indicators(text))

            cluster_metrics.append({
                'cluster': cluster,
                'avg_sentiment': avg_sentiment,
                'urgency_count': urgency_count,
                'article_count': cluster.article_count
            })

        if cluster_metrics:
            # Find extremes
            comparisons['most_negative'] = min(
                cluster_metrics, key=lambda x: x['avg_sentiment']
            )['cluster'].event_name

            comparisons['most_positive'] = max(
                cluster_metrics, key=lambda x: x['avg_sentiment']
            )['cluster'].event_name

            comparisons['most_urgent'] = max(
                cluster_metrics, key=lambda x: x['urgency_count']
            )['cluster'].event_name

            comparisons['most_active'] = max(
                cluster_metrics, key=lambda x: x['article_count']
            )['cluster'].event_name

            # Overall sentiment
            overall_sentiment = np.mean([m['avg_sentiment'] for m in cluster_metrics])
            comparisons['sentiment_summary']['overall'] = overall_sentiment
            comparisons['sentiment_summary']['interpretation'] = (
                'negative' if overall_sentiment < -0.1
                else 'positive' if overall_sentiment > 0.1
                else 'neutral'
            )

        return comparisons
