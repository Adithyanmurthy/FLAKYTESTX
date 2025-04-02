# FlakyTestX

## AI-Powered Flaky Test Detection and Resolution

![FlakyTestX Logo](https://via.placeholder.com/150x150?text=FlakyTestX)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A solution for the Kyiv QA Automation Summit 2025

## What is FlakyTestX?

FlakyTestX is a powerful tool that automatically detects flaky tests in your test suite and uses AI to provide actionable recommendations for fixing them. Flaky tests (those that inconsistently pass or fail without code changes) waste developer time and erode confidence in test suites. FlakyTestX transforms this persistent challenge into a solvable problem.

## Features

- 🔄 **Automated Flaky Test Detection**: Runs your test suite multiple times to identify inconsistent behavior
- 📊 **Statistical Analysis**: Calculates a flakiness score for each test based on pass/fail patterns
- 🤖 **AI-Powered Root Cause Analysis**: Examines test code and failure patterns to determine why tests are flaky
- 🛠️ **Actionable Fix Recommendations**: Provides specific suggestions and code examples to fix each flaky test
- 📈 **Interactive Dashboard**: Visualizes test stability and flakiness patterns for easy exploration

## Prerequisites

- Python 3.8 or higher
- Pytest-based test suite
- (Optional) OpenAI API key for enhanced AI insights

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/flakytestx.git
cd flakytestx

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following variables:

```
OPENAI_API_KEY=your_openai_api_key_here  # Optional, will use mock responses if not provided
TEST_ITERATIONS=10                        # Default number of test iterations
AI_ENABLED=true                           # Enable/disable AI features
```

## Usage

### Quick Start

Run a complete analysis of your test suite and view results in the dashboard:

```bash
python run_all.py --path path/to/tests/ --iterations 10 --dashboard
```

### Component Usage

FlakyTestX can be used in several ways depending on your needs:

#### 1. Detect Flaky Tests

Identify which tests in your suite are flaky:

```bash
python flaky_detector.py --path path/to/tests/ --iterations 5
```

#### 2. Generate AI Insights

Analyze previously identified flaky tests:

```bash
python ai_insight_generator.py --results path/to/results.json
```

#### 3. View Results Dashboard

Explore test results through an interactive dashboard:

```bash
python -m streamlit run dashboard.py
```

## Project Structure

```
FlakyTestX/
├── flaky_detector.py      # Detects flaky tests through multiple runs
├── ai_insight_generator.py # Analyzes flaky tests with AI
├── run_all.py             # Main entry point for full pipeline
├── dashboard.py           # Streamlit dashboard for visualization
├── config.py              # Configuration settings
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── logger.py          # Logging utilities
├── tests/                 # Sample test files
│   ├── test_sample1.py    # Example tests including flaky ones
│   └── test_sample2.py    # More example tests
└── results/               # Output directory for test results
```

## Command Line Arguments

### run_all.py

```
--path, -p         Path to test directory or file (required)
--iterations, -i   Number of test iterations (default: from config)
--output, -o       Custom output file path (optional)
--dashboard, -d    Launch dashboard after analysis
--no-ai            Disable AI analysis
```

### flaky_detector.py

```
--path, -p         Path to test directory or file (required)
--iterations, -i   Number of test iterations (default: from config)
--output, -o       Custom output file path (optional)
```

### ai_insight_generator.py

```
--results, -r      Path to results JSON file (required)
--openai-api-key   OpenAI API key (overrides env variable)
--openai-model     OpenAI model to use (default: from config)
--mock             Use mock responses instead of actual API calls
```

## Understanding the Results

### Flakiness Score

Tests are assigned a flakiness score from 0.0 to 1.0:
- **0.0**: The test consistently passes or fails (stable)
- **~1.0**: The test fails approximately 50% of the time (maximally flaky)

### AI Insights

For each flaky test, the AI generates:
- Root cause analysis
- Likely reason for flakiness
- Specific recommendations to fix the test
- Sample code fix implementation

## Example Output

```
================================
FlakyTestX Analysis Results
================================

📋 Test Suite Summary:
- Total tests: 12
- Flaky tests detected: 3
- Overall suite stability: 75%

🔍 Flaky Test Details:
1. test_async_api_call (test_sample1.py) - Flakiness: 60%
   └─ AI Insight: Race condition in asynchronous API call
   └─ Suggestion: Add proper awaiting with timeout and implement retry mechanism
```

## Troubleshooting

### Missing Dependencies

If you encounter errors about missing modules, ensure you've installed all dependencies:

```bash
pip install -r requirements.txt
```

### OpenAI API Issues

If you see "mock responses" in your AI insights:
1. Verify your OpenAI API key is correctly set in the `.env` file
2. Check your API usage limits and billing status

### Dashboard Not Loading

If the dashboard fails to launch:
1. Ensure Streamlit is installed: `pip install streamlit`
2. Try running it manually: `python -m streamlit run dashboard.py`
3. If port 8501 is in use, specify a different port: `streamlit run dashboard.py --server.port 8502`

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- The OpenAI team for providing the API that powers our AI insights
- The Pytest development team for their excellent testing framework
- The Streamlit team for their powerful data visualization platform

---

Built with ❤️ for the Kyiv QA Automation Summit 2025
