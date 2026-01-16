"""
Streamlit interface for Global Conflict Analysis.
Allows users to select topics, configure analysis depth, and view results with visualizations.
"""

import streamlit as st
import os
from datetime import datetime, timedelta
from typing import List, Dict
import json

# Configure page
st.set_page_config(
    page_title="Global Conflict Analysis Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.conflict_topics import (
    GLOBAL_CONFLICT_TOPICS,
    ANALYSIS_DEPTH_CONFIG,
    RISK_COLORS,
    CONFLICT_CATEGORIES,
    get_topics_by_risk_level,
    get_topics_by_category
)
from src.agents.coordinator import CoordinatorAgent
from src.utils.storage import DataStorage
from src.utils.topic_modeling import TopicModeler
from src.utils.visualizations import ConflictVisualizer
from src.models.article import ArticleCluster, RhetoricAnalysis, EventPrediction


# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'selected_topics' not in st.session_state:
    st.session_state.selected_topics = []


def main():
    """Main application function."""

    # Header
    st.title("🌍 Global Conflict Analysis Dashboard")
    st.markdown("""
    Analyze global conflicts and emerging threats that could affect world order.
    Select topics, configure analysis depth, and receive comprehensive reports with visualizations.
    """)

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Analysis depth selection
        st.subheader("Analysis Depth")
        depth_option = st.radio(
            "Select depth level:",
            options=["quick", "standard", "deep"],
            format_func=lambda x: f"{ANALYSIS_DEPTH_CONFIG[x]['name']} - {ANALYSIS_DEPTH_CONFIG[x]['description']}",
            index=1  # Default to standard
        )

        depth_config = ANALYSIS_DEPTH_CONFIG[depth_option]

        # Display depth details
        with st.expander("Depth Details"):
            st.write(f"**Days of data:** {depth_config['days_back']}")
            st.write(f"**Max articles:** {depth_config['max_articles']}")
            st.write(f"**Topic modeling:** {'✅' if depth_config['include_topic_modeling'] else '❌'}")
            st.write(f"**Predictions:** {'✅' if depth_config['include_predictions'] else '❌'}")

        st.divider()

        # Topic selection mode
        st.subheader("Topic Selection")
        selection_mode = st.radio(
            "Choose selection mode:",
            ["Select from predefined topics", "Analyze all discovered events"]
        )

        if selection_mode == "Select from predefined topics":
            # Filter options
            st.subheader("Filters")

            filter_by = st.selectbox(
                "Filter topics by:",
                ["All Topics", "Risk Level", "Category"]
            )

            available_topics = GLOBAL_CONFLICT_TOPICS

            if filter_by == "Risk Level":
                risk_filter = st.multiselect(
                    "Select risk levels:",
                    ["critical", "high", "medium", "low"],
                    default=["critical", "high"]
                )
                available_topics = [t for t in GLOBAL_CONFLICT_TOPICS
                                  if t["risk_level"] in risk_filter]

            elif filter_by == "Category":
                category_filter = st.multiselect(
                    "Select categories:",
                    list(CONFLICT_CATEGORIES.keys()),
                    format_func=lambda x: f"{CONFLICT_CATEGORIES[x]['icon']} {CONFLICT_CATEGORIES[x]['description']}"
                )
                available_topics = [t for t in GLOBAL_CONFLICT_TOPICS
                                  if t["category"] in category_filter]

            st.divider()

            # Topic selection
            st.subheader("Select Topics")
            selected_topics = []

            for topic in available_topics:
                col1, col2 = st.columns([0.7, 0.3])
                with col1:
                    if st.checkbox(
                        f"{topic['name']}",
                        key=topic['id']
                    ):
                        selected_topics.append(topic)
                with col2:
                    risk_color = RISK_COLORS[topic['risk_level']]
                    st.markdown(
                        f"<span style='color:{risk_color};font-weight:bold'>{topic['risk_level'].upper()}</span>",
                        unsafe_allow_html=True
                    )

            st.session_state.selected_topics = selected_topics

        else:
            st.info("Will analyze all events discovered in the news aggregation.")
            st.session_state.selected_topics = []

    # Main content area
    if not st.session_state.analysis_complete:
        # Show topic summary
        if selection_mode == "Select from predefined topics":
            if st.session_state.selected_topics:
                st.subheader("📋 Selected Topics")

                cols = st.columns(3)
                for i, topic in enumerate(st.session_state.selected_topics):
                    with cols[i % 3]:
                        category = CONFLICT_CATEGORIES[topic['category']]
                        st.markdown(f"""
                        **{category['icon']} {topic['name']}**

                        {topic['description']}

                        *Risk:* <span style='color:{RISK_COLORS[topic['risk_level']]}'>{topic['risk_level']}</span>
                        """, unsafe_allow_html=True)

                # Run analysis button
                if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
                    run_analysis(depth_config, st.session_state.selected_topics, selection_mode)
            else:
                st.info("👈 Please select at least one topic from the sidebar to begin analysis.")

        else:
            # Run analysis button for all events
            if st.button("🚀 Run Analysis on All Events", type="primary", use_container_width=True):
                run_analysis(depth_config, [], selection_mode)

    else:
        # Display results
        display_results(depth_config)

        # Reset button
        if st.button("🔄 New Analysis", type="secondary"):
            st.session_state.analysis_complete = False
            st.session_state.results = None
            st.session_state.selected_topics = []
            st.rerun()


def run_analysis(depth_config: Dict, selected_topics: List[Dict], selection_mode: str):
    """
    Run the conflict analysis.

    Args:
        depth_config: Analysis depth configuration
        selected_topics: List of selected topic dictionaries
        selection_mode: Topic selection mode
    """
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Initialize components
        status_text.text("🔧 Initializing analysis components...")
        coordinator = CoordinatorAgent()
        storage = DataStorage()
        progress_bar.progress(10)

        # Fetch news
        status_text.text("📰 Fetching news articles...")

        # Build search terms from selected topics
        if selection_mode == "Select from predefined topics" and selected_topics:
            search_terms = []
            for topic in selected_topics:
                search_terms.extend(topic['keywords'][:3])  # Top 3 keywords per topic
        else:
            search_terms = None  # Use default search terms

        articles = coordinator.news_aggregator.fetch_news(
            days_back=depth_config['days_back'],
            max_articles=depth_config['max_articles']
        )
        progress_bar.progress(30)

        if not articles:
            st.error("No articles found. Please try different topics or time range.")
            return

        status_text.text(f"✅ Found {len(articles)} articles")

        # Cluster events
        status_text.text("🔍 Clustering events...")
        clusters = coordinator.event_clustering.cluster_articles(articles)
        progress_bar.progress(50)

        if not clusters:
            st.error("No event clusters identified.")
            return

        status_text.text(f"✅ Identified {len(clusters)} events")

        # Analyze rhetoric
        status_text.text("📊 Analyzing rhetoric...")
        analyses = {}
        for cluster in clusters:
            analysis = coordinator.rhetoric_analyzer.analyze_cluster(cluster)
            analyses[cluster.id] = analysis
        progress_bar.progress(70)

        # Generate predictions
        predictions = []
        if depth_config['include_predictions']:
            status_text.text("🔮 Generating predictions...")
            for cluster in clusters:
                analysis = analyses[cluster.id]
                prediction = coordinator.prediction_agent.predict_trajectory(cluster, analysis)
                predictions.append(prediction)
        progress_bar.progress(85)

        # Topic modeling
        topic_results = {}
        if depth_config['include_topic_modeling']:
            status_text.text("🏷️ Performing topic modeling...")
            topic_modeler = TopicModeler(method="bertopic")
            for cluster in clusters:
                topics = topic_modeler.extract_topics_from_cluster(cluster, n_topics=None)
                topic_results[cluster.id] = topics
        progress_bar.progress(95)

        # Save results
        status_text.text("💾 Saving results...")
        storage.save_clusters(clusters)
        for cluster_id, analysis in analyses.items():
            storage.save_analysis(analysis)
        if predictions:
            storage.save_predictions(predictions)

        # Store in session state
        st.session_state.results = {
            'clusters': clusters,
            'analyses': analyses,
            'predictions': predictions,
            'topic_results': topic_results,
            'depth_config': depth_config,
            'selected_topics': selected_topics,
            'timestamp': datetime.now()
        }
        st.session_state.analysis_complete = True

        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")

        st.rerun()

    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


def display_results(depth_config: Dict):
    """
    Display analysis results with visualizations.

    Args:
        depth_config: Analysis depth configuration
    """
    results = st.session_state.results
    clusters = results['clusters']
    analyses = results['analyses']
    predictions = results['predictions']
    topic_results = results['topic_results']

    # Summary statistics
    st.header("📊 Analysis Summary")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Events Identified", len(clusters))
    with col2:
        total_articles = sum(len(c.articles) for c in clusters)
        st.metric("Total Articles", total_articles)
    with col3:
        if predictions:
            escalating = sum(1 for p in predictions if p.trajectory == "escalating")
            st.metric("Escalating Events", escalating, delta=f"{escalating/len(predictions)*100:.0f}%")
    with col4:
        st.metric("Analysis Depth", depth_config['name'])

    # Overall dashboard
    if predictions:
        st.subheader("🎯 Prediction Dashboard")
        visualizer = ConflictVisualizer()
        cluster_dict = {c.id: c for c in clusters}

        fig = visualizer.create_prediction_dashboard(predictions, cluster_dict)
        st.pyplot(fig)

    # Sentiment heatmap
    if len(clusters) > 1:
        st.subheader("🌡️ Sentiment Heatmap")
        visualizer = ConflictVisualizer()
        cluster_dict = {c.id: c for c in clusters}

        fig = visualizer.create_sentiment_heatmap(analyses, cluster_dict)
        st.pyplot(fig)

    st.divider()

    # Individual event analysis
    st.header("📰 Detailed Event Analysis")

    # Sort events by prediction trajectory
    sorted_clusters = clusters
    if predictions:
        pred_dict = {p.cluster_id: p for p in predictions}
        sorted_clusters = sorted(
            clusters,
            key=lambda c: (
                0 if pred_dict.get(c.id, type('obj', (), {'trajectory': 'stable'})).trajectory == "escalating"
                else 1 if pred_dict.get(c.id, type('obj', (), {'trajectory': 'stable'})).trajectory == "stable"
                else 2
            )
        )

    for cluster in sorted_clusters:
        with st.expander(f"📌 {cluster.event_name} ({len(cluster.articles)} articles)", expanded=False):
            analysis = analyses[cluster.id]
            prediction = next((p for p in predictions if p.cluster_id == cluster.id), None)

            # Event metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**First Seen:** {cluster.first_seen.strftime('%Y-%m-%d %H:%M')}")
            with col2:
                st.write(f"**Last Updated:** {cluster.last_updated.strftime('%Y-%m-%d %H:%M')}")
            with col3:
                if prediction:
                    color = {"escalating": "🔴", "stable": "🟡", "de-escalating": "🟢"}[prediction.trajectory]
                    st.write(f"**Trajectory:** {color} {prediction.trajectory.upper()}")

            # Tabs for different views
            tabs = st.tabs(["📈 Rhetoric Timeline", "🏷️ Topics", "👥 Actors", "📝 Report", "📄 Articles"])

            # Tab 1: Rhetoric timeline
            with tabs[0]:
                visualizer = ConflictVisualizer()
                fig = visualizer.create_rhetoric_timeline(analysis, cluster)
                st.pyplot(fig)

                # Tone shift summary
                if analysis.tone_shift:
                    shift = analysis.tone_shift
                    st.info(f"""
                    **Tone Evolution:** {shift['initial_tone']} → {shift['current_tone']}
                    **Direction:** {shift['direction']}
                    **Magnitude:** {shift['magnitude']:.2f}
                    """)

            # Tab 2: Topic modeling
            with tabs[1]:
                if cluster.id in topic_results:
                    topics = topic_results[cluster.id]

                    if topics.get('topics'):
                        # Topic visualization
                        visualizer = ConflictVisualizer()
                        fig = visualizer.create_topic_visualization(topics, cluster.event_name)
                        st.pyplot(fig)

                        # Topic details
                        st.subheader("Topic Details")
                        for i, topic in enumerate(topics['topics'][:3], 1):
                            st.markdown(f"**{topic['label']}** ({topic['count']} articles)")
                            keywords = ", ".join([kw['word'] for kw in topic['keywords'][:8]])
                            st.write(f"Keywords: {keywords}")

                            if topic.get('sample_titles'):
                                with st.expander("Sample articles"):
                                    for title in topic['sample_titles']:
                                        st.write(f"- {title}")
                    else:
                        st.info("No distinct topics identified for this event.")
                else:
                    st.info("Topic modeling not performed for this depth level.")

            # Tab 3: Actors
            with tabs[2]:
                if analysis.actor_mentions:
                    visualizer = ConflictVisualizer()
                    fig = visualizer.create_actor_network(analysis, cluster.event_name)
                    st.pyplot(fig)
                else:
                    st.info("No actors identified in this event.")

            # Tab 4: Text report
            with tabs[3]:
                st.subheader("Rhetoric Analysis")
                if analysis.rhetoric_evolution:
                    st.write(analysis.rhetoric_evolution)

                if analysis.urgency_indicators:
                    st.warning(f"**🚨 Urgency Indicators:** {len(analysis.urgency_indicators)}")
                    for indicator in analysis.urgency_indicators[:5]:
                        st.write(f"- {indicator}")

                if prediction:
                    st.subheader("Trajectory Prediction")
                    st.write(f"**Trajectory:** {prediction.trajectory.upper()}")
                    st.write(f"**Confidence:** {prediction.confidence_score * 100:.1f}%")

                    st.write("**Key Indicators:**")
                    for indicator in prediction.key_indicators:
                        st.write(f"- {indicator}")

                    st.write(f"**Short-term Outlook (7 days):** {prediction.short_term_outlook}")
                    st.write(f"**Medium-term Outlook (30 days):** {prediction.medium_term_outlook}")

                    if prediction.risk_factors:
                        st.write("**Risk Factors:**")
                        for risk in prediction.risk_factors:
                            st.write(f"- {risk}")

            # Tab 5: Articles
            with tabs[4]:
                st.write(f"**{len(cluster.articles)} articles in this cluster**")
                for article in cluster.articles[:10]:  # Show first 10
                    with st.container():
                        st.markdown(f"**{article.title}**")
                        st.caption(f"{article.source} - {article.published_at.strftime('%Y-%m-%d %H:%M')}")
                        if article.description:
                            st.write(article.description[:200] + "...")
                        if article.url:
                            st.markdown(f"[Read more]({article.url})")
                        st.divider()

    # Export options
    st.header("💾 Export Results")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Export Text Report"):
            report = generate_text_report(results)
            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"conflict_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

    with col2:
        if st.button("📊 Export JSON Data"):
            json_data = export_to_json(results)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"conflict_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )


def generate_text_report(results: Dict) -> str:
    """Generate comprehensive text report."""
    clusters = results['clusters']
    analyses = results['analyses']
    predictions = results['predictions']
    topic_results = results['topic_results']

    lines = []
    lines.append("=" * 80)
    lines.append("GLOBAL CONFLICT ANALYSIS REPORT")
    lines.append("=" * 80)
    lines.append(f"\nGenerated: {results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Analysis Depth: {results['depth_config']['name']}")
    lines.append(f"\nEvents Analyzed: {len(clusters)}")
    lines.append(f"Total Articles: {sum(len(c.articles) for c in clusters)}")

    if predictions:
        escalating = sum(1 for p in predictions if p.trajectory == "escalating")
        stable = sum(1 for p in predictions if p.trajectory == "stable")
        deescalating = sum(1 for p in predictions if p.trajectory == "de-escalating")
        lines.append(f"\nTrajectories:")
        lines.append(f"  - Escalating: {escalating}")
        lines.append(f"  - Stable: {stable}")
        lines.append(f"  - De-escalating: {deescalating}")

    lines.append("\n" + "=" * 80)
    lines.append("DETAILED EVENT ANALYSIS")
    lines.append("=" * 80)

    for cluster in clusters:
        analysis = analyses[cluster.id]
        prediction = next((p for p in predictions if p.cluster_id == cluster.id), None)

        lines.append(f"\n\n{'=' * 80}")
        lines.append(f"EVENT: {cluster.event_name}")
        lines.append(f"{'=' * 80}")
        lines.append(f"\nArticles: {len(cluster.articles)}")
        lines.append(f"Time Period: {cluster.first_seen.strftime('%Y-%m-%d')} to {cluster.last_updated.strftime('%Y-%m-%d')}")
        lines.append(f"Keywords: {', '.join(cluster.keywords[:10])}")

        if analysis.tone_shift:
            shift = analysis.tone_shift
            lines.append(f"\nTone: {shift['initial_tone']} → {shift['current_tone']} ({shift['direction']})")

        if prediction:
            lines.append(f"\nTrajectory: {prediction.trajectory.upper()}")
            lines.append(f"Confidence: {prediction.confidence_score * 100:.1f}%")
            lines.append(f"\nShort-term Outlook: {prediction.short_term_outlook}")
            lines.append(f"Medium-term Outlook: {prediction.medium_term_outlook}")

        if cluster.id in topic_results:
            topics = topic_results[cluster.id]
            if topics.get('topics'):
                lines.append(f"\nTopics Identified: {len(topics['topics'])}")
                for i, topic in enumerate(topics['topics'][:3], 1):
                    keywords = ", ".join([kw['word'] for kw in topic['keywords'][:5]])
                    lines.append(f"  {i}. {topic['label']} - {keywords}")

        lines.append("\n" + "-" * 80)

    return "\n".join(lines)


def export_to_json(results: Dict) -> str:
    """Export results to JSON format."""
    export_data = {
        'timestamp': results['timestamp'].isoformat(),
        'depth_config': results['depth_config']['name'],
        'events': []
    }

    for cluster in results['clusters']:
        analysis = results['analyses'][cluster.id]
        prediction = next((p for p in results['predictions'] if p.cluster_id == cluster.id), None)

        event_data = {
            'event_name': cluster.event_name,
            'article_count': len(cluster.articles),
            'first_seen': cluster.first_seen.isoformat(),
            'last_updated': cluster.last_updated.isoformat(),
            'keywords': cluster.keywords,
            'tone_shift': analysis.tone_shift,
            'urgency_indicators': analysis.urgency_indicators,
            'actor_mentions': analysis.actor_mentions,
        }

        if prediction:
            event_data['prediction'] = {
                'trajectory': prediction.trajectory,
                'confidence': prediction.confidence_score,
                'short_term_outlook': prediction.short_term_outlook,
                'medium_term_outlook': prediction.medium_term_outlook,
                'risk_factors': prediction.risk_factors
            }

        if cluster.id in results['topic_results']:
            event_data['topics'] = results['topic_results'][cluster.id]

        export_data['events'].append(event_data)

    return json.dumps(export_data, indent=2)


if __name__ == "__main__":
    main()
