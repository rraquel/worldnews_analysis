"""
Topic modeling utilities for conflict analysis.
Uses BERTopic for advanced topic modeling with pre-computed embeddings.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from collections import Counter
import re

try:
    from bertopic import BERTopic
    from bertopic.vectorizers import ClassTfidfTransformer
    from sklearn.feature_extraction.text import CountVectorizer
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer as SKCountVectorizer

from src.models.article import Article, ArticleCluster


class TopicModeler:
    """
    Advanced topic modeling for conflict analysis.
    Supports both BERTopic (preferred) and LDA fallback.
    """

    def __init__(self, method: str = "bertopic", n_topics: int = 5, language: str = "english"):
        """
        Initialize topic modeler.

        Args:
            method: "bertopic" or "lda"
            n_topics: Number of topics to extract (for LDA)
            language: Language for stopwords
        """
        self.method = method if BERTOPIC_AVAILABLE else "lda"
        self.n_topics = n_topics
        self.language = language
        self.model = None

        if self.method == "bertopic" and not BERTOPIC_AVAILABLE:
            print("⚠️  BERTopic not available, falling back to LDA")
            self.method = "lda"

    def extract_topics_from_cluster(
        self,
        cluster: ArticleCluster,
        n_topics: Optional[int] = None,
        n_words_per_topic: int = 10
    ) -> Dict:
        """
        Extract topics from an article cluster.

        Args:
            cluster: ArticleCluster to analyze
            n_topics: Number of topics (None = auto for BERTopic, default for LDA)
            n_words_per_topic: Number of representative words per topic

        Returns:
            Dictionary with topics, keywords, and metadata
        """
        if not cluster.articles:
            return {"topics": [], "method": self.method, "n_articles": 0}

        # Prepare documents
        documents = []
        timestamps = []
        for article in cluster.articles:
            # Combine title and description for better context
            text = f"{article.title or ''} {article.description or ''}"
            if text.strip():
                documents.append(text.strip())
                timestamps.append(article.published_at)

        if len(documents) < 2:
            return {
                "topics": [],
                "method": self.method,
                "n_articles": len(documents),
                "message": "Not enough articles for topic modeling"
            }

        # Extract embeddings if available
        embeddings = None
        if cluster.articles[0].embedding is not None:
            embeddings = np.array([
                article.embedding for article in cluster.articles
                if article.embedding is not None
            ])
            if len(embeddings) != len(documents):
                embeddings = None  # Mismatch, don't use embeddings

        # Run topic modeling
        if self.method == "bertopic":
            return self._extract_with_bertopic(
                documents, embeddings, timestamps, n_topics, n_words_per_topic
            )
        else:
            return self._extract_with_lda(
                documents, timestamps, n_topics or self.n_topics, n_words_per_topic
            )

    def _extract_with_bertopic(
        self,
        documents: List[str],
        embeddings: Optional[np.ndarray],
        timestamps: List[datetime],
        n_topics: Optional[int],
        n_words: int
    ) -> Dict:
        """Extract topics using BERTopic."""
        # Configure BERTopic
        vectorizer_model = CountVectorizer(
            stop_words=self.language,
            ngram_range=(1, 3),
            min_df=1
        )

        # Create model
        topic_model = BERTopic(
            vectorizer_model=vectorizer_model,
            nr_topics=n_topics,
            top_n_words=n_words,
            verbose=False,
            calculate_probabilities=False  # Faster
        )

        # Fit model
        try:
            topics, probs = topic_model.fit_transform(documents, embeddings)
        except Exception as e:
            return {
                "topics": [],
                "method": "bertopic",
                "error": str(e),
                "n_articles": len(documents)
            }

        # Extract topic information
        topic_info = topic_model.get_topic_info()

        result_topics = []
        for _, row in topic_info.iterrows():
            topic_id = row['Topic']
            if topic_id == -1:  # Skip outlier topic
                continue

            # Get topic words and scores
            topic_words = topic_model.get_topic(topic_id)
            if not topic_words:
                continue

            # Get documents in this topic
            topic_docs = [doc for doc, t in zip(documents, topics) if t == topic_id]
            topic_timestamps = [ts for ts, t in zip(timestamps, topics) if t == topic_id]

            # Calculate temporal distribution
            temporal_dist = self._calculate_temporal_distribution(topic_timestamps)

            result_topics.append({
                "topic_id": int(topic_id),
                "label": row.get('Name', f"Topic {topic_id}"),
                "keywords": [{"word": word, "score": float(score)} for word, score in topic_words[:n_words]],
                "count": len(topic_docs),
                "sample_titles": topic_docs[:3],
                "temporal_distribution": temporal_dist,
                "coherence_score": self._calculate_topic_coherence(topic_words)
            })

        return {
            "topics": sorted(result_topics, key=lambda x: x['count'], reverse=True),
            "method": "bertopic",
            "n_articles": len(documents),
            "n_topics": len(result_topics),
            "outliers": sum(1 for t in topics if t == -1)
        }

    def _extract_with_lda(
        self,
        documents: List[str],
        timestamps: List[datetime],
        n_topics: int,
        n_words: int
    ) -> Dict:
        """Extract topics using LDA (fallback method)."""
        # Vectorize documents
        vectorizer = SKCountVectorizer(
            max_df=0.95,
            min_df=2,
            stop_words=self.language,
            ngram_range=(1, 2)
        )

        try:
            doc_term_matrix = vectorizer.fit_transform(documents)
        except Exception as e:
            return {
                "topics": [],
                "method": "lda",
                "error": str(e),
                "n_articles": len(documents)
            }

        # Fit LDA
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=50
        )

        try:
            lda.fit(doc_term_matrix)
        except Exception as e:
            return {
                "topics": [],
                "method": "lda",
                "error": str(e),
                "n_articles": len(documents)
            }

        # Get feature names
        feature_names = vectorizer.get_feature_names_out()

        # Extract topics
        result_topics = []
        doc_topics = lda.transform(doc_term_matrix)

        for topic_idx in range(n_topics):
            # Get top words for this topic
            top_indices = lda.components_[topic_idx].argsort()[-n_words:][::-1]
            top_words = [(feature_names[i], lda.components_[topic_idx][i])
                         for i in top_indices]

            # Get documents primarily in this topic
            topic_doc_indices = [i for i, doc_topic in enumerate(doc_topics)
                                if doc_topic[topic_idx] > 0.3]
            topic_docs = [documents[i] for i in topic_doc_indices]
            topic_timestamps = [timestamps[i] for i in topic_doc_indices]

            # Calculate temporal distribution
            temporal_dist = self._calculate_temporal_distribution(topic_timestamps)

            result_topics.append({
                "topic_id": topic_idx,
                "label": f"Topic {topic_idx + 1}: {', '.join([w for w, _ in top_words[:3]])}",
                "keywords": [{"word": word, "score": float(score)} for word, score in top_words],
                "count": len(topic_docs),
                "sample_titles": topic_docs[:3],
                "temporal_distribution": temporal_dist,
                "coherence_score": 0.0  # Not calculated for LDA
            })

        return {
            "topics": sorted(result_topics, key=lambda x: x['count'], reverse=True),
            "method": "lda",
            "n_articles": len(documents),
            "n_topics": n_topics
        }

    def _calculate_temporal_distribution(self, timestamps: List[datetime]) -> Dict:
        """Calculate how topics evolve over time."""
        if not timestamps:
            return {"trend": "insufficient_data"}

        # Sort timestamps
        sorted_ts = sorted(timestamps)

        if len(sorted_ts) < 2:
            return {"trend": "single_point"}

        # Calculate periods (early, middle, late)
        total_span = (sorted_ts[-1] - sorted_ts[0]).total_seconds()
        if total_span == 0:
            return {"trend": "same_time"}

        third = total_span / 3
        early_cutoff = sorted_ts[0].timestamp() + third
        late_cutoff = sorted_ts[-1].timestamp() - third

        early = sum(1 for ts in sorted_ts if ts.timestamp() <= early_cutoff)
        middle = sum(1 for ts in sorted_ts if early_cutoff < ts.timestamp() <= late_cutoff)
        late = sum(1 for ts in sorted_ts if ts.timestamp() > late_cutoff)

        total = len(sorted_ts)

        # Determine trend
        if late > early * 1.5:
            trend = "increasing"
        elif early > late * 1.5:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "early_pct": round(early / total * 100, 1),
            "middle_pct": round(middle / total * 100, 1),
            "late_pct": round(late / total * 100, 1),
            "time_span_days": round(total_span / 86400, 1)
        }

    def _calculate_topic_coherence(self, topic_words: List[Tuple[str, float]]) -> float:
        """
        Simple coherence score based on semantic similarity of top words.
        Higher score = more coherent topic.
        """
        if not topic_words or len(topic_words) < 2:
            return 0.0

        # Use average score as a proxy for coherence
        avg_score = np.mean([score for _, score in topic_words[:5]])
        return float(avg_score)

    def compare_topics_across_clusters(
        self,
        cluster_topics: Dict[str, Dict]
    ) -> Dict:
        """
        Compare topics across multiple clusters to find common themes.

        Args:
            cluster_topics: Dictionary mapping cluster_id to topic extraction results

        Returns:
            Cross-cluster topic analysis
        """
        all_keywords = []
        cluster_labels = []

        for cluster_id, topics_data in cluster_topics.items():
            for topic in topics_data.get("topics", []):
                for kw in topic.get("keywords", [])[:5]:  # Top 5 keywords
                    all_keywords.append(kw["word"])
                    cluster_labels.append(cluster_id)

        # Find common themes
        keyword_counts = Counter(all_keywords)
        common_themes = keyword_counts.most_common(15)

        # Find unique themes per cluster
        cluster_unique = {}
        for cluster_id, topics_data in cluster_topics.items():
            all_cluster_keywords = set()
            for topic in topics_data.get("topics", []):
                all_cluster_keywords.update(kw["word"] for kw in topic.get("keywords", [])[:5])

            # Find keywords unique to this cluster (or rare in others)
            unique = [kw for kw in all_cluster_keywords
                     if all_keywords.count(kw) <= 2]
            cluster_unique[cluster_id] = unique[:5]

        return {
            "common_themes": [{"keyword": kw, "frequency": count}
                             for kw, count in common_themes],
            "unique_themes": cluster_unique,
            "total_topics": sum(len(data.get("topics", []))
                               for data in cluster_topics.values()),
            "clusters_analyzed": len(cluster_topics)
        }

    def generate_topic_summary(self, topic_data: Dict) -> str:
        """Generate human-readable summary of topic modeling results."""
        if not topic_data.get("topics"):
            return "No distinct topics identified in this cluster."

        lines = [f"Topic Modeling Analysis ({topic_data['method'].upper()})"]
        lines.append(f"Analyzed {topic_data['n_articles']} articles")
        lines.append(f"Found {topic_data['n_topics']} distinct topics\n")

        for i, topic in enumerate(topic_data["topics"][:5], 1):  # Top 5 topics
            lines.append(f"Topic {i}: {topic['label']}")
            lines.append(f"  Articles: {topic['count']}")

            # Top keywords
            top_kw = [kw['word'] for kw in topic['keywords'][:5]]
            lines.append(f"  Keywords: {', '.join(top_kw)}")

            # Temporal trend
            temp_dist = topic.get('temporal_distribution', {})
            trend = temp_dist.get('trend', 'unknown')
            if trend != "insufficient_data":
                lines.append(f"  Trend: {trend}")

            lines.append("")

        return "\n".join(lines)
