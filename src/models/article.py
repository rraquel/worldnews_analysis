from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Article(BaseModel):
    """Model for a news article"""
    id: str
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    url: str
    source: str
    author: Optional[str] = None
    published_at: datetime
    content_snippet: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    sentiment_score: Optional[float] = None
    embedding: Optional[List[float]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ArticleCluster(BaseModel):
    """Model for a cluster of related articles about the same event"""
    id: str
    event_name: str
    articles: List[Article]
    centroid_embedding: Optional[List[float]] = None
    keywords: List[str] = Field(default_factory=list)
    first_seen: datetime
    last_updated: datetime
    article_count: int

    def add_article(self, article: Article):
        """Add an article to the cluster"""
        self.articles.append(article)
        self.article_count = len(self.articles)
        self.last_updated = datetime.now()


class RhetoricAnalysis(BaseModel):
    """Model for rhetoric analysis of a cluster over time"""
    cluster_id: str
    event_name: str
    analysis_date: datetime
    time_period_days: int

    # Rhetoric metrics
    sentiment_trend: List[Dict[str, Any]]  # [{date, sentiment_score}]
    key_phrases: List[Dict[str, Any]]  # [{phrase, frequency, period}]
    tone_shift: Dict[str, Any]  # {initial_tone, current_tone, shift_magnitude}
    urgency_indicators: List[str]
    actor_mentions: Dict[str, int]  # {actor_name: mention_count}

    # Linguistic patterns
    linguistic_features: Dict[str, Any]
    rhetoric_evolution: str  # Narrative description


class EventPrediction(BaseModel):
    """Model for predictions about event trajectory"""
    cluster_id: str
    event_name: str
    prediction_date: datetime

    # Predictions
    trajectory: str  # escalating, de-escalating, stable
    confidence_score: float
    key_indicators: List[str]
    similar_historical_patterns: List[str]

    # Forecasts
    short_term_outlook: str  # next 7 days
    medium_term_outlook: str  # next 30 days
    risk_factors: List[str]
    attention_metrics: Dict[str, Any]  # coverage intensity, source diversity
