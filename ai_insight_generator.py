"""
AI Insight Generator for FlakyTestX.

This module analyzes flaky tests using AI and generates insights and suggestions for fixing them.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union

from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    MOCK_AI_RESPONSES,
    AI_ENABLED,
)
from utils import get_logger

# Set up logger
logger = get_logger(__name__)

# Conditionally import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI package not installed. Using mock responses.")
    OPENAI_AVAILABLE = False


class AIInsightGenerator:
    """
    Generates insights for flaky tests using AI models.
    """

    def __init__(
        self,
        results_file: Union[str, Path],
        openai_api_key: Optional[str] = OPENAI_API_KEY,
        openai_model: str = OPENAI_MODEL,
        mock_responses: bool = MOCK_AI_RESPONSES,
    ):
        self.results_file = Path(results_file)
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.mock_responses = mock_responses or not OPENAI_AVAILABLE
        self.client = self._initialize_openai_client()
        self.results = self._load_results()
        self.insights = self._initialize_insights()

    def _initialize_openai_client(self):
        """Initialize the OpenAI client if available."""
        if not self.mock_responses and self.openai_api_key:
            try:
                return openai.OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        return None

    def _load_results(self) -> Dict[str, Any]:
        """Load flaky test results from a JSON file."""
        try:
            with open(self.results_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading results from {self.results_file}: {e}")
            return {"tests": {}}

    def _initialize_insights(self) -> Dict[str, Any]:
        """Initialize the insights dictionary."""
        return {
            "metadata": {
                "source_file": str(self.results_file),
                "mock_responses": self.mock_responses,
            },
            "insights": {},
        }

    def generate_insights(self) -> Dict[str, Any]:
        """Generate insights for flaky tests."""
        if not AI_ENABLED:
            logger.info("AI insights are disabled in the configuration.")
            return self.insights

        flaky_tests = self._get_flaky_tests()
        if not flaky_tests:
            logger.info("No flaky tests found in the results.")
            return self.insights

        logger.info(f"Generating insights for {len(flaky_tests)} flaky tests.")
        for test_id, test_data in flaky_tests.items():
            try:
                insight = self._generate_test_insight(test_id, test_data)
                self.insights["insights"][test_id] = insight
            except Exception as e:
                logger.error(f"Error generating insight for {test_id}: {e}")

        self._save_insights()
        return self.insights

    def _get_flaky_tests(self) -> Dict[str, Any]:
        """Extract flaky tests from the results."""
        return {
            test_id: data
            for test_id, data in self.results.get("tests", {}).items()
            if data.get("flaky", False)
        }

    def _generate_test_insight(self, test_id: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insight for a single flaky test."""
        prompt = self._create_prompt(test_id, test_data)
        response_text = self._get_ai_response(prompt)
        return self._parse_ai_response(response_text, test_id, test_data)

    def _create_prompt(self, test_id: str, test_data: Dict[str, Any]) -> str:
        """Create a prompt for the AI model."""
        test_name = test_data.get("name", test_id.split("::")[-1])
        module = test_data.get("module", test_id.split("::")[0])
        flaky_score = test_data.get("flaky_score", 0.0)
        passes = test_data.get("passes", 0)
        failures = test_data.get("failures", 0)
        error_logs = "\n".join(log.get("log", "") for log in test_data.get("logs", [])) or "No error logs available."

        return f"""
You are an expert in test automation. Analyze the following flaky test:

Test ID: {test_id}
Test Name: {test_name}
Module: {module}
Flakiness Score: {flaky_score:.2f}
Passes: {passes}
Failures: {failures}

Error Logs:
{error_logs}

Provide:
1. Root cause analysis
2. Likely reason for flakiness
3. Recommendations to fix the test
4. Suggested code fix (if possible)
"""

    def _get_ai_response(self, prompt: str) -> str:
        """Get a response from the AI model or mock response."""
        if self.mock_responses:
            return self._get_mock_response()
        try:
            completion = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.2,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return self._get_mock_response()

    def _get_mock_response(self) -> str:
        """Return a mock response for testing."""
        return "Mock response: Unable to analyze the test due to insufficient data."

    def _parse_ai_response(self, response: str, test_id: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the AI response into structured insights."""
        return {
            "test_id": test_id,
            "test_name": test_data.get("name", test_id),
            "module": test_data.get("module", ""),
            "root_cause": response,
            "recommendations": response,
            "code_fix": response,
        }

    def _save_insights(self) -> None:
        """Save insights to a JSON file."""
        output_file = self.results_file.with_name(f"{self.results_file.stem}_insights.json")
        try:
            with open(output_file, "w") as f:
                json.dump(self.insights, f, indent=2)
            logger.info(f"Insights saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving insights: {e}")


def main():
    """Main function to run the AI insight generator."""
    parser = argparse.ArgumentParser(description="FlakyTestX - AI Insight Generator")
    parser.add_argument("--results", "-r", required=True, help="Path to flaky test results JSON file")
    parser.add_argument("--openai-api-key", help="OpenAI API key")
    parser.add_argument("--openai-model", default=OPENAI_MODEL, help="OpenAI model to use")
    parser.add_argument("--mock", action="store_true", help="Use mock responses instead of actual API calls")
    args = parser.parse_args()

    generator = AIInsightGenerator(
        results_file=args.results,
        openai_api_key=args.openai_api_key,
        openai_model=args.openai_model,
        mock_responses=args.mock,
    )
    insights = generator.generate_insights()

    print("\n" + "=" * 40)
    print("FlakyTestX AI Insights")
    print("=" * 40)
    if not insights["insights"]:
        print("No insights generated.")
    else:
        for test_id, insight in insights["insights"].items():
            print(f"\n- {insight['test_name']} (in {insight['module']})")
            print(f"  Root cause: {insight['root_cause'][:60]}...")
            print(f"  Recommendation: {insight['recommendations'][:60]}...")


if __name__ == "__main__":
    main()