import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from src.models import Article, ArticleCluster, RhetoricAnalysis, EventPrediction


class DataStorage:
    """Handles data persistence for articles, clusters, and analyses"""

    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "raw"
        self.processed_path = self.base_path / "processed"
        self.analysis_path = self.base_path / "analysis"

        # Create directories
        for path in [self.raw_path, self.processed_path, self.analysis_path]:
            path.mkdir(parents=True, exist_ok=True)

    def save_articles(self, articles: List[Article], batch_id: Optional[str] = None) -> str:
        """Save articles to JSON file"""
        if batch_id is None:
            batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        filepath = self.raw_path / f"articles_{batch_id}.json"
        data = {
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat(),
            "count": len(articles),
            "articles": [article.model_dump() for article in articles]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        return batch_id

    def load_articles(self, batch_id: Optional[str] = None) -> List[Article]:
        """Load articles from JSON file"""
        if batch_id:
            filepath = self.raw_path / f"articles_{batch_id}.json"
        else:
            # Load most recent
            files = sorted(self.raw_path.glob("articles_*.json"))
            if not files:
                return []
            filepath = files[-1]

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [Article(**article) for article in data['articles']]

    def load_all_articles(self, days: Optional[int] = None) -> List[Article]:
        """Load all articles, optionally filtered by days"""
        all_articles = []
        files = sorted(self.raw_path.glob("articles_*.json"))

        for filepath in files:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                articles = [Article(**article) for article in data['articles']]

                if days:
                    cutoff = datetime.now().timestamp() - (days * 86400)
                    articles = [
                        a for a in articles
                        if a.published_at.timestamp() > cutoff
                    ]

                all_articles.extend(articles)

        return all_articles

    def save_clusters(self, clusters: List[ArticleCluster], timestamp: Optional[str] = None) -> str:
        """Save article clusters"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filepath = self.processed_path / f"clusters_{timestamp}.json"
        data = {
            "timestamp": datetime.now().isoformat(),
            "count": len(clusters),
            "clusters": [cluster.model_dump() for cluster in clusters]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        return timestamp

    def load_clusters(self, timestamp: Optional[str] = None) -> List[ArticleCluster]:
        """Load article clusters"""
        if timestamp:
            filepath = self.processed_path / f"clusters_{timestamp}.json"
        else:
            files = sorted(self.processed_path.glob("clusters_*.json"))
            if not files:
                return []
            filepath = files[-1]

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [ArticleCluster(**cluster) for cluster in data['clusters']]

    def save_analysis(self, analysis: RhetoricAnalysis) -> None:
        """Save rhetoric analysis"""
        filepath = self.analysis_path / f"analysis_{analysis.cluster_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis.model_dump(), f, indent=2, ensure_ascii=False, default=str)

    def save_predictions(self, predictions: List[EventPrediction]) -> None:
        """Save event predictions"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.analysis_path / f"predictions_{timestamp}.json"

        data = {
            "timestamp": datetime.now().isoformat(),
            "predictions": [pred.model_dump() for pred in predictions]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    def get_latest_predictions(self) -> List[EventPrediction]:
        """Load most recent predictions"""
        files = sorted(self.analysis_path.glob("predictions_*.json"))
        if not files:
            return []

        with open(files[-1], 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [EventPrediction(**pred) for pred in data['predictions']]
