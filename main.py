#!/usr/bin/env python3
"""
Main entry point for the World News Analysis System

This system uses multiple AI agents to:
1. Aggregate news from various sources
2. Cluster articles by event
3. Analyze rhetoric and language patterns over time
4. Predict event trajectories

Usage:
    python main.py --mode full --days 7
    python main.py --mode update --days 1
    python main.py --mode status
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents import CoordinatorAgent


def load_config():
    """Load configuration from environment variables"""
    load_dotenv()

    config = {
        'newsapi_key': os.getenv('NEWSAPI_KEY'),
        'guardian_key': os.getenv('GUARDIAN_API_KEY'),
        'similarity_threshold': float(os.getenv('SIMILARITY_THRESHOLD', '0.7')),
        'min_cluster_size': int(os.getenv('MIN_ARTICLES_PER_CLUSTER', '2')),
        'time_period_days': int(os.getenv('ANALYSIS_LOOKBACK_DAYS', '30'))
    }

    return config


def check_api_keys(config):
    """Check if API keys are configured"""
    has_newsapi = bool(config.get('newsapi_key'))
    has_guardian = bool(config.get('guardian_key'))

    if not has_newsapi and not has_guardian:
        print("\n⚠️  WARNING: No API keys configured!")
        print("\nTo use this system, you need at least one news API key:")
        print("1. NewsAPI (https://newsapi.org) - Free tier: 100 requests/day")
        print("2. Guardian API (https://open-platform.theguardian.com) - Free, unlimited")
        print("\nCreate a .env file with your keys:")
        print("NEWSAPI_KEY=your_key_here")
        print("GUARDIAN_API_KEY=your_key_here")
        print("\nSee .env.example for reference.")
        return False

    print("\n✅ API Configuration:")
    if has_newsapi:
        print("   - NewsAPI: Configured")
    else:
        print("   - NewsAPI: Not configured (optional)")

    if has_guardian:
        print("   - Guardian API: Configured")
    else:
        print("   - Guardian API: Not configured (optional)")

    print()
    return True


def main():
    parser = argparse.ArgumentParser(
        description='World News Analysis System - Multi-Agent News Analysis'
    )

    parser.add_argument(
        '--mode',
        choices=['full', 'update', 'status'],
        default='full',
        help='Operation mode: full (complete analysis), update (add new articles), status (show system status)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back for news (default: 7)'
    )

    parser.add_argument(
        '--use-existing',
        action='store_true',
        help='Use existing articles instead of fetching new ones'
    )

    parser.add_argument(
        '--export',
        type=str,
        help='Export report to specified filename'
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Check API keys (skip for status mode)
    if args.mode != 'status':
        if not check_api_keys(config):
            return 1

    # Initialize coordinator
    coordinator = CoordinatorAgent(config)

    try:
        if args.mode == 'full':
            # Run full analysis
            results = coordinator.run_full_analysis(
                days_back=args.days,
                use_existing=args.use_existing
            )

            # Print summary
            print("\n" + "="*60)
            print("📊 RESULTS SUMMARY")
            print("="*60)
            print(f"Articles collected: {results.get('total_articles', 0)}")
            print(f"Events identified: {results.get('total_clusters', 0)}")
            print(f"Analyses performed: {results.get('total_analyses', 0)}")
            print(f"Predictions generated: {results.get('total_predictions', 0)}")

            # Export report if requested
            if args.export:
                coordinator.export_report(results, args.export)
            else:
                # Auto-export
                coordinator.export_report(results)

            # Print report preview
            if results.get('report'):
                print("\n" + "="*60)
                print("📄 REPORT PREVIEW")
                print("="*60)
                report_lines = results['report'].split('\n')
                for line in report_lines[:50]:  # First 50 lines
                    print(line)
                if len(report_lines) > 50:
                    print("\n... (see full report in exported file)")

        elif args.mode == 'update':
            # Update existing analysis
            results = coordinator.update_analysis(days_back=args.days)
            print("\n✅ Update complete!")
            print(f"New articles: {results.get('new_articles', 0)}")
            print(f"Total clusters: {results.get('total_clusters', 0)}")

        elif args.mode == 'status':
            # Show system status
            status = coordinator.get_status()
            print("\n" + "="*60)
            print("SYSTEM STATUS")
            print("="*60)
            print("\nStorage Paths:")
            for key, path in status['storage_paths'].items():
                print(f"  {key}: {path}")
            print("\nAgent Status:")
            for agent, state in status['agents'].items():
                print(f"  {agent}: {state}")
            print("\nConfiguration:")
            for key, value in status['config'].items():
                if 'key' in key.lower():
                    value = '***' if value else 'not set'
                print(f"  {key}: {value}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
