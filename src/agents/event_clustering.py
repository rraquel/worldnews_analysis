import hashlib
from datetime import datetime
from typing import List, Dict, Set
from collections import defaultdict
import numpy as np
from sklearn.cluster import DBSCAN
from src.models import Article, ArticleCluster
from src.utils import NLPProcessor


class EventClusteringAgent:
    """Agent responsible for clustering articles into events"""

    def __init__(self, similarity_threshold: float = 0.7, min_cluster_size: int = 2):
        self.similarity_threshold = similarity_threshold
        self.min_cluster_size = min_cluster_size
        self.nlp = NLPProcessor()

    def cluster_articles(self, articles: List[Article]) -> List[ArticleCluster]:
        """Cluster articles into events using semantic similarity"""
        print(f"📊 Clustering {len(articles)} articles into events...")

        if not articles:
            return []

        # Filter articles with embeddings
        articles_with_embeddings = [a for a in articles if a.embedding]

        if len(articles_with_embeddings) < self.min_cluster_size:
            print(f"⚠️  Not enough articles with embeddings to cluster")
            return []

        # Extract embeddings
        embeddings = np.array([a.embedding for a in articles_with_embeddings])

        # Use DBSCAN for clustering
        # eps is related to similarity threshold (1 - similarity)
        eps = 1 - self.similarity_threshold
        clusterer = DBSCAN(eps=eps, min_samples=self.min_cluster_size, metric='cosine')

        try:
            labels = clusterer.fit_predict(embeddings)
        except Exception as e:
            print(f"❌ Error during clustering: {e}")
            return []

        # Group articles by cluster
        clusters_dict: Dict[int, List[Article]] = defaultdict(list)
        for article, label in zip(articles_with_embeddings, labels):
            if label != -1:  # -1 means noise/unclustered
                clusters_dict[label].append(article)

        # Create ArticleCluster objects
        clusters = []
        for cluster_id, cluster_articles in clusters_dict.items():
            cluster = self._create_cluster(cluster_id, cluster_articles)
            clusters.append(cluster)

        # Sort clusters by size (most articles first)
        clusters.sort(key=lambda c: c.article_count, reverse=True)

        print(f"✅ Created {len(clusters)} event clusters")
        print(f"   Unclustered articles: {sum(1 for l in labels if l == -1)}")

        return clusters

    def _create_cluster(self, cluster_id: int, articles: List[Article]) -> ArticleCluster:
        """Create an ArticleCluster from a list of articles"""
        # Generate unique cluster ID
        article_ids = sorted([a.id for a in articles])
        cluster_hash = hashlib.md5(''.join(article_ids).encode()).hexdigest()[:12]

        # Calculate centroid embedding
        embeddings = [a.embedding for a in articles if a.embedding]
        if embeddings:
            centroid = np.mean(embeddings, axis=0).tolist()
        else:
            centroid = None

        # Extract common keywords
        all_keywords = []
        for article in articles:
            all_keywords.extend(article.keywords)

        # Count keyword frequencies
        keyword_counts = defaultdict(int)
        for keyword in all_keywords:
            keyword_counts[keyword] += 1

        # Get top keywords that appear in multiple articles
        min_occurrences = max(2, len(articles) // 3)
        cluster_keywords = [
            kw for kw, count in keyword_counts.items()
            if count >= min_occurrences
        ][:10]

        # Generate event name from most common keywords and titles
        event_name = self._generate_event_name(articles, cluster_keywords)

        # Get time range
        dates = [a.published_at for a in articles]
        first_seen = min(dates)
        last_updated = max(dates)

        return ArticleCluster(
            id=f"cluster_{cluster_hash}",
            event_name=event_name,
            articles=articles,
            centroid_embedding=centroid,
            keywords=cluster_keywords,
            first_seen=first_seen,
            last_updated=last_updated,
            article_count=len(articles)
        )

    def _generate_event_name(self, articles: List[Article], keywords: List[str]) -> str:
        """Generate a descriptive name for the event cluster"""
        # Extract entities from all titles
        all_entities = {
            'countries': [],
            'leaders': [],
            'organizations': []
        }

        for article in articles:
            entities = self.nlp.extract_entities(article.title)
            for key in all_entities:
                all_entities[key].extend(entities.get(key, []))

        # Count entity frequencies
        country_counts = defaultdict(int)
        for country in all_entities['countries']:
            country_counts[country] += 1

        leader_counts = defaultdict(int)
        for leader in all_entities['leaders']:
            leader_counts[leader] += 1

        # Build event name
        name_parts = []

        # Add top leaders
        if leader_counts:
            top_leader = max(leader_counts, key=leader_counts.get)
            name_parts.append(top_leader.title())

        # Add top countries
        if country_counts:
            top_countries = sorted(
                country_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:2]
            for country, _ in top_countries:
                name_parts.append(country.title())

        # Add key topic keyword
        if keywords:
            name_parts.append(keywords[0])

        if not name_parts:
            # Fallback: use most common words from titles
            all_titles = ' '.join([a.title for a in articles])
            fallback_keywords = self.nlp.extract_keywords(all_titles, top_n=3)
            name_parts = [kw.title() for kw in fallback_keywords[:2]]

        event_name = ' - '.join(name_parts) if name_parts else "Geopolitical Event"

        return event_name[:100]  # Limit length

    def merge_clusters(self, old_clusters: List[ArticleCluster],
                      new_articles: List[Article]) -> List[ArticleCluster]:
        """Merge new articles into existing clusters or create new ones"""
        print(f"🔄 Merging {len(new_articles)} new articles into {len(old_clusters)} existing clusters...")

        updated_clusters = []
        unassigned_articles = []

        for article in new_articles:
            if not article.embedding:
                continue

            # Find best matching cluster
            best_cluster = None
            best_similarity = 0

            for cluster in old_clusters:
                if cluster.centroid_embedding:
                    similarity = self.nlp.cosine_similarity(
                        article.embedding,
                        cluster.centroid_embedding
                    )

                    if similarity > best_similarity and similarity >= self.similarity_threshold:
                        best_similarity = similarity
                        best_cluster = cluster

            if best_cluster:
                # Add article to existing cluster
                best_cluster.add_article(article)
            else:
                # Article doesn't fit any existing cluster
                unassigned_articles.append(article)

        # Create new clusters from unassigned articles
        if unassigned_articles:
            new_clusters = self.cluster_articles(unassigned_articles)
            old_clusters.extend(new_clusters)

        print(f"✅ Updated clusters: {len(old_clusters)} total")
        return old_clusters

    def get_cluster_statistics(self, clusters: List[ArticleCluster]) -> Dict:
        """Get statistics about clusters"""
        if not clusters:
            return {
                'total_clusters': 0,
                'total_articles': 0,
                'avg_articles_per_cluster': 0,
                'largest_cluster_size': 0
            }

        total_articles = sum(c.article_count for c in clusters)
        largest_cluster = max(clusters, key=lambda c: c.article_count)

        return {
            'total_clusters': len(clusters),
            'total_articles': total_articles,
            'avg_articles_per_cluster': total_articles / len(clusters),
            'largest_cluster_size': largest_cluster.article_count,
            'largest_cluster_name': largest_cluster.event_name
        }
