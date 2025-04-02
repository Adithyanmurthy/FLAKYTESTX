"""
Dashboard for FlakyTestX.

This module provides a Streamlit-based dashboard for visualizing
flaky test results and insights.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Import from our own modules
from config import RESULTS_DIR
from utils import get_logger

# Set up logger
logger = get_logger(__name__)


def load_results_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load test results from a JSON file.
    
    Args:
        file_path: Path to JSON results file
        
    Returns:
        Dictionary containing test results
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading results file: {e}")
        return {}


def load_insights_file(results_file: Union[str, Path]) -> Dict[str, Any]:
    """
    Load AI insights for test results.
    
    Args:
        results_file: Path to results file (insights file name is derived from this)
        
    Returns:
        Dictionary containing insights
    """
    # Generate insights file path based on results file
    results_path = Path(results_file)
    insights_path = results_path.with_name(f"{results_path.stem}_insights.json")
    
    # Check if insights file exists
    if not insights_path.exists():
        return {}
    
    # Load insights
    try:
        with open(insights_path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading insights file: {e}")
        return {}


def get_results_files() -> List[Path]:
    """
    Get list of available results files.
    
    Returns:
        List of paths to results files
    """
    results_dir = Path(RESULTS_DIR)
    if not results_dir.exists():
        return []
    
    # Find all JSON files that don't have "_insights" in the name
    return sorted(
        [f for f in results_dir.glob("*.json") if "_insights" not in f.name],
        key=lambda f: f.stat().st_mtime,
        reverse=True,  # Most recent first
    )


def display_summary(results: Dict[str, Any]) -> None:
    """
    Display summary information for test results.
    
    Args:
        results: Test results dictionary
    """
    if not results or "summary" not in results:
        st.warning("No summary information available")
        return
    
    summary = results["summary"]
    metadata = results.get("metadata", {})
    
    # Display metadata
    st.subheader("Test Run Information")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Test Path", metadata.get("test_path", "Unknown"))
    with col2:
        st.metric("Iterations", metadata.get("iterations", 0))
    with col3:
        timestamp = metadata.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        st.metric("Timestamp", timestamp)
    
    # Display summary metrics
    st.subheader("Test Results Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tests", summary.get("total_tests", 0))
    with col2:
        st.metric("Flaky Tests", summary.get("flaky_tests", 0))
    with col3:
        st.metric("Always Pass", summary.get("always_pass", 0))
    with col4:
        st.metric("Always Fail", summary.get("always_fail", 0))
    
    # Create and display stability pie chart
    st.subheader("Test Stability Overview")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    labels = ["Always Pass", "Always Fail", "Flaky Tests"]
    sizes = [
        summary.get("always_pass", 0),
        summary.get("always_fail", 0),
        summary.get("flaky_tests", 0),
    ]
    colors = ["#4CAF50", "#F44336", "#FFC107"]  # Green, Red, Yellow
    
    # Only plot if there's data
    if sum(sizes) > 0:
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                startangle=90, shadow=True)
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.info("No data available for chart")


def display_flaky_tests(
    results: Dict[str, Any],
    insights: Dict[str, Any],
) -> None:
    """
    Display information about flaky tests.
    
    Args:
        results: Test results dictionary
        insights: Test insights dictionary
    """
    if not results or "tests" not in results:
        st.warning("No test information available")
        return
    
    # Extract flaky tests
    flaky_tests = {
        test_id: data
        for test_id, data in results["tests"].items()
        if data.get("flaky", False)
    }
    
    if not flaky_tests:
        st.info("No flaky tests detected")
        return
    
    # Create and display flakiness score chart
    st.subheader("Flakiness Scores")
    
    # Extract data for chart
    test_names = [data.get("name", test_id.split("::")[-1]) 
                 for test_id, data in flaky_tests.items()]
    scores = [data.get("flaky_score", 0.0) for _, data in flaky_tests.items()]
    
    # Sort by score descending
    sorted_indices = np.argsort(scores)[::-1]
    test_names = [test_names[i] for i in sorted_indices]
    scores = [scores[i] for i in sorted_indices]
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(test_names, scores, color='salmon')
    
    # Add labels and formatting
    ax.set_xlabel('Test Name')
    ax.set_ylabel('Flakiness Score (0-1)')
    ax.set_title('Flakiness Score by Test')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Add values above bars
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f'{score:.2f}', ha='center', va='bottom')
    
    st.pyplot(fig)
    
    # Display detailed information for each flaky test
    st.subheader("Flaky Test Details")
    
    for test_id, data in flaky_tests.items():
        with st.expander(f"{data.get('name', test_id)} - Flakiness: {data.get('flaky_score', 0.0):.2f}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Passes", data.get("passes", 0))
            with col2:
                st.metric("Failures", data.get("failures", 0))
            with col3:
                pass_rate = data.get("passes", 0) / (data.get("passes", 0) + data.get("failures", 0)) * 100 if data.get("passes", 0) + data.get("failures", 0) > 0 else 0
                st.metric("Pass Rate", f"{pass_rate:.1f}%")
            
            # Display test results as a sequence of pass/fail
            st.markdown("**Test Run Results:**")
            results_str = ""
            for i, result in enumerate(data.get("results", [])):
                if result:
                    results_str += "✅ "
                else:
                    results_str += "❌ "
                # Add line break every 10 results
                if (i + 1) % 10 == 0:
                    results_str += "\n"
            st.text(results_str)
            
            # Display AI insights if available
            if insights and "insights" in insights and test_id in insights["insights"]:
                test_insight = insights["insights"][test_id]
                
                st.markdown("### 🤖 AI Analysis")
                
                if test_insight.get("root_cause"):
                    st.markdown("**Root Cause:**")
                    st.markdown(test_insight["root_cause"])
                
                if test_insight.get("recommendations"):
                    st.markdown("**Recommendations:**")
                    st.markdown(test_insight["recommendations"])
                
                if test_insight.get("code_fix"):
                    st.markdown("**Suggested Code Fix:**")
                    st.code(test_insight["code_fix"], language="python")
            
            # Display error logs
            if data.get("logs"):
                st.markdown("### ⚠️ Error Logs")
                for log_entry in data.get("logs", []):
                    st.markdown(f"**Iteration {log_entry.get('iteration', '?')}:**")
                    st.text(log_entry.get("log", "No log available"))


def main():
    """
    Main function for the Streamlit dashboard.
    """
    st.set_page_config(
        page_title="FlakyTestX Dashboard",
        page_icon="🧪",
        layout="wide",
    )
    
    st.title("🧪 FlakyTestX Dashboard")
    st.markdown("### AI-Powered Flaky Test Detection and Analysis")
    
    # Get available results files
    results_files = get_results_files()
    
    if not results_files:
        st.warning("No test results found. Run the flaky test detector first.")
        return
    
    # Create file selector
    selected_file = st.sidebar.selectbox(
        "Select Results File",
        options=results_files,
        format_func=lambda x: f"{x.stem} ({datetime.fromtimestamp(x.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})",
    )
    
    if selected_file:
        # Load selected results file
        results = load_results_file(selected_file)
        
        # Load insights if available
        insights = load_insights_file(selected_file)
        
        if not results:
            st.error("Failed to load results file")
            return
        
        # Display results
        display_summary(results)
        st.markdown("---")
        display_flaky_tests(results, insights)
    else:
        st.info("Select a results file from the sidebar to view details")


if __name__ == "__main__":
    main()