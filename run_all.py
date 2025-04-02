"""
Main entry point for FlakyTestX.

This module connects all components of FlakyTestX:
1. Flaky test detector
2. AI insight generator
3. Dashboard (optional)
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from config import TEST_ITERATIONS, AI_ENABLED
from flaky_detector import FlakyDetector
from ai_insight_generator import AIInsightGenerator
from utils import get_logger

# Set up logger
logger = get_logger(__name__)


def run_flaky_detection(
    test_path: str,
    iterations: int = TEST_ITERATIONS,
    output_file: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run flaky test detection on the specified test path.
    
    Args:
        test_path: Path to test directory or file
        iterations: Number of test iterations
        output_file: Path to output file (optional)
        
    Returns:
        Dictionary containing test results
    """
    logger.info(f"Starting flaky test detection on {test_path}")
    
    # Initialize flaky detector
    detector = FlakyDetector(
        test_path=test_path,
        iterations=iterations,
        output_file=output_file,
    )
    
    # Run tests and get results
    results = detector.run_tests()
    
    logger.info(f"Flaky test detection completed. Found {results['summary']['flaky_tests']} flaky tests.")
    
    return results


def run_ai_analysis(results_file: str) -> Dict[str, Any]:
    """
    Run AI analysis on flaky test results.
    
    Args:
        results_file: Path to results file
        
    Returns:
        Dictionary containing insights
    """
    if not AI_ENABLED:
        logger.info("AI analysis disabled in configuration. Skipping.")
        return {}
    
    logger.info(f"Starting AI analysis on {results_file}")
    
    # Initialize AI insight generator
    generator = AIInsightGenerator(
        results_file=results_file,
    )
    
    # Generate insights
    insights = generator.generate_insights()
    
    logger.info(f"AI analysis completed. Generated insights for {len(insights.get('insights', {}))} tests.")
    
    return insights


def launch_dashboard() -> None:
    """
    Launch the Streamlit dashboard.
    """
    logger.info("Launching dashboard")
    
    try:
        # Check if Streamlit is installed
        import streamlit
        
        # Get path to dashboard.py
        dashboard_path = Path(__file__).parent / "dashboard.py"
        
        # Launch dashboard in a subprocess
        subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", str(dashboard_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        logger.info("Dashboard launched. Access at http://localhost:8501")
        print("\nDashboard is now running at http://localhost:8501")
    except ImportError:
        logger.error("Streamlit not installed. Cannot launch dashboard.")
        print("\nCannot launch dashboard: Streamlit not installed.")
        print("Install with: pip install streamlit")
    except Exception as e:
        logger.error(f"Error launching dashboard: {e}")
        print(f"\nError launching dashboard: {e}")


def print_summary(results: Dict[str, Any], insights: Dict[str, Any]) -> None:
    """
    Print a summary of the results and insights to the console.
    
    Args:
        results: Test results dictionary
        insights: Test insights dictionary
    """
    if not results:
        print("No results available")
        return
    
    summary = results.get("summary", {})
    
    print("\n" + "=" * 60)
    print("FlakyTestX Analysis Results")
    print("=" * 60)
    
    print("\n📋 Test Suite Summary:")
    print(f"- Total tests: {summary.get('total_tests', 0)}")
    print(f"- Flaky tests detected: {summary.get('flaky_tests', 0)}")
    print(f"- Overall suite stability: {summary.get('suite_stability_percentage', 0)}%")
    
    # Print flaky test details
    flaky_tests = {
        test_id: data
        for test_id, data in results.get("tests", {}).items()
        if data.get("flaky", False)
    }
    
    if flaky_tests:
        print("\n🔍 Flaky Test Details:")
        
        for i, (test_id, data) in enumerate(flaky_tests.items(), 1):
            test_name = data.get("name", test_id.split("::")[-1])
            module = data.get("module", test_id.split("::")[0])
            flaky_score = data.get("flaky_score", 0.0)
            
            print(f"{i}. {test_name} ({module}) - Flakiness: {flaky_score:.0%}")
            
            # Include AI insights if available
            if insights and "insights" in insights and test_id in insights["insights"]:
                test_insight = insights["insights"][test_id]
                
                if test_insight.get("root_cause"):
                    root_cause_first_line = test_insight['root_cause'].split('\n')[0]
                    print(f"   └─ AI Insight: {root_cause_first_line}")
                
                if test_insight.get("recommendations"):
                    root_cause_first_line = test_insight['root_cause'].split('\n')[0]
                    print(f"   └─ AI Insight: {root_cause_first_line}")
    
    print("\nResults saved to:", results.get("metadata", {}).get("output_file", "Unknown"))
    
    if AI_ENABLED:
        print("\nView detailed results and insights in the dashboard!")
    else:
        print("\nAI analysis is disabled. Enable it in config.py to get fix suggestions.")


def main():
    """
    Main entry point for FlakyTestX.
    """
    parser = argparse.ArgumentParser(description="FlakyTestX - Flaky Test Detector and Analyzer")
    parser.add_argument(
        "--path", "-p", 
        type=str, 
        required=True,
        help="Path to test directory or file"
    )
    parser.add_argument(
        "--iterations", "-i", 
        type=int, 
        default=TEST_ITERATIONS,
        help=f"Number of test iterations (default: {TEST_ITERATIONS})"
    )
    parser.add_argument(
        "--output", "-o", 
        type=str, 
        default=None,
        help="Output file path (default: auto-generated)"
    )
    parser.add_argument(
        "--dashboard", "-d", 
        action="store_true",
        help="Launch dashboard after analysis"
    )
    parser.add_argument(
        "--no-ai", 
        action="store_true",
        help="Disable AI analysis"
    )
    args = parser.parse_args()
    
    # Run flaky test detection
    results = run_flaky_detection(
        test_path=args.path,
        iterations=args.iterations,
        output_file=args.output,
    )
    
    # Run AI analysis if enabled
    insights = {}
    if not args.no_ai and AI_ENABLED and results["summary"]["flaky_tests"] > 0:
        insights = run_ai_analysis(results_file=results.get("metadata", {}).get("output_file"))
    
    # Print summary
    print_summary(results, insights)
    
    # Launch dashboard if requested
    if args.dashboard:
        launch_dashboard()


if __name__ == "__main__":
    main()