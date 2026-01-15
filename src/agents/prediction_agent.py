from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
from src.models import ArticleCluster, RhetoricAnalysis, EventPrediction
from src.utils import NLPProcessor


class PredictionAgent:
    """Agent responsible for predicting event trajectories and outcomes"""

    def __init__(self):
        self.nlp = NLPProcessor()

        # Historical patterns for reference
        self.escalation_patterns = [
            'increasing negative sentiment',
            'rising urgency indicators',
            'expanding geographic scope',
            'increasing military rhetoric',
            'diplomatic breakdown'
        ]

        self.de_escalation_patterns = [
            'improving sentiment',
            'diplomatic engagement',
            'reduced urgency',
            'stabilizing rhetoric',
            'constructive dialogue'
        ]

    def predict_trajectory(self, cluster: ArticleCluster,
                          analysis: RhetoricAnalysis) -> EventPrediction:
        """Predict the trajectory of an event based on analysis"""
        print(f"🔮 Predicting trajectory for: {cluster.event_name}")

        # Analyze trend direction
        trajectory = self._determine_trajectory(cluster, analysis)

        # Calculate confidence
        confidence_score = self._calculate_confidence(cluster, analysis)

        # Identify key indicators
        key_indicators = self._extract_key_indicators(analysis)

        # Find similar historical patterns
        similar_patterns = self._find_similar_patterns(trajectory, analysis)

        # Generate outlooks
        short_term = self._generate_short_term_outlook(trajectory, analysis)
        medium_term = self._generate_medium_term_outlook(trajectory, analysis)

        # Identify risk factors
        risk_factors = self._identify_risk_factors(cluster, analysis)

        # Calculate attention metrics
        attention_metrics = self._calculate_attention_metrics(cluster)

        return EventPrediction(
            cluster_id=cluster.id,
            event_name=cluster.event_name,
            prediction_date=datetime.now(),
            trajectory=trajectory,
            confidence_score=confidence_score,
            key_indicators=key_indicators,
            similar_historical_patterns=similar_patterns,
            short_term_outlook=short_term,
            medium_term_outlook=medium_term,
            risk_factors=risk_factors,
            attention_metrics=attention_metrics
        )

    def _determine_trajectory(self, cluster: ArticleCluster,
                             analysis: RhetoricAnalysis) -> str:
        """Determine if event is escalating, de-escalating, or stable"""
        scores = {
            'escalating': 0,
            'de-escalating': 0,
            'stable': 0
        }

        # Analyze sentiment trend
        if analysis.sentiment_trend:
            recent_sentiments = [
                s['sentiment_score']
                for s in analysis.sentiment_trend[-5:]
            ]

            if len(recent_sentiments) >= 2:
                # Calculate trend
                x = np.arange(len(recent_sentiments))
                y = np.array(recent_sentiments)
                trend = np.polyfit(x, y, 1)[0]

                if trend < -0.05:
                    scores['escalating'] += 2
                elif trend > 0.05:
                    scores['de-escalating'] += 2
                else:
                    scores['stable'] += 1

        # Analyze tone shift
        tone_shift = analysis.tone_shift
        if tone_shift['shift_direction'] == 'deteriorating':
            scores['escalating'] += 2
        elif tone_shift['shift_direction'] == 'improving':
            scores['de-escalating'] += 2
        else:
            scores['stable'] += 1

        # Urgency indicators
        if len(analysis.urgency_indicators) > 5:
            scores['escalating'] += 1
        elif len(analysis.urgency_indicators) < 2:
            scores['de-escalating'] += 1

        # Urgency change
        urgency_change = tone_shift.get('urgency_change', 0)
        if urgency_change > 2:
            scores['escalating'] += 1
        elif urgency_change < -2:
            scores['de-escalating'] += 1

        # Article frequency
        article_freq = analysis.linguistic_features.get('article_frequency', 0)
        if article_freq > 2:  # More than 2 articles per day
            scores['escalating'] += 1

        # Determine trajectory
        max_score = max(scores.values())
        if max_score == 0:
            return 'stable'

        for trajectory, score in scores.items():
            if score == max_score:
                return trajectory

        return 'stable'

    def _calculate_confidence(self, cluster: ArticleCluster,
                             analysis: RhetoricAnalysis) -> float:
        """Calculate confidence in prediction"""
        confidence_factors = []

        # Article count (more articles = higher confidence)
        article_confidence = min(1.0, cluster.article_count / 20)
        confidence_factors.append(article_confidence)

        # Time span (longer observation = higher confidence)
        time_span = analysis.linguistic_features.get('time_span_days', 0)
        time_confidence = min(1.0, time_span / 7)
        confidence_factors.append(time_confidence)

        # Source diversity (more sources = higher confidence)
        source_diversity = analysis.linguistic_features.get('source_diversity', 1)
        source_confidence = min(1.0, source_diversity / 5)
        confidence_factors.append(source_confidence)

        # Sentiment trend consistency
        if len(analysis.sentiment_trend) >= 3:
            sentiments = [s['sentiment_score'] for s in analysis.sentiment_trend]
            sentiment_std = np.std(sentiments)
            consistency_confidence = max(0, 1.0 - sentiment_std)
            confidence_factors.append(consistency_confidence)

        # Overall confidence is average of factors
        return float(np.mean(confidence_factors))

    def _extract_key_indicators(self, analysis: RhetoricAnalysis) -> List[str]:
        """Extract key indicators supporting the prediction"""
        indicators = []

        # Sentiment indicators
        tone_shift = analysis.tone_shift
        if tone_shift['shift_magnitude'] > 0.1:
            indicators.append(
                f"Tone shift from {tone_shift['initial_tone']} to {tone_shift['current_tone']}"
            )

        # Urgency indicators
        if analysis.urgency_indicators:
            indicators.append(
                f"Urgency indicators present: {', '.join(analysis.urgency_indicators[:3])}"
            )

        # New keywords
        new_keywords = tone_shift.get('new_keywords', [])
        if new_keywords:
            indicators.append(f"Emerging keywords: {', '.join(new_keywords[:3])}")

        # Actor involvement
        if analysis.actor_mentions:
            top_actors = list(analysis.actor_mentions.keys())[:3]
            indicators.append(f"Key actors: {', '.join(top_actors)}")

        return indicators

    def _find_similar_patterns(self, trajectory: str,
                               analysis: RhetoricAnalysis) -> List[str]:
        """Find similar historical patterns"""
        patterns = []

        if trajectory == 'escalating':
            # Check for specific escalation patterns
            if 'military' in str(analysis.key_phrases).lower():
                patterns.append("Military rhetoric escalation (similar to pre-conflict situations)")

            if any('sanction' in kw for kw in analysis.tone_shift.get('new_keywords', [])):
                patterns.append("Economic sanctions pattern (similar to trade war scenarios)")

            if len(analysis.urgency_indicators) > 5:
                patterns.append("High urgency pattern (similar to crisis situations)")

        elif trajectory == 'de-escalating':
            if 'dialogue' in str(analysis.key_phrases).lower() or 'talk' in str(analysis.key_phrases).lower():
                patterns.append("Diplomatic engagement pattern (similar to resolution scenarios)")

            if analysis.tone_shift['shift_direction'] == 'improving':
                patterns.append("Improving tone pattern (similar to post-crisis recovery)")

        else:  # stable
            patterns.append("Stable monitoring phase (similar to ongoing situations without major changes)")

        return patterns

    def _generate_short_term_outlook(self, trajectory: str,
                                     analysis: RhetoricAnalysis) -> str:
        """Generate 7-day outlook"""
        if trajectory == 'escalating':
            return (
                "Short-term outlook (7 days): Situation likely to intensify. "
                "Expect increased media coverage, possible diplomatic statements, "
                "and heightened rhetoric. Monitor for concrete actions matching the rhetoric."
            )
        elif trajectory == 'de-escalating':
            return (
                "Short-term outlook (7 days): Situation showing signs of stabilization. "
                "Expect continued dialogue, reduced inflammatory rhetoric, "
                "and possible diplomatic progress."
            )
        else:
            return (
                "Short-term outlook (7 days): Situation expected to remain stable. "
                "Continue monitoring for any sudden changes in rhetoric or actions."
            )

    def _generate_medium_term_outlook(self, trajectory: str,
                                      analysis: RhetoricAnalysis) -> str:
        """Generate 30-day outlook"""
        if trajectory == 'escalating':
            urgency_level = 'high' if len(analysis.urgency_indicators) > 5 else 'moderate'
            return (
                f"Medium-term outlook (30 days): With {urgency_level} urgency indicators, "
                f"the situation may develop into a more serious crisis. "
                f"Key factors to watch: actor responses, international involvement, "
                f"and whether rhetoric translates to concrete actions."
            )
        elif trajectory == 'de-escalating':
            return (
                "Medium-term outlook (30 days): If current trends continue, "
                "the situation should move toward resolution or at least stabilization. "
                "Watch for formal agreements or continued positive signals."
            )
        else:
            return (
                "Medium-term outlook (30 days): Situation likely to remain in current state "
                "unless external factors intervene. Monitor for any catalyst events "
                "that could shift the trajectory."
            )

    def _identify_risk_factors(self, cluster: ArticleCluster,
                               analysis: RhetoricAnalysis) -> List[str]:
        """Identify risk factors that could change the trajectory"""
        risk_factors = []

        # High urgency
        if len(analysis.urgency_indicators) > 5:
            risk_factors.append("High level of urgency indicators suggest rapid escalation risk")

        # Multiple powerful actors
        top_actors = list(analysis.actor_mentions.keys())[:5]
        if len(top_actors) >= 3:
            risk_factors.append(
                f"Multiple actors involved ({', '.join(top_actors)}), increasing complexity"
            )

        # Negative sentiment
        if analysis.sentiment_trend:
            recent_sentiment = np.mean([
                s['sentiment_score']
                for s in analysis.sentiment_trend[-5:]
            ])
            if recent_sentiment < -0.3:
                risk_factors.append("Persistently negative sentiment indicates deep tensions")

        # Rapidly increasing coverage
        article_freq = analysis.linguistic_features.get('article_frequency', 0)
        if article_freq > 3:
            risk_factors.append("Rapidly increasing media coverage suggests escalating importance")

        # Specific risk keywords
        risk_keywords = ['military', 'invasion', 'war', 'weapon', 'strike', 'attack']
        all_keywords = [kp['phrase'] for kp in analysis.key_phrases]
        found_risk_keywords = [kw for kw in risk_keywords if any(kw in phrase for phrase in all_keywords)]

        if found_risk_keywords:
            risk_factors.append(f"Presence of high-risk keywords: {', '.join(found_risk_keywords)}")

        return risk_factors

    def _calculate_attention_metrics(self, cluster: ArticleCluster) -> Dict[str, Any]:
        """Calculate metrics about attention and coverage"""
        # Sort by date
        sorted_articles = sorted(cluster.articles, key=lambda a: a.published_at)

        # Calculate coverage intensity
        if sorted_articles:
            time_span = (sorted_articles[-1].published_at - sorted_articles[0].published_at).days
            intensity = cluster.article_count / max(1, time_span)
        else:
            intensity = 0

        # Source diversity
        sources = set(a.source for a in cluster.articles)

        # Coverage trend
        if len(sorted_articles) >= 4:
            mid = len(sorted_articles) // 2
            early_count = mid
            recent_count = len(sorted_articles) - mid

            if recent_count > early_count * 1.5:
                trend = 'increasing'
            elif recent_count < early_count * 0.5:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'

        return {
            'coverage_intensity': intensity,
            'source_diversity': len(sources),
            'coverage_trend': trend,
            'total_articles': cluster.article_count,
            'sources': list(sources)
        }

    def generate_summary_report(self, predictions: List[EventPrediction]) -> Dict[str, Any]:
        """Generate a summary report across all predictions"""
        if not predictions:
            return {'status': 'no_predictions'}

        escalating = [p for p in predictions if p.trajectory == 'escalating']
        de_escalating = [p for p in predictions if p.trajectory == 'de-escalating']
        stable = [p for p in predictions if p.trajectory == 'stable']

        # Find highest confidence predictions
        top_predictions = sorted(predictions, key=lambda p: p.confidence_score, reverse=True)[:3]

        # Find most concerning
        most_concerning = sorted(
            escalating,
            key=lambda p: (len(p.risk_factors), p.confidence_score),
            reverse=True
        )[:3]

        return {
            'total_events': len(predictions),
            'escalating_count': len(escalating),
            'de_escalating_count': len(de_escalating),
            'stable_count': len(stable),
            'top_confidence_predictions': [
                {'event': p.event_name, 'confidence': p.confidence_score, 'trajectory': p.trajectory}
                for p in top_predictions
            ],
            'most_concerning_events': [
                {'event': p.event_name, 'risk_factors': len(p.risk_factors)}
                for p in most_concerning
            ]
        }
