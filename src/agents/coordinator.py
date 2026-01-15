import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from src.agents import (
    NewsAggregatorAgent,
    EventClusteringAgent,
    RhetoricAnalyzerAgent,
    PredictionAgent
)
from src.models import ArticleCluster, RhetoricAnalysis, EventPrediction
from src.utils import DataStorage


class CoordinatorAgent:
    """
    Master agent that coordinates all other agents to perform
    comprehensive news analysis workflow
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Initialize storage
        self.storage = DataStorage()

        # Initialize agents
        self.news_aggregator = NewsAggregatorAgent(
            newsapi_key=self.config.get('newsapi_key'),
            guardian_key=self.config.get('guardian_key')
        )

        self.clusterer = EventClusteringAgent(
            similarity_threshold=self.config.get('similarity_threshold', 0.7),
            min_cluster_size=self.config.get('min_cluster_size', 2)
        )

        self.rhetoric_analyzer = RhetoricAnalyzerAgent(
            time_period_days=self.config.get('time_period_days', 30)
        )

        self.predictor = PredictionAgent()

        print("✅ CoordinatorAgent initialized with all sub-agents")

    def run_full_analysis(self, days_back: int = 7, use_existing: bool = False) -> Dict[str, Any]:
        """
        Run the complete analysis pipeline:
        1. Fetch news articles
        2. Cluster into events
        3. Analyze rhetoric for each event
        4. Generate predictions
        5. Create summary report
        """
        print("\n" + "="*60)
        print("🚀 Starting Full News Analysis Pipeline")
        print("="*60 + "\n")

        results = {}

        # Step 1: Fetch or load articles
        if use_existing:
            print("📂 Loading existing articles...")
            articles = self.storage.load_all_articles(days=days_back)
            if not articles:
                print("⚠️  No existing articles found, fetching new ones...")
                articles = self.news_aggregator.fetch_news(days_back=days_back)
                batch_id = self.storage.save_articles(articles)
                results['batch_id'] = batch_id
        else:
            print("\n📰 STEP 1: Fetching News Articles")
            print("-" * 60)
            articles = self.news_aggregator.fetch_news(days_back=days_back)
            batch_id = self.storage.save_articles(articles)
            results['batch_id'] = batch_id

        results['total_articles'] = len(articles)

        if not articles:
            print("❌ No articles collected. Please check API keys.")
            return results

        # Step 2: Cluster articles into events
        print("\n🔗 STEP 2: Clustering Articles into Events")
        print("-" * 60)
        clusters = self.clusterer.cluster_articles(articles)
        results['total_clusters'] = len(clusters)

        if clusters:
            timestamp = self.storage.save_clusters(clusters)
            results['cluster_timestamp'] = timestamp

            # Get cluster statistics
            stats = self.clusterer.get_cluster_statistics(clusters)
            results['cluster_stats'] = stats

            print(f"\n📊 Cluster Statistics:")
            print(f"   Total clusters: {stats['total_clusters']}")
            print(f"   Total articles: {stats['total_articles']}")
            print(f"   Avg articles/cluster: {stats['avg_articles_per_cluster']:.1f}")
            print(f"   Largest cluster: {stats['largest_cluster_name']} ({stats['largest_cluster_size']} articles)")

        # Step 3: Analyze rhetoric for each cluster
        print("\n📝 STEP 3: Analyzing Rhetoric for Each Event")
        print("-" * 60)
        analyses = []
        for cluster in clusters:
            analysis = self.rhetoric_analyzer.analyze_cluster(cluster)
            analyses.append(analysis)
            self.storage.save_analysis(analysis)

        results['total_analyses'] = len(analyses)

        # Cross-cluster comparison
        if len(clusters) > 1:
            print("\n🔄 Comparing rhetoric across events...")
            comparison = self.rhetoric_analyzer.compare_clusters(clusters)
            results['cross_cluster_comparison'] = comparison

            print(f"\n📊 Cross-Cluster Analysis:")
            print(f"   Most negative: {comparison['most_negative']}")
            print(f"   Most positive: {comparison['most_positive']}")
            print(f"   Most urgent: {comparison['most_urgent']}")
            print(f"   Most active: {comparison['most_active']}")
            print(f"   Overall sentiment: {comparison['sentiment_summary']['interpretation']}")

        # Step 4: Generate predictions
        print("\n🔮 STEP 4: Generating Event Predictions")
        print("-" * 60)
        predictions = []
        for cluster, analysis in zip(clusters, analyses):
            prediction = self.predictor.predict_trajectory(cluster, analysis)
            predictions.append(prediction)

        if predictions:
            self.storage.save_predictions(predictions)
            results['total_predictions'] = len(predictions)

            # Generate summary report
            summary = self.predictor.generate_summary_report(predictions)
            results['prediction_summary'] = summary

            print(f"\n📊 Prediction Summary:")
            print(f"   Total events analyzed: {summary['total_events']}")
            print(f"   Escalating: {summary['escalating_count']}")
            print(f"   De-escalating: {summary['de_escalating_count']}")
            print(f"   Stable: {summary['stable_count']}")

            if summary.get('most_concerning_events'):
                print(f"\n⚠️  Most Concerning Events:")
                for event in summary['most_concerning_events']:
                    print(f"   - {event['event']}: {event['risk_factors']} risk factors")

        # Step 5: Generate detailed report
        print("\n📄 STEP 5: Generating Detailed Report")
        print("-" * 60)
        report = self._generate_report(clusters, analyses, predictions)
        results['report'] = report

        print("\n" + "="*60)
        print("✅ Analysis Complete!")
        print("="*60)

        return results

    def update_analysis(self, days_back: int = 1) -> Dict[str, Any]:
        """
        Update existing analysis with new articles
        """
        print("\n🔄 Updating Analysis with New Articles")
        print("-" * 60)

        # Fetch new articles
        new_articles = self.news_aggregator.fetch_news(days_back=days_back)

        if not new_articles:
            print("ℹ️  No new articles found")
            return {'new_articles': 0}

        # Save new articles
        batch_id = self.storage.save_articles(new_articles)

        # Load existing clusters
        existing_clusters = self.storage.load_clusters()

        # Merge new articles into clusters
        updated_clusters = self.clusterer.merge_clusters(existing_clusters, new_articles)

        # Save updated clusters
        timestamp = self.storage.save_clusters(updated_clusters)

        print(f"✅ Analysis updated with {len(new_articles)} new articles")

        return {
            'new_articles': len(new_articles),
            'batch_id': batch_id,
            'cluster_timestamp': timestamp,
            'total_clusters': len(updated_clusters)
        }

    def _generate_report(self, clusters: List[ArticleCluster],
                        analyses: List[RhetoricAnalysis],
                        predictions: List[EventPrediction]) -> str:
        """Generate a comprehensive text report"""
        report_lines = []

        report_lines.append("="*80)
        report_lines.append("GEOPOLITICAL NEWS ANALYSIS REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("="*80)
        report_lines.append("")

        # Executive Summary
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-"*80)
        report_lines.append(f"Total Events Analyzed: {len(clusters)}")
        report_lines.append(f"Total Articles Processed: {sum(c.article_count for c in clusters)}")
        report_lines.append("")

        # Event-by-event analysis
        report_lines.append("DETAILED EVENT ANALYSIS")
        report_lines.append("-"*80)
        report_lines.append("")

        for cluster, analysis, prediction in zip(clusters, analyses, predictions):
            report_lines.append(f"EVENT: {cluster.event_name}")
            report_lines.append(f"{'='*len(cluster.event_name)}")
            report_lines.append("")

            # Basic info
            report_lines.append(f"Articles: {cluster.article_count}")
            report_lines.append(f"Time Period: {cluster.first_seen.strftime('%Y-%m-%d')} to {cluster.last_updated.strftime('%Y-%m-%d')}")
            report_lines.append(f"Keywords: {', '.join(cluster.keywords[:10])}")
            report_lines.append("")

            # Rhetoric analysis
            report_lines.append("Rhetoric Analysis:")
            report_lines.append(f"  Tone: {analysis.tone_shift['initial_tone']} → {analysis.tone_shift['current_tone']}")
            report_lines.append(f"  Trend: {analysis.tone_shift['shift_direction']}")
            report_lines.append(f"  Rhetoric Evolution: {analysis.rhetoric_evolution}")
            report_lines.append("")

            # Prediction
            report_lines.append("Prediction:")
            report_lines.append(f"  Trajectory: {prediction.trajectory.upper()}")
            report_lines.append(f"  Confidence: {prediction.confidence_score:.2%}")
            report_lines.append(f"  Short-term Outlook: {prediction.short_term_outlook}")
            report_lines.append("")

            if prediction.risk_factors:
                report_lines.append("  Risk Factors:")
                for risk in prediction.risk_factors:
                    report_lines.append(f"    - {risk}")
                report_lines.append("")

            # Key indicators
            if prediction.key_indicators:
                report_lines.append("  Key Indicators:")
                for indicator in prediction.key_indicators:
                    report_lines.append(f"    - {indicator}")
                report_lines.append("")

            report_lines.append("-"*80)
            report_lines.append("")

        return "\n".join(report_lines)

    def export_report(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Export the analysis report to a file"""
        if filename is None:
            filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        filepath = os.path.join("data", "analysis", filename)

        report_text = results.get('report', '')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_text)

        print(f"📄 Report exported to: {filepath}")
        return filepath

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the analysis system"""
        return {
            'storage_paths': {
                'raw': str(self.storage.raw_path),
                'processed': str(self.storage.processed_path),
                'analysis': str(self.storage.analysis_path)
            },
            'agents': {
                'news_aggregator': 'ready',
                'clusterer': 'ready',
                'rhetoric_analyzer': 'ready',
                'predictor': 'ready'
            },
            'config': self.config
        }
