"""
Flaky Test Detector for FlakyTestX.

This module is responsible for running test suites multiple times,
collecting test results, and identifying flaky tests.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

import pytest
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

# Import from our own modules
from config import (
    TEST_ITERATIONS,
    RESULTS_DIR,
    FLAKY_THRESHOLD,
    PARALLEL_EXECUTIONS,
    GENERATE_HTML_REPORT,
)
from utils import get_logger

# Set up logger
logger = get_logger(__name__)


class FlakyDetector:
    """
    Detects flaky tests by running the test suite multiple times and analyzing results.
    """

    def __init__(
        self,
        test_path: Union[str, Path],
        iterations: int = TEST_ITERATIONS,
        output_file: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize the flaky test detector.

        Args:
            test_path: Path to test directory or file
            iterations: Number of times to run each test
            output_file: Path to save results
        """
        self.test_path = Path(test_path)
        self.iterations = iterations
        
        # Generate default output file name if not provided
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_file = RESULTS_DIR / f"flaky_results_{timestamp}.json"
        else:
            self.output_file = Path(output_file)
        
        # Create output directory if it doesn't exist
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize results data structure
        self.results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "iterations": iterations,
                "test_path": str(self.test_path),
                "output_file": str(self.output_file),
            },
            "tests": {},
            "summary": {
                "total_tests": 0,
                "flaky_tests": 0,
                "stable_tests": 0,
                "always_pass": 0,
                "always_fail": 0,
                "suite_stability_percentage": 0,
            },
        }

    def run_tests(self) -> Dict[str, Any]:
        """
        Run the test suite multiple times and collect results.

        Returns:
            Dictionary containing test results and flakiness metrics
        """
        logger.info(f"Starting test detection with {self.iterations} iterations")
        logger.info(f"Testing path: {self.test_path}")
        
        # Build test run command
        test_path_str = str(self.test_path)
        
        # Track all discovered tests
        all_tests: Set[str] = set()
        
        # Track pass/fail for each test across iterations
        test_results: Dict[str, List[bool]] = {}
        
        # Run tests multiple times and collect results
        for iteration in tqdm(range(self.iterations), desc="Running test iterations"):
            logger.info(f"Starting iteration {iteration + 1}/{self.iterations}")
            
            # Create a temporary results file for this iteration
            temp_results_file = RESULTS_DIR / f"temp_results_{iteration}.json"
            
            # Run pytest with JSON output
            pytest_args = [
                "-v",
                f"--json-report",
                f"--json-report-file={temp_results_file}",
                "--no-header",
                test_path_str,
            ]
            
            try:
                # Run pytest as a subprocess to isolate test runs
                result = subprocess.run(
                    [sys.executable, "-m", "pytest"] + pytest_args,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                
                # Parse test results from the JSON file
                if temp_results_file.exists():
                    with open(temp_results_file, "r") as f:
                        iteration_results = json.load(f)
                    
                    # Process test results
                    self._process_iteration_results(iteration_results, all_tests, test_results)
                    
                    # Clean up temporary file
                    temp_results_file.unlink()
                else:
                    logger.error(f"Results file not found for iteration {iteration + 1}")
                
            except Exception as e:
                logger.error(f"Error running tests in iteration {iteration + 1}: {e}")
                continue
            
            # Short pause between iterations to avoid resource conflicts
            time.sleep(0.5)
        
        # Calculate flakiness metrics
        self._calculate_flakiness_metrics(all_tests, test_results)
        
        # Save the results
        self._save_results()
        
        # Generate report if enabled
        if GENERATE_HTML_REPORT:
            self._generate_report()
        
        return self.results

    def _process_iteration_results(
        self,
        iteration_results: Dict,
        all_tests: Set[str],
        test_results: Dict[str, List[bool]],
    ) -> None:
        """
        Process results from a single test iteration.

        Args:
            iteration_results: Results from pytest JSON output
            all_tests: Set of all test IDs discovered
            test_results: Dictionary mapping test IDs to pass/fail results
        """
        # Extract test results from pytest JSON output
        if "tests" not in iteration_results:
            logger.warning("No tests found in iteration results")
            return
        
        for test_data in iteration_results["tests"]:
            # Get test ID (nodeid in pytest)
            test_id = test_data.get("nodeid", "")
            if not test_id:
                continue
            
            # Add to set of all tests
            all_tests.add(test_id)
            
            # Initialize list for this test if not already present
            if test_id not in test_results:
                test_results[test_id] = []
            
            # Check test outcome - treat "passed" as True, anything else as False
            passed = test_data.get("outcome") == "passed"
            test_results[test_id].append(passed)
            
            # Store detailed information if not already present
            if test_id not in self.results["tests"]:
                # Get module and test name from test_id
                test_parts = test_id.split("::")
                module = test_parts[0] if len(test_parts) >= 1 else ""
                test_name = test_parts[-1] if len(test_parts) >= 2 else test_id
                
                self.results["tests"][test_id] = {
                    "id": test_id,
                    "module": module,
                    "name": test_name,
                    "results": [],
                    "passes": 0,
                    "failures": 0,
                    "flaky": False,
                    "flaky_score": 0.0,
                    "always_passes": False,
                    "always_fails": False,
                    "logs": [],
                }
                
            # Store test outcome and logs for this iteration
            self.results["tests"][test_id]["results"].append(passed)
            
            # Store log information if available
            if "call" in test_data:
                log_text = test_data["call"].get("longrepr", "")
                if log_text and not passed:  # Only store logs for failures
                    self.results["tests"][test_id]["logs"].append({
                        "iteration": len(test_results[test_id]) - 1,
                        "log": log_text
                    })

    def _calculate_flakiness_metrics(
        self,
        all_tests: Set[str],
        test_results: Dict[str, List[bool]],
    ) -> None:
        """
        Calculate flakiness metrics for all tests.

        Args:
            all_tests: Set of all test IDs discovered
            test_results: Dictionary mapping test IDs to pass/fail results
        """
        # Initialize counters for summary
        total_tests = len(all_tests)
        flaky_tests = 0
        stable_tests = 0
        always_pass = 0
        always_fail = 0
        
        for test_id in all_tests:
            # Skip tests that weren't run in all iterations
            if len(test_results.get(test_id, [])) < self.iterations:
                logger.warning(f"Test {test_id} was not run in all iterations, results may be incomplete")
                continue
            
            # Count passes and failures
            results = test_results[test_id]
            passes = sum(results)
            failures = len(results) - passes
            
            # Update test results
            self.results["tests"][test_id]["passes"] = passes
            self.results["tests"][test_id]["failures"] = failures
            
            # Determine if test is flaky (some passes, some failures)
            is_flaky = 0 < passes < len(results)
            
            # Calculate flakiness score (0.0 = stable, 1.0 = maximally flaky)
            if passes == 0 or passes == len(results):
                flaky_score = 0.0  # Always passes or always fails = not flaky
            else:
                # Most flaky when pass/fail ratio is close to 50/50
                flaky_score = 2.0 * min(passes, failures) / len(results)
            
            # Update test flakiness information
            self.results["tests"][test_id]["flaky"] = is_flaky
            self.results["tests"][test_id]["flaky_score"] = round(flaky_score, 4)
            self.results["tests"][test_id]["always_passes"] = passes == len(results)
            self.results["tests"][test_id]["always_fails"] = failures == len(results)
            
            # Update summary counters
            if is_flaky:
                flaky_tests += 1
            else:
                stable_tests += 1
                if passes == len(results):
                    always_pass += 1
                elif failures == len(results):
                    always_fail += 1
        
        # Calculate overall suite stability percentage
        if total_tests > 0:
            suite_stability_percentage = 100 * (stable_tests - always_fail) / total_tests
        else:
            suite_stability_percentage = 100.0
        
        # Update summary
        self.results["summary"] = {
            "total_tests": total_tests,
            "flaky_tests": flaky_tests,
            "stable_tests": stable_tests,
            "always_pass": always_pass,
            "always_fail": always_fail,
            "suite_stability_percentage": round(suite_stability_percentage, 2),
        }

    def _save_results(self) -> None:
        """
        Save test results to a JSON file.
        """
        try:
            with open(self.output_file, "w") as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Results saved to {self.output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")

    def _generate_report(self) -> None:
        """
        Generate an HTML report and visualization of test results.
        """
        try:
            # Create charts directory if it doesn't exist
            charts_dir = RESULTS_DIR / "charts"
            charts_dir.mkdir(exist_ok=True)
            
            # Generate flakiness bar chart
            self._generate_flakiness_chart(charts_dir)
            
            # Generate test stability pie chart
            self._generate_stability_chart(charts_dir)
            
            logger.info(f"Report generated in {charts_dir}")
        except Exception as e:
            logger.error(f"Error generating report: {e}")

    def _generate_flakiness_chart(self, charts_dir: Path) -> None:
        """
        Generate a bar chart showing flakiness scores.
        
        Args:
            charts_dir: Directory to save chart
        """
        # Extract flaky tests and their scores
        flaky_tests = {
            test_id: data["flaky_score"]
            for test_id, data in self.results["tests"].items()
            if data["flaky"]
        }
        
        if not flaky_tests:
            logger.info("No flaky tests to chart")
            return
        
        # Sort by flakiness score (descending)
        sorted_tests = sorted(flaky_tests.items(), key=lambda x: x[1], reverse=True)
        
        # Prepare chart data
        test_names = [f"{t.split('::')[-1]}" for t, _ in sorted_tests]
        scores = [score for _, score in sorted_tests]
        
        # Create bar chart
        plt.figure(figsize=(12, 6))
        bars = plt.bar(test_names, scores, color='salmon')
        
        # Add labels and title
        plt.xlabel('Test Name')
        plt.ylabel('Flakiness Score (0-1)')
        plt.title('Flakiness Score by Test')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Add values above bars
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f'{score:.2f}', ha='center', va='bottom')
        
        # Save chart
        chart_path = charts_dir / "flakiness_scores.png"
        plt.savefig(chart_path)
        plt.close()
        
        logger.info(f"Flakiness chart saved to {chart_path}")

    def _generate_stability_chart(self, charts_dir: Path) -> None:
        """
        Generate a pie chart showing test stability breakdown.
        
        Args:
            charts_dir: Directory to save chart
        """
        # Extract summary data
        summary = self.results["summary"]
        
        # Prepare chart data
        labels = ['Always Pass', 'Always Fail', 'Flaky Tests']
        sizes = [summary["always_pass"], summary["always_fail"], summary["flaky_tests"]]
        colors = ['#4CAF50', '#F44336', '#FFC107']  # Green, Red, Yellow
        
        # Create pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                startangle=90, shadow=True)
        plt.axis('equal')
        plt.title('Test Stability Breakdown')
        
        # Save chart
        chart_path = charts_dir / "test_stability.png"
        plt.savefig(chart_path)
        plt.close()
        
        logger.info(f"Stability chart saved to {chart_path}")


def main():
    """
    Main function for running the flaky test detector from command line.
    """
    parser = argparse.ArgumentParser(description="FlakyTestX - Flaky Test Detector")
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
        help="Output file path (default: auto-generated in results directory)"
    )
    args = parser.parse_args()
    
    # Initialize and run flaky detector
    detector = FlakyDetector(
        test_path=args.path,
        iterations=args.iterations,
        output_file=args.output,
    )
    results = detector.run_tests()
    
    # Print summary to console
    summary = results["summary"]
    print("\n" + "=" * 40)
    print("FlakyTestX Analysis Summary")
    print("=" * 40)
    print(f"Total tests: {summary['total_tests']}")
    print(f"Flaky tests: {summary['flaky_tests']}")
    print(f"Suite stability: {summary['suite_stability_percentage']}%")
    print("=" * 40)
    
    if summary['flaky_tests'] > 0:
        print("\nFlaky Tests Detected:")
        for test_id, data in results["tests"].items():
            if data["flaky"]:
                print(f"  - {data['name']} (in {data['module']})")
                print(f"    Flakiness score: {data['flaky_score']:.2f}")
                print(f"    Passed {data['passes']}/{data['passes'] + data['failures']} runs")
    
    print(f"\nDetailed results saved to: {detector.output_file}")
    
    return results


if __name__ == "__main__":
    main()