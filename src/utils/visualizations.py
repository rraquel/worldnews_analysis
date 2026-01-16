"""
Visualization utilities for conflict analysis.
Creates charts and graphs for rhetoric evolution, sentiment trends, and topic analysis.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import io
import base64

from src.models.article import RhetoricAnalysis, ArticleCluster, EventPrediction


class ConflictVisualizer:
    """Creates visualizations for conflict analysis."""

    def __init__(self, style: str = "seaborn-v0_8-darkgrid"):
        """
        Initialize visualizer.

        Args:
            style: Matplotlib style to use
        """
        try:
            plt.style.use(style)
        except:
            plt.style.use("default")

        self.colors = {
            "escalating": "#d32f2f",
            "de-escalating": "#388e3c",
            "stable": "#fbc02d",
            "negative": "#e57373",
            "neutral": "#90a4ae",
            "positive": "#81c784"
        }

    def create_rhetoric_timeline(
        self,
        analysis: RhetoricAnalysis,
        cluster: ArticleCluster,
        title: Optional[str] = None
    ) -> Figure:
        """
        Create a timeline visualization showing how rhetoric evolves.

        Args:
            analysis: RhetoricAnalysis object
            cluster: ArticleCluster object
            title: Optional custom title

        Returns:
            Matplotlib Figure object
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        # Prepare sentiment trend data
        sentiment_trend = analysis.sentiment_trend
        if sentiment_trend and len(sentiment_trend) >= 2:
            dates = [datetime.fromisoformat(point["date"]) for point in sentiment_trend]
            scores = [point["score"] for point in sentiment_trend]

            # Plot 1: Sentiment over time
            ax1.plot(dates, scores, marker='o', linewidth=2, markersize=6,
                    color=self._get_sentiment_color(np.mean(scores)))
            ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
            ax1.fill_between(dates, scores, 0, alpha=0.3)
            ax1.set_ylabel('Sentiment Score', fontsize=11, fontweight='bold')
            ax1.set_title(title or f'Rhetoric Evolution: {cluster.event_name}',
                         fontsize=13, fontweight='bold', pad=15)
            ax1.grid(True, alpha=0.3)

            # Add tone shift annotation
            if analysis.tone_shift and analysis.tone_shift.get("direction") != "stable":
                shift = analysis.tone_shift
                ax1.text(0.02, 0.95,
                        f"Tone: {shift['initial_tone']} → {shift['current_tone']} "
                        f"({shift['direction']}, magnitude: {shift['magnitude']:.2f})",
                        transform=ax1.transAxes,
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                        verticalalignment='top',
                        fontsize=9)

        # Plot 2: Article frequency over time
        article_dates = [article.published_at for article in cluster.articles
                        if article.published_at]
        if article_dates:
            # Create histogram
            ax2.hist(article_dates, bins=min(20, len(article_dates)),
                    color='#1976d2', alpha=0.7, edgecolor='black')
            ax2.set_ylabel('Article Count', fontsize=11, fontweight='bold')
            ax2.set_xlabel('Date', fontsize=11, fontweight='bold')
            ax2.grid(True, alpha=0.3, axis='y')

            # Format x-axis
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Add urgency indicators
        if analysis.urgency_indicators:
            urgency_text = f"🚨 Urgency Indicators: {len(analysis.urgency_indicators)}"
            fig.text(0.98, 0.02, urgency_text, ha='right', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='#ffcdd2', alpha=0.8))

        plt.tight_layout()
        return fig

    def create_sentiment_heatmap(
        self,
        analyses: Dict[str, RhetoricAnalysis],
        clusters: Dict[str, ArticleCluster]
    ) -> Figure:
        """
        Create a heatmap showing sentiment across multiple events over time.

        Args:
            analyses: Dictionary mapping cluster_id to RhetoricAnalysis
            clusters: Dictionary mapping cluster_id to ArticleCluster

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(14, max(6, len(analyses) * 0.5)))

        # Prepare data
        event_names = []
        sentiment_data = []
        dates_list = []

        for cluster_id, analysis in analyses.items():
            cluster = clusters.get(cluster_id)
            if not cluster or not analysis.sentiment_trend:
                continue

            event_names.append(cluster.event_name[:50])  # Truncate long names
            dates = [datetime.fromisoformat(p["date"]) for p in analysis.sentiment_trend]
            scores = [p["score"] for p in analysis.sentiment_trend]

            dates_list.extend(dates)
            sentiment_data.append((dates, scores))

        if not sentiment_data:
            ax.text(0.5, 0.5, 'No sentiment data available',
                   ha='center', va='center', fontsize=14)
            return fig

        # Find common date range
        all_dates = sorted(set(dates_list))
        if len(all_dates) < 2:
            ax.text(0.5, 0.5, 'Insufficient temporal data',
                   ha='center', va='center', fontsize=14)
            return fig

        # Create grid
        matrix = np.zeros((len(event_names), len(all_dates)))
        matrix[:] = np.nan  # Fill with NaN for missing data

        for i, (dates, scores) in enumerate(sentiment_data):
            for date, score in zip(dates, scores):
                try:
                    j = all_dates.index(date)
                    matrix[i, j] = score
                except ValueError:
                    continue

        # Plot heatmap
        im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1,
                      interpolation='nearest')

        # Customize
        ax.set_xticks(np.arange(len(all_dates)))
        ax.set_yticks(np.arange(len(event_names)))
        ax.set_xticklabels([d.strftime('%m/%d') for d in all_dates], rotation=45, ha='right')
        ax.set_yticklabels(event_names)

        ax.set_title('Sentiment Heatmap Across Events', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Date', fontsize=11, fontweight='bold')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Sentiment Score', fontsize=10, fontweight='bold')

        plt.tight_layout()
        return fig

    def create_prediction_dashboard(
        self,
        predictions: List[EventPrediction],
        clusters: Dict[str, ArticleCluster]
    ) -> Figure:
        """
        Create a dashboard showing predictions and risk levels.

        Args:
            predictions: List of EventPrediction objects
            clusters: Dictionary mapping cluster_id to ArticleCluster

        Returns:
            Matplotlib Figure object
        """
        fig = plt.figure(figsize=(14, 10))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # Plot 1: Trajectory distribution (pie chart)
        ax1 = fig.add_subplot(gs[0, 0])
        trajectory_counts = {"escalating": 0, "de-escalating": 0, "stable": 0}
        for pred in predictions:
            trajectory_counts[pred.trajectory] += 1

        colors = [self.colors[t] for t in trajectory_counts.keys()]
        ax1.pie(trajectory_counts.values(), labels=trajectory_counts.keys(),
               autopct='%1.1f%%', colors=colors, startangle=90)
        ax1.set_title('Event Trajectories', fontsize=12, fontweight='bold')

        # Plot 2: Confidence scores
        ax2 = fig.add_subplot(gs[0, 1])
        event_names = [clusters.get(pred.cluster_id, type('obj', (), {'event_name': 'Unknown'})).event_name[:30]
                      for pred in predictions[:10]]  # Top 10
        confidences = [pred.confidence_score * 100 for pred in predictions[:10]]
        trajectory_colors = [self.colors[pred.trajectory] for pred in predictions[:10]]

        y_pos = np.arange(len(event_names))
        ax2.barh(y_pos, confidences, color=trajectory_colors, alpha=0.7)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(event_names, fontsize=8)
        ax2.set_xlabel('Confidence Score (%)', fontsize=10, fontweight='bold')
        ax2.set_title('Prediction Confidence', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')

        # Plot 3: Risk factors
        ax3 = fig.add_subplot(gs[1, :])
        risk_categories = {}
        for pred in predictions:
            for risk in pred.risk_factors:
                category = self._categorize_risk(risk)
                risk_categories[category] = risk_categories.get(category, 0) + 1

        if risk_categories:
            categories = list(risk_categories.keys())
            counts = list(risk_categories.values())

            bars = ax3.bar(categories, counts, color='#ff6f00', alpha=0.7, edgecolor='black')
            ax3.set_ylabel('Frequency', fontsize=10, fontweight='bold')
            ax3.set_title('Risk Factor Distribution', fontsize=12, fontweight='bold')
            ax3.grid(True, alpha=0.3, axis='y')
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontsize=9)

        plt.suptitle('Conflict Analysis Dashboard', fontsize=15, fontweight='bold', y=0.98)
        plt.tight_layout()
        return fig

    def create_topic_visualization(
        self,
        topic_data: Dict,
        cluster_name: str
    ) -> Figure:
        """
        Create visualization for topic modeling results.

        Args:
            topic_data: Topic modeling results
            cluster_name: Name of the cluster

        Returns:
            Matplotlib Figure object
        """
        topics = topic_data.get("topics", [])
        if not topics:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No topics identified',
                   ha='center', va='center', fontsize=14)
            ax.set_title(f'Topic Analysis: {cluster_name}', fontsize=13, fontweight='bold')
            return fig

        n_topics = min(5, len(topics))
        fig, axes = plt.subplots(n_topics, 1, figsize=(12, 3 * n_topics))

        if n_topics == 1:
            axes = [axes]

        for i, topic in enumerate(topics[:n_topics]):
            ax = axes[i]

            # Get top keywords
            keywords = [kw["word"] for kw in topic["keywords"][:10]]
            scores = [kw["score"] for kw in topic["keywords"][:10]]

            # Horizontal bar chart
            y_pos = np.arange(len(keywords))
            bars = ax.barh(y_pos, scores, color='#1976d2', alpha=0.7)

            # Gradient effect
            for j, bar in enumerate(bars):
                bar.set_alpha(0.9 - j * 0.05)

            ax.set_yticks(y_pos)
            ax.set_yticklabels(keywords)
            ax.invert_yaxis()
            ax.set_xlabel('Relevance Score', fontsize=9, fontweight='bold')
            ax.set_title(f'{topic["label"]} (n={topic["count"]})',
                        fontsize=10, fontweight='bold', loc='left')

            # Add temporal trend
            temp_dist = topic.get("temporal_distribution", {})
            trend = temp_dist.get("trend", "unknown")
            if trend != "insufficient_data":
                trend_emoji = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(trend, "")
                ax.text(0.98, 0.95, f"{trend_emoji} {trend}",
                       transform=ax.transAxes,
                       ha='right', va='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7),
                       fontsize=8)

            ax.grid(True, alpha=0.3, axis='x')

        plt.suptitle(f'Topic Modeling: {cluster_name}',
                    fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        return fig

    def create_actor_network(
        self,
        analysis: RhetoricAnalysis,
        cluster_name: str,
        top_n: int = 15
    ) -> Figure:
        """
        Create a visualization of actors mentioned in the conflict.

        Args:
            analysis: RhetoricAnalysis object
            cluster_name: Name of the cluster
            top_n: Number of top actors to display

        Returns:
            Matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        actor_mentions = analysis.actor_mentions
        if not actor_mentions:
            ax.text(0.5, 0.5, 'No actor mentions identified',
                   ha='center', va='center', fontsize=14)
            ax.set_title(f'Actor Analysis: {cluster_name}', fontsize=13, fontweight='bold')
            return fig

        # Sort by frequency
        sorted_actors = sorted(actor_mentions.items(), key=lambda x: x[1], reverse=True)[:top_n]
        actors = [actor for actor, _ in sorted_actors]
        counts = [count for _, count in sorted_actors]

        # Create bar chart with color gradient
        colors_gradient = plt.cm.Reds(np.linspace(0.4, 0.9, len(actors)))
        bars = ax.barh(actors, counts, color=colors_gradient, edgecolor='black', linewidth=0.5)

        ax.set_xlabel('Mention Count', fontsize=11, fontweight='bold')
        ax.set_title(f'Key Actors: {cluster_name}', fontsize=13, fontweight='bold', pad=15)
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')

        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, counts)):
            ax.text(count, bar.get_y() + bar.get_height()/2,
                   f' {count}',
                   ha='left', va='center', fontsize=9, fontweight='bold')

        plt.tight_layout()
        return fig

    def _get_sentiment_color(self, score: float) -> str:
        """Get color based on sentiment score."""
        if score < -0.3:
            return self.colors["negative"]
        elif score > 0.3:
            return self.colors["positive"]
        else:
            return self.colors["neutral"]

    def _categorize_risk(self, risk_factor: str) -> str:
        """Categorize a risk factor into broader categories."""
        risk_lower = risk_factor.lower()

        if any(word in risk_lower for word in ["military", "weapon", "armed", "force"]):
            return "Military"
        elif any(word in risk_lower for word in ["diplomatic", "negotiation", "talk"]):
            return "Diplomatic"
        elif any(word in risk_lower for word in ["economic", "sanction", "trade"]):
            return "Economic"
        elif any(word in risk_lower for word in ["urgent", "crisis", "emergency"]):
            return "Urgency"
        elif any(word in risk_lower for word in ["actor", "country", "leader"]):
            return "Actors"
        elif any(word in risk_lower for word in ["coverage", "attention", "media"]):
            return "Media Coverage"
        else:
            return "Other"

    def fig_to_base64(self, fig: Figure) -> str:
        """
        Convert matplotlib figure to base64 string for embedding in HTML.

        Args:
            fig: Matplotlib Figure object

        Returns:
            Base64 encoded string
        """
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        return img_str

    def save_figure(self, fig: Figure, filepath: str, dpi: int = 300):
        """
        Save figure to file.

        Args:
            fig: Matplotlib Figure object
            filepath: Path to save the figure
            dpi: Resolution in dots per inch
        """
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
